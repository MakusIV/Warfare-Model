# Proposta: un'occasione di rilevamento per ogni passaggio nel volume di rilevamento PROPRIO dell'osservatore (FP)

**Stato: BOZZA (2026-11-06).** Decisioni **FP-1..FP-9 aperte** (§3), da prendere una per volta. Sonda **P-0 da
eseguire** come primo passo della prossima sessione sul ProArt (§1.8), prima di ogni codice.
- **Regola dell'utente (vincolante, 2026-11-06)**: per una coppia di asset nemici il rilevamento di un osservatore si
  valuta **per singolo passaggio del bersaglio nel volume di rilevamento PROPRIO dell'osservatore**, indipendentemente
  dalla finestra dell'altro asset. Se il bersaglio esce e rientra nel volume dell'osservatore sono **due passaggi
  distinti**, ciascuno con la sua permanenza, la sua estrazione di rilevamento e (se differente) la sua finestra
  d'ingaggio; **mai la somma delle permanenze**. L'utente ha scelto di considerare l'alternativa B (un'occasione per
  passaggio): la raccomandazione e' una variante di B; qui si discute il "come".
- **Esecutore**: `des-developer` (Claude Sonnet, sforzo alto: zona delicata RNG/interruttori). Alternativa:
  `oc-developer`. L'esecutore segue il piano di §4 cosi' com'e'; se il codice reale non corrisponde (righe, firme,
  esiti), si ferma e riferisce.
- **Nessun file di codice o di test modificato da questo documento.** Scritti: questo file, gli script di sola
  lettura in `Analysis/Document/Rapporti/Sonde_Finestre_Passaggio/` (P-0, P-1, LEGGIMI) e una nota di 5 righe in
  `Proposta_Dwell_Time_Rilevamento.md` §5.2.

**Convenzioni**: **[V]** = verificato leggendo il codice (`file:riga`, righe del checkout del 2026-11-06, HEAD
`8943b292` piu' il blocco B della D-5 non ancora committato) o eseguendolo; **[I]** = ipotesi o conoscenza generale,
non verificata nel repository; **[S]** = stima o scelta di progetto, mai dato tarato. Percorsi di codice relativi a
`Code/Dynamic_War_Manager/Source/`. Sonde **P-0, P-1**; decisioni **FP-1, FP-2, ...**.

---

## 0. Sintesi

Oggi il DES fa **una sola estrazione di rilevamento per finestra di contatto e direzione**, con la distanza minima
dell'intera finestra. La finestra e' l'intervallo in cui la distanza e' entro la portata **maggiore** delle due
parti. Per l'osservatore che ha la portata maggiore la regola e' gia' rispettata (uscita e rientro dal suo volume =
due finestre). Per l'osservatore con la portata **minore** (tipicamente un SAM o un'AAA contro un aereo, che vede i
bersagli a terra fino a 80 km) una finestra puo' contenere **piu' passaggi** nel suo volume, ma riceve **una sola**
occasione; con la D-5 accesa, in piu', la permanenza e' la **somma** dei passaggi. Il limite e' **precedente alla
D-5** e **non e' dichiarato** nel manuale.

