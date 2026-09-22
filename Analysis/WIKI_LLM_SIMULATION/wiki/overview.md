---
title: "Panoramica — Modelli di Simulazione Bellica"
type: overview
tags: [campaign-model, combat-simulation, wargame, warfare-model]
created: 2026-05-27
updated: 2026-09-22
sources: ["[[source-theater-level-campaign-model]]", "[[source-simulation-techniques-past-conflicts]]", "[[source-lanchester-scenari-ai]]", "[[source-hughes-salvo-event-driven]]"]
---

# Panoramica del Dominio

> Questo documento rappresenta la sintesi evoluta di tutta la conoscenza accumulata nel wiki. Viene aggiornato da Claude dopo ogni ingestione significativa.

---

## Dominio di Ricerca

Questa base di conoscenza copre la **modellazione e simulazione di conflitti militari**, con focus su:

1. **Modelli di campagna militare** (Theater/Campaign Level Models): sistemi che simulano operazioni militari su scala operativa o strategica, considerando logistica, forze, territorio e dinamiche di combattimento.

2. **Tecniche di simulazione dei conflitti**: metodologie matematiche e computazionali usate per rappresentare il combattimento — da modelli Lanchester alle simulazioni ad agenti.

3. **Sviluppo del Warfare-Model**: progetto in corso che implementa un Dynamic War Manager (DWM) per il simulatore DCS (Digital Combat Simulator), con gestione dinamica di risorse aeree, navali e terrestri.

---

## Progetto Warfare-Model

Il progetto principale a cui questo wiki fa riferimento è situato in:
`/home/marco/Sviluppo/Warfare-Model/`

**Aggiornamento 2026-09-18**: la struttura del codice e le decisioni architetturali adottate NON vivono più qui (questa sezione era stale dal 2026-05-27 — citava ancora `Manager.py` come "orchestratore principale" e `Military_Resources_Assigner.py`, rinominato da tempo in `Air_Resources_Assigner.py`). Le due nuove sezioni del wiki sono ora la fonte di verità:

