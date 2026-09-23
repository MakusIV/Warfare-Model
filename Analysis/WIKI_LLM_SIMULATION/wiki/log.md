# Log delle Operazioni Wiki

## [2026-09-23] implementazione | Fase 7 del motore DES: validazione — MOTORE COMPLETO (7/7 fasi)

Scenari S1-S18 (batteria estesa da 11 a 18 su richiesta dell'utente, con 7 nuovi scenari legati
alla classificazione reale Block/mil_category del progetto), harness `Test/Scenario_Fixtures.py`,
test di determinismo e agnosticismo (`Test/Test_Session_Validation.py` — agnosticismo come test di
contratto, nessun adapter DCS esiste ancora nel codice Python). Durante la scrittura dei test sono
stati trovati e corretti 5 bug pre-esistenti mai innescati in produzione (costruttori rotti di
`Transport`/`Storage`/`Urban`/`Production`/`Structure`, `Block.set_asset` che rifiutava le
sottoclassi di `Asset`), aggiunta la regola "i blocchi non-Military non si disingaggiano mai", e
ricalibrata la saturazione difensiva della Fase 4 (nuovo `Mobile.interceptor_stock` distinto dalle
munizioni offensive, pool condiviso per i SAM puri dopo verifica sui registri, nuovo tipo
`InterceptionEvent`). Sei agenti Opus effort alto in sequenza nella stessa sessione. Verificato
dalla sessione principale ad ogni passo: suite finale **3371 test OK (skipped=5)**. Dettaglio in
[[project_virtual_session_engine_design]], pagina [[virtual-session-engine-des]] aggiornata.
**Il motore di sessioni virtuali a 7 fasi è completo.**

## [2026-09-23] implementazione | Fase 6 del motore DES: Session_Simulator + ingaggi N-forze

`Logic/Session_Simulator.py` (nuovo): orchestratore a coda eventi che mette in fila
`Contact_Scheduler`→`Engagement_Resolver`→`Fuel_Model`→`Session_Types.assemble_session_outcome`
per una sessione con più forze per lato. In corso d'opera, su richiesta dell'utente, due estensioni:
fix del bug id casuale di `Block`/`Military` (nuovo parametro `id` opzionale, retrocompatibile) e
generalizzazione di `Engagement_Resolver.resolve_engagement` a N forze simultanee (`extra_forces`,
`contact_broken` diventato `broken_forces` per-forza) con `Session_Simulator` che raggruppa le
forze per componenti connesse invece che per coppie — risolve un difetto reale (non solo
un'approssimazione) sulle forze impegnate su più fronti sovrapposti nel tempo. Tre agenti Opus
effort alto in sequenza nella stessa sessione. Verificato dalla sessione principale: suite
rieseguita indipendentemente ad ogni passo, **3168 test OK (skipped=5)** finali (da 3115).
Dettaglio in [[project_virtual_session_engine_design]], pagina [[virtual-session-engine-des]]
aggiornata. Non ancora committato.

## [2026-09-23] implementazione | Fase 5 del motore DES: SessionOutcome, RNG di sessione, carburante

`Command/Session_Types.py` (`SessionOrder`/`SessionOutcome`/`assemble_session_outcome`, chiude anche
la "Fase 0" del contratto di dominio mai fatta), `Utility/Session_Rng.py` (seed SHA-256 su chiave
canonica, mai `hash()` di Python), `Logic/Fuel_Model.py` + carburante su `Mobile`/`Aircraft`
(frazione del carico pieno, non kg — confermato dall'utente; fattore 2× sul raggio aerei —
confermato; navi nucleari non modellate — confermato). Implementato da un secondo agente Opus
effort alto nella stessa sessione della Fase 4. Verificato dalla sessione principale: suite
rieseguita indipendentemente, **3115 test OK (skipped=5)**, +88 sulla Fase 4. Dettaglio in
[[project_virtual_session_engine_design]] (memoria), pagina [[virtual-session-engine-des]]
aggiornata con lo stato Fase 3-5. Non ancora committato.

## [2026-09-23] implementazione | Fase 4 del motore DES: Engagement_Resolver.py

`Logic/Engagement_Resolver.py` + `Context/Reaction_Profile.py` (nuovi), estesi `Context/Doctrine.py`
(soglie di disingaggio), `Block/Military.py` (`salvo_interceptors`/`salvo_interception_capacity`),
`Asset/Mobile.py` (munizioni per asset). Implementato da un agente Opus effort alto su richiesta
dell'utente, con le 3 decisioni accettate in questa stessa sessione (v. voce sotto) come vincoli.
Verificato dalla sessione principale: suite completa rieseguita indipendentemente, **3002 test OK
(skipped=5)**, +144 sulla baseline Fase 3 (2858). Dettaglio in
[[project_virtual_session_engine_design]] (memoria), pagine [[soglie-disingaggio-e-attrito-aggregato]]
e [[risolutore-ingaggio-salva-fase4]] aggiornate con nota di implementazione completata. **11 punti
aperti di calibrazione** lasciati con l'opzione conservativa (selezione arma, ripartizione fuoco,
finestra di salvo, munizioni aerei, degradazione Pd meteo/notte — lista completa in memoria), non
ancora sottoposti all'utente. Nessun commit ancora eseguito.

## [2026-09-23] aggiornamento | Cadenza sessioni virtuali (6) e riarmo post-sessione confermati

