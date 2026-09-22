---
title: "I 9 documenti Lanchester valgono un cambio di rotta del motore DES?"
type: analysis
tags: [lanchester, attrition, combat-resolution, discrete-event, dwm, architecture]
created: 2026-09-22
updated: 2026-09-22
query: "I documenti Lanchester in RAW/Lanchester/ aggiungono qualcosa che supera lo scetticismo già documentato dal progetto, e cosa cambia nello sviluppo del sistema di esecuzione delle sessioni virtuali?"
sources: ["[[source-lanchester-scenari-ai]]", "[[lanchester-models]]"]
related: ["[[virtual-session-engine-des]]", "[[cadem]]", "[[soglie-disingaggio-e-attrito-aggregato]]", "[[logic-decision]]"]
---

# I 9 documenti Lanchester valgono un cambio di rotta del motore DES?

## Domanda

I nove `.docx` in `RAW/Lanchester/` contengono qualcosa che superi lo scetticismo metodologico già
registrato in [[virtual-session-engine-des]] sui modelli Lanchester, e in particolare: cambiano
qualcosa nello sviluppo del motore di esecuzione delle sessioni virtuali?

## Risposta Sintetica

**No sulla matematica, sì — in misura limitata e ben circoscritta — su tre punti.** I documenti non
portano una sola evidenza nuova a favore dei modelli Lanchester: sono esercizi numerici con
coefficienti dichiaratamente inventati, cioè precisamente il caso che l'avvertimento metodologico
del progetto vieta. Restano utilizzabili: **(1)** cinque strutture di scenario come batteria di casi
di test; **(2)** la **regola di disingaggio a soglia**, che il progetto oggi non ha in nessuna forma
e di cui un motore a eventi ha comunque bisogno; **(3)** la **forma eterogenea vettoriale** come
bersaglio di fit per l'ATCAL interno, al posto della tabella di coefficienti a mano oggi in
`calcFightResult`. Sullo **strato 1** (scheduler dei contatti) l'impatto è **rigorosamente zero**,
verificato riga per riga.

---

## 1. Che modelli Lanchester contengono, e con che provenienza

| Variante | Dove | Etichettata come |
|---|---|---|
| Legge lineare / legge quadratica | doc 02 (a parole) | assunzioni dottrinali dello scenario |
| Forma generalizzata di Bracken $\dot R = -gR^qG^p$ | doc 04 | «validata» su Ardenne/Kursk, $p=q\approx0{,}5$ |
| Legge a potenza frazionaria 1.5 | doc 04 (valida) / doc 03 (superata) | contraddittoria fra i due |
| Eterogeneo vettoriale $d\vec R/dt = -\mathbf{M}\vec G$ | doc 07, 09, e *di fatto* tutti gli esercizi | parametri **ipotizzati** |
| Soglie di ritirata (Helmbold) | doc 02, 03, 05, 06, 08 | parametri di scenario, scelti a mano |
| Logaritmico non-da-combattimento (Peterson) | doc 04 | solo citato |
| Fattore di superiorità informativa $\mu$ | doc 04 | solo citato |
| SINDy (identificazione dai dati) | doc 04, 09 | metodo, non modello |
| **Equazioni a salva (Hughes)** | **assenti** | — |

**Calibrati o di esempio?** Di esempio, e il set lo dichiara: «Valori di efficacia giornaliera
**ipotizzati**» (doc 02). Gli unici numeri agganciati alla storia sono i **due esponenti** $p,q
\approx 0{,}5$ di Bracken e l'esponente 1.5/1.2 della Battaglia d'Inghilterra: sono *forme*, non
tassi di attrito, e arrivano con citazioni non verificabili (nomi di dominio nudi — v.
[[source-lanchester-scenari-ai]] § Lacune A). **Zero coefficienti $\alpha$ riusabili.**

Va anche detto che *nessuna* ODE viene mai integrata: ogni esercizio è **un singolo passo di Eulero
esplicito con $\Delta t = 1$ giorno** valutato sui valori iniziali. Non è "un modello Lanchester
applicato": è la forma quadratica valutata una volta sola con un passo di 86 400 s.

## 2. C'è qualcosa di genuinamente nuovo?

### (a) Coefficienti di calibrazione storica → **no**

Nessuno. L'unico contributo in questa direzione è **indiretto ma non banale**: se e quando il
progetto farà girare l'ATCAL interno, dovrà scegliere *quale forma funzionale* fittare. I documenti
ricordano che le candidate sensate sono due — la matriciale eterogenea (già in wiki come [[cadem]])
e la generalizzata di Bracken con esponenti liberi — e che **entrambe sono più espressive della
tabella `k_ratio` oggi cablata in `calcFightResult`**. Questo è un suggerimento sulla forma, non
sui numeri, e come tale è legittimo.