| Tema | Raccomandazione | Effetto sulla fotografia (interruttore spento) |
|---|---|---|
| Dove si calcolano i passaggi (FP-1) | nel **risolutore**, dai tratti (`range_intervals` con la portata propria), come la permanenza D-5; `ContactWindow` e scheduler invariati | nessuno |
| Ordine delle estrazioni (FP-2) | primo passaggio dallo stream dell'ingaggio, nella posizione di oggi; dal secondo in poi uno **stream separato** (`pass_event_id`, come la tempra): lo stream dell'ingaggio resta identico anche con la regola accesa | nessuno |
| Finestra d'ingaggio per passaggio (FP-3) | il candidato al tiro di un passaggio vale fino all'**inizio del passaggio successivo**; l'ultimo fino alla fine della finestra (come oggi) | nessuno |
| Distanza per passaggio (FP-4) | **CPA del passaggio** per ogni passaggio | nessuno |
| Istante di rilevamento per R-INT (FP-5) | con la regola accesa il **primo** istante (oggi: l'ultimo in ordine di lista, difetto latente) | nessuno |
| D-5 (FP-6) | con FP spento e D-5 acceso: permanenza = **il passaggio che contiene il CPA** (mai la somma); con FP acceso: permanenza del proprio passaggio | nessuno (D-5 spenta) |
| Interruttore (FP-7) | `Engagement_Resolver.FP_PER_PASS_DETECTION = False`; `Session_Simulator` passa `pass_rng` solo se acceso | **1009 identiche** |
| Scenario (FP-8) | S33-PASSES: A-10C che entrano due volte nel volume della ZSU restando nella stessa finestra, 4 varianti x 5 semi = **20 nuove** | +20 |
| Pianificatore (FP-9) | nessun cambio (gia' per attraversamento); limite dichiarato sulla metrica `max_detection_probability` | nessuno |

**Dimensione stimata** [S]: blocco 1 ~150 righe di codice + ~330 di test (17 test); blocco 2 ~190 righe di test
(7 test) + 6 righe nella tabella della fotografia. Suite attesa: `Ran 4812` dopo il blocco 1, `Ran 4819` dopo il
blocco 2 (base `Ran 4795`).

---

## 1. Problema e comportamento attuale

### 1.1 La finestra di contatto usa la portata maggiore [V]

- `Logic/Contact_Scheduler.py` `contact_windows` (`:1023-1100`): `outer = max(portate)` (`:1067`), `inner = min` (`:1068`);
  **una finestra per ogni intervallo** di `range_intervals(legs_a, legs_b, outer)` (`:1070`, ciclo `:1083-1098`).
  Gli intervalli entro la portata minore (`mutual_intervals`, `:1075`) sono calcolati ma nella finestra entra solo
  il **primo** contenuto (`_first_contained`, `:1086`, `:1117-1126`) come `t_mutual_start/t_mutual_end`.
- `ContactWindow` (`:196-240`): `t_start/t_end`, `t_cpa/distance_cpa` (massimo avvicinamento dell'**intera**
  finestra), `range_a/range_b`, `t_mutual_*`, `first_detector`. **Non porta il sensore** ne' gli intervalli
  successivi al primo nella portata minore.
- Le finestre sono spezzate agli istanti di decollo/atterraggio (`_pair_windows`, `:1492-1524`), ritagliate dal G4a
  (`trim_contact_window`, `:1129-1172`, chiamata da `Session_Simulator._trim_busy`, `Logic/Session_Simulator.py:1296-1329`,
  e da `reschedule`, `:2853`), ordinate per `(t_start, id_a, id_b)` (`:1487`).

### 1.2 Una estrazione per finestra e direzione [V]

- `Logic/Engagement_Resolver.py` `_detect` (`:2064-2083`): finestre in ordine `(t_start, id_a, id_b, t_end)`, per
  ognuna `_detect_direction` a->b poi b->a.
- `_detect_direction` (`:2085-2142`): esce **senza estrarre** solo se l'osservatore non ha portata (`:2087-2088`) o e'
  un aereo a terra (`:2090-2093`); altrimenti **una** estrazione (`self._draw()`, `:2112`) anche quando il bersaglio non
  entra mai nella portata propria (Pd 0, `:2114`); `distance = window.distance_cpa` (`:2113`): la distanza minima
  **dell'intera finestra**, anche se cade in un passaggio diverso da quello del rilevamento.
- Istante (`_detection_time`, `:2192-2218`): con i tratti, il primo istante in cui la distanza scende sotto il raggio
  estratto, nel **primo** intervallo che tocca la finestra.
- Candidato al tiro (`:2132-2137`): `t_ready = istante + profilo.total`, ammesso se `t_ready <= window.t_end`, con
  `_Candidate.t_end = window.t_end`: un rilevamento nel primo passaggio fa sparare anche nel secondo (traccia
  mantenuta fra i passaggi), finche' l'arma e' a portata (`_range_entry`, `:2984-3017`).
- Contratto RNG scritto nel modulo (**`:412-417`**, non `:385-390` come nel compito: le righe sono slittate): prima
  tutte le estrazioni di rilevamento nell'ordine canonico, a->b poi b->a, una per direzione; poi una per colpo non
  intercettato. La tempra usa lo stream separato `breakpoint_rng` (`Session_Simulator.py:2783-2785`).

### 1.3 Dove la regola e' gia' rispettata e dove no [V]

| Caso | Oggi | Regola |
|---|---|---|
| osservatore con la portata **maggiore** (o uguale, o unica) | una finestra per ogni ingresso nel suo volume: un'estrazione per passaggio | rispettata |
| osservatore con la portata **minore**, un solo passaggio nella finestra | un'estrazione, distanza della finestra = distanza del passaggio (il minimo cade nell'unico passaggio) | rispettata |
| osservatore con la portata **minore**, **>= 2 passaggi** nella stessa finestra | **una** estrazione, con la distanza minima fra tutti i passaggi; candidato valido fino alla fine della finestra | **violata** |
| come sopra con la D-5 accesa | permanenza = **somma** dei passaggi (`_exposure_time`, `:2220-2250`, somma a `:2238-2240`) | **violata** |
| pianificatore (blocco B della D-5, working tree) | `Path.compute_detection_metrics` raggruppa per minaccia i tratti **contigui** (`CROSSING_JOIN_TOLERANCE_S`): tratti non contigui = attraversamenti distinti | rispettata |

### 1.4 Esempio numerico [V sui registri, calcolo]

ZSU-57-2 in (1000, -300): portata visiva contro bersagli aerei **6000 m**; A-10C a 3000 m: portata contro bersagli a
terra **80 000 m** (`mutual_detection_ranges(zsu, a10) = (6000.0, 80000.0)`, verificato eseguendo lo scheduler sui
registri il 2026-11-06). Un A-10C che sorvola la linea, si allontana a 14 km e ritorna resta sempre entro 80 km:
**una** finestra. Entra due volte nei 6 km della ZSU (per esempio [200, 254] s e [380, 434] s, numeri illustrativi
[S]). Oggi la ZSU ha **un'occasione** sola, con la distanza minima dei due passaggi; se la manca, non spara in
nessuno dei due. Con distanze minime 5,5 km nel primo e 3,3 km nel secondo:
- oggi: Pd = 1 - 0,5 * (3,3/6)^4 = **0,954**, una volta (il primo passaggio "eredita" la distanza del secondo);
- per passaggio: 1 - 0,5 * (5,5/6)^4 = **0,647** e **0,954**; probabilita' di almeno un rilevamento
  1 - 0,353 * 0,046 = **0,984**.

### 1.5 Relazione con la D-5 [V]

- Il limite e' **precedente** alla D-5: c'e' dalla nascita del risolutore (una estrazione per finestra e direzione)
  e non dipende dalla permanenza.
- La D-5 (blocco A, `8943b292`, interruttore `D5_DWELL_TIME` spento, `:519-525`) lo **aggrava** nel solo caso
  multi-passaggio: `_exposure_time` somma i passaggi (`:2238-2240`). Con un passaggio solo e' corretta.
- Il blocco B della D-5 (`Logic/Air_Route_Manager.py`, nel working tree, non committato) e' gia' per attraversamento.

### 1.6 Altri chiamanti [V]

- `contact_windows`/`schedule_contacts`/`trim_contact_window`/`ContactWindow` sono usati **solo** da
  `Logic/Session_Simulator.py` (`:1314`, `:2390`, `:2841`, `:2853`) e dai test; nessun altro modulo del core li
  importa (`Mission_Adapter` usa solo `Leg`, `route_legs`, `clamp_legs`, `GroundedSchedule`, `TIME_EPS`;
  `Session_Validator` solo `TIME_EPS`).
- `Logic/Weapon_Delivery.py` **non** usa ne' finestre ne' estrazioni: `_evaluate_exposure` (`:433`) e' una stima
  deterministica di pianificazione. Non tocca.
- `Logic/Air_Route_Manager.py` usa solo `detection_probability`/`dwell_factor` del risolutore (metriche). Non tocca
  (FP-9).
- `first_detector` e `is_mutual` **non** sono letti fuori dallo scheduler; `t_mutual_*` solo dai ripieghi senza tratti
  del risolutore (`:2212-2218`, `:2244-2250`).
- `EngagementResult.detections` e' letto da `_detection_time_of` (`:3187-3193`, regola R-INT) e dai test
  (`Test_Session_Scenarios.py:1249`, `:1375-1380`, `Test_Session_Scenarios_S32.py:122`); **non** e' nella fotografia
  (`Test/Scenario_Baseline.py`, nessun riferimento ai `Detection`).
- Adapter DCS: nessun riferimento. Il core resta indifferente al simulatore.

### 1.7 Il manuale non dichiara il limite [V]

Ricerca in `Analysis/Document/Manuale_Motore_DES/` il 2026-11-06: nessun passo dichiara "una sola estrazione per
finestra anche con piu' passaggi nel volume minore". Il capitolo 3 §3.5 (`04_Strato1_Scheduler_Contatti.md:195-201`)
dice che `[t_mutual_start, t_mutual_end]` e' l'intervallo "da quel momento entrambi si vedono", senza dire che e'
solo il **primo**; il capitolo 4 §4.2 (`05_Strato2_Risolutore_Ingaggio.md:144-147`) descrive "una sola estrazione"
per finestra come pregio; l'atlante (`11a_Atlante_Risolutore.md:1310`) dice "una per finestra e direzione". Il limite
va aggiunto al capitolo 9 (file `10_Limiti_Estensioni_Divergenze.md`) comunque vada la decisione.

### 1.8 Sonda P-0 (da eseguire, sola lettura) — PRIMO PASSO della prossima sessione

Script versionato: `Analysis/Document/Rapporti/Sonde_Finestre_Passaggio/probe_passes.py` (istruzioni in `LEGGIMI.md`
della stessa cartella). Avvolge `_detect_direction` e `run` del risolutore **senza cambiarne il comportamento** (chiama
l'originale, poi misura dai tratti senza consumare l'RNG), aggiunge al riassunto di ogni esecuzione una voce
`probe_passes` e riesegue `Scenario_Baseline --compare` con `--ignore probe_passes`. Misura, per esecuzione:
direzioni con >= 2 passaggi (`multi`), estrazioni in piu' (`extra_draws`), istogramma dei passaggi, coppie di
modelli, CPA fuori dal primo passaggio, rilevamenti di oggi che col solo primo passaggio sparirebbero, salve che
dipendono dalla fine del candidato (FP-3), salve dopo il passaggio con un solo passaggio (FP-3 (a)), coppie R-INT con
"ultimo" diverso da "primo" (FP-5).

Comando (root del repo, `<python>` = interprete dell'ESITO di `verifica.sh`; mai in parallelo con suite o confronto):

    mkdir -p .ai-run/sonde_passaggi/p0
    PYTHONPATH=. <python> Analysis/Document/Rapporti/Sonde_Finestre_Passaggio/probe_passes.py .ai-run/sonde_passaggi/p0 \
        > .ai-run/sonde_passaggi/p0/log.txt 2>&1

Tempo atteso [S]: ~11-13 minuti sul ProArt (confronto ~10 minuti piu' la misura), ~20-22 su osboxes (ultimo
confronto 1175 s, `.ai-run/confronto.log`). Esito atteso del confronto: `compared 1029 runs: 20 difference lines`,
tutte `NEW S32-DWELL/...`, **0 righe DIFF** (`PROBE_RC 1` e' atteso per le righe NEW). Il numero di esecuzioni
`RUNS_WITH_MULTI` e' il **massimo** delle esecuzioni che possono cambiare con la regola accesa; con lo stream separato
(FP-2) ne cambia un sottoinsieme, misurato dopo il blocco 1 dalla sonda P-1 (`probe_switch_on.py`).

**Esito**: _da riportare qui (righe `RUNS`, `RUNS_WITH_MULTI`, `TOTALS`, `HIST`, `UNITS`, `MODELS` e l'elenco
`MULTI`) prima delle decisioni._ Attesa qualitativa [I]: direzioni multi probabili dove un aereo torna su un sito
(rientro a ritroso S26, orbite S23-CAP, doppio ingaggio S27, S5); `multi_outer` deve essere 0.

### 1.9 Precisazioni sul compito [V]

- Righe del contratto RNG: `Engagement_Resolver.py:412-417` (non `:385-390`).
- Un'estrazione avviene anche se il bersaglio non entra mai nella portata propria (Pd 0): con zero passaggi la
  regola nuova non cambia nulla (resta un'estrazione).
- **Difetto latente R-INT, precedente**: `_detection_time_of` (`:3187-3193`) costruisce un dizionario
  `{(osservatore, bersaglio): istante}` in cui vince l'**ultimo** rilevamento in ordine di lista, non il primo. Con
  piu' finestre della stessa coppia succede gia' oggi; con un'estrazione per passaggio diventerebbe frequente e
  peggiorerebbe la regola R-INT (un lancio "visto" nel primo passaggio risulterebbe "non visto" per il rilevamento
  del secondo). Trattato in FP-5.
- `_pair_windows` divide gia' oggi un passaggio fisico a cavallo di un decollo/atterraggio in due finestre (due
  estrazioni): limite precedente, con stato a terra diverso nelle due parti; non cambia (§5).

---

## 2. Alternative e raccomandazione

### 2.1 (A) Minimo: un solo passaggio nella permanenza, una estrazione come oggi

`_exposure_time` usa il passaggio che contiene `t_cpa` (in subordine il piu' lungo) invece della somma; nessuna
estrazione nuova.
- Pro: nessun cambio di RNG; corregge la sola violazione introdotta dalla D-5; due righe.
- Contro: lascia la violazione principale (una sola occasione per finestra, distanza "ereditata" dal passaggio
  migliore, candidato valido attraverso i passaggi). Non e' la regola dell'utente.
- Uso raccomandato: **come comportamento della D-5 quando FP e' spento** (FP-6), dentro la B.

### 2.2 (B) Un'occasione per passaggio: dove calcolare i passaggi (FP-1)

| Opzione | Dove | Pro | Contro |
|---|---|---|---|
| B-S1 | **scheduler, finestre per direzione/sensore**: per la direzione con portata minore una `ContactWindow` per ogni intervallo della portata minore | la finestra diventa davvero "per osservatore" | cambia **il numero delle finestre**: episodi G4a (`_episodes`, `Session_Simulator.py:1222-1293`), `_trim_busy`, `covered` del G4b, istanti d'inizio degli episodi, `counter` degli stream, `first_detector` e `t_mutual_*` da ridefinire; ogni finestra di oggi andrebbe sdoppiata per direzione (anche quelle a un passaggio), quindi l'ordine canonico e lo stream cambiano ovunque; tocca `ContactWindow`, `contact_windows`, `trim_contact_window`, `_pair_windows`, `_group_windows` |
| B-S2 | **scheduler, campo nella finestra**: `ContactWindow.mutual_intervals` (tutti gli intervalli della portata minore, non solo il primo); il risolutore lo consuma | la geometria resta nello strato geometrico; lo scheduler li calcola gia' (`:1075`); funziona anche senza tratti se chi costruisce la finestra dichiara il campo | tocca `ContactWindow` (campo nuovo, uguaglianza e `repr` di tutte le finestre), `contact_windows`, `trim_contact_window`; i tratti dello scheduler (`presence_legs`) e del risolutore (`all_legs`) coincidono in sessione [V `Session_Simulator.py:2397-2409`] ma restano due calcoli da tenere allineati; le finestre costruite a mano nei test non hanno il campo |
| **B-R** | **risolutore**: per la direzione, gli intervalli di `range_intervals(tratti_oss, tratti_bers, portata_propria)` che toccano la finestra (stessa regola di `_exposure_time`) | modifica locale al risolutore (come la D-5, DW-4); finestre, episodi, scheduler, `ContactWindow` invariati; costo nullo a interruttore spento; i passaggi rispettano anche i ritagli G4a (si calcolano sulla finestra ricevuta) | un `range_intervals` in piu' per direzione con la regola accesa (trascurabile [I]); **senza tratti** (chiamate dirette dei test) i passaggi non si calcolano: un'estrazione come oggi (limite dichiarato) |

**Raccomandazione: B-R.** E' coerente con la decisione DW-4 della D-5 (permanenza nel risolutore dai tratti), non
tocca la struttura degli episodi e rende la regola un fatto del solo strato 2. In sessione i tratti ci sono sempre
(`all_legs`, `Session_Simulator.py:2397-2409`).

### 2.3 Ordine delle estrazioni nuove (FP-2)

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| O1 in linea | nello stream dell'ingaggio: per finestra, a->b passaggi 1..n, poi b->a | ordine naturale, un solo stream | ogni estrazione successiva slitta: con la regola accesa cambia quasi ogni esecuzione con almeno una direzione multi e almeno una salva, anche se l'occasione in piu' non decide nulla; il confronto con la regola accesa diventa difficile da leggere |
| O2 in coda | primo passaggio nella posizione di oggi; i passaggi dal secondo in poi dopo tutte le estrazioni di rilevamento | i rilevamenti delle altre coppie non cambiano | le estrazioni di danno slittano comunque (stesso effetto di O1 sugli esiti); codice in due giri |
| **O3 stream separato** | primo passaggio dallo stream dell'ingaggio, **nella posizione di oggi**; passaggi 2..n da `pass_rng`, nell'ordine (finestra canonica, a->b poi b->a, passaggio) | lo stream dell'ingaggio resta **identico in ogni stato dell'interruttore** (stesso numero, stesso ordine): cambia un'esecuzione solo se l'occasione in piu', la Pd del primo passaggio o la fine del candidato cambiano una decisione; precedenti nel progetto (tempra: `breakpoint_rng`; fuoco su posizione F7b) | un parametro in piu' (`pass_rng`), un `event_id` nuovo (`pass_event_id`) |

**Raccomandazione: O3.** E' l'unica che soddisfa alla lettera "non cambiare l'ordine delle estrazioni" (AGENTS.md)
anche con la regola accesa, e rende il confronto leggibile: ogni esecuzione cambiata si deve alla regola, non a un
flusso spostato.

### 2.4 Distanza per passaggio (FP-4)

| Opzione | Contenuto | Contro |
|---|---|---|
| **(a) CPA del passaggio** | `closest_point_of_approach` sui tratti ritagliati al passaggio, per ogni passaggio | il primo passaggio puo' avere Pd minore di oggi (se il minimo della finestra cade in un passaggio successivo) |
| (b) distanza della finestra per tutti | come oggi | un passaggio lontano "eredita" la distanza del passaggio migliore: contro la regola |
| (c) finestra per il primo, propria per gli altri | massima continuita' col passato | incoerente: il primo passaggio usa la distanza di un altro |

**Raccomandazione (a).** Con un solo passaggio il CPA del passaggio coincide con quello della finestra, ma il
risolutore usa comunque il percorso di oggi (nessun ricalcolo) per avere esiti identici al bit.

### 2.5 Finestra d'ingaggio per passaggio (FP-3)

| Opzione | Candidato di un passaggio valido fino a | Effetto |
|---|---|---|
| (a) fine del passaggio | `hi` del passaggio, anche con un solo passaggio | la piu' "pura" (il sensore ha perso il bersaglio); cambia anche le direzioni a **un** passaggio dell'osservatore con portata minore quando l'arma tira oltre la portata del sensore o senza `max_range` (contatore `AFTER_PASS` di P-0) |
| **(b) inizio del passaggio successivo** | `lo` del passaggio successivo; l'ultimo fino a `window.t_end` | niente traccia mantenuta fra i passaggi (ogni passaggio ha la sua finestra d'ingaggio); con un solo passaggio identico a oggi; resta il tiro dopo l'uscita dal volume finche' non ricomincia un passaggio (limite di oggi, dichiarato) |
| (c) fine della finestra | `window.t_end` per tutti | ogni passaggio aggiunge solo occasioni: il rilevamento del primo continua a far sparare nel secondo (traccia mantenuta), contro "la sua finestra d'ingaggio" |

**Raccomandazione (b).** Partiziona la finestra in finestre d'ingaggio per passaggio senza cambiare le direzioni a un
passaggio; (a) e' un'estensione separata possibile, da decidere sui numeri di P-0 (`AFTER_PASS`, `salvos_gap`).

### 2.6 Istante di rilevamento per la regola R-INT (FP-5)

| Opzione | Contenuto |
|---|---|
| **(a) il primo istante** con la regola accesa | "l'intercettore aveva gia' rilevato il lanciatore al lancio" = esiste un rilevamento <= `t_launch`; spento: l'ultimo in ordine di lista, come oggi |
| (b) invariato | con la regola accesa un rilevamento del secondo passaggio sostituisce quello del primo: un lancio nel primo passaggio diventa "non visto" (regressione introdotta dalla regola) |
| (c) correzione separata | difetto latente corretto in un'altra Proposta con un suo interruttore |

**Raccomandazione (a)**: corregge il difetto proprio dove la regola lo renderebbe frequente; cambia anche coppie a piu'
finestre (contatore `RINT` di P-0), ma solo con l'interruttore acceso.

### 2.7 Interazione con la D-5 (FP-6)

- Con **FP acceso**, ogni occasione ha la permanenza **del suo passaggio** (`min(end, t_end) - start`, non tagliata
  all'inizio della finestra come in DW-4): la somma sparisce, **la B assorbe la A**.
- Con **FP spento e D-5 acceso** resta un'estrazione per finestra: la permanenza va comunque presa da **un**
  passaggio. Raccomandazione: **il passaggio che contiene `t_cpa`** della finestra (quello la cui distanza entra nella
  Pd), in subordine il piu' lungo. E' la (A) di §2.1, **dentro** l'interruttore della D-5: nessun interruttore nuovo,
  perche' la D-5 e' spenta e nessuna esecuzione della fotografia la accende; le 20 esecuzioni di S32 (un solo
  passaggio della ZSU e del P-18) restano uguali (verifica in §4.1.6).
- Alternativa: lasciare la somma con FP spento (la D-5 violerebbe la regola finche' FP non e' acceso). Non raccomandata.

### 2.8 Interruttore (FP-7)

| Opzione | Contenuto |
|---|---|
| **(a)** `Engagement_Resolver.FP_PER_PASS_DETECTION = False`, letto da `Session_Simulator.engage` che passa `pass_rng` solo se acceso; nel risolutore la regola e' attiva se e solo se `pass_rng` non e' None | stesso schema della D-5 (lettore passato solo se acceso): a interruttore spento la chiamata a `resolve_engagement` e' **letteralmente** quella di prima |
| (b) costante letta dentro `_detect_direction` | agisce anche sulle chiamate dirette; serve comunque uno stream per O3 |
| (c) in `Session_Simulator` come gli F*/G* | il risolutore non lo vede senza importare l'orchestratore |

**Raccomandazione (a), spento.** L'accensione si decide dopo la sonda P-1, non in questo piano; la fotografia **non** si
reinstalla senza decisione esplicita dell'utente.

### 2.9 Scenario (FP-8)

| Opzione | Contenuto |
|---|---|
| **(a) S33-PASSES, 4 varianti x 5 semi = 20** | `off`, `on`, `dwell_off` (D-5 acceso, FP spento, dwell di test 600 s sulla ZSU), `dwell_on` (entrambi accesi) |
| (b) 2 varianti x 5 semi = 10 | solo `off`/`on`: non prova FP-6 in sessione |

**Raccomandazione (a).** Geometria: S32 (ZSU in (1000, -300), 3 BMP-2, 4 A-10C a 3000 m) con rotta di andata, uscita
a 14 km e ritorno sulla linea: due passaggi nei 6 km della ZSU, sempre entro gli 80 km dell'A-10C (una finestra).

### 2.10 Pianificatore (FP-9)

`Path.compute_detection_metrics` (blocco B della D-5) da' la Pd **per attraversamento** e `max_detection_probability`
= massimo sui tratti. Con la regola accesa il DES da' un'occasione per attraversamento, quindi la probabilita' di
essere rilevati almeno una volta su due attraversamenti a 0,4 e' 1 - 0,6^2 = 0,64 contro 0,4 della metrica. Ma
anche oggi due attraversamenti dello stesso volume dell'osservatore con portata maggiore sono due finestre: la
divergenza esiste gia'. **Raccomandazione: nessun cambio**, limite dichiarato; una metrica cumulativa
(`cumulative_detection_probability`) e' un'estensione futura.

### 2.11 Effetti della raccomandazione (B-R, O3, FP-3 (b), FP-4 (a)) sugli altri pezzi [V sul codice letto]

| Pezzo | Effetto |
|---|---|
| `ContactWindow`, `contact_windows`, `_pair_windows`, `trim_contact_window`, `schedule_contacts` | **invariati** |
| `t_mutual_*` | invariati; usati solo dai ripieghi senza tratti |
| ordine canonico delle finestre, stream dell'ingaggio | invariati (numero e ordine delle estrazioni identici in ogni stato) |
| stream nuovo `pass_rng` | ordine: finestra canonica, a->b poi b->a, passaggio 2..n |
| `t_end` del candidato | per passaggio (FP-3 (b)) |
| `distance_cpa` | per passaggio in `Detection` e `_Candidate` (FP-4) |
| `first_detector` | non letto dal risolutore: invariato |
| RWR | una percezione per passaggio rilevato (`rwr_class` accumula `(istante, classe)`, `_air_threat` filtra per istante) |
| percezione/identificazione (`seen_by`, `identified_by`) | minimo degli istanti: un rilevamento del secondo passaggio conta solo se e' il primo |
| R-INT | primo istante con la regola accesa (FP-5) |
| eventi di danno | estrazioni di danno nello stream dell'ingaggio, invariate se le salve sono le stesse; cambiano dove cambiano i lanci |
| episodi G4a/G4b, `busy_until`, `covered`, `counter` | invariati (finestre invariate) |
| `Detection` | 4 campi nuovi a `None` di default (`pass_index`, `pass_count`, `pass_start`, `pass_end`), valorizzati solo nelle direzioni multi con la regola accesa |
| pianificatore, `Weapon_Delivery`, adapter DCS | invariati |

---

## 3. Decisioni aperte per l'utente (una per volta)

**FP-1 — Dove si calcolano i passaggi.** Raccomandazione: **B-R, nel risolutore** dai tratti.
Esempio: un A-10C nella stessa finestra [0, 700] s con la ZSU entra nei suoi 6 km in [200, 254] e [380, 434]. B-S1
farebbe tre finestre (A-10C -> ZSU [0, 700]; ZSU -> A-10C [200, 254] e [380, 434]) e cambierebbe gli episodi; B-R
lascia la finestra [0, 700] e da' alla ZSU due estrazioni dentro la stessa finestra.

**FP-2 — Ordine delle estrazioni.** Raccomandazione: **O3, stream separato** per i passaggi dal secondo in poi.
Esempio: stream dell'ingaggio 0,31 / 0,72 / 0,05 ... Oggi 0,31 va alla ZSU, 0,72 all'A-10C. Con O1 il secondo
passaggio della ZSU prende 0,72, l'A-10C prende 0,05 e tutto il resto slitta. Con O3 la ZSU ha ancora 0,31 nel primo
passaggio, l'A-10C ancora 0,72, e il secondo passaggio prende il primo numero dello stream `pass_event_id`.

**FP-3 — Finestra d'ingaggio per passaggio.** Raccomandazione: **(b)**, fino all'inizio del passaggio successivo.
Esempio: passaggi [200, 254] e [380, 434], fine finestra 700, ZSU che rileva a 205 con reazione 8 s (t_ready 213).
(a) candidato fino a 254; **(b) fino a 380**; (c), cioe' oggi, fino a 700. Con t_ready 390 (reazione lunga) il primo
passaggio non da' candidato in (a) ne' in (b); oggi si', e la ZSU sparerebbe nel secondo passaggio senza averlo
rilevato.

**FP-4 — Distanza per passaggio.** Raccomandazione: **(a), CPA del passaggio.**
Esempio (§1.4): 5,5 km e 3,3 km. (a): Pd 0,647 e 0,954. (b): 0,954 e 0,954 (il passaggio lontano eredita la distanza
del vicino). (c): 0,954 nel primo (distanza del secondo), 0,954 nel secondo.

**FP-5 — Istante di rilevamento per R-INT.** Raccomandazione: **(a), il primo istante con la regola accesa.**
Esempio: un SAM rileva un aereo a 210 s (primo passaggio) e a 390 s (secondo); l'aereo lancia un missile a 300 s.
Oggi (ultimo) vale 390 > 300: lancio "non visto", tempo di reazione pieno (`total`) invece di `refire_interval`, e
l'intercettazione puo' fallire. Con (a) vale 210 <= 300: lancio visto.

**FP-6 — D-5 senza FP.** Raccomandazione: **permanenza del passaggio che contiene `t_cpa`** (mai la somma), senza
interruttore nuovo. Esempio: dwell di test 600 s, passaggi di 54 s e 54 s. Oggi: g = 108/600 = 0,18 su un'estrazione.
FP spento con la raccomandazione: g = 54/600 = 0,09 su un'estrazione. FP acceso: g = 0,09 su ciascuna di due
estrazioni (almeno un rilevamento a distanza nulla: 1 - 0,91^2 = 0,172).

**FP-7 — Interruttore.** Raccomandazione: **`Engagement_Resolver.FP_PER_PASS_DETECTION = False`**, `pass_rng` passato
da `Session_Simulator` solo se acceso. Esempio di lettura: spento, `resolve_engagement` riceve gli stessi argomenti di
oggi (verificato dal test di §4.1.5 punto 15) e la fotografia resta 1009 identiche; acceso (sonda P-1), cambiano al
piu' le esecuzioni elencate `MULTI`/`RINT` dalla sonda P-0.

**FP-8 — Scenario.** Raccomandazione: **S33-PASSES, 4 varianti x 5 semi = 20 esecuzioni nuove** (circa un minuto di
suite in piu' [I], come S31/S32). Esempio: per ogni seme la ZSU ha 4 rilevamenti (uno per A-10C) in `off` e 8 (due
per A-10C) in `on`.

**FP-9 — Pianificatore.** Raccomandazione: **nessun cambio**, limite dichiarato. Esempio: due attraversamenti a Pd 0,4:
metrica 0,4, DES con la regola 0,64.

---

## 4. Piano di intervento (per le raccomandazioni FP-1..FP-9)

Se l'utente sceglie diversamente anche su una sola decisione, questo piano va aggiornato da chi pianifica **prima**
dell'esecuzione.

### 4.0 Precondizioni (l'esecutore le verifica e si ferma se mancano)

1. Il blocco B della D-5 e' committato (`git log` mostra il commit; `git status` pulito su
   `Logic/Air_Route_Manager.py`, `Test/Test_Air_Route_Manager.py`, `Test/Test_Threat_AA_Factory.py`).
2. Base: suite `Ran 4795 tests`, `OK (skipped=7)` [V: `.ai-run/suite.log` del 2026-11-06 su osboxes, working tree con
   il blocco B]; confronto `compared 1029 runs: 20 difference lines` (20 NEW di S32-DWELL) [V:
   `.ai-run/confronto.log`].
3. La sonda P-0 e' stata eseguita (§1.8), i suoi numeri sono in §1.8, le decisioni FP-1..FP-9 sono prese.
4. Copia della cattura di P-0 conservata: `.ai-run/sonde_passaggi/p0/capture.json` (serve alla verifica di S32 in
   §4.1.6).

### 4.1 Blocco 1 — risolutore e orchestratore

#### 4.1.1 `Logic/Engagement_Resolver.py`

1. **Import** (`:463-470`): aggiungere `clamp_legs` e `closest_point_of_approach` all'import da `Contact_Scheduler`
   (ordine alfabetico come oggi).
2. **Interruttore**, subito dopo `D5_DWELL_TIME = False` (`:525`), testo esatto:

```python
# Rilevamento per passaggio nella portata propria (Proposta_Finestre_Per_Passaggio_Portata_Propria.md), interruttore
# dedicato:
#   * `FP_PER_PASS_DETECTION` (SPENTO): un'occasione di rilevamento per OGNI passaggio del bersaglio nel volume PROPRIO
#     dell'osservatore dentro una finestra di contatto (prima: una sola estrazione per finestra e direzione, con la
#     distanza minima dell'intera finestra). Lo legge Session_Simulator, che passa al risolutore lo stream separato
#     `pass_rng` solo se acceso. Spento: chiamata e comportamento di prima. Acceso: lo stream `rng` non cambia (stesse
#     estrazioni, stesso ordine); le estrazioni dei passaggi dal secondo in poi vengono da `pass_rng`.
FP_PER_PASS_DETECTION = False
```

3. **`Detection`** (`:651-669`): la prima riga del docstring diventa "Esito di un'estrazione di rilevamento (una per
   finestra e direzione; con il rilevamento per passaggio, FP, una per passaggio)."; quattro campi in coda, con
   default None, e una frase nel docstring ("`pass_index`,
   `pass_count`, `pass_start`, `pass_end` (FP): indice del passaggio nel volume proprio, numero di passaggi della
   direzione nella finestra, estremi del passaggio ritagliati alla finestra; None se l'estrazione e' l'unica della
   direzione, come prima"):

```python
    pass_index: Optional[int] = None       # FP: indice del passaggio (0 = primo); None = estrazione unica della direzione
    pass_count: Optional[int] = None       # FP: passaggi della direzione nella finestra; None = estrazione unica
    pass_start: Optional[float] = None     # FP: inizio del passaggio [s], ritagliato alla finestra
    pass_end: Optional[float] = None       # FP: fine del passaggio [s], ritagliata alla finestra
```

4. **Funzione di modulo nuova** `_detection_times`, vicino a `registry_dwell_time` (dopo `:1197`):

```python
def _detection_times(detections, earliest: bool = False) -> Dict[Tuple[str, str], float]:
    """Istante di rilevamento per (osservatore, bersaglio) dai `Detection` rilevati, nell'ordine dato.

    `earliest` False: l'ULTIMO in ordine di lista, il comportamento precedente (con piu' finestre della stessa coppia
    vince l'ultima: difetto latente, Proposta_Finestre_Per_Passaggio_Portata_Propria.md FP-5). True (rilevamento per
    passaggio, `pass_rng` dato): il PRIMO istante, cioe' "rilevato entro t" = esiste un rilevamento <= t.
    """
    times: Dict[Tuple[str, str], float] = {}

    for detection in detections:
        if not detection.detected or detection.time is None:
            continue

        key = (detection.observer_id, detection.target_id)
        times[key] = min(times[key], detection.time) if earliest and key in times else detection.time

    return times
```

5. **`_EngagementRun.__init__`** (`:1742-1746`): parametro in coda `pass_rng=None`; accanto a `self.dwell_time_for`
   (`:1811`): `# FP: stream separato dei passaggi dal secondo in poi; None = un'estrazione per finestra e direzione.`
   e `self.pass_rng = pass_rng`.
6. **`_detect_direction`** (`:2085-2142`): dopo il calcolo di `factor` (`:2095-2098`) e **prima** di
   `exposure = dwell = None` (`:2100`), inserire:

```python
        if self.pass_rng is not None:
            # FP (FP_PER_PASS_DETECTION, v. docstring del modulo): con >= 2 passaggi nel volume proprio dentro la
            # finestra, un'estrazione per passaggio. Con 0 o 1 passaggio, o senza tratti, il percorso di prima.
            passes = self._own_passes(window, observer.id, target.id, own_range)

            if passes is not None and len(passes) >= 2:
                self._detect_passes(window, observer, target, own_range, factor, passes)
                return
```

   Il resto del metodo **non cambia di una riga**.
7. **Metodi nuovi** di `_EngagementRun`, dopo `_exposure_time` (`:2250`), testo esatto del corpo:

```python
    def _own_passes(self, window, observer_id: str, target_id: str,
                    own_range: float) -> Optional[List[Tuple[float, float, float, float]]]:
        """Passaggi del bersaglio nel volume PROPRIO dell'osservatore dentro la finestra (FP), in ordine di tempo.

        Ogni passaggio e' `(lo, hi, start, end)`: `(start, end)` e' un intervallo di `range_intervals` con la portata
        propria che tocca la finestra (stesso criterio di `_exposure_time`), `[lo, hi]` lo stesso ritagliato alla
        finestra. None senza i tratti di entrambi (chiamate dirette): il chiamante usa l'estrazione unica di prima.
        Nessuna estrazione.
        """
        legs_observer = self.legs.get(observer_id)
        legs_target = self.legs.get(target_id)

        if not (legs_observer and legs_target):
            return None

        passes = []

        for start, end in range_intervals(legs_observer, legs_target, own_range):
            if end >= window.t_start - TIME_EPS and start <= window.t_end + TIME_EPS:
                lo = max(float(start), float(window.t_start))
                passes.append((lo, max(lo, min(float(end), float(window.t_end))), float(start), float(end)))

        return passes

    def _pass_cpa(self, window, observer_id: str, target_id: str, lo: float, hi: float) -> Tuple[float, float]:
        """`(t_cpa, distanza)` del massimo avvicinamento dentro il passaggio `[lo, hi]` (FP-4). Ripiego (non atteso:
        il passaggio viene dagli stessi tratti) il CPA della finestra, con un log."""
        cpa = closest_point_of_approach(clamp_legs(self.legs[observer_id], lo, hi),
                                        clamp_legs(self.legs[target_id], lo, hi))

        if cpa is None:
            logger.debug(f"_pass_cpa: no CPA for {observer_id!r}->{target_id!r} in [{lo}, {hi}], window CPA used")
            return float(window.t_cpa), max(float(window.distance_cpa), 0.0)

        return float(cpa.time), max(float(cpa.distance), 0.0)

    def _pass_detection_time(self, observer_id: str, target_id: str, lo: float, hi: float,
                             radius: float, t_cpa: float) -> float:
        """Istante del rilevamento dentro il passaggio `[lo, hi]`: primo istante in cui la distanza scende sotto il
        raggio estratto (come `_detection_time`, ma nel passaggio); ripiego il CPA del passaggio."""
        for start, end in range_intervals(self.legs[observer_id], self.legs[target_id], radius):
            if end >= lo - TIME_EPS and start <= hi + TIME_EPS:
                return max(float(start), lo)

        return t_cpa

    def _detect_passes(self, window, observer: _Shadow, target: _Shadow, own_range: float, factor: float,
                       passes: List[Tuple[float, float, float, float]]) -> None:
        """Un'estrazione per passaggio nel volume proprio (FP, >= 2 passaggi). Il primo estrae dallo stream
        dell'ingaggio nella posizione dell'estrazione unica di prima; dal secondo in poi da `pass_rng`, nell'ordine
        (finestra canonica, a->b poi b->a, passaggio). Ogni passaggio ha la sua distanza minima (FP-4), la sua
        permanenza D-5 (FP-6) e un candidato al tiro valido fino all'inizio del passaggio successivo, l'ultimo fino
        alla fine della finestra (FP-3)."""
        dwell = None

        if self.dwell_time_for is not None:
            mode = GROUNDED_DETECTION_MODE if self._grounded_in(target.id, window) else detection_mode_for(target.asset)
            dwell = _check_dwell(self.dwell_time_for(observer.asset, target.asset, mode))

        count = len(passes)

        for index, (lo, hi, start, end) in enumerate(passes):
            pass_factor = factor
            exposure = None

            if dwell is not None:
                exposure = max(0.0, min(end, float(window.t_end)) - start)
                pass_factor = factor * dwell_factor(exposure, dwell)

            draw = self._draw() if index == 0 else self._draw(self.pass_rng)
            t_cpa, distance = self._pass_cpa(window, observer.id, target.id, lo, hi)
            probability = detection_probability(distance, own_range, pass_factor) if distance <= own_range else 0.0
            detected = draw < probability
            time = None

            if detected:
                radius = detection_radius(draw, own_range, pass_factor)
                time = self._pass_detection_time(observer.id, target.id, lo, hi, radius, t_cpa)
                self._perceive(observer.force_id, target.id, time)
                identified = self.identified_by.setdefault(self.domain_of[observer.force_id], {})
                identified[target.id] = min(identified.get(target.id, time), time)

                if not self._grounded_in(target.id, window) \
                        and ADE.rwr_perception(target.asset, observer.asset) == ADE.PERCEIVED_AT_DETECTION:
                    self._perceive_rwr(target, observer, time)

                t_ready = time + self._profile(observer.id).total
                t_until = passes[index + 1][0] if index + 1 < count else float(window.t_end)

                if t_ready <= t_until + TIME_EPS:
                    self.candidates.setdefault(observer.id, []).append(
                        _Candidate(t_ready=t_ready, target_id=target.id, t_end=t_until, t_cpa=t_cpa,
                                   distance_cpa=distance))

            self.detections.append(Detection(observer_id=observer.id, target_id=target.id,
                                             sensor_range=float(own_range), distance_cpa=distance,
                                             probability=probability, draw=draw, detected=detected, time=time,
                                             exposure_s=exposure, dwell_time_s=dwell, pass_index=index,
                                             pass_count=count, pass_start=lo, pass_end=hi))
```

8. **`_exposure_time`** (`:2220-2250`, FP-6): sostituire il ramo con i tratti (`:2235-2242`, dall'`if` al
   `return exposure`) con:

```python
        if legs_observer and legs_target:
            touching = [(start, end) for start, end in range_intervals(legs_observer, legs_target, own_range)
                        if end >= window.t_start - TIME_EPS and start <= window.t_end + TIME_EPS]

            if not touching:
                return 0.0

            # FP-6 (Proposta_Finestre_Per_Passaggio_Portata_Propria.md): UN passaggio, mai la somma. Quello che contiene
            # il massimo avvicinamento della finestra (la distanza della Pd); in mancanza il piu' lungo (il primo a pari).
            longest = max(touching, key=lambda item: min(item[1], window.t_end) - item[0])
            start, end = next(((s, e) for s, e in touching if s - TIME_EPS <= window.t_cpa <= e + TIME_EPS), longest)

            return max(0.0, min(end, window.t_end) - start)
```

   Docstring: "somma, sugli intervalli ..." diventa "con i tratti di entrambe le rotte: la permanenza del passaggio
   (intervallo di `range_intervals` con la portata propria che tocca la finestra) che contiene `t_cpa`, in mancanza
   del piu' lungo, `min(end, t_end) - start`; MAI la somma dei passaggi (regola dell'utente del 2026-11-06, FP-6)".
   Il ramo senza tratti non cambia.
9. **`_draw`** (`:2258-2264`): firma `def _draw(self, rng=None) -> float:`, prima riga
   `value = (self.rng if rng is None else rng).random()`; il resto invariato.
10. **`_detection_time_of`** (`:3187-3193`): la costruzione del dizionario diventa
    `self.detected_at = _detection_times(self.detections, earliest=self.pass_rng is not None)`; docstring: "Con il
    rilevamento per passaggio (FP-5) il primo istante, altrimenti l'ultimo in ordine di lista (comportamento
    precedente)".
11. **`resolve_engagement`** (`:3762-3930`): parametro in coda `pass_rng=None`; validazione accanto a quella di
    `dwell_time_for` (`:3896-3897`): `if pass_rng is not None and not callable(getattr(pass_rng, 'random', None)):
    raise TypeError("pass_rng must expose a random() method returning a float in [0, 1)")`; passato a
    `_EngagementRun(..., dwell_time_for=dwell_time_for, pass_rng=pass_rng)`. Voce nel docstring degli argomenti,
    dopo `dwell_time_for`: "pass_rng: flusso casuale SEPARATO (oggetto con `.random()`) per il rilevamento per
    passaggio (FP, v. "Rilevamento per passaggio"): se dato, una direzione con >= 2 passaggi nel volume proprio dentro
    una finestra ha un'estrazione per passaggio; la prima dallo stream `rng` nella posizione di prima, le altre da
    questo. None (default) = un'estrazione per finestra e direzione, comportamento precedente. In sessione lo passa
    Session_Simulator (`pass_event_id`) solo con FP_PER_PASS_DETECTION acceso."
12. **Docstring del modulo**: (i) nel punto del contratto RNG (`:412-415`) la parentesi "(invariato dalla D-5)"
    diventa "(invariato dalla D-5 e dal rilevamento per passaggio: con `pass_rng` i passaggi dal secondo in poi
    estraggono da quello stream separato, nell'ordine canonico seguito dall'indice del passaggio, e lo stream `rng`
    resta identico)"; (ii) una sezione nuova, dopo quella della D-5, intitolata `## Rilevamento per passaggio nella
    portata propria (FP, interruttore FP_PER_PASS_DETECTION)`, con: la regola dell'utente (un'occasione per passaggio,
    mai la somma), i passaggi dai tratti (`_own_passes`), le quattro scelte FP-2/3/4/6, R-INT (FP-5), il ripiego
    senza tratti, la frase "spento (`pass_rng` None) il comportamento e' quello di prima".

#### 4.1.2 `Logic/Session_Simulator.py`

1. Dopo `TEMPER_EVENT_TAG = 'temper'` (`:798`):

```python
# Tag dell'event_id del flusso casuale SEPARATO dei passaggi di rilevamento dal secondo in poi (FP,
# Engagement_Resolver.FP_PER_PASS_DETECTION): stesse forze, flusso diverso da quelli dell'ingaggio e della tempra.
PASS_EVENT_TAG = 'detection_pass'
```

2. Dopo `temper_event_id` (`:1022-1032`):

```python
def pass_event_id(*force_ids: str) -> str:
    """`event_id` del flusso dei passaggi di rilevamento (FP) per l'ingaggio fra le forze date.

    Stessa forma e stessi vincoli di `engagement_event_id`, tag diverso: le estrazioni dei passaggi dal secondo in poi
    non spostano quelle di rilevamento e danno dello stream dell'ingaggio.
    """
    engagement_event_id(*force_ids)  # stessa validazione

    return json.dumps([PASS_EVENT_TAG, *sorted(force_ids)],
                      ensure_ascii=True, separators=(',', ':'))
