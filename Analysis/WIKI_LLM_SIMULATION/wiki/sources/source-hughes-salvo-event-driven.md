---
title: "Modello event-driven a salva di Hughes — sessione conversazionale con assistente AI"
type: source
tags: [hughes, salvo-combat-model, discrete-event, combat-resolution, sead, ground, air, naval, medium-confidence]
created: 2026-09-22
updated: 2026-09-22
file: RAW/Event_Driven_Salva_Hughes/ (6 file .docx + edit.pdf)
authors: [assistente AI non identificato, prompt dell'utente]
year: 2026
related: ["[[salvo-combat-model]]", "[[wayne-hughes]]", "[[event-driven-simulation]]", "[[virtual-session-engine-des]]", "[[hughes-salvo-vs-engagement-resolver]]", "[[source-lanchester-scenari-ai]]"]
---

# Modello event-driven a salva di Hughes — sessione conversazionale

## Perché una sola pagina per sette file

I sette file **non sono sette fonti indipendenti**: sono i turni consecutivi di **una sola
conversazione** con un assistente AI, e la catena si verifica nel testo — ogni documento si chiude
con un elenco di proseguimenti proposti, e il documento successivo è la risposta a uno di essi.
Ricostruita integralmente:

```
D1  "Illustrami cos'è il modello event-driven a salva di Hughes"
      └─► (domanda nuova dell'utente)
D2  "Come viene applicato … in contesti eterogenei … con supporto aereo (CAS)"
      └─► propone: algoritmo di targeting · fattore stocastico/terreno · simulazione numerica
D3        "Sviluppa tutte e tre gli argomenti." ── risponde esattamente ai tre
            └─► propone: variabile SEAD · munizioni limitate
D4          "Introduci la variabile SEAD, le scorte limitate … e … una ritirata"
              └─► propone: «come una contro-salva di artiglieria Blu avrebbe potuto
                  interrompere la fase SEAD di Rossa»
D5            `edit.pdf` ── risponde a quella domanda (event tree, TTE, scelta dello scenario)
                └─► propone: estensione matematica · coda degli eventi
D6              "si illustra sia l'estensione matematica che la coda degli eventi"
                  └─► propone: radar fallibile · spostamento fisico
D7                "Introduci sia il puntamento di radar fallibile che lo spostamento fisico"
```

`edit.pdf` **non è un documento di sintesi**: è la stampa da browser (Firefox/cairo, 3 pagine) del
turno intermedio D5, che non era stato salvato in `.docx`. Occupa il suo posto nella catena e non
riassume nulla.

**Verifica richiesta esplicitamente: questa fonte non ha alcun rapporto con
[[source-lanchester-scenari-ai]].** Controllato sul contenuto, non sui nomi file: non compare una
sola equazione differenziale, né i nomi Lanchester/Bracken/Helmbold/Dupuy/SINDy, né alcuno dei
coefficienti $\alpha,\beta,\gamma$ di quel set, né i suoi scenari (100 tank + 200 mecc + 24 CAS
ecc.). Le composizioni di forze qui sono altre (20 Tank Blu / 30 Tank Rossi / 4 CAS / 5 SHORAD /
5 batterie), il passo temporale è il secondo e non il giorno, e la famiglia matematica è quella
degli impulsi discreti. Sono due fonti disgiunte.

## Riepilogo Esecutivo

La sessione parte da un'esposizione **corretta** del modello a salva di Hughes (D1: attribuzione,
anno, equazioni di base, dogma *fire effectively first*) e lo estende in sei passi verso un
risolutore d'ingaggio terrestre/aereo event-driven: vettorializzazione eterogenea e matrici di
letalità incrociata (D2), algoritmo di targeting greedy con anti-overkill e modificatori di terreno
(D3), degradazione difensiva da SEAD, scorte di munizioni e doppia soglia di ritirata (D4),
alberi degli eventi e criteri di selezione dello scenario (D5), coda degli eventi a priorità con
iniezione dinamica delle reazioni (D6), probabilità di acquisizione radar e *shoot-and-scoot* con
codice Python eseguibile (D7).

Il valore della fonte è **strutturale, non numerico**, e va letto in due blocchi nettamente
diversi per affidabilità:

- **D1 è solido.** È l'unico documento della sessione con contenuto verificabile, e regge: il
  modello, l'autore, l'anno e le equazioni corrispondono alla letteratura. Colma la lacuna
  segnalata come prioritaria dall'ingestione Lanchester (*«la lacuna resta aperta e va colmata con
  una fonte su Hughes»*, [[lanchester-vs-motore-des]] § 2b). Distillato in [[salvo-combat-model]].