Attenzione a un falso allarme: il doc 04 presenta il fit Ardenne/Kursk come «validazione», il
progetto registra «9 test falliti» sulle stesse battaglie. **Non è una contraddizione**: entrambi
dicono che le leggi classiche non tengono là. La discrepanza è che il doc chiama validazione un fit
a posteriori con due parametri liberi su una singola battaglia. L'avvertimento metodologico di
[[virtual-session-engine-des]] resta quindi intatto e **non va modificato**.

### (b) Tecniche a salva → **nessuna sovrapposizione, sono famiglie diverse**

Verificato: la parola "salva" compare una volta sola, retoricamente («la prima micidiale salva
invisibile BVR», doc 03), e **non esiste una sola equazione a salva in tutto il set**. Le salvo
equations di Hughes sono un modello a **impulsi discreti** con potenza offensiva, potenza difensiva
e capacità di assorbimento del bersaglio; i nove documenti sono interamente nella famiglia delle
ODE continue. L'`Engagement_Resolver` della Fase 4 **non trova qui nulla da riusare**, né in
positivo né in negativo. La lacuna resta aperta e va colmata con una fonte su Hughes.

### (c) Strutture di scenario → **sì, è il contributo reale**

Cinque scenari, riusabili come casi di test indipendentemente dal risolutore. Sono utili perché
ciascuno stressa un meccanismo che il motore ha appena costruito o deve ancora costruire:

| # | Scenario | Cosa mette sotto stress nel motore |
|---|---|---|
| S1 | Combined arms terrestre: A (100 tank + 200 mecc + 24 CAS) vs B (150 mecc + 40 art + 30 AAA/VSHORAD) | Targeting cross-dominio; `Military.air_defense_power()` (Q3); il ramo SEAD di `calculate_priority` |
| S2 | SEAD preliminare che **sottrae** 4 velivoli al CAS | Il trade-off di allocazione in `Air_Resources_Assigner`: degradare la difesa nemica costa volume di fuoco oggi e lo rende in Giorno 2 |
| S3 | Aereo asimmetrico: 12 stealth vs 36 gen-4.5, rilevamento fortemente sbilanciato | Fase 2: `Mobile.detection_range(mode, sensor, range_type)` e le latenze di reazione — chi spara per primo |
| S4 | SAM a lungo raggio come terza componente che obbliga a distrarre 1/3 della flotta | Bersagli statici ad alta minaccia e basso combat power: esattamente il caso di Q3 |
| S5 | Interdizione profonda: difesa a 3 strati MR-SAM → SHORAD → AAA, bersaglio = 100 PVS in 3 sotto-componenti con durezza diversa | `Block`/`Component` come bersaglio composito; munizioni adeguate al bersaglio (`air-priority-target-specific-loadout`); esito "serve un secondo raid dedicato" |

Due osservazioni che valgono più degli scenari stessi:

- **S3 e S5 sono argomenti *a favore* dell'architettura DES, non contro.** In S3 l'asimmetria
  stealth va imposta a mano con due coefficienti ($\alpha=0{,}8$ contro $\beta=0{,}1$) scelti
  dall'autore; nel DES la stessa asimmetria **emerge** dal confronto fra portate di rilevamento e
  latenze di reazione, che sono dati fisici già in casa dalla Fase 2. In S5 la sequenza
  MR-SAM → SHORAD → AAA è cablata come "fase"; nel DES è una conseguenza della geometria, cioè
  **la produce lo strato 1 gratis**. Dove i documenti devono parametrizzare, il motore deduce.
- **S5 introduce un'idea di bersaglio che il progetto può usare subito**: l'infrastruttura non è un
  `health` scalare ma un vettore di sotto-componenti con durezza e munizione richiesta diverse, il
  cui danno parziale si traduce in un effetto operativo datato ("fuori uso 12-18 mesi") e in un
  residuo che richiede una missione dedicata. È la stessa forma di `Block`/`Component`, ed è un
  buon test di quel modello.

### (d) Un quarto elemento, non previsto dalla domanda: le soglie di disingaggio

Ogni esercizio definisce una regola del tipo «A interrompe l'attacco se perde il 30% dei carri o il
50% del CAS». Non è matematica Lanchester, è una **regola di transizione di stato**, ed è compatibile
con qualsiasi risolutore, DES incluso. Il motore oggi non ce l'ha: `Engagement_Resolver` (Fase 4) ha
bisogno di un criterio di fine ingaggio diverso dall'annientamento, e `SessionOutcome` di un campo
che distingua "distrutto" da "disingaggiato". Proposta concreta in
[[soglie-disingaggio-e-attrito-aggregato]].

