---
title: "Modelli Lanchester e scenari applicati — sessione conversazionale con assistente AI"
type: source
tags: [lanchester, attrition, combat-simulation, air, ground, sead, scenario, low-confidence]
created: 2026-09-22
updated: 2026-09-22
file: RAW/Lanchester/ (9 file .docx + drive-download-*.zip ridondante)
authors: [assistente AI non identificato, prompt dell'utente]
year: 2026
related: ["[[lanchester-models]]", "[[cadem]]", "[[killer-victim-scoreboard]]", "[[virtual-session-engine-des]]", "[[lanchester-vs-motore-des]]"]
---

# Modelli Lanchester e scenari applicati — sessione conversazionale

## Perché una sola pagina per nove file

I nove `.docx` **non sono nove fonti indipendenti**: sono i turni di **una sola sessione di
conversazione** con un assistente AI, e lo si verifica nel testo, non solo dai nomi file. Ogni
documento si chiude con una domanda di proseguimento che è letteralmente il titolo del documento
successivo:

```
"Puoi indicarmi dei modelli Lanchester validi…"   (04)
      └─► "Ti interesserebbe approfondire … un modello eterogeneo (vettoriale) … oppure SINDy?"
            └─► "tutti e due" (09)
                  └─► "Desideri … simulare un micro-calcolo numerico …?"
                        └─► "simulare un micro-calcolo numerico" (07)

"Analizziamo uno scenario di scontro aereo…" (03)
      └─► "…introduciamo una terza componente come i sistemi SAM…?"
            └─► "terza componente: sistemi SAM" (08)

"Analizza il seguente scenario: … CAS" (02)
      └─► "…introducendo una missione SEAD preliminare…?"
            └─► "si introduci una missione SEAD preliminare" (06)  ──► ri-emesso come (01)

"missione di interdizione" (05)   — ramo autonomo, stesso impianto
```

Il file `…CAS(1).docx` (01) **non è un documento nuovo**: è la sola tabella comparativa finale di
(06), ri-emessa con gli stessi identici numeri (95 / 191 / 15 / 109 / 35 / 28). Sono quindi ~8
turni utili, non 9 documenti. Nove pagine `sources/` separate avrebbero prodotto otto pagine
quasi vuote senza provenienza propria: una pagina sola, con la tabella per-documento qui sotto,
conserva la stessa informazione senza frammentare l'indice. Lo `.zip` è un duplicato dello stesso
download ed è ignorato.

## Riepilogo Esecutivo

La sessione fa due cose distinte. Il **documento 04** è l'unico a carattere bibliografico: elenca
varianti Lanchester attribuite a tre ere storiche (Bracken generalizzato per la WWII, modelli
eterogenei/vettoriali e a soglia per la Guerra Fredda, SINDy e "supporto informativo spaziale" per
i conflitti attuali). Tutti gli **altri otto documenti sono esercizi numerici costruiti
dall'assistente**, con coefficienti dichiarati esplicitamente come ipotizzati («Valori di efficacia
giornaliera ipotizzati»), su scenari proposti dall'utente: combined arms terrestre con CAS, SEAD
preliminare, duello aereo stealth-vs-massa, SAM come terza componente, interdizione profonda contro
infrastruttura industriale.

Il valore della fonte **non sta nella matematica** — che è, in ogni singolo esercizio, un passo di
Eulero esplicito con `Δt = 1 giorno` su coefficienti inventati — ma nella **mappa nominale delle
varianti Lanchester** (04) e nella **struttura degli scenari** (02/03/05/06/08), che è riusabile
come batteria di casi di test per il motore di sessioni virtuali indipendentemente dal risolutore
scelto.

## Contenuto per documento

| # | File | Natura | Contenuto tecnico |
|---|---|---|---|
| 01 | `…missioni CAS(1).docx` | duplicato | Tabella comparativa finale di (06), numeri identici |
| 02 | `…missioni CAS.docx` | esercizio | Scenario combined arms A(100 tank+200 mecc+24 CAS) vs B(150 mecc+40 art+30 AAA/VSHORAD); 5 coefficienti α/β ipotizzati; soglie di ritirata 30%/50% |
| 03 | `Analizziamo uno scenario di scontro aereo…` | esercizio | 12 stealth vs 36 gen-4.5; α=0.8 / β=0.1 asimmetrici per stealth; soglie 25%/50% |
| 04 | `Puoi indicarmi dei modelli Lanchester…` | rassegna | Bracken generalizzato $p,q$; legge 1.5; KDB/Dupuy; eterogeneo vettoriale; Peterson logaritmico; Helmbold a soglia; SINDy; fattore informativo $\mu$ |
| 05 | `missione di interdizione.docx` | esercizio | Raid su complesso petrolchimico = vettore di 100 PVS in 3 sotto-componenti con durezza diversa; difesa a 3 strati MR-SAM/SHORAD/AAA ingaggiati in sequenza geometrica; 24 strike + 8 SEAD |
| 06 | `si introduci una missione SEAD preliminare.docx` | esercizio | Stesso scenario di (02) con Fase Zero SEAD (4 velivoli sottratti al CAS, α=0.4) |
| 07 | `simulare un micro-calcolo numerico.docx` | esercizio | Forma eterogenea minima: $dC_R/dt = -(\alpha_{C\to C} C_B + \alpha_{D\to C} D_B)$, 50 carri + 200 droni FPV vs 120 carri |
| 08 | `terza componente: sistemi SAM.docx` | esercizio | (03) + 4 batterie SAM a lungo raggio; Alfa divide 12 caccia in 8 A2A + 4 SEAD |
| 09 | `tutti e due.docx` | rassegna | Forma matriciale $d\vec{R}/dt = -\mathbf{M}_{G\to R}\vec{G}$; SINDy come "switched system" applicato al conflitto russo-ucraino |