- **D2-D7 sono estensioni inventate dall'assistente**, senza alcuna citazione, con parametri scelti
  a mano e con **cinque difetti aritmetici o logici accertati** (v. § Lacune). La loro utilità sta
  nei *meccanismi* proposti — saturazione difensiva, capacità d'intercettazione per salva,
  esaurimento munizioni, soglia di shock, re-scheduling dopo lo spostamento — non nelle formule
  con cui sono scritti né nei numeri con cui sono illustrati.

## Contenuto per documento

| # | File | Natura | Contenuto tecnico |
|---|---|---|---|
| D1 | `Illustrami cos'è il modello event-driven a salva di Hughes…` | esposizione | Hughes 1995; parametri $\alpha,\beta$ (offesa), $y,z$ (difesa), $w,x$ (staying power); $\Delta A = -(\beta B - yA)/w$; clamp del numeratore a 0; effetto cascata; *fire effectively first*; estensioni stocastiche/Monte Carlo |
| D2 | `Come viene applicato … contesti eterogenei … (CAS)` | estensione | Vettore di stato per categoria; matrici di offesa $\mathbf A$ e difesa $\mathbf Z$; staying power dipendente dal tipo di minaccia; sequenza a 4 fasi CAS→SHORAD→impatto→risposta; **effetto saturazione**; SEAD come apri-strada |
| D3 | `Sviluppa tutte e tre gli argomenti.` | estensione | Algoritmo di targeting in 5 fasi (matrice priorità $P[i][j]$ = efficacia × valore tattico, greedy con stop a saturazione per evitare l'overkill); $\alpha_{\text{eff}} = \alpha \cdot C_{\text{terr}} \cdot X_{\text{stoc}}$; tabella terreno (pianura 1.0/1.0, bosco 0.6/1.5, urbano 0.3/2.5); scenario numerico 20 Tank Blu + 5 SHORAD vs 30 Tank Rossi + 4 CAS |
| D4 | `Introduci la variabile SEAD, le scorte … e … una ritirata` | estensione | $z_{\text{eff}} = z(1-\sigma)$ con $\sigma = \min(1, S\alpha_{\text{SEAD}}/(B_{\text{SH}} w_{\text{SH}}))$; munizioni come scorta decrementata per salva, a zero l'offesa crolla; **due** soglie di ritirata: perdite cumulate (% dell'organico) e **shock da salva** (% persa in un solo impulso) |
| D5 | `edit.pdf` | estensione | Time-to-Event = sensor-to-shooter + reazione C2 + tempo di volo; albero degli eventi a 3 rami; selezione dello scenario con Monte Carlo (metodo A) o utilità $U = \text{danni} - \text{perdite} - \text{munizioni}$ + minimax (metodo B); ricalcolo di Hughes "in flight" |
| D6 | `si illustra sia l'estensione matematica che la coda degli eventi` | estensione | Sistema a impulsi accoppiati per il duello controbatteria; $\gamma_{\text{Blu}}$ = frazione di colpi sparati prima di subire l'impatto; $S_{\text{eff}} = (R_{\text{Art}} + \gamma_{\text{Blu}}\Delta R_{\text{Art}})\alpha_{\text{SEAD}}$; coda a priorità con riordino per iniezione |
| D7 | `Introduci sia il puntamento di radar fallibile che lo spostamento fisico` | estensione | $P_{\text{acq}} = P_{\text{base}}(1-\text{ECM})C_{\text{meteo}}$, test Bernoulli all'evento di fuoco; $T_{\text{flight}} = d/v_{\text{proj}}$; $E_{\text{evasione}} \in \{0,1\}$ da confronto di tempi; `EVENT_UNIT_DISPLACEMENT`; ~90 righe di Python con `heapq` |

## Contributi Principali

1. **Esposizione corretta del modello a salva** (D1) — colma la lacuna dichiarata. V.
   [[salvo-combat-model]].
2. **Termine difensivo con saturazione** (D1, D2) — il parametro $z$ è una **capacità di
   intercettazione per salva**, non una probabilità per colpo. È la differenza che produce la
   saturazione: oltre la capacità, il surplus penetra *integralmente*. È l'unico elemento
   strutturale che il progetto oggi non ha in nessuna forma (v.
   [[hughes-salvo-vs-engagement-resolver]] § 2).
3. **Doppia soglia di ritirata** (D4) — non solo perdite cumulate ma anche **shock da salva**
   (perdita istantanea oltre una quota in un solo impulso). Estende la proposta P1 già in piedi in
   [[soglie-disingaggio-e-attrito-aggregato]], che contemplava la sola soglia cumulata.