- **`wiki/project/`**: struttura attuale del codice, sottosistema per sottosistema, verificata contro il codice reale — [[asset-air]], [[asset-ground-naval]], [[asset-base]], [[context-foundation]], [[context-state]], [[block]], [[component]], [[logic-routing]], [[logic-decision]], [[datatype]], [[utility-manager]], [[testing-conventions]].
- **`wiki/decisions/`**: log delle decisioni architetturali adottate, in stile ADR — [[region-tactical-strategic-refactor]], [[combat-power-priority-redesign]], [[datatype-route-edge-waypoint]], [[air-priority-target-specific-loadout]], [[asset-type-vs-category]], [[c2-hierarchy-design]], [[campaign-temporal-model]] (superata da quest'ultima), [[module-audit-2026-08-16]] (storica).

`Analysis/Modules/00-11_*.md` resta come istantanea storica dell'audit del 2026-08-16, non aggiornata da allora — ogni pagina rimanda ora esplicitamente alla corrispondente pagina `wiki/project/`.

**Sintesi architetturale corrente** (dettaglio nelle pagine sopra): DWM = pacchetti `Asset/`, `Block/`, `Component/`, `Context/`, `DataType/`, `Logic/` sotto `Code/Dynamic_War_Manager/Source/`; un nuovo pacchetto `Command/` (C2 a due livelli + `Theater_Session_Manager`) è **progettato ma non ancora costruito** (vedi [[c2-hierarchy-design]]).

**Aggiornamento 2026-09-22**: due decisioni architetturali aggiuntive guidano ora lo sviluppo —
[[core-simulator-agnostic]] (il core deve restare indifferente al simulatore, DCS è solo un
adapter dietro un contratto `SessionOrder`/`SessionOutcome`) e [[virtual-session-engine-des]] (il
motore di esecuzione delle sessioni virtuali è un DES a coda eventi con scheduling analitico dei
contatti, non un tick fisso). Le Fasi 1 (cinematica) e 2 (percezione/`ThreatAA`) di quest'ultima
sono fatte e pushate sul branch `analysis/dce-dcs-persistence`, non ancora su `main`; la Fase 3
(`Logic/Contact_Scheduler.py`, scheduler analitico dei contatti) è completata sullo stesso branch.

Tre proposte aperte in attesa di decisione dell'utente: [[soglie-disingaggio-e-attrito-aggregato]]
(soglie di disingaggio, forma del fallback aggregato, scenari S1-S11), [[llm-locale-ruolo-e-confini]]
(dove un LLM può e non può stare nel motore) e [[risolutore-ingaggio-salva-fase4]] (termini del
modello a salva di Hughes da adottare in `Logic/Engagement_Resolver.py`: saturazione difensiva,
soglia di shock, scorte munizioni per asset).

### Domande di Ricerca Aperte
*(Da aggiornare man mano che si ingeriscono fonti)*
- Come modellare al meglio l'interazione aria-terra nelle campagne dinamiche?
- Quali metriche (MOE/MOP) sono più appropriate per valutare lo stato della campagna?
- Come integrare simulazioni Monte Carlo per la valutazione degli esiti tattici?

---

## Stato della Conoscenza

| Area | Fonti | Copertura | Note |
|------|-------|-----------|------|
| Campaign Models | 1 | Buona | TLC (RAND 1994) — prototipo prossima generazione |
| Combat Simulation Techniques | 2 | Buona | TLC (computazionale) + Sabin (manuale/accademico) |
| Ground Attrition (CADEM) | 1 | Buona | Metodologia CADEM dettagliata |
| Air Warfare (SAM, A-A, A-G) | 1 | Media | Processo TLC descritto, dati da TAC BRAWLER/RJARS/JMEM |
| Adaptive Resource Allocation | 1 | Buona | Algoritmo SAGE descritto |
| Historical Conflict Modelling | 1 | Media | Sabin: wargaming accademico, comparative dynamic modelling |
| Wargame Design Theory | 1 | Buona | Anti-hindsight, 3 ruoli simulazione, dialettica Clausewitz |
| Modelli Lanchester | 1 | Scarsa | [[lanchester-models]]: tassonomia delle varianti + stato di validazione (negativo). Fonte a **bassa affidabilità**, nessuna fonte primaria |
| Equazioni a salva (Hughes) | 1 | Media | [[salvo-combat-model]]: formulazione base verificata (D1); 6 estensioni non verificate con difetti accertati (D2-D7). È la famiglia adottata dallo strato 2 del motore. Manca ancora una fonte primaria (*Fleet Tactics* stesso) |
| Agent-Based Models | 0 | Nessuna | Da acquisire fonti specifiche |

---

## Tesi in Evoluzione

Dopo le prime due ingestioni emergono le seguenti tesi di sintesi:

1. **La struttura game board è fondamentale**: la scelta tra piston/griglia/generalizzata determina cosa il modello può e non può rappresentare. La rete generalizzata del TLC è l'evoluzione naturale verso cui punta anche il DWM (Route/Area/Region).

2. **La simulazione stocastica è necessaria per l'analisi robusta**: i modelli deterministici danno false certezze. Gli esiti del combattimento sono intrinsecamente stocastici e devono essere trattati come tali. Sabin rafforza questo argomento: l'anti-hindsight richiede esiti incerti anche in simulazioni operative.

3. **L'allocazione adattiva delle risorse è il cuore del C²**: i modelli con script fissi non possono valutare il valore dei sistemi C⁴I. SAGE rappresenta un approccio concreto già implementato nel 1994 — direttamente applicabile ad `Air_Resources_Assigner.py`.

4. **La cross-resolution è necessaria ma difficile**: nessun approccio di aggregazione è teoricamente perfetto; la coerenza è approssimata. Il costo in dati e risorse è elevato.

5. **La validazione tramite "refighting" è il metodo sistematico per il DWM**: il comparative dynamic modelling di Sabin — variare assunzioni e confrontare con esiti noti — è esattamente il metodo da applicare a `tactical_evaluation_results.csv` per calibrare i parametri del DWM. Questa convergenza tra approccio storico (Sabin) e calibrazione computazionale (CADEM) è un risultato non ovvio.

6. **Wargame manuale e campaign model computazionale sono complementari, non alternativi**: risolvono lo stesso problema (dialettica tra volontà opposte) con diversi trade-off di fedeltà, velocità e scopo. Il DWM si colloca nel quadrante computazionale-analitico, ma deve mantenere la dimensione di agency tramite le missioni DCS.

7. **Nei modelli di attrito la matematica è la parte facile; la provenienza dei coefficienti è il
   problema** (ingestione 2026-09-22, v. [[lanchester-vs-motore-des]]). La differenza fra un modello
   Lanchester eterogeneo qualsiasi e [[cadem]] non è la forma delle equazioni — è identica — ma il
   fatto che i coefficienti del secondo vengano da [[killer-victim-scoreboard]] generati da un
   modello ad alta risoluzione. Ne segue la regola operativa del progetto: di una fonte di modelli
   aggregati si può prendere la *forma*, mai i *numeri*. Corollario verificato sul campo: dove un
   modello aggregato deve parametrizzare a mano (l'asimmetria stealth, la sequenza
   MR-SAM → SHORAD → AAA), un motore a eventi con geometria e percezione **deduce** lo stesso
   fenomeno dai dati fisici già disponibili.

8. **La riproducibilità è una proprietà di *costruzione*, non di *configurazione*** (analisi
   2026-09-22, v. [[llm-locale-nel-motore-des]]). Un PRNG seedato è riproducibile perché l'algoritmo
   è intero, specificato e indipendente dall'hardware; uno stack di inferenza LLM non lo è nemmeno a
   temperatura 0 — misurato, **17,6% di risposte byte-identiche fra seed su Qwen2.5-7B** — perché la
   sua determinatezza emerge da kernel, ordine di riduzione in virgola mobile, dimensione del batch
   e versione dei driver, che nessuno strato dichiara come contratto. Ne discende la regola generale
   proposta in [[llm-locale-ruolo-e-confini]], che non nomina gli LLM e vale anche per servizi di
   rete e modelli appresi: **nessun componente non riproducibile per costruzione sulla traiettoria
   di stato di una sessione**. Corollario emerso nello stesso conto: il costo per evento è la
   metrica che discrimina, e va misurato, non stimato a occhio — la stessa misura ha rivelato che
   `closest_point_of_approach` spende il 99,9% del tempo a imballare in `sympy.Point3D` un risultato
   calcolato in 21,6 µs.

9. **Una fonte tecnicamente debole può comunque colmare una lacuna, se letta a due velocità**
   (ingestione 2026-09-22, v. [[hughes-salvo-vs-engagement-resolver]]). Dei sette documenti di
   [[source-hughes-salvo-event-driven]], solo il primo è verificabile e regge; gli altri sei sono
   estensioni inventate da un assistente AI, senza citazioni, con almeno undici difetti aritmetici o
   logici accertati (una violazione di causalità, doppi conteggi, un `random.random()` senza seed).
   Eppure la fonte è comunque il primo passo utile a colmare la lacuna critica su Hughes: non per i
   numeri, che si scartano in blocco come già fatto con Lanchester, ma per i **meccanismi** che
   propone — saturazione difensiva per-salva, soglia di shock da salva, congelamento del payload
   all'istante di fuoco, scorte di munizioni come precondizione mai considerata prima. È la stessa
   disciplina "forma sì, numeri no" del punto 7, applicata questa volta a una fonte dove persino la
   forma va vagliata pezzo per pezzo, perché la fonte stessa contiene un pezzo di forma sbagliata
   (il ricalcolo retroattivo di una salva già in volo) accanto a pezzi corretti.

---

## Lacune da Colmare

- **Fonti primarie** sui modelli Lanchester — la lacuna è **solo parzialmente colmata** da
  [[source-lanchester-scenari-ai]], che dà una tassonomia ma **nessuna citazione verificabile**.
  Piste da chiudere: Bracken (calibrazione Ardenne/Kursk), Lawrence/Dupuy Institute (KDB e test
  falliti), Helmbold (soglie di ritirata)
- **Hughes, *Fleet Tactics* — testo o fonte primaria originale**: la lacuna critica è **parzialmente
  colmata** da [[source-hughes-salvo-event-driven]] (D1 verificato), ma resta senza fonte primaria
  citabile — se si vorrà calibrare il modello con numeri reali serve il testo originale, non una
  sessione conversazionale con un assistente AI
- Letteratura su modelli ad agenti per conflitti (MANA, ISAAC, ecc.)
- Standard NATO/militari per simulazione (DSEEP, HLA/RPR FOM)
- Documentazione DCS sull'architettura di missione e hook disponibili
- Letteratura su ottimizzazione per resource allocation in warfare (MILP, reinforcement learning)
- Fonti sull'algoritmo SAGE originale (TAC SAGE predecessore di RAND)

---

## Risorse Esterne Raccomandate

*(Da espandere)*
- [Military Operations Research Society (MORS)](https://www.mors.org)
- [Journal of Defense Modeling and Simulation](https://journals.sagepub.com/home/jdm)
- [Simulation Interoperability Standards Organization (SISO)](https://www.sisostandards.org)