## 3. Cosa NON è utilizzabile, e perché

Nell'ordine di gravità, con riferimento al documento specifico:

1. **Tutti i coefficienti $\alpha,\beta,\gamma$** (doc 02, 03, 05, 06, 07, 08) — dichiarati
   «ipotizzati». È testualmente il caso vietato dall'avvertimento di
   [[virtual-session-engine-des]]: *«i coefficienti vanno stimati con un ATCAL interno, non
   inventati a tavolino»*. Non è lo scetticismo generico sulla famiglia: sono numeri senza alcuna
   provenienza, nemmeno cattiva.
2. **Il passo di integrazione** (tutti gli esercizi) — un solo passo di Eulero esplicito a
   $\Delta t = 1$ giorno. Conseguenza misurabile, non teorica: nel doc 06 le perdite CAS sono
   $28{,}4\times0{,}30 = 8{,}5$ **su 20 velivoli presenti**, e l'attrito non dipende dalla
   numerosità della forza che lo subisce. Con 8 velivoli inviati il modello ne avrebbe abbattuti
   8,5. Un risolutore che può restituire sopravvissuti negativi non è un fallback, è un bug.
3. **L'output frazionario e aggregato** (tutti) — «8,5 velivoli», «23,7 caccia-bombardieri», «2,4
   batterie». Incompatibile con il vincolo utente #3 di [[virtual-session-engine-des]] (perdite e
   danni **per singolo asset**, mai aggregati) e con `Asset.apply_damage()`.
4. **Il determinismo senza varianza** (tutti) — nessuna estrazione, nessuna ripetizione, nessuna
   banda. Nel doc 03 il verdetto strategico si gioca su 8,4 velivoli contro una soglia intera di 9.
   Confligge con il vincolo #2 (riproducibilità **da seed**, che presuppone estrazioni) e con
   [[stochastic-simulation]].
5. **Il confronto SEAD/non-SEAD del doc 06 è un artefatto dell'ordine di risoluzione** — nel doc 02
   l'artiglieria di B spara a 40 pezzi e i carri di A ingaggiano a 100 (simultaneo, valori a $t=0$);
   nel doc 06 l'artiglieria spara a 35, già decurtata dal CAS dello stesso giorno, e i carri
   ingaggiano a 94,8 (sequenziale). Il «+1 carro preservato grazie al SEAD» **nasce dal cambio di
   sequenza fra le due simulazioni, non dal SEAD**. È una dimostrazione involontaria del vincolo #2
   del progetto: l'ordine di risoluzione degli eventi fa parte del contratto di riproducibilità.
   Le conclusioni dottrinali che ne discendono vanno scartate in blocco.
6. **La matematica dichiarata non è quella usata** (doc 02) — l'artiglieria è annunciata come legge
   lineare e il CAS come legge quadratica, ma ogni interazione è calcolata come
   $N_{\text{tiratori}} \times \alpha$, cioè fuoco mirato per tutti. La distinzione
   lineare/quadratica, che è il perno della conclusione dottrinale, non compare in nessuna equazione
   valutata.
7. **Conclusioni narrative senza base numerica** (doc 05) — «senza SEAD i MR-SAM avrebbero abbattuto
   circa 4-5 caccia»: con i coefficienti del documento stesso il conto è $6\times0{,}15 = 0{,}9$.
8. **Le citazioni del doc 04** — quattordici note che sono nomi di dominio nudi (`mdpi.com`,
   `researchgate.net`, `en.wikipedia.org`, `github.com`). Nessuna affermazione bibliografica del
   set è citabile; i nomi (Bracken, Helmbold, Peterson, KDB) valgono come **piste da verificare**.
9. **L'attribuzione «JAAM e STORM»** (doc 09) come «spina dorsale dei simulatori del Pentagono»
   basati su Lanchester matriciale — non verificata e sospetta: STORM è un modello di campagna
   stocastico/event-based. Le pagine [[jicm-model]], [[tacwar]], [[cem-model]] già in wiki
   descrivono i modelli che *davvero* usano attrito aggregato.
10. **Le due incoerenze interne** — esponente «1.5» poi $G^{1.2}$ (doc 04); la legge 1.5 «valida»
    (doc 04) e «da abbandonare» (doc 03).

---

## Verifica esplicita: strato 1 o strato 2?