4. **Munizioni come risorsa consumabile per-asset** (D4, D7) — con l'unica conseguenza operativa
   che conta: a scorta esaurita l'unità non è neutra, è un **bersaglio inerme** o si ritira per
   ragioni logistiche. Il progetto non ha nulla del genere (v. § Applicabilità).
5. **Re-scheduling dopo lo spostamento fisico** (D7) — `EVENT_UNIT_DISPLACEMENT` come evento di
   prima classe che invalida i calcoli geometrici già in coda. È un punto architetturale, non un
   dettaglio: v. [[hughes-salvo-vs-engagement-resolver]] § 4.
6. **Targeting anti-overkill** (D3) — allocare fuoco a un bersaglio *fino a saturazione o
   distruzione stimata*, poi passare al successivo. Semplice, e risolve un problema reale di
   qualunque risolutore molti-contro-molti.

## Entità Menzionate

- [[wayne-hughes]] — autore del modello; attribuzione, grado e anno **verificati e corretti**,
  unica affermazione bibliografica solida del set.

## Concetti Chiave Trattati

- [[salvo-combat-model]] — trattato correttamente in D1, esteso in modo non verificato in D2-D7
- [[event-driven-simulation]] — coda a priorità, iniezione dinamica, salto temporale fra eventi:
  esposizione corretta e coerente con la pagina già in wiki
- [[stochastic-simulation]] — annunciata (Monte Carlo, $X_{\text{stoc}}$, $P_{\text{acq}}$) ma
  **mai applicata** in nessuno dei tre scenari numerici, che restano tutti deterministici

## Citazioni Rilevanti

> «Il combattimento non è visto come un flusso costante di danni, ma come una successione di
> "impulsi" istantanei (le salve). Ciascun lancio di missili costituisce un evento singolo che
> altera improvvisamente e radicalmente lo stato delle forze in campo.» (D1)

È la frase che giustifica la scelta già fatta dal progetto: la famiglia a salva è nativamente
compatibile con un DES a coda eventi, quella di Lanchester no.

> «Se il CAS lancia una salva di dimensioni superiori alla capacità massima di tracciamento e
> ingaggio dello SHORAD, i sistemi difensivi vengono saturati. Il surplus di missili penetra le
> difese indisturbato.» (D2)

> «Se le munizioni terminano, il potere offensivo di quell'unità crolla istantaneamente a 0,
> trasformando l'unità in un bersaglio inerme o costringendola a una ritirata logistica.» (D4)

> «Le equazioni di Hughes vengono quindi ricalcolate dinamicamente tenendo conto che l'attaccante
> originario (Rossa) è ora, a sua volta, sotto attacco.» (`edit.pdf`, D5)

Citata perché è **sbagliata**, ed è l'errore concettualmente più grave del set: v. Lacuna A.

## Lacune e Contraddizioni

**A. Violazione di causalità: la salva in volo viene ridotta retroattivamente.** È il difetto
centrale di D5 e D6, e contamina la loro conclusione dottrinale. In D6 l'Artiglieria Rossa spara a
$t=10{:}00$ con 45 s di volo; la controbatteria Blu impatta a $t=10{:}40$, cioè **5 secondi prima**
che i proiettili Rossi — già in aria da 40 secondi — arrivino a destinazione. Il documento allora
riduce il volume della salva Rossa a posteriori, tramite
$S_{\text{eff}} = (R_{\text{Art}} + \gamma \Delta R_{\text{Art}})\alpha_{\text{SEAD}}$, «tenendo
conto che Rossa è ora sotto attacco». Ma i proiettili sono partiti: distruggere i pezzi non fa
sparire le munizioni in volo. La controbatteria sopprime la salva **successiva**, non quella già
lanciata. Il documento ottiene così il risultato che vuole (lo SHORAD Blu sopravvive e respinge il
CAS) da un meccanismo che non esiste. Da questo discende la conseguenza progettuale più importante
della fonte, in positivo: **il payload di una salva va congelato all'istante di fuoco**, non
ricalcolato all'istante d'impatto.

**B. Errore aritmetico e doppia notazione temporale in D6.** Il testo calcola l'impatto della
controbatteria Blu come «$10.00 + 5 (\text{radar}) + 15 (\text{C2}) + 20 (\text{volo}) = 40.00s$»:
la somma di quegli addendi è **50**, non 40 (il termine `10.00` è stato semplicemente omesso). E la
coda immediatamente sotto riporta un terzo valore ancora, `t = 10.40s`. I tre numeri sono
reciprocamente incompatibili. La spiegazione è che i timestamp sono in realtà in notazione
`mm.ss` — $10{:}00 + 5\text{s} + 15\text{s} = 10{:}20$, $+20\text{s} = 10{:}40$ — ma sono etichettati
in secondi per tutto il documento, e la formula in prosa li tratta come secondi. Tre notazioni in
quattro righe.