Rilettura OCR (fast + docling, concordi) di `Analysis/Document/Prospetto:Moduli.Analisi.e.Decisioni.pdf`
pag. 3, poi confermata dall'utente: dopo una sessione DCS il motore esegue **6 sessioni virtuali**
(il PDF mostra anche "3 sessioni DCS" sulla stessa pagina, rapporto 3:6 nel disegno originale, ma
solo il 6 è stato re-confermato come vincolante). L'utente ha inoltre precisato che **dopo ogni
sessione** (non solo le virtuali) la campagna deve aggiornare stato — perdite, consumi — **e
riarmare gli asset** prima di poter pianificare/eseguire la sessione successiva. Aggiornata
[[c2-hierarchy-design]] (modello sessioni + punto 5 di `Theater_Session_Manager`) e
[[project_c2_hierarchy_design]] (memoria). Collega il rifornimento munizioni della Fase 4
([[risolutore-ingaggio-salva-fase4]] R3, che lo rimanda esplicitamente "al ciclo di campagna") a
questo punto esatto del ciclo C2 — nessun codice ancora coinvolto (`Theater_Session_Manager.py`
non esiste ancora).

## [2026-09-23] decisione | Le 3 proposte pendenti su Fase 4: risposta dell'utente

L'utente ha risposto alle tre proposte lasciate `status: proposed` a fine sessione 2026-09-22:

- **[[soglie-disingaggio-e-attrito-aggregato]] → accepted**: P1 (soglia di disingaggio) e P3
  (batteria S1-S11) accettate; P2 resta nota d'orientamento. Soglia in `Context/Doctrine.py`,
  granularità per forza intera, `calcFightResult` intatto fino a dopo la Fase 4, S1-S11 solo Fase 7.
- **[[llm-locale-ruolo-e-confini]] → resta proposed, rimandata**: "per il momento non consideriamo
  LLM nel motore" — non un rifiuto, nessuna delle opzioni R1-R4 formalizzata.
- **[[risolutore-ingaggio-salva-fase4]] → accepted**: R1-R4 accettate integralmente. Capacità di
  intercettazione in funzione dedicata; soglia di shock stessa sede/granularità di P1; munizioni
  per asset con rifornimento fuori scope; congelamento payload subito, re-scheduling rimandato.

Prossimo passo: implementazione di `Logic/Engagement_Resolver.py` + `Context/Reaction_Profile.py`
(Fase 4 del motore DES), con le scelte sopra come vincoli di design.

## [2026-09-22] ingestione | Modello event-driven a salva di Hughes (RAW/Event_Driven_Salva_Hughes/)

Sette file (6 `.docx` + `edit.pdf`), ricostruiti come i turni consecutivi di **una sola
conversazione** con un assistente AI (catena D1→D7 verificata nel testo: ogni documento propone i
proseguimenti a cui il successivo risponde). Colma — solo in parte — la lacuna critica già
registrata in [[lanchester-models]] § Note: *"Hughes, wiki a zero fonti"*.