## Contributi Principali

1. **Mappa nominale delle varianti Lanchester** (doc 04, 09) — l'unico contributo che colma una
   lacuna dichiarata del wiki (`overview.md` § Lacune: «Fonti sui modelli Lanchester (classici e
   moderni)»). Distillata in [[lanchester-models]]. Va trattata come **elenco di nomi da
   verificare**, non come bibliografia: v. § Lacune.
2. **Forma eterogenea/vettoriale esplicita** (doc 07, 09) — la matrice di letalità incrociata
   $\mathbf{M}$ scritta per esteso. È la stessa famiglia già documentata in [[cadem]]/ATCAL, non
   una novità, ma il wiki non ne aveva la forma minima scritta.
3. **Cinque strutture di scenario** (doc 02, 03, 05, 06, 08) riusabili come casi di test — v.
   [[lanchester-vs-motore-des]] § Scenari.
4. **Regole di disingaggio a soglia** ("la Fazione A interrompe l'attacco se perde il 30% dei
   carri") usate in ogni esercizio e attribuite in (04) al modello di Helmbold. È l'unico elemento
   *strutturale* dei documenti che il progetto oggi non ha in nessuna forma.

## Concetti Chiave Trattati

- [[lanchester-models]] — legge lineare, legge quadratica, forma generalizzata di Bracken, legge
  1.5, eterogeneo vettoriale, soglie di Helmbold, SINDy, fattore di superiorità informativa
- [[cadem]] — non citato per nome dai documenti, ma la forma eterogenea di (07)/(09) **è** la
  famiglia CADEM/ATCAL già in wiki
- [[killer-victim-scoreboard]] — assente dai documenti; è esattamente ciò che manca per dare
  provenienza ai coefficienti $\alpha$ inventati

## Entità Menzionate

Tutte **prive di riferimento verificabile** nei documenti (v. § Lacune):

- Jerome **Bracken** — autore del modello generalizzato e della calibrazione Ardenne/Kursk
- **Dupuy Institute** / **KDB** (Kursk Database) — validazione sulle sole *contact forces*
- **Helmbold** — Lanchester con rapporto di forze, postura e soglie di ritirata
- **Peterson** — modello logaritmico per l'attrito non da combattimento
- **SINDy** (Sparse Identification of Nonlinear Dynamics) — identificazione dell'equazione dai dati
- [[tacwar]], [[janus-model]] — citati come simulatori Guerra Fredda (coerente con le pagine wiki
  esistenti)
- **JAAM**, **STORM** — citati come «spina dorsale dei simulatori del Pentagono». Attribuzione
  **non verificata e sospetta**: STORM è un modello di campagna stocastico/event-based, non un
  risolutore Lanchester matriciale.

## Citazioni Rilevanti

> «Valori di efficacia giornaliera ipotizzati: $\alpha_{CAS \to Ar} = 0.25$ …» (doc 02)

È la frase più importante dell'intero set: **ogni numero prodotto nei nove file discende da qui**.

> «L'analista Jerome Bracken ha dimostrato che la Campagna delle Ardenne (1944) e la Battaglia di
> Kursk (1943) non seguono la legge del quadrato. I dati reali si posizionano perfettamente
> impostando gli esponenti $p = 0.5$ e $q = 0.5$» (doc 04)

> «La matematica di Lanchester valida la dottrina della guerra moderna» (doc 01)

Conclusione dottrinale **non sostenuta** dai calcoli che la precedono: v. § Lacune.

## Lacune e Contraddizioni

**A. Citazioni non verificabili.** Le 14 note del doc 04 sono **nomi di dominio nudi**
(`https://www.mdpi.com`, `https://www.researchgate.net`, `https://en.wikipedia.org`,
`https://github.com`): nessun titolo, autore, anno, DOI o numero di pagina. Non è una bibliografia,
è un elenco di siti. Nessuna affermazione del doc 04 è quindi citabile come tale nel wiki.

**B. Contraddizione interna al doc 04.** Dichiara per la Battaglia d'Inghilterra «un esponente di
1.5» e due righe dopo scrive $\Delta B \sim G^{1.2}$.

**C. Contraddizione fra documenti.** Il doc 03 apre con «dobbiamo abbandonare i vecchi modelli
della Battaglia d'Inghilterra (Legge 1.5)»; il doc 04 la elenca fra i modelli «considerati validi».

**D. La matematica dichiarata non è la matematica usata.** Il doc 02 attribuisce all'artiglieria la
**legge lineare** e al CAS la **legge quadratica**, ma poi calcola *ogni* interazione come
`perdite = N_tiratori × α` — cioè la forma a fuoco mirato, per tutti. La distinzione
lineare/quadratica, che è il punto dottrinale dell'intera conclusione, **non compare in nessuna
equazione effettivamente valutata**.

**E. Nessuna equazione differenziale viene mai integrata.** Le ODE sono scritte e poi risolte con
un unico passo di Eulero esplicito a `Δt = 1 giorno`, valutato sui valori a $t=0$. Ne segue che
l'attrito subito da una forza **non dipende dalla sua numerosità** e non è limitato da essa: nel
doc 06 le perdite CAS valgono $28{,}4 \times 0{,}30 = 8{,}5$ velivoli su **20 presenti** — con 8
velivoli inviati il modello ne avrebbe abbattuti 8,5, cioè più di quanti ne esistessero. Il
problema non è la legge quadratica (che come ODE è corretta), è il passo di integrazione.

**F. Il confronto "con SEAD vs senza SEAD" è un artefatto dell'ordine di risoluzione.** Nel doc 02
(senza SEAD) l'artiglieria di B spara a **40** pezzi e i carri di A ingaggiano a **100**, cioè
tutti sui valori a $t=0$ (risoluzione *simultanea*). Nel doc 06 (con SEAD) l'artiglieria spara a
**35** — già decurtata dal CAS **dello stesso giorno** — e i carri ingaggiano a **94,8**
(risoluzione *sequenziale*). Il titolo di merito attribuito al SEAD («+1 carro preservato») nasce
**dal cambio di sequenza fra le due simulazioni, non dal SEAD**. È una dimostrazione involontaria
del vincolo #2 di [[virtual-session-engine-des]]: *l'ordine di risoluzione degli eventi fa parte
del contratto di riproducibilità*.

**G. Conclusioni narrative senza corrispettivo numerico.** Il doc 05 afferma che senza SEAD i
MR-SAM «avrebbero abbattuto circa 4-5 caccia»; con i suoi stessi coefficienti il conto è
$6 \times 0{,}15 = 0{,}9$. Il numero 4-5 non deriva da nessuna equazione del documento.

**H. Determinismo senza varianza.** Nessun esercizio ha estrazioni casuali, ripetizioni o bande di
incertezza: ogni scenario è una singola realizzazione puntuale. Nel doc 03 il verdetto strategico
(Alfa si ritira) si gioca su 8,4 velivoli contro una soglia intera di 9.

**I. Perdite frazionarie.** «8,5 velivoli», «23,7 caccia-bombardieri», «2,4 batterie», «1,6 sistemi
AD»: l'output è per costruzione non intero e aggregato — incompatibile con il vincolo #3 di
[[virtual-session-engine-des]] (perdite e danni **per singolo asset**).

**J. Nessuna contraddizione con [[virtual-session-engine-des]].** Sembra esserci sul dato
Ardenne/Kursk — la decisione registra «9 test falliti», il doc 04 parla di «validazione». In realtà
le due letture **concordano**: entrambe dicono che su quelle battaglie le leggi classiche (lineare
e quadratica) *non tengono*. La differenza è solo interpretativa: il doc 04 chiama "validazione" il
**fit a posteriori** di una forma a due parametri libere ($p,q \approx 0{,}5$) su una singola
battaglia, che non è una validazione predittiva. L'avvertimento metodologico permanente della
decisione resta quindi **integralmente in piedi**, e questa fonte non porta alcuna evidenza per
scalfirlo.

## Applicabilità al Warfare-Model

Valutazione completa, con le raccomandazioni operative, in
**[[lanchester-vs-motore-des]]**. In sintesi:

- **Nessun coefficiente di questa fonte è utilizzabile**: sono tutti dichiaratamente ipotizzati, ed
  è esattamente il caso vietato dall'avvertimento metodologico di [[virtual-session-engine-des]]
  («i coefficienti vanno stimati con un ATCAL interno, non inventati a tavolino»).
- **Nessun contenuto tocca lo strato 1** (scheduler dei contatti): nei nove documenti non compare
  una sola coordinata, velocità, rotta, distanza, portata di rilevamento o tempo di contatto. Il
  contatto è **assunto** a $t=0$.
- **Tre cose sono riusabili**: le cinque strutture di scenario come casi di test; le **soglie di
  disingaggio**, che il progetto non ha; la **forma eterogenea** come bersaglio di fit per un
  eventuale ATCAL interno, al posto della tabella di coefficienti a mano di
  `Tactical_Evaluation.calcFightResult`.