**C. $\gamma_{\text{Blu}}$ compare al quadrato senza giustificazione** (D6). Dato
$\Delta R_{\text{Art}} = -\gamma_{\text{Blu}}\beta_{\text{CB}}B_{\text{Art}}/x_{\text{Art}}$,
sostituire in $S_{\text{eff}} = (R_{\text{Art}} + \gamma_{\text{Blu}}\Delta R_{\text{Art}})
\alpha_{\text{SEAD}}$ dà
$S_{\text{eff}} = (R_{\text{Art}} - \gamma_{\text{Blu}}^2\beta_{\text{CB}}B_{\text{Art}}/
x_{\text{Art}})\alpha_{\text{SEAD}}$. Il fattore di tempismo è applicato due volte allo stesso
effetto. Non c'è lettura in cui $\gamma^2$ abbia senso: la frazione di colpi sparati in tempo utile
è già dentro $\Delta R_{\text{Art}}$.

**D. Il modello uccide 10 unità su 5 — e viola la propria formula.** In D4 la salva SEAD vale 10
colpi contro 5 SHORAD di staying power 1, e il documento scrive
$\Delta B_{\text{SHORAD}} = -10/1 = -10$ unità su una forza che ne conta 5. È lo stesso difetto già
trovato in [[source-lanchester-scenari-ai]] (§ Lacuna E), qui però **aggravato**: il medesimo
documento, tre paragrafi sopra, definisce $\sigma = \min(1, \cdot)$ proprio per limitare la
soppressione, e poi non la usa. Il clamp di D1 («se la difesa supera l'attacco il numeratore
diventa 0») copre solo il termine difensivo; né D1 né i suoi seguiti limitano mai $\Delta$ alla
consistenza della forza bersaglio, che è invece parte del modello originale.

**E. Doppio conteggio nella formula di soppressione** (D4). In
$\sigma = \min(1, S\alpha_{\text{SEAD}}/(B_{\text{SHORAD}}w_{\text{SH}}))$ il simbolo $S$ è definito
come «volume della salva SEAD» e viene poi moltiplicato di nuovo per $\alpha_{\text{SEAD}}$. Nello
scenario dello stesso documento il volume della salva **è** $5 \times \alpha_{\text{SEAD}} = 10$:
$S\alpha_{\text{SEAD}}$ vale quindi 20, cioè il doppio dei colpi realmente sparati.

**F. Il confronto "con SEAD vs senza SEAD" è confondato dal cambio di regole, non solo dall'ordine.**
D3 e D4 sono lo **stesso scenario** (20 Tank Blu, 5 SHORAD, 30 Tank Rossi, 4 CAS, terreno collinare
$w_{\text{eff}} = 3.6$), rispettivamente senza e con la fase SEAD, e il secondo conclude che Rossa
«vince l'ingaggio con zero perdite di corazzati». Ma in D3 Blu perde 10 Tank su 20 in un solo
impulso, cioè il **50%**, ben oltre la soglia di shock del **35%** che D4 introduce: applicando a
D3 le regole di D4, anche lì Blu sarebbe andata in rotta senza sparare, e i 3 carri Rossi
distrutti — l'unica perdita Rossa dell'intera sessione, e la sola base del merito attribuito al
SEAD — non ci sarebbero stati. Il vantaggio misurato del SEAD si riduce a 7 superstiti contro 10.
È la stessa classe di errore trovata in [[source-lanchester-scenari-ai]] (§ Lacuna F), con una
variante: là cambiava l'ordine di risoluzione fra le due simulazioni, qui cambia il **regolamento**.

**G. Il codice Python di D7 non implementa il modello di Hughes.** La riga che pretende di
risolverlo è `danni = salva / forces['Blu']['SHORAD_Staying']`: **manca il termine difensivo**, cioè
l'unica cosa che distingue Hughes da una divisione. Il campo `SHORAD_Z = 2` è dichiarato nel
dizionario delle forze e non viene mai letto. Il ramo controbatteria usa un letterale
(`danni = 5 / …`) invece della consistenza reale. `random.random()` è chiamato **senza seed**, che è
già una precondizione bloccante nota del progetto. `Is_Moving` è scritto e mai letto, `Ammo` è
decrementato e mai verificato per terminare la simulazione. Il codice è illustrativo, non
eseguibile come risolutore.