**Da leggere a due velocità**: D1 (*"Illustrami cos'è il modello event-driven a salva di
Hughes…"*) è **solido** — attribuzione, anno ed equazioni base verificati contro la letteratura,
l'unico documento del set con contenuto verificabile. D2-D7 sono **estensioni inventate
dall'assistente**, senza alcuna citazione, con **undici difetti aritmetici o logici accertati**
(violazione di causalità nel ricalcolo retroattivo di una salva già in volo; una somma sbagliata e
tre notazioni temporali incompatibili nello stesso paragrafo; un fattore di tempismo applicato due
volte; un modello che uccide più unità di quante ce ne siano; doppio conteggio nella formula di
soppressione; un confronto "con SEAD/senza SEAD" confondato dal cambio di regolamento fra i due
scenari; codice Python che non implementa il termine difensivo che dichiara di implementare;
stocasticità annunciata e mai usata; parametri incoerenti fra documenti; tempo di volo balistico
come moto rettilineo uniforme; citazioni-nomi-di-dominio senza titolo/autore/anno).

**Pagine create**:
- `wiki/sources/source-hughes-salvo-event-driven.md` — riepilogo completo, tabella dei 7 documenti,
  11 lacune dettagliate, applicabilità al progetto
- `wiki/entities/wayne-hughes.md` — autore, attribuzione verificata
- `wiki/concepts/salvo-combat-model.md` — formulazione base del modello (impulsi discreti,
  saturazione difensiva, staying power)
- `wiki/analyses/hughes-salvo-vs-engagement-resolver.md` — valutazione componente per componente
  contro `Logic/Engagement_Resolver.py` (Fase 4): **4 meccanismi adottabili** (saturazione
  difensiva per-salva, soglia di shock, congelamento del payload all'istante di fuoco, targeting
  anti-overkill), **1 precondizione nuova** (scorte munizioni per asset — verificato che il
  progetto non ce l'ha in nessuna forma, gap già annotato in `Block/Military.py:720`), **1 punto
  architetturale** (re-scheduling delle finestre di contatto dopo uno spostamento fisico a ingaggio
  in corso — appartiene allo strato 1/`Contact_Scheduler`, non alla Fase 4)
- `wiki/decisions/risolutore-ingaggio-salva-fase4.md` — **`status: proposed`**, mai `accepted`:
  R1 (saturazione difensiva per-salva), R2 (soglia di shock, seconda soglia indipendente accanto a
  P1 di [[soglie-disingaggio-e-attrito-aggregato]]), R3 (scorte munizioni per asset), R4
  (congelamento payload adottabile subito + re-scheduling registrato ma non progettato). 4 punti
  aperti da confermare con l'utente

**Nessun coefficiente, latenza o tempo di volo della fonte è stato importato in nessuna pagina** —
stessa disciplina già applicata a [[source-lanchester-scenari-ai]]: si prende la forma, mai i
numeri, e ogni meccanismo è stato verificato contro il codice reale (`Damage_Model.py`,
`Contact_Scheduler.py`, `Military.py`, `Ground_Weapon_Data.py`) prima di essere proposto.

**Cosa non cambia**: architettura a 4 strati di [[virtual-session-engine-des]] invariata; il modello
a salva di Hughes resta la scelta per lo strato 2, confermata non messa in discussione.

---

## [2026-09-22] analisi | Un LLM locale può valutare le condizioni dei passi event-driven?

Proposta dell'utente: usare un LLM locale (Qwen2.5-7B o Qwen3 8-27B quantizzato, RTX 3090 24 GB)
per «valutare le diverse condizioni che possono verificarsi durante i passi event-driven» delle
sessioni virtuali. Formulazione volutamente aperta → **primo compito la disambiguazione** contro la
pipeline reale a 7 fasi (Fase 3 completata, Fase 4 il prossimo passo), non la valutazione in
astratto. Nessuna riga di codice toccata.

**Quattro letture valutate una per una** (v. [[llm-locale-nel-motore-des]]):

- **(a) per singolo evento** (Pk, esito di un colpo, CPA) — **respinta**. Conto: chiamata LLM 7B Q4
  su 3090, caso ottimistico dal benchmark CUDA ufficiale di llama.cpp (pp512 5.560 t/s, tg128
  162 t/s), prompt 1.000 + risposta 100 token = **0,80 s**. Costo misurato sul repo di ciò che
  sostituirebbe: `resolve_hit` **0,859 µs**, nucleo analitico CPA **21,6 µs**. Rapporto **931.000×**
  / 37.000×. Proiezione al limite superiore dichiarato (10⁶ colpi): **9,2 giorni per sessione**
  contro 0,86 s in forma chiusa — **entro un fattore 8 dai 74 giorni** con cui la Strategia 1 a
  tick è già stata respinta.
- **(b) decisione qualitativa/dottrinale** (soglia P1, ROE, indirizzo C2) — **respinta, ma non per
  aritmetica**: ~50 ingaggi × 0,80 s = 40 s, dentro il budget sul caso tipico (fallisce alla scala:
  26,7 ore). Fallisce sulla **riproducibilità** (vincolo #1) e sul vincolo simulator-agnostic; e
  chiederebbe all'LLM proprio ciò che [[soglie-disingaggio-e-attrito-aggregato]] § P1 vieta — la
  soglia «non va inventata, è un parametro dottrinale dichiarato».
- **(c) debrief narrativo a stato già risolto** — **passa**, con tre confini (mai sulla traiettoria
  di stato, fuori dal core, testo salvato come artefatto versionato e non rigenerato al replay).
  Priorità bassa: non risolve alcun punto aperto.
- **(d) uso offline a tempo di progettazione** — **passa ed è l'unica utile subito**: fixture degli
  scenari S1-S11, tabelle di `Context/Reaction_Profile.py`, enumerazione dei casi ROE/dottrina.
  Condizione: si prende la *forma*, mai i *numeri* — stessa regola già applicata alle fonti esterne.

**Vincolo #1 verificato, non dato per scontato.** Misura pubblicata (Larsen, arXiv:2512.12066,
vLLM, decodifica greedy a temperatura 0,0, confronto fra seed): Llama 3.1 8B **73,4%** di risposte
byte-identiche, **Qwen 2.5 7B solo 17,6%** — cioè proprio il modello proposto cambia più di quattro
risposte su cinque. Il rimedio (kernel batch-invarianti di vLLM) esiste ma la documentazione di vLLM
stessa non promette nulla **fra generazioni hardware, versioni di libreria o driver**, e non
quantifica il costo prestazionale. Differenza qualitativa col PRNG registrata: la riproducibilità di
un PRNG seedato è *per costruzione*, quella di un LLM è *emergente* da uno stack in virgola mobile
che nessuno strato dichiara come contratto.

**Paradosso del batching** (argomento strutturale, non implementativo): l'unico modo di avvicinare
un LLM al throughput dell'opzione (a) è il batching (~1.035 t/s a 64 concorrenti su 27B/3090, vs
127 a utente singolo) — ma la composizione del batch è **esattamente** ciò che rende l'inferenza non
riproducibile. Le due proprietà sono in opposizione diretta.

**Reperto collaterale, estraneo alla proposta ma da decidere**: misurando il termine di paragone è
emerso che `Contact_Scheduler.closest_point_of_approach` costa **52,95 ms/chiamata**, di cui il
**99,8%** (quota cumulativa `cProfile`) è la costruzione di due `sympy.Point3D` sul risultato (`nsimplify` → `mpmath.pslq` su
coordinate float "brutte": **23 ms per punto**). La matematica vera costa **21,6 µs** → fattore
**2.450×**. Contraddice il docstring del modulo stesso e la regola già scritta nel documento di
architettura (§6: *«sympy è simbolico ed esatto, quindi lento: […] non per milioni di
valutazioni»*). Impatto: allo scenario di stress **S8** (~2,5·10⁶ CPA) il motore costerebbe
**36,8 ore per sessione** invece di **54 secondi** — cioè sfonderebbe il budget di «minuti» già
adesso, senza alcun LLM, e S8 attribuirebbe la colpa al posto sbagliato.

**Pagine create**:
- `wiki/analyses/llm-locale-nel-motore-des.md` (analisi completa, con tutti i conti e le fonti)
- `wiki/decisions/llm-locale-ruolo-e-confini.md` — **`status: proposed`**, mai `accepted`: R1
  (regola generale «niente componenti non riproducibili sulla traiettoria di stato», formulata
  senza nominare gli LLM perché copra anche servizi di rete e modelli appresi), R2 (esclusi (a) e
  (b)), R3 (ammesso il debrief), R4 (ammesso e incoraggiato l'uso offline). 4 punti aperti da
  confermare con l'utente.

**Cosa non cambia**: architettura a 4 strati di [[virtual-session-engine-des]] invariata; la Fase 4
`Engagement_Resolver` nasce interamente in forma chiusa come già deciso.

---

## [2026-09-22] aggiornamento | Batteria di validazione Fase 7 estesa da S1-S5 a S1-S11

Su richiesta esplicita dell'utente ("ulteriori scenari di test oltre S1-S5"). I 5 scenari
ereditati da [[source-lanchester-scenari-ai]] coprono solo terra/aria a due parti, ingaggio
singolo, forze già in contatto — non toccano il dominio navale, i bersagli economici/logistici,
la scala (10.000 asset), il fog-of-war, la soglia di disingaggio proposta in P1 (nessuna fonte
la implementava), né il confine sessione-DCS/sessione-sintetica.

**6 nuovi scenari definiti per questa sessione** (non derivati da alcuna fonte esterna) in
[[soglie-disingaggio-e-attrito-aggregato]] § P3, ciascuno mirato a un meccanismo specifico del
motore non esercitato da S1-S5: S6 gruppo navale vs difesa costiera, S7 interdizione di linea
logistica (bersaglio `Production`/`Storage`/`Transport`, non `Military`), S8 fronte multiplo /
stress di scala (verifica la potatura gerarchica del `Contact_Scheduler`), S9 targeting sotto
fog-of-war parziale (`recon_cp_snapshot`), S10 regressione mirata sulla soglia di disingaggio
(test di non-regressione di P1 stessa), S11 confine sessione DCS/sintetica (test end-to-end del
contratto `SessionOrder`/`SessionOutcome`, l'unico esplicitamente richiesto dalla roadmap
originale per la Fase 7).

Aggiunto un quinto punto aperto: S6-S11 sono una proposta di partenza di questa sessione, non
ancora confermata come batteria ufficiale.

---

## [2026-09-22] ingestione | Modelli Lanchester e scenari applicati (9 `.docx`, `RAW/Lanchester/`)

**Fonte**: 9 file `.docx` (+ uno `.zip` ridondante, ignorato). Letti integralmente. Verificato nel
testo che **non sono 9 fonti indipendenti** ma i turni di **una sola sessione conversazionale** con
un assistente AI: ogni documento si chiude con la domanda che titola il successivo, e `…CAS(1).docx`
è la ri-emissione della sola tabella finale di `si introduci una missione SEAD preliminare.docx`
(numeri identici). Da qui la scelta di **una sola pagina `sources/`**, con tabella per-documento.

**Esito della valutazione**: **negativo sulla matematica, parzialmente positivo sulla struttura.**
Il doc 04 è l'unico a carattere bibliografico (Bracken generalizzato, legge 1.5, KDB/Dupuy,
eterogeneo vettoriale, Peterson, Helmbold, SINDy, fattore informativo $\mu$) ma con **citazioni che
sono nomi di dominio nudi**, non verificabili. Gli altri otto sono esercizi numerici con
coefficienti dichiarati «ipotizzati», risolti con **un singolo passo di Eulero a $\Delta t = 1$
giorno**. **Nessuna equazione a salva (Hughes) in tutto il set**: nessuna sovrapposizione con lo
strato 2 previsto.

**Difetti specifici trovati** (dettaglio in [[lanchester-vs-motore-des]] § 3): attrito indipendente
dalla numerosità della forza che lo subisce (doc 06: 8,5 velivoli persi su 20 presenti); output
frazionario e aggregato, incompatibile col vincolo «perdite per singolo asset»; determinismo senza
varianza; **il confronto SEAD/non-SEAD del doc 06 è un artefatto del cambio di ordine di risoluzione
fra le due simulazioni**, non un effetto del SEAD — dimostrazione involontaria del vincolo #2 di
[[virtual-session-engine-des]]; il doc 02 dichiara legge lineare/quadratica e poi calcola tutto a
fuoco mirato; il doc 05 afferma «4-5 caccia abbattuti» dove i suoi stessi coefficienti danno 0,9.

**Falso allarme risolto**: il doc 04 chiama «validazione» il fit Ardenne/Kursk che il progetto
registra come «9 test falliti». **Non è una contraddizione** — entrambi dicono che le leggi
classiche non tengono; il doc chiama validazione un fit a posteriori con due parametri liberi.
L'avvertimento metodologico di [[virtual-session-engine-des]] **resta invariato** e non è stato
toccato.

**Verifica strato 1 vs strato 2**: confermata l'ipotesi, e più nettamente. Nei 9 documenti **non
compare una sola coordinata, velocità, rotta, portata o tempo di contatto**: il contatto è assunto a
$t=0$. Lo scheduler dei contatti (Fase 3, in lavorazione da un altro agente) **non è toccato**.
Corollario registrato: la sequenza di fasi che i documenti cablano a mano
(MR-SAM → SHORAD → AAA) è esattamente ciò che lo strato 1 produce dalla geometria — argomento *a
favore* dell'architettura già scelta.

**Pagine create (4)**:
- `wiki/sources/source-lanchester-scenari-ai.md`
- `wiki/concepts/lanchester-models.md` — colma la lacuna dichiarata in `overview.md` («Fonti sui
  modelli Lanchester»), almeno come tassonomia
- `wiki/analyses/lanchester-vs-motore-des.md` — **prima pagina `analyses/` del wiki**
- `wiki/decisions/soglie-disingaggio-e-attrito-aggregato.md` — **`status: proposed`**, richiede
  decisione dell'utente

**Pagine aggiornate (3)**: `index.md`, `log.md`, `overview.md`.

**Nessun file di codice toccato.** Analisi e ingestione soltanto.

---

## [2026-09-22] aggiornamento | Chiusi i 3 punti aperti dopo Q1-Q3 (SEAD, MIN_EFFECTIVE_HIT_DAMAGE, Edge.calcLength) + bug intersectPoint

**SEAD collegato** (commit `efb93cab`): `Tactical_Evaluation.calculate_priority` legge
`Military.air_defense_power()` del bersaglio quando l'attaccante è aereo e il target ha combat
power 0 — prima saturava sempre al floor 0.1, quindi un C2 aereo non avrebbe mai visto un sito
SAM come bersaglio prioritario. Mappatura lineare `[0,1]→[0.1,10.0]`, stessa scala degli altri
rami. Attaccanti ground/sea invariati. Trovato e corretto un fixture di test rotto dal nuovo call
site (`TestCalculatePriorityTargetAffinity._target`, mock `spec=Military` senza
`air_defense_power` configurato).

**`MIN_EFFECTIVE_HIT_DAMAGE`**: confermata, nessuna modifica.

**`Edge.calcLength()`**: il commento era il bug (dichiarava una distinzione 2D/3D per
`path_type` mai implementata), corretto il commento, codice invariato — le posizioni asset
hanno già quota reale anche a terra, la 3D è la scelta fisicamente corretta.

**Bug trovato per strada, corretto separatamente** (commit `5a87ebb2`, prima di questi 3 punti):
`Edge.intersectPoint(Line2D)` intersecava la retta 3D dell'edge invece della sua proiezione 2D
— falso negativo silenzioso per ogni edge non a quota zero. Zero chiamanti in produzione oggi
(dormiente), nuovo `Test_Edge.py` (prima nessuna copertura).

**3 pagine `wiki/decisions/`/`wiki/project/` aggiornate**: [[virtual-session-engine-des]],
[[route-model-unification]], [[block]] — le note "da confermare con l'utente" sostituite con
l'esito reale.

---

> **Registro cronologico** in sola aggiunta di tutte le operazioni sul wiki.
> Formato voci: `## [YYYY-MM-DD] tipo | Descrizione`
>
> Tipi: `ingestione` | `query` | `health-check` | `aggiornamento` | `setup`
>
> **Ricerca rapida** (da terminale):
> ```bash
> grep "^## \[" wiki/log.md | tail -10    # ultime 10 voci
> grep "ingestione" wiki/log.md            # tutte le ingestioni
> grep "query" wiki/log.md                 # tutte le query
> ```

---

## [2026-09-22] aggiornamento | Sync motore sessioni virtuali (DES): 2 nuove decisioni + 3 pagine project aggiornate

**Applicazione della regola "SYNC EVOLUZIONE PROGETTO"**, su richiesta esplicita dell'utente
("allinea i contenuti del wiki con le decisioni sul sistema di simulazione virtuale"), mentre due
subagent lavoravano in parallelo su `analysis/dce-dcs-persistence` (Fase 2 appena chiusa, e le 3
questioni aperte pre-Fase 3 in corso). Colma un buco reale: tutto il lavoro del 2026-09-18/21 su
quel branch (mai mergiato in `main`) non era mai arrivato al wiki.

**2 nuove pagine `wiki/decisions/`**:
- [[virtual-session-engine-des]] — verdetto sulle due strategie proposte dall'utente (tick 1ms
  scartato: 74 giorni di calcolo proiettati; probabilistica incompleta: non dice quando due forze
  si incontrano), architettura DES a coda eventi scelta, roadmap a 7 fasi, stato Fase 1
  (cinematica, `3af377c5`) e Fase 2 (percezione/`ThreatAA`, `30a6ee55`) — entrambe fatte e
  pushate, non ancora su `main`.
