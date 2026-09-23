---
title: "Ruolo e confini di un LLM locale nel motore di sessione"
type: decision
tags: [architecture, dwm, llm, reproducibility, discrete-event, core]
created: 2026-09-22
updated: 2026-09-22
status: proposed
affects: ["[[logic-decision]]", "[[logic-routing]]", "[[command]]"]
related: ["[[llm-locale-nel-motore-des]]", "[[virtual-session-engine-des]]", "[[core-simulator-agnostic]]", "[[soglie-disingaggio-e-attrito-aggregato]]"]
---

> **`status: proposed`** — questa pagina è una **raccomandazione**, non una decisione presa. Nessuna
> riga di codice è stata scritta o modificata. La decisione spetta all'utente; finché non è
> accettata, il comportamento vigente resta quello di [[virtual-session-engine-des]] (nessun LLM da
> nessuna parte nel motore).
>
> **Aggiornamento 2026-09-23**: l'utente ha **rimandato** la decisione — "per il momento non
> consideriamo LLM nel motore". Non è un rifiuto (la pagina non va marcata `superseded`): nessuna
> delle quattro opzioni (R1-R4) è stata formalizzata, R3 non entra nel backlog. Si riprende se/quando
> la domanda si ripresenterà.

## Contesto

L'utente ha proposto di usare un **LLM locale** (Qwen2.5-7B o Qwen3 nell'ordine di 8-27B
quantizzato, su RTX 3090 da 24 GB) per «valutare le diverse condizioni che possono verificarsi
durante i passi event-driven» delle sessioni virtuali. La formulazione era volutamente aperta.

La valutazione completa — disambiguazione in quattro letture possibili, conto sul budget di calcolo,
verifica sperimentale della riproducibilità — è in [[llm-locale-nel-motore-des]]. Questa pagina
registra solo cosa se ne propone di fare.

La domanda si ripresenterà (un servizio di rete, un modello appreso, un'API esterna pongono lo
stesso problema), quindi conviene fissare una regola generale invece di rispondere caso per caso.

## Decisione proposta

### R1 — Regola generale: niente componenti non riproducibili sulla traiettoria di stato

**Nessun componente la cui riproducibilità non sia garantita per costruzione può partecipare alla
determinazione dello stato di una sessione.** La regola non nomina gli LLM: copre ogni componente
la cui uscita dipenda da qualcosa che il progetto non controlla e non versiona — ordine di riduzione
in virgola mobile su GPU, composizione di un batch, versione di un driver, un servizio remoto, i
pesi di un modello appreso.

