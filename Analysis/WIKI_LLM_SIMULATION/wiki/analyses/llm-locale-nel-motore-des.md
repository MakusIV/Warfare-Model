---
title: "Un LLM locale può valutare le condizioni dei passi event-driven?"
type: analysis
tags: [architecture, dwm, discrete-event, llm, reproducibility, performance, combat-resolution]
created: 2026-09-22
updated: 2026-09-22
query: "Usare un LLM locale (Qwen2.5-7B / Qwen3 8-27B quantizzato, RTX 3090 24 GB) per valutare le diverse condizioni che possono verificarsi durante i passi event-driven della simulazione delle sessioni virtuali: è praticabile?"
sources: ["[[virtual-session-engine-des]]", "[[core-simulator-agnostic]]", "[[soglie-disingaggio-e-attrito-aggregato]]"]
related: ["[[llm-locale-ruolo-e-confini]]", "[[event-driven-simulation]]", "[[stochastic-simulation]]", "[[lanchester-vs-motore-des]]"]
---

# Un LLM locale può valutare le condizioni dei passi event-driven?

## Domanda

L'utente propone di usare un **LLM locale** — in esecuzione sulla stessa macchina del progetto,
nell'ordine di 7-27 miliardi di parametri quantizzati, hardware di riferimento una RTX 3090 da
24 GB — per «valutare le diverse condizioni che possono verificarsi durante i passi event-driven»
della simulazione delle sessioni virtuali.

La formulazione è deliberatamente aperta. La prima parte del lavoro è quindi **disambiguarla**
contro la pipeline reale a 7 fasi di [[virtual-session-engine-des]] (Fase 3 completata, Fase 4 il
prossimo passo), non valutarla in astratto; la seconda è misurarla contro i quattro vincoli duri
già stabiliti, con lo stesso tipo di conto che ha scartato la Strategia 1 a tick.

## Risposta Sintetica

**Due delle quattro letture possibili sono da scartare, due passano.** Un LLM **per evento**
(opzione a) costa fra 9·10⁵ e 4·10⁴ volte il calcolo in forma chiusa che sostituirebbe: proiettato
sul limite superiore dichiarato dà **9,2 giorni per sessione** contro un budget di «minuti» — cioè
atterra nello stesso ordine di grandezza dei 74 giorni con cui la Strategia 1 a tick è già stata
respinta. Un LLM **per ingaggio** (opzione b) supera il conto sul caso tipico ma fallisce sulla
riproducibilità, che è il vincolo #1: una misura pubblicata su **Qwen2.5-7B** — esattamente il
modello proposto — riporta **17,6% di risposte byte-identiche a temperatura 0 fra seed diversi**.
Restano legittime la **generazione di debrief narrativo a stato già risolto** (opzione c) e l'**uso
offline a tempo di progettazione** (opzione d), che non tocca la traiettoria di stato per
costruzione ed è l'unica a indirizzare punti aperti reali del progetto.

Nel fare il conto è emerso un **difetto di prestazioni misurato nel codice della Fase 3**, non
legato alla proposta: `closest_point_of_approach` costa **52,95 ms per chiamata**, di cui il 99,8%
è la costruzione di due `sympy.Point3D` sul risultato. La matematica vera costa **21,6 µs**. Il
fattore è **2.450×**, ed è una violazione misurabile di una regola già scritta nel documento di
architettura. Dettaglio in § 5.

---

## 1. Disambiguazione: a cosa si applicherebbe un LLM, esattamente

La pipeline decide cose a quattro granularità diverse, con frequenze che differiscono di quattro
ordini di grandezza. «Valutare le condizioni dei passi event-driven» può voler dire una qualsiasi
delle quattro, e la risposta cambia completamente a seconda di quale.