**Ipotesi di lavoro da verificare**: un contenuto Lanchester incide sullo strato 2 (risolutore
d'ingaggio, Fase 4), mai sullo strato 1 (scheduler dei contatti, Fase 3, geometrico — CPA/TCPA,
intersezione rotta↔volume).

**Esito: ipotesi confermata, e più nettamente di quanto l'ipotesi stessa affermi.**

Verifica condotta sul testo dei nove documenti: **non compare una sola coordinata, posizione,
velocità, rotta, distanza, portata di rilevamento, quota o tempo di contatto**. La sola grandezza
geometrica nominata è qualitativa («i velivoli CAS devono operare dentro la bolla VSHORAD», doc 02;
«le batterie a medio raggio colpiscono per prime», doc 05) e non entra in nessun calcolo. Il
contatto è **assunto come dato iniziale**: tutte le forze sono in ingaggio a $t=0$, per ipotesi.
L'unica struttura temporale presente è l'indice di giornata e un ordinamento di fasi
(SEAD → CAS → artiglieria → fuoco diretto) che è un **ordine di risoluzione**, non uno *scheduling*:
non dice quando un evento accade, dice in che ordine valutare le formule.

Due conseguenze operative:

1. **Lo strato 1 (Fase 3, in lavorazione) non è toccato**: nessuna riga di questa fonte ha
   giurisdizione sullo scheduler dei contatti. Nessun rischio di collisione con il lavoro in corso.
2. Lo strato 2 è toccato **solo marginalmente e non nel risolutore primario**: la giurisdizione di
   questa fonte arriva al *fallback aggregato* (`calcFightResult`) e alla *regola di fine ingaggio*,
   non al meccanismo di risoluzione colpo-per-colpo.

Un corollario che merita di essere registrato: la sequenza di fasi che i documenti devono cablare a
mano (MR-SAM ingaggia prima di SHORAD, che ingaggia prima dell'AAA) **è esattamente l'output dello
strato 1**. Dove il modello aggregato mette un parametro dottrinale, il DES mette una conseguenza
della geometria. È un argomento a favore dell'architettura già scelta, non contro.

## Fonti Utilizzate

- [[source-lanchester-scenari-ai]] — tutti e 9 i documenti, letti integralmente
- [[lanchester-models]] — tassonomia delle varianti e stato di validazione
- [[virtual-session-engine-des]] — architettura a 4 strati, vincoli utente, avvertimento metodologico
- `Code/Dynamic_War_Manager/Source/Logic/Tactical_Evaluation.py:251` — `calcFightResult`, letto per
  verificarne la forma effettiva (v. sotto)

## Conclusioni e Implicazioni per Warfare-Model

**Cosa NON cambia** (e va detto per primo, perché è la risposta principale):

- L'architettura a 4 strati di [[virtual-session-engine-des]] resta invariata.
- Il risolutore primario resta event-driven per singolo colpo, con Hughes per il
  molti-contro-molti. Nessun elemento di questa fonte lo mette in discussione, e nessuno lo
  informa.
- L'avvertimento metodologico permanente resta invariato — anzi, il set lo **rafforza**: è un
  campione di cosa succede quando si usa questa famiglia con coefficienti a piacere.
- Lo **sviluppo in corso della Fase 3 non è toccato in alcun modo**.

**Cosa può cambiare**, subordinato a conferma dell'utente (dettaglio in
[[soglie-disingaggio-e-attrito-aggregato]]):

1. **Soglie di disingaggio** — `Engagement_Resolver` (Fase 4) e `SessionOutcome` (Fase 0/6): un
   ingaggio deve poter finire per rottura del morale/coesione, non solo per annientamento.
2. **Forma del fallback aggregato** — se `calcFightResult` verrà mai rifatto, il bersaglio è la
   forma eterogenea di [[cadem]] con coefficienti da ATCAL interno, non un'altra tabella a mano.
   Oggi la funzione è **omogenea** (prende due scalari `n_fr`/`n_en` e due efficienze), usa una
   tabella `k_ratio` di quattro righe interpolate, e chiama `random.uniform` dal `random` di modulo
   — cioè **non seedato**, che è già nell'elenco delle precondizioni bloccanti. Nota: la funzione
   eterogenea esiste già accanto, `evaluateCombatSuperiority(action, asset_fr, asset_en)`, che
   ragiona per categoria e combat power — è lì che un'eventuale matrice andrebbe innestata.
3. **Batteria di scenari di test** S1-S5 per la validazione della Fase 7.

**Da non fare**: importare un singolo coefficiente da questa fonte, in qualunque modulo.