Il criterio di ammissione è quello già applicato a `Damage_Model.resolve_hit`, che riceve `draw` dal
chiamante e non genera mai un numero casuale internamente: **la sorgente di variabilità deve essere
un dato in ingresso, esplicito, seedato e versionabile**. Un PRNG seedato lo soddisfa per
costruzione (algoritmo intero, esattamente specificato, indipendente dall'hardware); uno stack di
inferenza LLM no — la sua riproducibilità è una proprietà emergente che nessuno strato dichiara come
contratto. Misura di riferimento: **17,6% di risposte byte-identiche su Qwen2.5-7B a temperatura 0
fra seed diversi** (v. [[llm-locale-nel-motore-des]] § 3).

**Test operativo**, sulla falsariga del test di agnosticismo di [[core-simulator-agnostic]]:
*rimuovendo il componente, la sessione deve produrre lo stesso `SessionOutcome` byte per byte, a
parità di seed.* Se cambia qualcosa, quel componente era sulla traiettoria di stato e non doveva
esserci.

### R2 — Esclusi: LLM per evento e LLM per decisione dottrinale a runtime

Sono **respinti**, e ciascuno per due ragioni indipendenti:

- **per evento** (Pk, esito di un colpo, CPA): fallisce il budget di calcolo di 3-6 ordini di
  grandezza — **9,2 giorni per sessione** al limite superiore dichiarato, contro 0,86 s in forma
  chiusa; è lo stesso ordine di grandezza dei 74 giorni con cui la Strategia 1 a tick è già stata
  respinta. E viola R1.
- **per decisione dottrinale** (soglia di disingaggio P1, ROE, indirizzo strategico C2): viola R1
  in modo più insidioso, perché la frequenza bassa la fa sembrare innocua. E chiederebbe all'LLM
  proprio ciò che [[soglie-disingaggio-e-attrito-aggregato]] § P1 vieta esplicitamente — il valore
  di soglia «**non** va inventato: appartiene alla dottrina, quindi a `Context/Doctrine.py` o al
  livello C2, dove è un parametro dichiarato del lato». È la stessa regola che il progetto si è
  data sui coefficienti di attrito (*«stimati con un ATCAL interno, non inventati a tavolino»*),
  nella sua versione peggiore: un coefficiente inventato da una fonte scritta è almeno stabile e
  ispezionabile.

**Onestà sul conto**: la seconda opzione, limitata al *caso tipico* e a una chiamata per ingaggio
con un modello da 7B, costerebbe ~40 s e starebbe dentro il budget. Non è per aritmetica che viene
respinta, ma per R1 e per il vincolo simulator-agnostic — e va detto così, senza travestire
un'obiezione di principio da conto.

### R3 — Ammesso: debrief narrativo a valle, fuori dal core

Generazione di testo narrativo (debrief di missione, racconto di campagna) **dopo** che il
`SessionOutcome` è stato scritto, con questi confini:

1. **mai sulla traiettoria di stato**: legge `SessionOutcome`/`Campaign_State`, non scrive nulla che
   il motore rilegga mai. Il test R1 è il criterio di accettazione del componente, non
   un'aspirazione: va scritto come test;
2. **fuori dal core**, in un pacchetto di presentazione a sé, con import locale del runtime di
   inferenza — il core deve girare identico con il pacchetto disinstallato;
3. **il testo prodotto è un artefatto versionato**, non rigenerato a ogni apertura della campagna:
   una volta generato viene salvato accanto allo `SessionOutcome`, e il replay lo rilegge invece di
   richiamare il modello. Questo rende il debrief stabile senza chiedere all'inferenza una garanzia
   che non può dare;
4. **priorità bassa**: non risolve alcun punto aperto del progetto ed è esplicitamente subordinato
   alle Fasi 0, 4, 6, 7.

### R4 — Ammesso e incoraggiato: uso offline, a tempo di progettazione

Uso di un LLM (locale o no — a tempo di progettazione la distinzione non è architetturale) per
**enumerare, redigere e criticare** materiale che entra nel repo come codice o dato, mai come
chiamata a runtime. Costo a runtime: zero. Impatto su R1 e sul vincolo simulator-agnostic: nessuno,
per costruzione — è uno strumento di sviluppo, allo stesso titolo di un IDE.

È l'unica delle quattro opzioni che indirizza punti aperti reali e già catalogati:

- le **fixture degli scenari S1-S11** per la Fase 7 (composizioni di forze, domande poste, esiti
  qualitativi attesi);
- le tabelle di **`Context/Reaction_Profile.py`** (Fase 4) a partire dalle latenze SAM già
  documentate (Osa ~26 s, S-300P ~28 s, Tor 5-8 s, pilota 1-2 s, equipaggio carro ~31 s);
- l'enumerazione dei **casi di ROE e dottrina** per `Context/Doctrine.py`, e delle candidate
  soglie di disingaggio di P1.

**Condizioni non negoziabili**, che sono le stesse già adottate per le fonti esterne (v.
[[lanchester-vs-motore-des]]): ogni artefatto passa per revisione umana prima di entrare nel repo;
la provenienza va dichiarata; e si prende la **forma** (l'enumerazione dei casi, la struttura di una
tabella), **mai i numeri** — un valore di soglia o un coefficiente resta o una dichiarazione
dell'utente o l'esito di un ATCAL interno, mai un'uscita di modello accettata così com'è.

## Motivazione

La discriminazione fra le quattro letture è fatta su numeri verificabili — latenza di inferenza
misurata su hardware reale, costo delle primitive in forma chiusa misurato su questo repo, stima
degli eventi per sessione con assunzioni dichiarate — e su una misura sperimentale pubblicata di
non-determinismo a temperatura 0, non su una preferenza di design. È lo stesso metodo con cui è
stata respinta la Strategia 1 a tick, ed è per questo che due delle quattro opzioni passano invece
di essere respinte in blocco.

R1 vale più della risposta specifica sugli LLM: è la formulazione generale del vincolo #2
dell'utente, e risponde in anticipo alla prossima proposta della stessa famiglia.

## Conseguenze

**Se accettata**:

- nulla cambia nella Fase 4 in partenza: `Engagement_Resolver` nasce interamente in forma chiusa,
  come già previsto;
- R1 diventa un criterio di revisione dichiarato, con un test associato (stesso seed + componente
  rimosso → stesso `SessionOutcome`), da aggiungere alla Fase 7 accanto al test di agnosticismo;
- R3 entra nel backlog a priorità bassa, come pacchetto di presentazione fuori dal core;
- R4 formalizza una pratica di fatto già in uso, con le condizioni di revisione e provenienza rese
  esplicite.

**Se respinta**: nulla cambia; [[llm-locale-nel-motore-des]] resta come analisi archiviata e questa
pagina va marcata `status: superseded` o rimossa.

**Esplicitamente fuori perimetro**: il difetto di prestazioni su
`Contact_Scheduler.closest_point_of_approach` (52,95 ms/chiamata contro 21,6 µs di matematica vera,
v. [[llm-locale-nel-motore-des]] § 6). È stato trovato durante questa analisi ma non c'entra nulla
con gli LLM, riguarda codice già spedito, e va deciso separatamente.

## Punti aperti da confermare con l'utente

1. **Quante delle tre macchine del progetto hanno una GPU adatta?** Se la RTX 3090 è su una sola, R3
   è comunque un componente che non tutte le macchine possono eseguire — accettabile per un
   componente di presentazione, decisivo se un giorno si volesse rivalutare R2.
2. **L'intenzione originale era (a), (b), (c) o (d)?** L'analisi le valuta tutte e quattro senza
   sceglierne una, ma se l'intenzione era specificamente (b) — le decisioni dottrinali — vale la
   pena guardare insieme la controproposta implicita: quelle decisioni vanno *dichiarate* in
   `Context/Doctrine.py`, e l'LLM può aiutare a scriverle (R4), non a prenderle (R2).
3. **Il debrief narrativo (R3) interessa davvero?** Non è mai stato chiesto in nessun documento di
   progetto; è ammissibile, non è necessario.
4. **R1 va adottata come regola generale o solo come risposta a questa proposta?** Come regola
   generale ha implicazioni oltre gli LLM (servizi di rete, modelli appresi, API esterne).

## Fonti

- [[llm-locale-nel-motore-des]] — analisi che origina questa proposta, con tutti i numeri
- [[virtual-session-engine-des]] — architettura e i 4 vincoli entro cui la proposta deve stare
- [[core-simulator-agnostic]] — test di agnosticismo, modello del test di R1
- [[soglie-disingaggio-e-attrito-aggregato]] — P1/S9, i punti aperti che la proposta intercettava
- `Code/Dynamic_War_Manager/Source/Logic/Damage_Model.py` — `resolve_hit(accuracy,
  destroy_capacity, draw)`, il modello di riferimento per il criterio di R1