- [[core-simulator-agnostic]] — il vincolo architetturale dichiarato dall'utente il 2026-09-18
  (core indifferente al simulatore, DCE come controesempio negativo analizzato in dettaglio),
  contratto `SessionOrder`/`SessionOutcome`, ordine di lavoro imposto (contratto → resolver
  sintetico → campagna senza simulatore → solo dopo l'adapter DCS).

**3 pagine `wiki/project/` aggiornate** (non solo aggiunte — anche bug ormai risolti spostati
dalla sezione "confermati" a "risolti"): [[asset-base]] (schema `SPEED_SCHEMA`/`Mobile.speed` in
m/s, `detection_range`, e soprattutto il bug storico `Mobile.checkParam` senza `self` — confermato
ancora presente il 2026-09-18 — ora marcato risolto dalla Fase 1), [[block]] (nuovi
`Military.air_defense_threats()`/`detection_range()`), [[logic-routing]] (fabbrica
`build_threat_aa()`, e nota esplicita che la triplicazione `Route`/`Edge`/`Waypoint` — già nota
dal 2026-08-21 — è ora una precondizione bloccante per il `Contact_Scheduler`).

**Pagina esistente annotata, non riscritta**: [[datatype-route-edge-waypoint]] — aggiunta una nota
che segnala la rivalutazione in corso (sessione parallela al 2026-09-22) della scelta "Air resta
separato da `DataType.Route`", senza presumerne l'esito.

**Deliberatamente non fatto in questa sessione**: le 3 questioni aperte pre-Fase 3 (modello
`Route` vincente, semantica della perdita per-asset, SAM/AAA/EWR nel combat power) sono in
lavorazione in una sessione parallela sullo stesso branch — il wiki le registra come "in corso"
in [[virtual-session-engine-des]] e [[logic-routing]], da aggiornare con l'esito reale a lavoro
concluso, per non contraddire una decisione ancora da prendere.

---

## [2026-09-22] aggiornamento | Riconciliazione: le 3 questioni pre-Fase 3 sono state chiuse

**Seguito diretto della voce precedente**: la sessione parallela ha completato le 3 decisioni
mentre questa sessione scriveva il wiki. Riconciliazione fatta leggendo i 4 commit reali
(`6c421579`/`f1f5b7d4`/`64538f16`/`27d53e56`) e le memorie che li accompagnano, non i placeholder
"in corso" scritti prima.

**1 nuova pagina `wiki/decisions/`**: [[route-model-unification]] — `DataType.Route` confermato
unico modello di dominio anche per l'aria (non solo ground come deciso in agosto); le classi
locali di `Air_`/`Ground_Route_Manager` restano come stato di lavoro privato della ricerca;
nuovo `Logic/Route_Adapter.py` alla frontiera pubblica; piano a 5 fasi, Fase 1 fatta. Il blocco
tecnico reale era un bug in `DataType/Edge.py` (segmenti degeneri non costruibili con sympy per
una salita verticale pura), non una difficoltà architetturale.

**[[datatype-route-edge-waypoint]] marcata `superseded`** (era `accepted` con nota provvisoria
"in rivalutazione") → `superseded_by: [[route-model-unification]]`, come da convenzione ADR di
questo wiki.

**[[virtual-session-engine-des]] aggiornata** con l'esito reale delle 3 questioni: Q1 v. sopra;
Q2 (perdita per-asset) → nuovo `Logic/Damage_Model.py` + `Asset.apply_damage()`, contratto
Ph×Pk|h da `accuracy`/`destroy_capacity` già nei registri arma, soglia `Destroyed ≤ 15`
confermata invariata; Q3 (SAM/AAA/EWR) → combat power 0 confermato intenzionale, nuova
dimensione separata `Military.air_defense_power()` (non una tabella di efficacia inventata,
scartata deliberatamente dal subagent che ha fatto il lavoro).

**3 pagine `wiki/project/` aggiornate di conseguenza**: [[logic-routing]] (`Route_Adapter.py`,
correzione della frase "Air resta deliberatamente sulle sue classi locali", ormai imprecisa),
[[asset-base]] (`Asset.apply_damage`), [[block]] (`Military.air_defense_power`).

**Verifica indipendente** (non solo lettura del report del subagent): suite riesguita per
intero, **2753 test, 1 fallimento non riproducibile** (`testCalcFightResult`, isolato e
rieseguito 8/8 volte in verde) — dovuto a `random.uniform` non seedato in
`Tactical_Evaluation.calcFightResult`, file **non toccato** dai 4 commit in esame; non è una
regressione, è il gap già tracciato in [[virtual-session-engine-des]] ("random non seedato a
livello di modulo").

**3 punti restano da confermare con l'utente prima della Fase 4** (segnalati esplicitamente dal
subagent, non decisi unilateralmente): collegare `air_defense_power` alla priorità di targeting
SEAD (cambio di game balance); la costante `MIN_EFFECTIVE_HIT_DAMAGE = 1` in `Damage_Model.py`
(altrimenti le infrastrutture, `destroy_capacity ≈ 0`, sarebbero indistruttibili per
costruzione); se il bug in `Edge.calcLength()` (non distingue per `path_type` nonostante il
commento) sia il codice o il commento a dover cambiare.

---

## [2026-09-18] aggiornamento | TASK 2 (Fase A) implementato: RegionInfoReport / Meteo_Analysis / limes

**Prima applicazione della regola "SYNC EVOLUZIONE PROGETTO"** aggiunta a `CLAUDE.md` nella stessa giornata: implementazione di codice, non solo documentazione, quindi wiki aggiornato nella stessa sessione invece di aspettare.

**Codice consegnato** (v. [[c2-hierarchy-design]] per il dettaglio completo): property pubblica `Region.limes` (sola lettura); nuovo `Logic/Meteo_Analysis.py` (placeholder meteo deterministico, shape identica a `mission_requirements['usability']` di `Air_Resources_Assigner`); `Region.get_meteorological_reports` agganciato al nuovo modulo (firma cresciuta con `date`/`time`); nuovo package `Command/` con `Command_Types.py::RegionInfoReport`; nuovo `Region.build_info_report(side, date, time)` che lo assembla da metodi `Region` già testati. Suite completa: 2540 test OK (skipped=5), +21 rispetto a prima (2519).

**Pagine wiki aggiornate**: [[c2-hierarchy-design]] (TASK 2 da "non iniziato" a "fatto"), [[context-state]] (rimossi i riferimenti a `limes`/`get_meteorological_reports` come stub), nuova [[command]] per il package appena nato.

**Bug trovato e non corretto (fuori scope)**: `Payload.__eq__` considera "diversi" due `Payload` entrambi a zero — [[datatype]] afferma erroneamente che gli operatori di confronto di `Payload` sono "completi"; correzione della pagina rimandata a una prossima sessione dedicata.

---

## [2026-09-18] aggiornamento | Unificazione struttura di progetto + decisioni architetturali nel wiki

**Motivazione**: `Analysis/Modules/00-11_*.md` (audit del 2026-08-16) era ormai stale di un mese di refactoring attivo; le decisioni architetturali vivevano solo in `.claude/memory/project_*.md`, non nel wiki. L'utente ha chiesto di unificare teoria + struttura di progetto + decisioni in un unico posto, con la regola che ogni evoluzione futura del progetto vada anche documentata qui (vedi `CLAUDE.md` §5 "SYNC EVOLUZIONE PROGETTO", aggiunto in questa stessa operazione).

**Schema esteso**: aggiunte due nuove categorie di pagina a `CLAUDE.md` — `wiki/project/` (stato attuale di un sottosistema, verificato contro il codice reale) e `wiki/decisions/` (log ADR-style delle decisioni architetturali, distillato dalle memorie `project_*`/`feedback_*`).

**12 pagine `wiki/project/` create** (una per sottosistema, verificate contro codice+test reali, non copiate dall'audit): [[asset-air]], [[asset-ground-naval]], [[asset-base]], [[context-foundation]], [[context-state]], [[block]], [[component]], [[logic-routing]], [[logic-decision]], [[datatype]], [[utility-manager]], [[testing-conventions]] (nuova, nessun equivalente nell'audit).

**8 pagine `wiki/decisions/` create**: [[region-tactical-strategic-refactor]], [[combat-power-priority-redesign]], [[datatype-route-edge-waypoint]], [[air-priority-target-specific-loadout]], [[asset-type-vs-category]], [[c2-hierarchy-design]], [[campaign-temporal-model]] (superseded), [[module-audit-2026-08-16]] (superseded, storica).

**Drift significativo scoperto rispetto all'audit del 2026-08-16** (ogni pagina `project/` lo documenta in dettaglio): diversi bug che l'audit segnalava come bloccanti sono ora risolti (import circolare Aircraft, `Military.get_military_category()`, `Edge`/`Waypoint` non istanziabili, `asea.FAST_ATTACK`, `Test_Air_Route_Manager` 26 errori→48/48 OK), mentre altri restano aperti e sono ora tracciati esplicitamente (`Ship`/`Aircraft.loadAssetDataFromContext` senza `.items()`, `Military._is_attack_asset()`→`is_helibase()` inesistente, `Production`/`Storage`/`Transport`/`Urban` stub, `Ground_Route_Manager` non produce ancora `DataType.Route`, `Coalition.py` non ancora eliminato nonostante l'approvazione).

**Pagina esistente corretta**: `wiki/concepts/c2-planner.md` aggiornata — riferimenti obsoleti a `Manager.py` e `Military_Resources_Assigner.py` sostituiti con lo stato attuale e link a [[c2-hierarchy-design]].

**`wiki/overview.md` e `wiki/index.md` aggiornati** per puntare alle nuove sezioni come fonte di verità corrente.

**`Analysis/Modules/00-11_*.md` NON eliminati** (decisione utente): restano come istantanea storica, con banner in testa che rimanda alla pagina `wiki/project/` corrispondente.

**Metodo**: 6 subagent paralleli hanno letto il codice sorgente reale ed eseguito le suite di test pertinenti (non solo letto testo), verificando ogni claim invece di copiare l'audit vecchio. Bug di frontmatter YAML introdotti da alcuni agenti (liste di wikilink malformate) e link a pagine inesistenti (titoli invece di nomi-file kebab-case) sono stati trovati e corretti in fase di consolidamento.

---

## [2026-05-27] aggiornamento | Creazione stub ad alta priorità (13 pagine)

**Entità create (7)**:
- `wiki/entities/tac-thunder.md` — Theater Air Campaign Model USAF (griglia quadrata)
- `wiki/entities/cem-model.md` — Concepts Evaluation Model US Army (CAA), predecessore CADEM
- `wiki/entities/jicm-model.md` — Joint Integrated Contingency Model RAND (scope globale)
- `wiki/entities/rsas.md` — RAND Strategy Assessment System (predecessore TLC)
- `wiki/entities/modsim-ii.md` — Linguaggio di simulazione OOP CACI
- `wiki/entities/rjars.md` — RAND Jamming and Radar Simulation (dati superficie-aria)
- `wiki/entities/tac-sage.md` — Predecessore USAF dell'algoritmo SAGE

**Concetti creati (6)**:
- `wiki/concepts/piston-network.md` — Struttura game board lineare legacy
- `wiki/concepts/killer-victim-scoreboard.md` — Tabelle di efficacia cross-resolution
- `wiki/concepts/c2-planner.md` — Pianificatore C² del TLC (integra SAGE + manovre)
- `wiki/concepts/variable-resolution-modeling.md` — Variazione dinamica del livello di dettaglio
- `wiki/concepts/nonlinear-combat.md` — Combattimento non-lineare post-Guerra Fredda
- `wiki/concepts/historical-conflict-simulation.md` — Simulazione conflitti storici (Sabin)

**Index aggiornato**: entità 7→14, concetti 9→15; nuova sezione "Strutture Spaziali"

**Link rotti risolti**: da 26 a 11 (rimangono solo pagine a bassa priorità ≤2 refs)

---

## [2026-05-27] health-check | Prima verifica integrità wiki

**Fix applicati automaticamente (2)**:
1. Rinomina file sorgenti: aggiunto prefisso `source-` per allineare nomi file ai wikilink usati in tutto il wiki (`source-theater-level-campaign-model.md`, `source-simulation-techniques-past-conflicts.md`)
2. Pulizia anomalia `[[generalized-network]]` in `index.md`: rimosso doppione nella sezione "da creare" con nota contraddittoria

**Link rotti rilevati (26 wikilink senza pagina)**:
- Entità ad alta priorità (5+ ref): `[[tac-thunder]]`(8), `[[cem-model]]`(6), `[[jicm-model]]`(6), `[[rsas]]`(5), `[[modsim-ii]]`(5), `[[rjars]]`(5), `[[tac-sage]]`(4)
- Concetti ad alta priorità (3+ ref): `[[c2-planner]]`(5), `[[killer-victim-scoreboard]]`(5), `[[historical-conflict-simulation]]`(5), `[[piston-network]]`(5), `[[variable-resolution-modeling]]`(4), `[[nonlinear-combat]]`(3)
- Entità/concetti a bassa priorità (1-2 ref): `[[anti-hindsight]]`, `[[british-doae]]`, `[[kings-college-london]]`, `[[lost-battles]]`, `[[eadsim]]`, `[[apex-model]]`, `[[clausewitz]]`, `[[simulating-war]]`, `[[jmem]]`, `[[manual-simulation]]`, `[[idahex]]`

**Pagine orfane** (0 link in entrata): `source-theater-level-campaign-model`, `source-simulation-techniques-past-conflicts` — normale, sono le radici del grafo

**Contraddizioni**: nessuna contraddizione tra fonti — Sabin e Hillestad/Moore sono prospettive complementari (confermato)

**Stato frontmatter**: tutti i 19 file hanno frontmatter YAML completo ✓

**Raccomandazione priorità creazione stub**: `[[piston-network]]`, `[[c2-planner]]`, `[[killer-victim-scoreboard]]`, `[[tac-thunder]]` — massimo impatto sul grafo di link

---

## [2026-05-27] ingestione | Simulation Techniques in the Modelling of Past Conflicts (Sabin, KCL, 2008)

**File**: `RAW/simulationtechniquesinthemodellingofpastconflicts.doc` (951 parole, workshop HEA Warwick)

**Pagine create** (5 totali):
- `wiki/sources/simulation-techniques-past-conflicts.md`
- `wiki/entities/philip-sabin.md`
- `wiki/concepts/wargaming.md`
- `wiki/concepts/comparative-dynamic-modelling.md`

**Contributi principali**:
- 3 ruoli delle simulazioni: coinvolgimento, anti-hindsight, comprensione sistemica
- Wargaming come "contesa dialettica" (Clausewitz)
- Comparative dynamic modelling: validazione per variazione di assunzioni
- Argomento manuale vs computerizzato — accessibilità e bilanciamento

**Nessuna contraddizione** con fonte TLC — prospettive complementari (storico/accademico vs operativo/tecnico)

**Applicabilità al Warfare-Model**:
- Anti-hindsight → rinforza argomento per simulazione stocastica DWM
- Comparative dynamic modelling → metodologia per calibrazione e validazione DWM con `tactical_evaluation_results.csv`
- Clausewitz dialettica → fondamento concettuale del modulo avversario DWM

---

## [2026-05-27] ingestione | The Theater-Level Campaign Model (Hillestad & Moore, RAND, 1994)

**File**: `RAW/The Theater-Level Campaign Model.pdf` (MR-388-AF/A)

**Pagine lette**: frontmatter + pp. 1-42 (Cap. 1-3) + pp. 58-77 (Cap. 4)

**Pagine create** (12 totali):
- `wiki/sources/theater-level-campaign-model.md`
- `wiki/entities/tlc-model.md`
- `wiki/entities/rand-corporation.md`
- `wiki/entities/janus-model.md`
- `wiki/entities/tac-brawler.md`
- `wiki/entities/tacwar.md`
- `wiki/entities/mapview.md`
- `wiki/concepts/campaign-model.md`
- `wiki/concepts/generalized-network.md`
- `wiki/concepts/cadem.md`
- `wiki/concepts/sage-algorithm.md`
- `wiki/concepts/cross-resolution-modeling.md`
- `wiki/concepts/event-driven-simulation.md`
- `wiki/concepts/stochastic-simulation.md`

**Entità referenziate non ancora paginati**: tac-thunder, cem-model, jicm-model, rsas, modsim-ii, rjars, eadsim, british-doae, c2-planner, piston-network, killer-victim-scoreboard, variable-resolution-modeling, nonlinear-combat

**Applicabilità al Warfare-Model — sintesi**:
- Generalized Network → Route/Area/Region DWM (struttura analoga)
- SAGE → Air_Resources_Assigner / Military_Resources_Assigner (stesso problema)
- CADEM → calibrazione attrito da `tactical_evaluation_results.csv`
- Stochastic simulation → già presente (parzialmente) nel DWM
- C² Planner → Manager.py logica di pianificazione campagna

---

## [2026-05-27] setup | Inizializzazione del Wiki LLM

**Operazione**: Creazione della struttura iniziale del wiki.

**Azioni eseguite**:
- Creato `CLAUDE.md` con schema completo del wiki
- Creata struttura cartelle: `wiki/`, `wiki/entities/`, `wiki/concepts/`, `wiki/sources/`, `wiki/analyses/`, `wiki/assets/`
- Creato `wiki/index.md` (catalogo contenuti)
- Creato `wiki/log.md` (questo file)
- Creato `wiki/overview.md` (panoramica del dominio)
- Configurato `.obsidian/` per visualizzazione ottimale

**Fonti RAW disponibili per ingestione**:
1. `The Theater-Level Campaign Model.pdf`
2. `simulationtechniquesinthemodellingofpastconflicts.doc`

**Prossimi passi suggeriti**:
- Ingesta le due fonti RAW esistenti
- Configura Obsidian Web Clipper per aggiungere fonti da browser