```

3. In `engage`, subito dopo il blocco D-5 (`:2770-2772`):

```python
        if ER.FP_PER_PASS_DETECTION:
            # FP: un'occasione di rilevamento per passaggio nel volume proprio (v. Engagement_Resolver.FP_PER_PASS_DETECTION),
            # stream separato con lo stesso `counter` dell'episodio. Spento: chiamata di prima.
            extra['pass_rng'] = order.rng(mission_id=None, event_id=pass_event_id(*force_ids), counter=counter)
```

4. Docstring del modulo, dopo "## Permanenza nel volume (D-5)" (`:730-733`), sezione
   `## Rilevamento per passaggio (FP)`: "Interruttore del risolutore: `Engagement_Resolver.FP_PER_PASS_DETECTION`
   (SPENTO). Acceso, `engage` passa a `resolve_engagement` lo stream separato
   `pass_rng = order.rng(mission_id=None, event_id=pass_event_id(*forze), counter=ordinale dell'episodio)`; spento, la
   chiamata e' quella di prima."

#### 4.1.3 Effetti sui chiamanti [V]

- Chiamate dirette a `resolve_engagement` e a `_EngagementRun` (test: `Test_Engagement_Resolver.py:2406`, `:2435`,
  `Test_Aircraft.py:345`): parametro in coda con default, nessun cambio.