| | Dove nella pipeline | Frequenza | Sulla traiettoria di stato? |
|---|---|---|---|
| **(a)** Risoluzione numerica del singolo evento: Pk, esito di un colpo, CPA/TCPA | Fase 3 `Contact_Scheduler`, Fase 4 `Engagement_Resolver`, Fase 5 `Damage_Model` | 10³-10⁶ / sessione | **sì** |
| **(b)** Decisione qualitativa/dottrinale: soglia di disingaggio P1, interpretazione ROE, indirizzo strategico C2 | Fase 4 `Engagement_Resolver`, [[c2-hierarchy-design]] | 10¹-10⁵ / sessione | **sì** |
| **(c)** Debrief narrativo **dopo** che lo stato è risolto | a valle di `SessionOutcome` | 1 / sessione | **no** |
| **(d)** Uso offline a tempo di progettazione: enumerare regole, tabelle, casi di test | mai a runtime | 0 / sessione | **no** |

La linea che conta non è la dimensione del modello né la frequenza: è **se l'output dell'LLM entra
nella traiettoria di stato**. Le prime due opzioni ci entrano, le altre due no, e questo determina
da solo l'esito sul vincolo #1.

---

## 2. Il conto sul budget di calcolo (vincolo #2)

### 2.a Costo di una chiamata LLM su RTX 3090 — dati reali, caso ottimistico