**H. La stocasticità è annunciata e mai usata.** D3 dedica una sezione a $X_{\text{stoc}}$
(gaussiana o Weibull) e alla Monte Carlo; D5 descrive per esteso l'estrazione fra scenari e le
10.000 repliche. Nei tre scenari numerici effettivamente svolti (D3, D4, D6) **non viene estratto
nulla**: sono singole realizzazioni deterministiche. L'unica estrazione dell'intero set è
`random.random()` nel codice di D7.

**I. Parametri incoerenti fra documenti, senza spiegazione.** Le latenze della stessa catena
sensore→C2 valgono 5 s + 15 s in D6 e 3 s + 7 s in D7, per lo stesso scenario. Il coefficiente di
terreno collinare $C_{\text{terr}} = 1.2$ usato in D3 e D4 **non compare nella tabella dei terreni
dello stesso D3** (che elenca solo 1.0, 1.5, 2.5). L'arrotondamento è incoerente: $-12{,}7 \to -13$
in D4, $-3{,}33 \to -3$ in D3.

**J. Contraddizione interna sulla contabilità delle munizioni** (D3 vs D4). D3 usa $z = 2$
intercettazioni per SHORAD e fa abbattere **10** missili ai 5 sistemi; D4 attribuisce agli stessi
5 sistemi «1 sola salva difensiva a testa (**5 razzi totali**)». Le due cifre non possono coesistere.
Più in generale, la regola di consumo di D4
($M_{\text{attuali}} = M_{\text{attuali}} - \text{Salva Lanciata}$) è dimensionalmente sbagliata
rispetto al suo stesso scenario, dove $M$ è contato in **salve** («Tank: 3 salve») mentre il
sottraendo è un numero di **colpi**.

**K. Tempo di volo balistico calcolato come moto rettilineo uniforme** (D7).
$T_{\text{flight}} = d/v_{\text{proj}}$ con $v$ = velocità alla bocca dà 37,5 s per 30 km a
800 m/s; il valore reale per un tiro d'artiglieria a quella distanza è dell'ordine di 70-90 s. Non
invalida la struttura (un tempo di volo *è* un ritardo da schedulare) ma nessuno dei numeri di D7 è
utilizzabile come dato.

**L. Citazioni: stesso difetto della fonte Lanchester.** Le 11 note di D1 sono **nomi di dominio
nudi** (`en.wikipedia.org`, `scispace.com`, `cimsec.org`, `warquants.com`, `usni.org`,
`brocku.scholaris.ca`, `repository.gatech.edu`, `apps.dtic.mil`, `calhoun.nps.edu`, `nwiss.org`) —
nessun titolo, autore, anno, DOI o pagina. D2-D7 non hanno **alcuna** citazione. La differenza
rispetto a [[source-lanchester-scenari-ai]] è che qui le affermazioni di D1 sono comunque
verificabili altrove e **risultano corrette** (v. [[wayne-hughes]]): la fonte non è citabile, ma il
suo nucleo non è inventato.

## Applicabilità al Warfare-Model

Valutazione completa, componente per componente, in
**[[hughes-salvo-vs-engagement-resolver]]**. In sintesi:

- **Il progetto ha già scelto questo modello** come risolutore primario molti-contro-molti della
  Fase 4 ([[virtual-session-engine-des]] § Architettura, strato 2). Questa fonte è quindi la prima
  a descrivere ciò che il progetto ha deciso di costruire, ed è la ragione per cui va letta in
  positivo e non, come la precedente, in negativo.
- **Direttamente utilizzabile**: il termine difensivo a **capacità di intercettazione per salva**
  con saturazione (l'unico pezzo strutturale mancante), la soglia di **shock da salva**, il
  congelamento del payload all'istante di fuoco (per contrasto con la Lacuna A), il targeting
  greedy anti-overkill.
- **Da non importare**: nessun coefficiente, nessuna latenza, nessun tempo di volo, nessuno dei
  parametri di terreno. Il progetto ha già in casa dati migliori e ricercati —
  `Air_Route_Manager.threat_reaction_times()` restituisce
  `(min_detection_time, min_fire_time)` da una tabella SAM reale, cioè esattamente la
  decomposizione che D5/D7 inventano con numeri a piacere.
- **Introduce una precondizione nuova**: le **scorte di munizioni per asset**, che non esistono nel
  progetto in nessuna forma e non erano nell'elenco delle 11 precondizioni bloccanti di
  [[virtual-session-engine-des]].
- **Solleva un punto architetturale**: lo spostamento fisico *durante* l'ingaggio invalida le
  finestre di contatto già calcolate. V. [[hughes-salvo-vs-engagement-resolver]] § 4 e
  [[risolutore-ingaggio-salva-fase4]] § R4.