- `Detection` costruiti nei test: campi nuovi con default; il confronto di `Test_Engagement_Resolver.py:3779-3780`
  (`dataclasses.replace(..., exposure_s=None, dwell_time_s=None)`) resta valido (campi nuovi None da entrambe le
  parti).
- `_exposure_time`: chiamato solo con `dwell_time_for` (D-5 accesa); nessun test esistente asserisce la somma
  (`Test_Engagement_Resolver.py:3809-3856`: un solo intervallo, o finestre senza tratti).
- Nessun altro modulo del core cambia (§1.6).

#### 4.1.4 Vincoli

- **RNG**: con `pass_rng` None nessuna istruzione nuova eseguita prima del vecchio percorso salvo il test
  `self.pass_rng is not None`; con `pass_rng` dato lo stream `rng` ha lo stesso numero e lo stesso ordine di
  estrazioni (il primo passaggio prende la posizione dell'estrazione unica). Vietato il modulo `random`.
- **Interruttore**: `FP_PER_PASS_DETECTION = False`, letto a ogni chiamata di `engage` (globale di modulo,
  sostituibile con `patch.object`).
- **Nessuna costante stimata nuova**; tolleranze = `TIME_EPS` esistente. Il dwell di 600 s di S33 e' un valore
  **dichiarato di test** (come S32 `short`).
- Core indifferente al simulatore; import col percorso completo; logger mockato nei test come negli altri.

#### 4.1.5 Test del blocco 1 (17)

Geometria comune ai test 2-14 (`Test/Test_Engagement_Resolver.py`), da definire come costanti di modulo della classe
nuova: osservatore `b1` fermo in (0, 0, 0) per [0, 430]; bersaglio `r1` con tre tratti:
`Leg(0, 200, (-10000, 0, 0), (10000, 0, 0))`, `Leg(200, 230, (10000, 0, 0), (10000, 3000, 0))`,
`Leg(230, 430, (10000, 3000, 0), (-10000, 3000, 0))`. Finestra
`ContactWindow('b1', 'r1', t_start=0.0, t_end=430.0, t_cpa=100.0, distance_cpa=0.0, range_a=5000.0, range_b=20000.0,
t_mutual_start=50.0, t_mutual_end=150.0)`; i tratti passati a `resolve_engagement(..., legs={'b1': [...], 'r1': [...]})`
(senza `legs` i passaggi non si calcolano: e' il test 11). Passaggi di `b1` (portata 5 km): **[50, 150]** (CPA 0 m a 100 s) e
**[290, 370]** (CPA 3000 m a 330 s; Pd 1 - 0,5 * 0,6^4 = **0,9352**). `r1` (20 km) ha un solo passaggio. Forze
`_Force('blue', 'Blue', [_Asset('b1')])`, `_Force('red', 'Red', [_Asset('r1')])`, `reaction_profile_for=_profiles({...})`,
RNG `_ScriptedRng`.

Classe nuova `TestDetectionPerPass(unittest.TestCase)` (logger mockato in `setUp` come `TestDwellTimeInTheResolver`):
1. `test_switch_is_off_by_default`: `ER.FP_PER_PASS_DETECTION is False`.
2. `test_without_pass_rng_one_draw_per_window`: senza `pass_rng`, una `Detection` di `b1` su `r1`, campi `pass_*`
   None; `rng.calls == 2`.
3. `test_with_pass_rng_one_draw_per_pass`: rng `[0.3, 0.6]`, pass_rng `[0.7]`: due `Detection` di `b1` con
   `pass_index` 0 e 1, `pass_count` 2, `(pass_start, pass_end)` ~ (50, 150) e (290, 370) (`places=6`); la `Detection`
   di `r1` ha i campi `pass_*` None.
4. `test_the_engagement_stream_is_unchanged`: `fire=lambda s, t: None`; stessa sequenza nei due stati:
   `rng.calls` uguale (2), draw della `Detection` di `b1` con `pass_index` 0 uguale a quello dell'estrazione unica
   (0.3), `pass_rng.calls == 1`.
5. `test_each_pass_uses_its_own_cpa`: `distance_cpa` 0 e 3000 (`places=6`), `probability` 1.0 e 0.9352 (`places=9`).
6. `test_detection_time_is_inside_its_pass`: rng `[0.0, 0.9]`, pass_rng `[0.0]`: istanti 50.0 e 290.0 (`places=6`).
7. `test_the_second_pass_is_a_new_occasion`: `detection_factor=lambda o, t: 0.9`, profilo di `b1` (10, 1), fire control
   `_kill()` per `b1` e None per `r1`; rng `[0.95, 0.99]`, pass_rng `[0.1]`. Senza `pass_rng`: nessuna salva di `b1`
   (0.95 >= 0.9). Con: una salva di `b1` su `r1` con `t_launch` 300.0 (`places=6`).
8. `test_a_pass_candidate_ends_where_the_next_pass_begins` (FP-3): profilo di `b1` (300, 1), fire control `_kill()`
   per `b1`; rng `[0.0, 0.99]`, pass_rng `[0.99]`. Senza `pass_rng`: una salva di `b1` a 350.0 (rilevamento a 50,
   candidato fino a 430). Con: nessuna salva (candidato del primo passaggio fino a 290 < 350; secondo passaggio
   mancato).
9. `test_dwell_exposure_is_per_pass` (FP-6 con FP): `dwell_time_for=lambda o, t, m: 400.0`, pass_rng dato:
   `exposure_s` 100 e 80, `probability` 0.25 e 0.2 * 0.9352 (`places=9`), `dwell_time_s` 400.
10. `test_single_pass_direction_is_unchanged`: `r1` con il solo primo tratto e finestra [0, 200]: `Detection` uguali
    (osservatore, bersaglio, probabilita', draw, rilevato, istante) con e senza `pass_rng`, `pass_rng.calls == 0`.
11. `test_without_legs_one_draw`: finestra `_window('b1', 'r1', range_a=1000.0, range_b=2000.0)` senza `legs`:
    una `Detection` per direzione, `pass_rng.calls == 0`.
12. `test_pass_rng_must_expose_random`: `pass_rng=object()` -> `TypeError`.
13. `test_detection_times_first_or_last` (FP-5): lista di tre `Detection` della coppia ('i', 'l') nell'ordine
    rilevata a 210, rilevata a 390, non rilevata (`time=None`): `ER._detection_times(lista, earliest=True)[('i', 'l')]
    == 210`, `earliest=False` -> 390 (l'ultima rilevata, come il dizionario di oggi).

Nella classe esistente `TestDwellTimeInTheResolver`:
14. `test_exposure_is_the_pass_containing_the_cpa`: stessa geometria, `dwell` 400, **senza** `pass_rng`: una
    `Detection` di `b1` con `exposure_s` 100.0 (passaggio che contiene `t_cpa` = 100; la somma sarebbe 180) e
    `probability` 0.25.

`Test/Test_Session_Simulator.py`, classe nuova `TestPerPassDetectionSwitch(_Base)` modellata su `TestDwellTimeSwitch`
(`:235-266`):
15. `test_switch_off_passes_no_pass_rng`: nessuna chiamata a `resolve_engagement` riceve `pass_rng`.
16. `test_switch_on_passes_the_pass_stream`: con `patch.object(ER, 'FP_PER_PASS_DETECTION', True)` ogni chiamata
    riceve `pass_rng` con un metodo `random` chiamabile.
17. `test_pass_event_id_is_distinct_and_order_free`: `pass_event_id('a', 'b') == pass_event_id('b', 'a')`, diverso
    da `engagement_event_id('a', 'b')` e da `temper_event_id('a', 'b')`; `ValueError` con un solo id.

#### 4.1.6 Esito atteso del blocco 1

- Suite: **`Ran 4812 tests`** (4795 + 17), `OK (skipped=7)`.
- Confronto con la fotografia: **1009 identiche, 0 cambiate, 20 nuove** (`S32-DWELL`), cioe'
  `compared 1029 runs: 20 difference lines` come prima. Le 1009 restano identiche perche' l'interruttore e' spento:
  `engage` non passa `pass_rng`, `_detect_direction` esegue le stesse istruzioni, `_exposure_time` non e' mai
  chiamato (D-5 spenta), `_detection_time_of` usa `earliest=False` (stesso dizionario di prima).
- **Verifica di S32** (le sue esecuzioni non sono nella fotografia: un cambio non si vedrebbe nel confronto):
  `<python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare .ai-run/sonde_passaggi/p0/capture.json
  --against .ai-run/confronto_capture.json --only 'S32-DWELL' --ignore probe_passes` -> `compared 20 runs:
  IDENTICAL` (attesa: in S32 la ZSU e il P-18 hanno un solo passaggio, quindi FP-6 non cambia la permanenza).
  Se non e' IDENTICAL: fermarsi e riferire le righe.

### 4.2 Blocco 2 — scenario S33-PASSES

#### 4.2.1 `Test/Test_Session_Scenarios_S33.py` (nuovo, 7 test)

Docstring di modulo nello stile di S32 (`Test_Session_Scenarios_S32.py:1-28`) con la tabella delle varianti e la frase
"600 s e' un periodo di rivisita DICHIARATO DI TEST sulla ZSU-57-2, non un dato". Costruzione:

```python
SEEDS = [f'S33-PASSES-{index}' for index in range(5)]
# variante -> (FP_PER_PASS_DETECTION, dwell DICHIARATO DI TEST sulla ZSU [s] con D5_DWELL_TIME acceso | None)
VARIANT_SPEC = {
    'off': (False, None),
    'on': (True, None),
    'dwell_off': (False, 600.0),
    'dwell_on': (True, 600.0),
}
VARIANTS = tuple(VARIANT_SPEC)
CAS_IDS = tuple(f'Blue-CAS/cas{index}' for index in range(4))
# Andata sulla linea Red, uscita a 14 km, ritorno, uscita: due passaggi nei 6 km della ZSU (visivo, quota 3000 m),
# sempre entro gli 80 km dell'A-10C contro bersagli a terra (una sola finestra per coppia A-10C/ZSU).
REENTRY = [(0.0, 0.0), (-14_000.0, 0.0), (0.0, 0.0), (-30_000.0, 0.0)]
```

`build` e `ZSU` importati da `Test_Session_Scenarios_S32` (`build(with_ewr=False)`); `run_variant` come quello di S32
(`:83-110`) con `REENTRY` al posto di `OVERFLIGHT`, `patch.object(ER_MODULE, 'FP_PER_PASS_DETECTION', switch)` e
`patch.object(ER_MODULE, 'D5_DWELL_TIME', dwell is not None)` attorno all'intera esecuzione,
`F.declare_dwell(red.assets[ZSU], {'air': dwell})` se `dwell` non e' None, spia su `ER.resolve_engagement`; restituisce
`(outcome, [EngagementResult, ...])`. Ciclo esterno sui semi, interno sulle varianti (stesso `session_id` per le 4
varianti di un seme). Classe `TestS33DetectionPerPass(F.LoggerSilencer, unittest.TestCase)`; `_zsu(results, cas=None)` =
le `Detection` con `observer_id == ZSU` (e `target_id == cas` se dato) di tutti i risultati. Test:
1. `test_premise_two_passes_per_aircraft`: in `on`, per ogni seme e A-10C, esattamente 2 `Detection` della ZSU, con
   `pass_index` {0, 1}, `pass_count` 2 e `pass_end` del passaggio 0 < `pass_start` del passaggio 1.
2. `test_switch_off_one_draw_per_window`: in `off`, per ogni seme e A-10C, esattamente 1 `Detection` della ZSU, con
   `pass_index` None.
3. `test_the_engagement_stream_is_unchanged`: per ogni seme, nel PRIMO `EngagementResult`,
   `[d.draw for d in off.detections] == [d.draw for d in on.detections if d.pass_index in (None, 0)]`.
4. `test_a_launch_after_the_next_pass_needs_a_new_detection` (FP-3): in `on`, per ogni salva della ZSU in un risultato,
   esiste una `Detection` rilevata della ZSU sullo stesso bersaglio con `time <= t_launch + 1e-9`; se la piu' recente
   ha `pass_count == 2` e `pass_index == 0`, allora `t_launch < pass_start` della `Detection` con `pass_index == 1`
   della stessa coppia nello stesso risultato `+ 1e-6`.
5. `test_dwell_exposure_is_the_own_pass`: in `dwell_on` ogni `Detection` della ZSU ha `dwell_time_s == 600`,
   `|exposure_s - (pass_end - pass_start)| < 1e-6` e `probability <= exposure_s / 600 + 1e-12`.
6. `test_dwell_single_draw_uses_one_pass_never_the_sum` (FP-6): per ogni seme e A-10C, nel primo risultato,
   l'`exposure_s` della `Detection` della ZSU in `dwell_off` e' uguale (entro 1e-6) a una delle due di `dwell_on` ed e'
   minore della loro somma di almeno 1e-6.
7. `test_premise_the_zsu_fires_without_the_switch`: in `off` la ZSU spara in almeno un seme.

Valori attesi [I, da leggere all'esecuzione, NON da scrivere come asserzioni]: passaggi della ZSU di ~50-60 s ciascuno
separati da ~2 minuti (velocita' dell'A-10C ~155 m/s ricavata dalle permanenze misurate in S32, 62-67 s per un
sorvolo); 4 rilevamenti della ZSU per seme in `off`, 8 estrazioni in `on`. Se (1) fallisse (la geometria non da' due
passaggi in una finestra), l'esecutore **non** cambia la rotta: si ferma e riferisce `pass_count`, gli istanti e le
finestre osservate.

#### 4.2.2 `Test/Scenario_Baseline.py`

In `UNITS`, dopo S32-DWELL (`:395-397`):

```python
    # ── S33 (FP: un'occasione di rilevamento per passaggio nel volume proprio) — in coda, nomi stabili ──
    ('S33-PASSES', 'Test_Session_Scenarios_S33', 'TestS33DetectionPerPass', None,
     _by_occurrence('off', 'on', 'dwell_off', 'dwell_on')),
```

e nel docstring, dopo "## Permanenza nel volume dopo la D-5" (`:176-181`):

```
## Rilevamento per passaggio dopo la FP

Il rilevamento per passaggio nella portata propria (`Engagement_Resolver.FP_PER_PASS_DETECTION`, SPENTO,
`Proposta_Finestre_Per_Passaggio_Portata_Propria.md`) non cambia le esecuzioni esistenti (interruttore spento). Aggiunge
in coda l'unita' S33-PASSES (4 varianti, 5 seed): 20 esecuzioni nuove; nessuna voce nuova nel riassunto (i `Detection`
non sono registrati).
```

#### 4.2.3 Vincoli del blocco 2

- **Nomi stabili**: unita' `S33-PASSES`; varianti `off`, `on`, `dwell_off`, `dwell_on`; semi `S33-PASSES-0..4`; asset
  `Red-Line/ad0` (ZSU), `Red-Line/ifv0..2`, `Blue-CAS/cas0..3`. Nessun nome esistente cambia.
- Valore di test 600 s dichiarato come tale nel codice (commento) e nel rapporto.

#### 4.2.4 Esito atteso del blocco 2

- Suite: **`Ran 4819 tests`** (4812 + 7), `OK (skipped=7)`.
- Confronto: **1009 identiche, 0 cambiate, 40 nuove** (20 `S32-DWELL`, 20 `S33-PASSES/S33-PASSES-<k>/<variante>`),
  cioe' `compared 1049 runs: 40 difference lines`. Fra le nuove, `off` e `on` di un seme possono differire nel
  contenuto (e' l'effetto della regola); nessuna asserzione lo richiede.

### 4.3 Dopo i blocchi (sessione principale, non l'esecutore)

1. Sonda **P-1** (`probe_switch_on.py`, §1.8 e LEGGIMI): confronto con la regola accesa in memoria. Atteso: le
   esecuzioni cambiate sono un sottoinsieme delle righe `MULTI` e `RINT` di P-0; una cambiata fuori da quell'elenco e'
   un errore da diagnosticare. Il numero esatto non e' prevedibile prima (dipende da quali occasioni in piu' decidono
   qualcosa).
2. Lettura delle cambiate per gruppi (scenario, coppia di modelli) e decisione dell'utente sull'accensione. **Nessuna
   nuova fotografia** senza decisione esplicita.

### 4.4 Tempi di verifica (ProArt, `tools/ai/verifica.sh`, mai in parallelo)

Per blocco: suite ~10 minuti, poi confronto ~10 minuti [AGENTS.md]; P-0 ~11-13 minuti prima del blocco 1; P-1 ~10-12
minuti dopo. Totale macchina ~65-75 minuti [S].

### 4.5 Scelte minori lasciate all'esecutore (da elencare nel rapporto)

Nomi delle variabili locali e delle costanti di test, posizione dei metodi nuovi dentro la classe, testo dei
messaggi di log, struttura interna di `Test_Session_Scenarios_S33.py` (riuso o copia locale di `run_variant`), la
sessione minima dei test 15-16 (quella di `_Base`), il modo di raccogliere le salve nel test S33 4 (dai
`EngagementResult` catturati).

---

## 5. Rischi e limiti

### 5.1 Rischi di esecuzione

- `_detect_direction` e' il punto piu' delicato del motore. La rete: test 2, 4, 10 (stream e percorso di prima),
  confronto **0 cambiate** a interruttore spento (una sola cambiata = errore d'implementazione), verifica di S32
  (§4.1.6).
- Il test 4 di S33 controlla un invariante della sola implementazione FP-3 (b): se l'utente sceglie (a) o (c) va
  riscritto.
- Il costo con la regola accesa: un `range_intervals` per direzione e un CPA (con `Point3D` di sympy) per passaggio
  multi; trascurabile rispetto a una sessione [I], da confermare con i tempi di P-1.
- `Test_Session_Scenarios_S33` aggiunge 20 sessioni (~1 minuto di suite [I]).
- La sonda P-0 misura con la stessa regola dei passaggi del piano: se l'implementazione se ne discostasse, P-1
  mostrerebbe cambiate fuori dall'elenco `MULTI`.

### 5.2 Limiti di modello (da dichiarare nel manuale)

- **Senza tratti** (chiamate dirette) nessun passaggio: un'estrazione per finestra e direzione, come prima.
- **Tiro dopo l'uscita dal volume**: con FP-3 (b) il candidato dell'ultimo passaggio (e di un passaggio unico) vale
  fino alla fine della finestra anche quando il bersaglio e' fuori dal volume del sensore (limite di oggi, invariato;
  la (a) lo toglierebbe).
- **Passaggi tangenti o ritagliati a durata nulla** contano come passaggi (Pd sul bordo = 0,5 x fattore, legge di
  oggi); con la D-5 la permanenza nulla li annulla.
- **Passaggio diviso da un decollo/atterraggio** (`_pair_windows`): due finestre, due estrazioni, come oggi (stato a
  terra diverso nelle due parti).
- **Pianificatore** (FP-9): `max_detection_probability` e' per attraversamento, non cumulativa.
- **Detection non nella fotografia**: il numero di estrazioni non e' visibile nel confronto; lo verificano i test.
- **R-INT** con l'interruttore spento: resta il difetto latente "ultimo rilevamento" (§1.9), corretto solo con la
  regola accesa.

---

## 6. Documenti da aggiornare dopo (non scritti qui)

- **Manuale DES** (`des-manual-writer`, insieme all'aggiornamento della D-5 ancora da fare): cap. 3 §3.5
  (`04_Strato1_Scheduler_Contatti.md:195-201`: `t_mutual_*` e' il **primo** intervallo nella portata minore; i
  passaggi successivi li conta il risolutore); cap. 4 §4.2 (Pd per passaggio, distanza del passaggio, FP-6), §4.11
  (stream `pass_rng`, `pass_event_id`), §4.26 (R-INT: primo istante con la regola accesa); cap. 6 (orchestratore,
  `07_Orchestratore_Session_Simulator.md`: `pass_event_id` fra gli stream); cap. 8 (`09_Validazione.md`: S33-PASSES);
  cap. 9 (`10_Limiti_Estensioni_Divergenze.md`: il limite "una sola estrazione per finestra con piu' passaggi nel
  volume minore" come **storico** e i limiti di §5.2); atlante `11a_Atlante_Risolutore.md` (costante
  `FP_PER_PASS_DETECTION`, campi nuovi di `Detection` a `:1310`, metodi `_own_passes`, `_pass_cpa`,
  `_pass_detection_time`, `_detect_passes`, funzione `_detection_times`, sequenza di `_detect_direction`).
- **`F4_Differenze_Scenari.md`**: sezione "FP — rilevamento per passaggio (2026-11-xx)": il cambio, 1009 identiche,
  20 nuove di S33, esiti di P-0 e P-1, limiti.
- **`Piano_Implementazione_Missione.md`**: riga in §5 fuori dalla numerazione F, come D-4b/D-4c e D-5, con lo stato
  dell'interruttore.
- **`Proposta_Dwell_Time_Rilevamento.md`**: nota in §5.2 gia' scritta (rimando a questa Proposta); a lavoro fatto,
  l'esito.
- **`Rapporti/Sonde_Finestre_Passaggio/LEGGIMI.md`**: esiti di P-0 e P-1.
- **Memoria** (solo la sessione principale): decisioni FP, interruttore, esiti delle sonde.