I numeri di riferimento sono presi dal **benchmark CUDA ufficiale di llama.cpp** (discussione
#15013), riga RTX 3090, Llama-2-7B Q4_0:

| fase | tokens/s misurati |
|---|---|
| prompt processing `pp512` (prefill), flash attention attiva | **5.560 t/s** |
| generazione `tg128` (decode) | **162 t/s** |

Sono i valori **ottimistici** della forchetta pubblicata: benchmark comunitari su Q4_K_M in
condizioni normali riportano piuttosto 80-95 t/s in decode per la classe 7-8B sulla stessa scheda,
55 t/s a 13B e 28 t/s a 34B. Usare il caso migliore è deliberato: se la proposta non passa con i
numeri migliori, non passa.

Una decisione strutturata realistica per questo dominio — stato dell'ingaggio, composizione delle
due forze, dottrina e ROE applicabili in ingresso; una decisione in JSON con una riga di
motivazione in uscita — sta in circa **1.000 token di prompt e 100 di risposta**:

| modello | prefill 1.000 tok | decode 100 tok | **totale per chiamata** |
|---|---|---|---|
| 7B Q4 | 1000/5560 = 0,180 s | 100/162 = 0,617 s | **0,80 s** |
| 27B Q4 (decode ~40 t/s, prefill ~1.400 t/s) | 0,71 s | 2,50 s | **3,2 s** |
| 7B Q4 con *thinking* (800 token di ragionamento) | 0,18 s | 5,56 s | **5,7 s** |
| 27B Q4 con *thinking* (800 token) | 0,71 s | 20,0 s | **20,7 s** |

**0,80 s per chiamata** è quindi il pavimento assoluto: modello più piccolo, quantizzazione
aggressiva, risposta brevissima, nessun ragionamento esplicito, nessuna coda, modello già caricato
in VRAM.

### 2.b Costo del calcolo in forma chiusa — misurato su questo progetto

Misure prese con `timeit` sul codice reale del repo (Python 3.10.12, macchina `osboxes`, minimo di
3 ripetizioni; script in scratchpad, non committato):

| primitiva | modulo | µs/chiamata |
|---|---|---|
| `resolve_hit(accuracy, destroy_capacity, draw)` | `Logic/Damage_Model.py` | **0,859** |
| `hit_outcome_probabilities(accuracy, destroy_capacity)` | `Logic/Damage_Model.py` | 0,628 |
| nucleo analitico CPA, soli float (`_overlap`+`_breakpoints`+`_relative_motion`) | `Logic/Contact_Scheduler.py` | **21,6** |
| `range_intervals(legs_a, legs_b, raggio)` | `Logic/Contact_Scheduler.py` | 30,4 |
| `closest_point_of_approach` **come spedita oggi** | `Logic/Contact_Scheduler.py` | **52.953** ⚠ |

L'ultima riga è il difetto di § 5 e **non** va usata come termine di paragone per l'architettura:
il termine corretto è il nucleo analitico, 21,6 µs.

**Rapporto per evento**: 0,80 s / 0,859 µs = **931.000×** contro la risoluzione di un colpo;
0,80 s / 21,6 µs = **37.000×** contro un CPA.

### 2.c Quanti eventi ci sono in una sessione

Il progetto non ha ancora una sessione end-to-end da misurare (Fase 6 non iniziata), quindi questa
è una **stima con assunzioni dichiarate**, non un dato — ma le assunzioni sono conservative e la
conclusione è robusta a un paio di ordini di grandezza in entrambe le direzioni.

Sessione di 2 h = 7.200 s. Due scale, quelle già fissate in [[virtual-session-engine-des]]: il
**caso tipico** su cui il progetto dichiara di voler progettare, e il **limite superiore teorico**
di 10.000 asset (= 100 blocchi × 100 asset).

Assunzioni: la potatura gerarchica a livello `Block` lascia passare ~10% delle coppie di blocchi;
~10% delle coppie di asset candidate arriva effettivamente a distanza di contatto; ~50% delle
finestre di contatto diventa un ingaggio per ROE; ogni asset che ingaggia spara ~20 colpi nella
finestra.

| grandezza | caso tipico (100 vs 100) | limite superiore (5.000 vs 5.000) |
|---|---|---|
| coppie di asset prima della potatura | 10⁴ | 2,5·10⁷ |
| valutazioni CPA dopo la potatura | ~10³ | ~2,5·10⁶ |
| finestre di contatto | ~10² | ~2,5·10⁵ |
| ingaggi | ~50 | ~1,2·10⁵ |
| **colpi risolti** (`resolve_hit`) | **~10³-10⁴** | **~10⁶** |

### 2.d Il verdetto aritmetico

| | eventi/sessione | costo LLM 7B (0,80 s/ev.) | costo forma chiusa | budget «minuti»? |
|---|---|---|---|---|
| **(a)** per colpo, caso tipico | 10³-10⁴ | **13 min – 2,2 h** | 0,9-8,6 ms | **no** |
| **(a)** per colpo, limite sup. | 10⁶ | **9,2 giorni** | **0,86 s** | **no** |
| **(a)** per CPA, limite sup. | 2,5·10⁶ | **23 giorni** | 54 s | **no** |
| **(b)** per ingaggio, caso tipico | ~50 | **40 s** (7B) / 160 s (27B) | — | **al limite** |
| **(b)** per evento di perdita, caso tipico | 10³-10⁴ | come (a) | — | **no** |
| **(b)** per ingaggio, limite sup. | 1,2·10⁵ | **26,7 ore** | — | **no** |
| **(c)** debrief | 1 | **~9 s** (7B, 1.500 token) | — | **sì** |
| **(d)** offline | 0 a runtime | **0** | — | **sì** |

**Il numero che chiude la questione sull'opzione (a)**: 9,2 giorni per sessione al limite superiore.
La Strategia 1 a tick da 1 ms è stata scartata a **74 giorni** proiettati. Un LLM per evento sta
**entro un fattore 8 dall'opzione che il progetto ha già respinto con un conto** — e la respingeva
per la ragione precisa che un costo per-passo moltiplicato per un numero enorme di eventi non è
sostenibile. Qui il numero di eventi è quattro ordini di grandezza più basso, ma il costo per evento
è sei ordini più alto: il prodotto torna dov'era.

Va detto con altrettanta chiarezza che **l'opzione (b) sul solo caso tipico non fallisce per
aritmetica**: 40 s con un modello da 7B è dentro un budget di «minuti». Fallisce per altro (§ 3 e
§ 4), e va respinta per quelle ragioni, non travestendo un'obiezione di principio da conto.

### 2.e Il paradosso del batching

C'è un solo modo di avvicinare un LLM al throughput richiesto dall'opzione (a): il **batching**. Una
configurazione ottimizzata pubblicata per un 27B su singola 3090 con vLLM riporta ~127 t/s a utente
singolo contro **~1.035 t/s a 64 richieste concorrenti** — circa un fattore 8.

Anche accettandolo per intero, non basta: 10⁶ colpi a ~10 decisioni/s restano **27 ore**. Ma il
punto vero è un altro, ed è strutturale:

> **la composizione del batch è esattamente ciò che rende l'inferenza non riproducibile.**

Il risultato per una singola richiesta dipende dal batch in cui è stata eseguita, e il batch non è
stabile fra un'esecuzione e l'altra. L'unica cosa che potrebbe rendere l'opzione (a) abbastanza
veloce è quindi la stessa che la rende non replayabile. Non è un dettaglio implementativo da
risolvere con più ingegneria: le due proprietà sono in opposizione diretta.

---

## 3. Riproducibilità (vincolo #1) — verificata, non data per scontata

Il vincolo dell'utente è più forte della semplice ripetibilità: *«l'ordine di risoluzione degli
eventi fa parte del contratto, salvare il solo seed non basta»*. Tutta la Fase 5 è stata scritta
attorno a questo — `resolve_hit` riceve `draw` dal chiamante e non genera mai un numero casuale al
proprio interno.

**L'affermazione da verificare**: un LLM, anche a temperatura 0, non garantisce output
bit-riproducibile fra esecuzioni diverse. **Verificata, e il dato più pertinente nomina proprio il
modello proposto.** Da una misura pubblicata (Larsen, *The Instability of Safety*, arXiv:2512.12066,
appendice «Greedy Decoding Non-Determinism»), con inferenza vLLM e decodifica greedy a temperatura
0,0, confrontando i testi di risposta fra seed diversi:

> «Llama 3.1 8B showed 73.4% exact-match responses across seeds, while **Qwen 2.5 7B showed only
> 17.6% exact matches**, indicating substantial inference non-determinism even at temperature 0.0.»

Cioè: **oltre quattro risposte su cinque cambiano**, a temperatura 0, a parità di prompt, sullo
stesso modello, sulla stessa macchina. Gli autori attribuiscono la variazione alla non-determinismo
in virgola mobile dell'inferenza vLLM batchata.

Il rimedio esiste e ha un nome — **kernel batch-invarianti** (RMSNorm, matmul, attention riscritti
perché l'ordine di riduzione non dipenda dalla dimensione del batch), supportati opzionalmente da
vLLM. Ma la documentazione di vLLM stessa lo qualifica in modo che non regge il vincolo #1:
richiede compute capability ≥ 8.0, *«may impact performance compared to the default
non-deterministic mode»* senza quantificare di quanto, ed è validato solo su un elenco di modelli.
Soprattutto **non promette nulla attraverso generazioni hardware, versioni di libreria o
aggiornamenti dei driver** — che è esattamente la garanzia che serve a un salvataggio di campagna
che deve poter essere rigiocato fra sei mesi, magari su un'altra delle tre macchine del progetto.

**La differenza qualitativa col PRNG va detta esplicitamente**, perché è il cuore della questione.
Un generatore pseudocasuale seedato è riproducibile *per costruzione*: l'algoritmo è intero,
esattamente specificato, indipendente dall'hardware, e l'unica condizione è che l'ordine delle
chiamate non cambi — condizione che il progetto ha già preso in carico. La riproducibilità di un
LLM è invece una proprietà *emergente* di uno stack in virgola mobile — kernel, ordine di riduzione,
dimensione del batch, versione di cuBLAS, driver, metodo di quantizzazione — di cui nessuno strato
la dichiara come contratto. Non è lo stesso problema in scala diversa: è un problema di natura
diversa.

**Conseguenza sulle quattro opzioni**: (a) e (b) mettono un componente non riproducibile
*sulla traiettoria di stato*, dove una singola divergenza non resta locale — cambia l'esito
dell'ingaggio, quindi lo stato di campagna, quindi tutte le sessioni successive. (c) e (d) non
toccano la traiettoria e quindi non sono vincolate.

Una mitigazione va nominata per completezza e archiviata: *«chiamare l'LLM una volta, cachare
l'output, rigiocare dalla cache»*. È coerente — e infatti è precisamente il meccanismo che rende
accettabile l'opzione (c). Ma applicata a (a)/(b) non risolve nulla: rende riproducibile *quella*
partita già giocata, non la campagna, perché al primo evento nuovo (cache miss) serve di nuovo il
modello, e una campagna è fatta di eventi nuovi. Sposta il problema dal replay alla generazione.

---

## 4. Vincolo core simulator-agnostic (#3) e convenzioni del core (#4)

Il vincolo di [[core-simulator-agnostic]] ha un test operativo dichiarato: *«cancellando l'adapter
DCS, la campagna deve continuare a funzionare»*, e in linea teorica il core deve poter far girare
una campagna **con sole sessioni sintetiche**, senza alcun simulatore esterno.

Le opzioni (a) e (b) sostituirebbero quella dipendenza con una peggiore. Una sessione che non si
risolve senza «una GPU con 24 GB di VRAM e un modello da 5-16 GB installato» non ha un core
agnostico: ha un core con un requisito infrastrutturale più stringente di DCS stesso. Il difetto
strutturale diagnosticato in DCE — *«se il risolutore vive fuori dal core, il core smette di essere
un modello e diventa un traduttore»* — si ripresenterebbe identico, col peso del modello al posto
del simulatore. E fra le tre macchine del progetto, il numero di quelle con una RTX 3090 è un dato
che va verificato prima di qualunque decisione (§ 7, punto 1).

C'è anche un conflitto diretto con la convenzione #4, «mai dipendenze pesanti a livello di modulo».
Oggi `Damage_Model.py` e `Contact_Scheduler.py` non importano nulla di pesante in testa al file. Un
`Engagement_Resolver` che a runtime debba parlare con un runtime di inferenza rompe quella proprietà
in maniera non aggirabile con un import locale: l'import locale nasconde il costo di caricamento,
non la dipendenza.

Le opzioni (c) e (d) sono compatibili per costruzione: (c) è un componente **opzionale fuori dal
core**, che consuma un `SessionOutcome` già scritto e la cui assenza non cambia niente di ciò che il
core produce; (d) non esiste a runtime affatto — è uno strumento di sviluppo, allo stesso titolo di
un IDE o di questa stessa analisi.

---

## 5. Il problema che risolverebbe è reale?

Le «condizioni complesse» a cui la proposta plausibilmente allude esistono davvero, e sono
catalogate: sono i punti aperti di [[soglie-disingaggio-e-attrito-aggregato]], in particolare
**P1** (soglia di disingaggio) e **S9** (targeting sotto fog-of-war, con la tensione fra visibilità
geometrica e visibilità informativa). Sono decisioni genuinamente difficili da formalizzare, ed è
ragionevole pensare a un LLM guardandole.

Ma va guardato **cosa** quei punti aperti chiedono. P1 non chiede un giudizio: chiede di decidere
*dove vive un parametro dichiarato*. Il testo della proposta è esplicito — il valore di soglia
«**non** va inventato: appartiene alla dottrina, quindi a `Context/Doctrine.py` o al livello C2, dove
è un parametro dichiarato del lato, non una costante nel risolutore». Un LLM interrogato a runtime
produrrebbe esattamente ciò che quella frase vieta: un numero senza provenienza, per giunta non
rintracciabile a posteriori. È la stessa regola che il progetto si è già data sui coefficienti di
attrito — *«stimati con un ATCAL interno, non inventati a tavolino»* — e che
[[lanchester-vs-motore-des]] ha appena applicato respingendo in blocco i coefficienti «ipotizzati»
di una fonte esterna. Un LLM a runtime è la versione peggiore di quel difetto: i coefficienti
inventati di una fonte scritta sono almeno **stabili e ispezionabili**.

Lo stesso vale per S9: il conflitto fra `recon_cp_snapshot` parziale e `detection_range` geometrico
è una questione di **contratto fra due nozioni di visibilità**, che va decisa una volta e scritta,
non arbitrata caso per caso da un giudice probabilistico.

**Dove il bisogno invece è reale e non coperto**: scrivere quelle regole, enumerare i casi, produrre
le fixture degli undici scenari S1-S11 per la Fase 7, redigere le tabelle di
`Context/Reaction_Profile.py` a partire dalle latenze SAM già documentate. È lavoro di **authoring**,
e cade interamente nell'opzione (d).

---

## 6. Reperto collaterale: `closest_point_of_approach` costa 2.450× il necessario

Trovato misurando il termine di paragone del § 2.b, **non ha nulla a che vedere con la proposta LLM**,
ma va registrato perché è un difetto reale in codice appena spedito e perché stringe il budget di
calcolo su cui tutto il resto si appoggia.

```
closest_point_of_approach (3+3 legs)      : 52.952,805 us/call   <- timeit, 2000 iterazioni
  nucleo analitico, soli float            :      21,591 us/call   <- stessa matematica, senza wrapping
  cProfile: quota cumulativa in _to_point :      99,8 %           <- 1,327 s su 1,329 s, 20 iterazioni

_to_point (-> sympy.Point3D), float "brutti" (caso reale) : 23.032,9 us/call
_to_point (-> sympy.Point3D), float "puliti" (1.0,2.0,3.0):  1.618,5 us/call
```

Il profilo (`cProfile`, 20 iterazioni) è inequivocabile: il 99,8% del tempo cumulativo sta dentro
`sympy/geometry/point.py:__new__` → `nsimplify` → `_real_to_rational` → **`mpmath.identification.pslq`**.
`Point3D` passa ogni coordinata float attraverso `nsimplify`, che lancia una ricerca di relazione
intera (PSLQ) per tentare di riconoscere il float come razionale esatto. Su una coordinata "pulita"
la ricerca termina subito (1,6 ms); su una coordinata reale di CPA — 44.234,789… metri — cerca a
lungo prima di arrendersi (**23 ms**).

Sono le coordinate del *risultato*, non del calcolo: `closest_point_of_approach` fa tutta la
matematica correttamente su terne di float, poi spende mille volte tanto a imballare l'esito. Il
difetto contraddice due regole già scritte:

- il docstring di `Leg` nel modulo stesso: *«le posizioni sono terne di float […] perché dentro ai
  cicli si fanno migliaia di prodotti scalari e l'aritmetica esatta di sympy li renderebbe
  inutilmente costosi; i `Point3D` ricompaiono sui risultati»* — la premessa è giusta, ma il
  risultato è dentro il ciclo, perché un CPA per coppia di asset **è** il ciclo;
- la disciplina trasversale del documento di architettura, § 6: *«Geometria numerica (float/numpy)
  dentro il risolutore. `sympy` è simbolico ed esatto, quindi lento: va bene per costruire gli
  scenari, non per milioni di valutazioni.»*

**Impatto sul budget**, con le stime di § 2.c: allo scenario di stress **S8** (2,5·10⁶ valutazioni
CPA) il costo attuale è **36,8 ore per sessione**; col solo nucleo analitico sarebbe **54 secondi**.
Cioè il motore sfonda il budget di «minuti» già adesso, senza alcun LLM, per una ragione che non ha
niente a che vedere con l'architettura scelta. S8 è, per sua definizione, *«l'unico scenario pensato
per misurare tempo di calcolo»*: lo misurerebbe e fallirebbe, attribuendo la colpa al posto
sbagliato.

Rimedio (da decidere, **nessuna riga toccata**): restituire terne di float in `CPA`/`ContactWindow`
e costruire i `Point3D` solo al confine verso un consumatore che li richieda, oppure — se i
`Point3D` devono restare nella firma — costruirli con coordinate già razionalizzate, bypassando
`nsimplify`. La prima è coerente con la § 6 del documento di architettura.

---

## 7. Fonti Utilizzate

- [[virtual-session-engine-des]] — architettura a 4 strati, roadmap 7 fasi, i 4 vincoli utente,
  verdetto sulla Strategia 1 (74 giorni)
- [[core-simulator-agnostic]] — test di agnosticismo, cosa non entra mai nel core
- [[soglie-disingaggio-e-attrito-aggregato]] — P1 (soglia di disingaggio), S9 (fog-of-war), S8
  (stress di scala): i punti aperti che la proposta plausibilmente intercetta
- `Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` — §3.3 (conto sul tick),
  §4.2 (latenze RIV/VAL/COM/ATT), §6 (disciplina trasversale, regola su sympy)
- `Code/Dynamic_War_Manager/Source/Logic/Contact_Scheduler.py`,
  `Code/Dynamic_War_Manager/Source/Logic/Damage_Model.py` — misurati direttamente
- [llama.cpp — Performance on Nvidia CUDA, discussione #15013](https://github.com/ggml-org/llama.cpp/discussions/15013)
  — RTX 3090, Llama-2-7B Q4_0: pp512 5.560 t/s, tg128 162 t/s
- [LLM Tokens/Sec Benchmarks 2026 (llama.cpp b3520, Q4_K_M, 2048 ctx)](https://mustafa.net/llm-tokens-per-second-benchmarks/)
  — RTX 3090: 7B 95 t/s, 13B 55 t/s, 34B 28 t/s
- [HyperQwen — Qwen3 27B su singola RTX 3090 con vLLM](https://github.com/syv-ai/qwen38-27b-rtx3090)
  — 127 t/s a utente singolo, ~1.035 t/s a 64 concorrenti
- Erik Larsen, [*The Instability of Safety*, arXiv:2512.12066](https://arxiv.org/pdf/2512.12066),
  appendice «Greedy Decoding Non-Determinism» — Llama 3.1 8B 73,4% / **Qwen 2.5 7B 17,6%** di
  risposte byte-identiche a temperatura 0,0 fra seed diversi
- [vLLM — Batch Invariance](https://docs.vllm.ai/en/latest/features/batch_invariance/) — garanzie,
  limiti hardware, costo prestazionale non quantificato, nessuna garanzia fra versioni/hardware
- [Thinking Machines Lab — Defeating Nondeterminism in LLM Inference](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)
  — diagnosi della varianza da batch come causa radice

## 8. Conclusioni e Implicazioni per Warfare-Model

**Cosa non cambia**: l'architettura a 4 strati di [[virtual-session-engine-des]] resta invariata. La
Fase 4 (`Engagement_Resolver`) va scritta come già deciso — Pk = accuracy × destroy_capacity, salva
di Hughes per il molti-contro-molti, latenze di reazione come eventi futuri schedulati, tutto in
forma chiusa. Nessuno dei quattro vincoli è stato aggirato o rinegoziato da questa analisi.

**Cosa la proposta guadagna**: due usi legittimi e precisamente delimitati — (c) debrief narrativo a
valle dello stato, (d) authoring offline — più una **regola generale che vale la pena scrivere una
volta sola**, perché la domanda si ripresenterà: *nessun componente non riproducibile per
costruzione può stare sulla traiettoria di stato di una sessione*. Formulata così, la regola non
parla di LLM e copre anche i casi futuri (un servizio di rete, un modello appreso, un'API esterna).
Proposta formale in [[llm-locale-ruolo-e-confini]], `status: proposed`.

**Cosa va corretto a prescindere da qualunque decisione sull'LLM**: il difetto di § 6 su
`closest_point_of_approach`. È l'unico elemento di questa analisi che riguarda codice esistente e
che ha un impatto misurato su un vincolo dichiarato.
