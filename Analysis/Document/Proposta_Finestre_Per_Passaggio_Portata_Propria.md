# Proposta: un'occasione di rilevamento per ogni passaggio nel volume di rilevamento PROPRIO dell'osservatore (FP)

**Stato: BOZZA (2026-11-06; esito della sonda P-0 registrato il 2026-11-07; FP-1, FP-2 e FP-3 decise il 2026-11-07).**
Decisioni: **FP-1 DECISA dall'utente il 2026-11-07 = B-R** (passaggi calcolati nel risolutore dai tratti, §2.2);
**FP-2 DECISA dall'utente il 2026-11-07 = O3** (stream separato `pass_rng` per i passaggi dal secondo in poi, §2.3);
**FP-3 DECISA dall'utente il 2026-11-07 = (a)** (il candidato al tiro vale fino alla FINE del passaggio, anche con un
passaggio solo, §2.5; diversa dalla raccomandazione (b) iniziale); **FP-4 DECISA dall'utente il 2026-11-07 = (a)**
(CPA del passaggio, §2.4); **FP-5 SOSPESA** in attesa di `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` (la regola
nuova sui bersagli intercettabili puo' renderla marginale, §2.6); **FP-6..FP-10 aperte** (§3), da prendere una per
volta (FP-10, tolleranza di unione dei passaggi ravvicinati, aggiunta il 2026-11-07). **Blocco 1 aggiornato il 2026-11-07 per la decisione VA-6 (a)** di
`Proposta_Allineamento_Volumi_DES_Pianificatore.md`: `_own_intervals` e' l'unico punto di chiamata del volume proprio
di rilevamento (§4.1.1 punti 7 e 8-bis, test 20); nessun'altra FP decisa da questa modifica. Sonda **P-0 eseguita** il
2026-11-07 sul ProArt (§1.8): confronto invariato (0 righe DIFF)
e **nessuna direzione a piu' passaggi** in tutte le 1029 esecuzioni (`RUNS_WITH_MULTI 0`, `RUNS_WITH_RINT 0`,
`RUNS_WITH_AFTER_PASS 44`). Con FP-3 (a) la regola ACCESA cambia al piu' le 44 esecuzioni `AFTER_PASS`; spenta, la
fotografia resta 1009 identiche. Motivazioni, impatti e rischi riallineati ai numeri. Su
richiesta dell'utente (2026-11-07) S33-PASSES ha in piu' le 4 varianti **CAS** (§2.9, §4.2): 8 varianti x 5 semi.
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

**Termini**: **finestra** = solo la finestra di contatto (`ContactWindow`, intervallo entro la portata MAGGIORE delle
due parti); **passaggio** = intervallo continuo in cui il bersaglio e' entro la portata PROPRIA dell'osservatore;
**finestra d'ingaggio** = intervallo di validita' del candidato al tiro (`_Candidate.t_end`).

**Glossario delle sigle** (significato verificato dove indicato; "incerto" = da confermare dall'utente):

| Sigla | Significato | Fonte / verifica |
|---|---|---|
| DES | *Discrete Event Simulation*: il motore delle sessioni virtuali, a coda di eventi | `Logic/Session_Simulator.py:1-45` (schema dei passi) |
| CPA / TCPA | *Closest Point of Approach* (punto e distanza di massimo avvicinamento fra due mobili) / *Time to CPA* (istante del massimo avvicinamento) | `Logic/Contact_Scheduler.py:31`, `:184` |
| RNG | *Random Number Generator*: nel motore solo l'RNG di sessione, uno stream per chiave (missione, evento, contatore) | `Utility/Session_Rng.py`, `Command/Session_Types.py:388-390` |
| Pd | probabilita' di rilevamento di un sensore contro un bersaglio a distanza d | `Logic/Engagement_Resolver.py:1096-1105` (`detection_probability`) |
| D-5 | decisione D-5 di `Proposta_Volumi_Rilevamento_Intercettazione.md` §9, opzione 2: Pd dipendente dalla permanenza (`Proposta_Dwell_Time_Rilevamento.md`, interruttore `D5_DWELL_TIME`, spento) | `Proposta_Dwell_Time_Rilevamento.md:1`, `:17` |
| DW-1..DW-9 | decisioni della Proposta D-5 (tutte prese il 2026-11-06) | `Proposta_Dwell_Time_Rilevamento.md:3-8` |
| dwell (`dwell_time_s`) | periodo di rivisita del sensore [s]: con la D-5 la Pd e' moltiplicata per min(1, permanenza / dwell) | `Logic/Engagement_Resolver.py:146`; `Test/Test_Session_Scenarios_S32.py:5-8` |
| FP | questa Proposta: "finestre per passaggio", un'occasione di rilevamento per passaggio nel volume proprio; decisioni FP-1..FP-10 | questo documento |
| EWR | *Early Warning Radar*: radar di scoperta lontana (es. P-18-Terek, FPS-117) | `Proposta_Dwell_Time_Rilevamento.md` (10 EWR del registro) |
| SAM | *Surface-to-Air Missile*: sistema missilistico superficie-aria | conoscenza generale [I] |
| AAA | *Anti-Aircraft Artillery*: artiglieria contraerea (cannoni) | conoscenza generale [I] |
| ZSU | ZSU-57-2, semovente contraereo a cannoni da 57 mm; nel registro solo sensore visivo, portata 6000 m contro bersagli aerei | §1.4 [V eseguendo lo scheduler]; espansione russa della sigla [I] |
| R-INT | regola dell'intercettazione con tempo di reazione (2026-09-30, `Proposta_Intercettazione_Reazione.md`): un intercettore ferma i colpi solo se ne ha una traccia e il tempo di reagire; se aveva gia' rilevato il lanciatore "vede il lancio" (reazione breve) | `Logic/Engagement_Resolver.py:49-55`, `:1803-1805`, `:3251-3260` |
| G4a | raggruppamento delle finestre in **episodi d'ingaggio** (sovrapposte entro `EPISODE_GAP` = 300 s), un `resolve_engagement` per episodio; finestre successive ritagliate | `Logic/Session_Simulator.py:11`, `:85-86`; `Piano_Implementazione_Missione.md:299` |
| G4b | **ri-pianificazione degli aerei dopo l'episodio** (bingo, rientro dopo disingaggio) e ricalcolo dei contatti non ancora risolti | `Logic/Session_Simulator.py:14`, `:45-46`; `Piano_Implementazione_Missione.md:300` |
| B-R / B-S1 / B-S2 | opzioni di FP-1: passaggi calcolati nel **R**isolutore / nello **S**cheduler con finestre per direzione / nello Scheduler come campo della finestra | §2.2 |
| O1 / O2 / O3 | opzioni di FP-2 per l'ordine delle estrazioni: in linea / in coda / stream separato | §2.3 |
| S32 | scenario S32-DWELL (D-5): ZSU, 3 BMP-2, 4 A-10C in sorvolo; 5 varianti x 4 semi = 20 esecuzioni nuove, non nella fotografia | `Test/Test_Session_Scenarios_S32.py:1-28` |
| S33 | scenario nuovo S33-PASSES di questa Proposta (FP-8): rientro e CAS, 8 varianti x 5 semi | §2.9, §4.2 |
| P-0 / P-1 | sonde di sola lettura: P-0 prima del codice (conta i passaggi), P-1 dopo il blocco 1 (regola accesa in memoria) | §1.8, §4.3, `Rapporti/Sonde_Finestre_Passaggio/` |
| `ContactWindow` | finestra di contatto fra due asset: `t_start/t_end`, CPA, portate delle due parti, primo intervallo nella portata minore | `Logic/Contact_Scheduler.py:196-240` |
| `TIME_EPS` | 1e-9 s: due istanti piu' vicini sono lo stesso istante; serve anche a fondere intervalli contigui fra tratti consecutivi | `Logic/Contact_Scheduler.py:88-92`, `:938-952` |
| CAS | *Close Air Support*: tipo di missione aerea d'appoggio ravvicinato (`mission_type='CAS'` negli scenari) | `Test/Test_Session_Scenarios_S32.py:103` |
| GA | **incerto**: inteso come *Ground Attack* (attacco al suolo). Nel codice non esiste un tipo di missione 'GA'; "Ground Attack" e' un nome di task nei loadout e coincide con Strike | `Asset/Aircraft_Loadouts.py:2768`, `Context/Context.py:409` |

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
| Dove si calcolano i passaggi (FP-1, **DECISA 2026-11-07: B-R**) | nel **risolutore**, dai tratti (`range_intervals` con la portata propria), come la permanenza D-5; `ContactWindow` e scheduler invariati | nessuno |
| Ordine delle estrazioni (FP-2, **DECISA 2026-11-07: O3**) | primo passaggio dallo stream dell'ingaggio, nella posizione di oggi; dal secondo in poi uno **stream separato** (`pass_rng`, `pass_event_id`, come la tempra): lo stream dell'ingaggio resta identico anche con la regola accesa | nessuno |
| Finestra d'ingaggio per passaggio (FP-3, **DECISA 2026-11-07: (a)**) | il candidato al tiro vale fino alla **fine del passaggio** (uscita dal volume proprio: traccia persa), per ogni direzione con passaggi calcolabili, anche con un passaggio solo; al rientro serve un nuovo rilevamento. Osservatore con la portata maggiore e chiamate senza tratti: fine della finestra, come oggi | nessuno a interruttore spento; **acceso: al piu' le 44 esecuzioni `AFTER_PASS` di P-0** |
| Distanza per passaggio (FP-4, **DECISA 2026-11-07: (a)**) | **CPA del passaggio** per ogni passaggio | nessuno |
| Istante di rilevamento per R-INT (FP-5) | con la regola accesa il **primo** istante (oggi: l'ultimo in ordine di lista, difetto latente) | nessuno |
| D-5 (FP-6) | con FP spento e D-5 acceso: permanenza = **il passaggio che contiene il CPA** (mai la somma); con FP acceso: permanenza del proprio passaggio | nessuno (D-5 spenta) |
| Interruttore (FP-7) | `Engagement_Resolver.FP_PER_PASS_DETECTION = False`; `Session_Simulator` passa `pass_rng` solo se acceso | **1009 identiche** |
| Scenario (FP-8) | S33-PASSES: A-10C che entrano due volte nel volume della ZSU restando nella stessa finestra, con due geometrie (rientro e CAS a 3 bersagli), 8 varianti x 5 semi = **40 nuove** | +40 |
| Pianificatore (FP-9) | nessun cambio (gia' per attraversamento); limite dichiarato sulla metrica `max_detection_probability` | nessuno |
| Passaggi ravvicinati (FP-10) | nessuna tolleranza di modello: passaggi distinti se separati da piu' di `TIME_EPS`, come oggi le finestre e gli attraversamenti del pianificatore | nessuno |

**Esito della sonda P-0 (2026-11-07, §1.8)** [V]: nelle 1029 esecuzioni (1009 della fotografia e 20 di S32-DWELL)
nessuna direzione ha piu' di un passaggio nel volume proprio (`multi` 0, `extra_draws` 0) e nessuna coppia ha
rilevamenti a istanti diversi nello stesso ingaggio (`rint_last_not_earliest` 0). Conseguenze: a interruttore
**spento** la fotografia resta **1009 identiche**; a interruttore **acceso** (sonda P-1) cambiano **al piu' le 44
esecuzioni `AFTER_PASS`** di P-0 (151 salve lanciate dopo la fine dell'unico passaggio di un osservatore con portata
minore: S13, S14, S21, S24-ORBIT, S26-BINGO, S28-CLASS), effetto della decisione FP-3 (a); le altre parti della regola
(passaggi multipli, FP-4/5/6) sono provabili **solo** sul nuovo scenario S33-PASSES e nei test unitari.

**Dimensione stimata** [S]: blocco 1 ~165 righe di codice + ~390 di test (20 test, compreso `_own_intervals` di VA-6 (a)); blocco 2 ~340 righe di test
(14 test: 7 della geometria di rientro, 7 della variante CAS) + 7 righe nella tabella della fotografia. Suite attesa:
`Ran 4815` dopo il blocco 1, `Ran 4829` dopo il blocco 2 (base `Ran 4795`; se BI e VA sono eseguite prima, la base e' la loro e i due numeri crescono di conseguenza: +20 e +34).

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

### 1.8 Sonda P-0 (sola lettura) — ESEGUITA il 2026-11-07 sul ProArt

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

**Esito (2026-11-07, ProArt)** [V: `.ai-run/sonde_passaggi/p0/log.txt` righe 1205-1257, `stats.json` della stessa
cartella; numeri ricontrollati sul log da chi pianifica]:

    compared 1029 runs: 20 difference lines (484.4 s)
    PROBE_RC 1
    RUNS 1029 (in fotografia 1009, nuove 20)
    RUNS_WITH_MULTI 0 (in fotografia 0)
    RUNS_WITH_AFTER_PASS 44  RUNS_WITH_RINT 0
    TOTALS {"cpa_not_in_first": 0, "directions": 33910, "engagements": 1258, "extra_draws": 0, "first_flip_by_distance": 0,
            "inner_single_salvos_after_pass": 151, "multi": 0, "multi_detected": 0, "multi_detected_after_first": 0,
            "multi_outer": 0, "multi_with_salvos": 0, "rint_last_not_earliest": 0, "salvos": 28214,
            "salvos_after_next_pass_start": 0, "salvos_between_passes": 0, "without_legs": 0} MAX_PASSES 0
    HIST {"0": 946, "1": 32964}
    UNITS {}
    MODELS []

- **Confronto invariato**: le 20 righe di differenza sono tutte `NEW S32-DWELL/S32-DWELL-<0..3>/<ewr_off|ewr_on|long|off|
  short>` (S32 non e' nella fotografia), **0 righe DIFF**: la sonda non ha alterato il motore. `PROBE_RC 1` e' quello
  atteso (le righe NEW contano come differenze). Durata 484,4 s (~8 minuti), meno della stima di 11-13 minuti.
- **Nessuna direzione a piu' passaggi**: `multi` 0 su 33 910 direzioni con estrazione (1258 ingaggi, 28 214 salve),
  quindi `extra_draws` 0, elenco `MULTI` vuoto, `UNITS` e `MODELS` vuoti, e tutti i contatori derivati dalle direzioni
  multi a 0 (`cpa_not_in_first`, `first_flip_by_distance`, `multi_detected*`, `multi_with_salvos`,
  `salvos_after_next_pass_start`, `salvos_between_passes`). Vale anche per le 20 esecuzioni di S32-DWELL.
  `multi_outer` 0 (controllo di coerenza rispettato, ma banalmente).
- **Istogramma dei passaggi**: 32 964 direzioni con un passaggio (97,2 %), 946 con **zero** passaggi (2,8 %: il bersaglio
  non entra mai nella portata propria dentro la finestra, estrazione a Pd 0, §1.9); nessuna con due o piu'.
  `without_legs` 0: in sessione i tratti ci sono sempre, il ripiego senza tratti di B-R non scatta mai.
- **R-INT**: `rint_last_not_earliest` 0, nessuna esecuzione `RINT`: il difetto latente di §1.9 (vince l'ultimo
  rilevamento in ordine di lista) **non si manifesta** in nessuna esecuzione della fotografia.
- **Salve dopo il passaggio (FP-3 (a))**: 151 salve, in **44 esecuzioni tutte della fotografia** (nessuna di S32), di un
  osservatore con portata minore e un solo passaggio, partite dopo la fine di quel passaggio. Elenco compatto
  (esecuzione: salve):
  - S13 (2 esecuzioni, 6 salve): `S13-2` 2, `S13-4` 4;
  - S14 (1, 2): `S14-4` 2;
  - S21 (6, 19): `S21-3/control` 3, `S21-3/parked` 8, `S21-5/control` 4, `S21-5/parked` 1, `S21-7/control` 2,
    `S21-7/parked` 1;
  - S24-ORBIT (1, 1): `S24-ORBIT-0/full` 1;
  - S26-BINGO (32, 121): tutti gli 8 semi `S26-BINGO-0..7` per tutte e 4 le varianti (`engagement_fuel_off`, `none`,
    `switch_off`, `transfer_continue`), 4 salve ciascuna, tranne `S26-BINGO-4/{engagement_fuel_off, none, switch_off}`
    3 (`transfer_continue` 4) e `S26-BINGO-6/` tutte e 4 le varianti 3;
  - S28-CLASS (2, 2): `S28-CLASS-2/self_defence` 1, `S28-CLASS-2/self_defence_off` 1.

**Lettura.** L'attesa qualitativa scritta prima della sonda [I] ("direzioni multi probabili dove un aereo torna su un
sito: rientro a ritroso S26, orbite S23-CAP, doppio ingaggio S27, S5") e' **smentita**: in nessuno scenario della
fotografia un bersaglio rientra nel volume proprio dell'osservatore con la portata minore restando nella stessa finestra
di contatto. Perche' [I, non verificato]: nei rientri e nelle orbite il bersaglio esce anche dalla portata maggiore
(due finestre, regola gia' rispettata, §1.3), oppure il secondo passaggio cade in un episodio successivo (finestra
ritagliata dal G4a, quindi un'altra estrazione). Conseguenze per il piano:
1. con la regola accesa la parte "passaggi multipli" non cambia nessuna esecuzione della fotografia:
   `_detect_passes` non scatta mai (nessuna direzione con >= 2 passaggi), FP-5 (a) da' lo stesso dizionario
   (`rint_last_not_earliest` 0; al piu' differenze entro `TIME_EPS`, §5.1), FP-6 non cambia la permanenza (al piu' un passaggio per direzione) e lo stream
   `pass_rng` e' una derivazione pura senza effetti sugli altri stream [V: `Command/Session_Types.py:388-390`,
   `Session_Rng.session_rng`];
2. il comportamento dei passaggi multipli e' provabile **solo** sul nuovo scenario S33-PASSES (FP-8) e nei test
   unitari del blocco 1;
3. FP-3 (a), **decisa dall'utente il 2026-11-07**, vale anche per le direzioni a un passaggio: con la regola accesa
   cambiano **al piu' le 44 esecuzioni** elencate sopra (probabilmente quasi tutte [I]: togliere una salva toglie anche
   le sue estrazioni di danno dallo stream dell'ingaggio e fa slittare le successive). E' il nuovo atteso di P-1
   (§4.3).

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

### 1.10 Come il DES rappresenta un attacco CAS a piu' bersagli [V, verifica del 2026-11-07]

Domanda dell'utente: i tratti di una missione CAS che attacca piu' bersagli contengono ingresso e uscita sopra ciascun
bersaglio, o un tratto unico?
- **Il moto di un aereo e' la spezzata dei punti della missione**, a velocita' costante per arco: `Mission_Adapter`
  prende la rotta di riferimento (`Mission.route` o, in mancanza, la spezzata dei `MissionWaypoint`,
  `reference_route`, `Logic/Mission_Adapter.py:473-488`, `_route_from_waypoints` `:450-470`), applica l'offset di
  formazione punto per punto (`:9-40`, `asset_route` `:628`) e la scompone in tratti con
  `Contact_Scheduler.route_legs` (`Logic/Contact_Scheduler.py:383-410`), piu' i tratti fermi delle attese (`_timeline`,
  `Mission_Adapter.py:959-1000`) e della presenza prima/dopo (`movement_legs`, `:1002-1028`). Dopo un bingo o un
  disingaggio i tratti sono sostituiti dal rientro (`_legs_after_bingo`, `Logic/Session_Simulator.py:1628`; G4b).
- **Nessun modulo genera manovre d'attacco** (pop-up, giro sul bersaglio, riattacco, uscita): i tratti passano sopra un
  bersaglio **solo se** il pianificatore della missione ha messo un punto li'. Il bersaglio di una missione e' **uno**
  (`Mission.target`, `Command/Mission_Types.py:955`): un GROUP con `asset_ids`, o un'area/zona. I ruoli di punto
  IP/ATTACK/EGRESS esistono (`Command/Mission_Types.py:107-120`) e i punti ATTACK possono essere piu' d'uno, ma il
  motore ne legge solo l'ultimo, e solo per la fine dell'attacco della ROE `priority_designated` (`attack_point`,
  `Mission_Adapter.py:1948-1966`); il fixture degli scenari ne ammette uno solo (`attack_waypoint`,
  `Test/Scenario_Fixtures.py:734-735`).
- **Il tiro non dipende dalla rotta**: il controllo del fuoco spara quando l'arma e' a portata lungo la spezzata
  (`_range_entry`, `Logic/Engagement_Resolver.py:2984-3017`); il Maverick parte da ~15-16 km
  (`Test/Test_Session_Scenarios_S19_Air_Defence.py:5`, `:20`). L'ordine degli attacchi lo decidono priorita' e portate,
  non la sequenza dei punti.
- **Nessun costruttore di missioni nel codice di produzione**: `Mission(` e `MissionWaypoint(` compaiono solo nei test
  (ricerca del 2026-11-07); `Weapon_Delivery` e' solo pianificazione (§1.6). Il "caso reale" e' quindi la rotta a punti
  che un pianificatore (oggi gli scenari, domani la campagna) dichiara.
- **Geometria**: **nel DES** il volume proprio e' una **sfera** (`range_intervals` risolve |Δr + Δv s|^2 = R^2 in 3D,
  `Contact_Scheduler.py:876-933`); **nel pianificatore** e' un **cilindro** con fascia di quota (`AirThreat`,
  `Logic/Air_Route_Manager.py:83-137`; per il rilevamento `build_detection_threat`, raggio tagliato dall'orizzonte).
  Entrambi sono **convessi**, quindi in tutti e due **un tratto rettilineo lo attraversa al piu' una volta**. Non vale
  per forme **non convesse** (portata minima, cono di silenzio, unione di volumi), che un solo tratto puo'
  attraversare due volte: v. `Proposta_Allineamento_Volumi_DES_Pianificatore.md` §2.3. Due
  passaggi non contigui richiedono almeno un cambio di direzione (riattacco, rientro, orbita, bersaglio fuori volume
  raggiunto e poi abbandonato tornando indietro). Una missione CAS dichiarata con un tratto unico sopra piu' bersagli in
  linea da' **un** passaggio per osservatore: il caso multi-passaggio esiste solo con rotte a piu' punti con virate.

Conseguenza per la variante CAS di S33 (§2.9, §4.2): la geometria usa una rotta a punti con un punto sopra ciascun
bersaglio e una virata dopo il bersaglio fuori volume, cioe' esattamente la forma che il DES sa rappresentare. Limiti
dichiarati (§5.2): niente manovre d'attacco, ordine degli attacchi non garantito dalla rotta, rotta che non cambia se i
bersagli sono distrutti prima (salvo G4b).

### 1.11 Intervalli adiacenti oggi [V]

- `range_intervals` (`Logic/Contact_Scheduler.py:874-935`) calcola gli intervalli dentro il raggio su ogni
  sottointervallo a velocita' relativa costante e li fonde con `_merge_intervals` (`:938-952`) **solo** se si toccano o
  si sovrappongono entro `TIME_EPS` = 1e-9 s (`:88-92`: "una rotta che entra in un volume sull'arco i ed esce sull'arco
  i+2 e' UNA finestra"). Due intervalli separati da un'uscita di qualunque durata maggiore di 1e-9 s restano distinti.
- Le **finestre** (`contact_windows`, `:1070`) usano gli stessi intervalli con la portata maggiore: oggi l'osservatore
  con la portata maggiore riceve gia' **due estrazioni** per un'uscita di pochi secondi (due finestre).
- `_exposure_time` (D-5, `Logic/Engagement_Resolver.py:2220-2250`) somma gli intervalli che toccano la finestra: la
  pausa fra due intervalli non entra nella permanenza (ma la somma viola la regola, FP-6).
- Il pianificatore (blocco B della D-5) unisce due tratti dello stesso volume solo se il secondo entra entro
  `CROSSING_JOIN_TOLERANCE_S` = 1e-6 s dall'uscita del primo (`Logic/Air_Route_Manager.py:35-38`, uso `:1190`): una
  tolleranza **numerica**, non di modello. Stesso comportamento: uscite brevi = attraversamenti distinti.
- Quindi con B-R un aereo che esce dal volume della ZSU per 3 s fra due bersagli vicini ha **due** passaggi (due
  estrazioni). E' la decisione aperta FP-10 (§2.11).

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

**DECISA dall'utente il 2026-11-07: B-R** (era la raccomandazione).

**Perche' non B-S1** (l'utente ha chiesto di esaminarla prima di decidere): B-S1 renderebbe la finestra davvero "per
osservatore", ma cambia il **numero e l'ordine delle finestre per tutte le coppie con portate asimmetriche** (ogni
finestra di oggi andrebbe sdoppiata per direzione, anche con un solo passaggio: 32 964 direzioni a un passaggio in
P-0), quindi l'ordine canonico, gli episodi G4a (`_episodes`), i ritagli (`_trim_busy`), il `counter` degli stream e
lo stream dell'ingaggio cambierebbero quasi ovunque e la fotografia andrebbe rifatta; in cambio **nessun beneficio
misurabile** sulla fotografia (P-0: 0 direzioni con piu' passaggi). B-R ottiene la stessa regola dentro lo strato 2
senza toccare scheduler ed episodi.

**Raccomandazione (ora decisione): B-R.** E' coerente con la decisione DW-4 della D-5 (permanenza nel risolutore dai tratti), non
tocca la struttura degli episodi e rende la regola un fatto del solo strato 2. In sessione i tratti ci sono sempre
(`all_legs`, `Session_Simulator.py:2397-2409`; P-0: `without_legs` 0 su 33 910 direzioni).
P-0 rafforza la scelta: B-R non cambia nessuna esecuzione della fotografia nemmeno con la regola accesa (nessuna
direzione multi), mentre B-S1 sdoppierebbe tutte le finestre (anche le 32 964 direzioni a un passaggio) e cambierebbe
la fotografia senza che nessuna esecuzione abbia piu' passaggi.

### 2.3 Ordine delle estrazioni nuove (FP-2)

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| O1 in linea | nello stream dell'ingaggio: per finestra, a->b passaggi 1..n, poi b->a | ordine naturale, un solo stream | ogni estrazione successiva slitta: con la regola accesa cambia quasi ogni esecuzione con almeno una direzione multi e almeno una salva, anche se l'occasione in piu' non decide nulla; il confronto con la regola accesa diventa difficile da leggere |
| O2 in coda | primo passaggio nella posizione di oggi; i passaggi dal secondo in poi dopo tutte le estrazioni di rilevamento | i rilevamenti delle altre coppie non cambiano | le estrazioni di danno slittano comunque (stesso effetto di O1 sugli esiti); codice in due giri |
| **O3 stream separato** | primo passaggio dallo stream dell'ingaggio, **nella posizione di oggi**; passaggi 2..n da `pass_rng`, nell'ordine (finestra canonica, a->b poi b->a, passaggio) | lo stream dell'ingaggio resta **identico in ogni stato dell'interruttore** (stesso numero, stesso ordine): cambia un'esecuzione solo se l'occasione in piu', la Pd del primo passaggio o la fine del candidato cambiano una decisione; precedenti nel progetto (tempra: `breakpoint_rng`; fuoco su posizione F7b) | un parametro in piu' (`pass_rng`), un `event_id` nuovo (`pass_event_id`) |

**DECISA dall'utente il 2026-11-07: O3** (era la raccomandazione).

**Raccomandazione (ora decisione): O3.** E' l'unica che soddisfa alla lettera "non cambiare l'ordine delle estrazioni" (AGENTS.md)
anche con la regola accesa, e rende il confronto leggibile: ogni esecuzione cambiata si deve alla regola, non a un
flusso spostato.

**Dopo P-0** (`extra_draws` 0): sulla fotografia attuale O1, O2 e O3 sono **equivalenti** (nessuna estrazione in piu',
nessuna esecuzione cambiata in nessuno dei tre casi), quindi l'argomento "confronto leggibile" oggi non pesa sulla
fotografia. La raccomandazione resta O3 per due motivi che P-0 non tocca: (i) la proprieta' "stream dell'ingaggio
identico in ogni stato" vale in **qualunque** sessione, comprese quelle di campagna con rientri sullo stesso sito, che
la fotografia non rappresenta; (ii) e' la proprieta' che rende verificabili S33 (test 3 di §4.2.1, `off` e `on` con le
stesse estrazioni dello stream dell'ingaggio) e il test unitario 4. Il costo di O3 rispetto a O1 (un parametro e un
`event_id` in piu') resta piccolo; O1 sarebbe un po' piu' semplice e, per i numeri di P-0, oggi non cambierebbe la
fotografia: e' un'alternativa legittima se l'utente preferisce un solo stream.

### 2.4 Distanza per passaggio (FP-4)

| Opzione | Contenuto | Contro |
|---|---|---|
| **(a) CPA del passaggio** | `closest_point_of_approach` sui tratti ritagliati al passaggio, per ogni passaggio | il primo passaggio puo' avere Pd minore di oggi (se il minimo della finestra cade in un passaggio successivo) |
| (b) distanza della finestra per tutti | come oggi | un passaggio lontano "eredita" la distanza del passaggio migliore: contro la regola |
| (c) finestra per il primo, propria per gli altri | massima continuita' col passato | incoerente: il primo passaggio usa la distanza di un altro |

**DECISA dall'utente il 2026-11-07: (a), CPA del passaggio** (era la raccomandazione).

**Raccomandazione (ora decisione): (a).** Con un solo passaggio il CPA del passaggio coincide con quello della finestra, ma il
risolutore usa comunque il percorso di oggi (nessun ricalcolo) per avere esiti identici al bit. P-0: `cpa_not_in_first`
e `first_flip_by_distance` 0 (nessuna direzione multi): le tre opzioni sono indistinguibili sulla fotografia, la scelta
conta solo in S33 e nelle sessioni future.

### 2.5 Finestra d'ingaggio per passaggio (FP-3)

| Opzione | Candidato di un passaggio valido fino a | Effetto |
|---|---|---|
| **(a) fine del passaggio** | `hi` del passaggio (al piu' `window.t_end`), anche con un solo passaggio | all'uscita dal volume proprio la traccia e' persa: niente salve nuove dopo l'uscita; al rientro serve un nuovo rilevamento (nuovo passaggio = nuova estrazione). Cambia anche le direzioni a **un** passaggio dell'osservatore con portata minore quando l'arma tira oltre la portata del sensore o senza `max_range` (contatore `AFTER_PASS` di P-0) |
| (b) inizio del passaggio successivo | `lo` del passaggio successivo; l'ultimo fino a `window.t_end` | niente traccia mantenuta da un passaggio all'altro, ma la traccia resta valida **fuori** dal volume fino al rientro; con un solo passaggio identico a oggi |
| (c) fine della finestra | `window.t_end` per tutti | ogni passaggio aggiunge solo occasioni: il rilevamento del primo continua a far sparare nel secondo (traccia mantenuta), contro "la sua finestra d'ingaggio" |

**DECISA dall'utente il 2026-11-07: (a).** Motivo dell'utente: all'uscita dal volume proprio la traccia e' persa; al
rientro serve una nuova acquisizione. Il candidato al tiro (occasione di tiro dell'osservatore contro il bersaglio)
vale quindi fino alla **fine del passaggio**, non fino all'inizio del passaggio successivo ne' fino alla fine della
finestra.

**Perche' (b) e' scartata.** La (b), raccomandata nella prima stesura, lascia la traccia valida anche fuori dal volume
del sensore (fino al rientro, o fino alla fine della finestra dopo l'ultimo passaggio): non rispetta la regola "traccia
persa all'uscita". Era motivata solo dalla **compatibilita' con la fotografia** (nessuna esecuzione cambiata a
interruttore acceso), non dalla fedelta' del modello: un argomento di confronto, non di modello.

**Applicazione** (vincolante per il piano, §4.1.1):
- **tutte le direzioni con passaggi calcolabili**, anche con un passaggio solo (applicarla solo ai passaggi multipli
  sarebbe incoerente: la stessa uscita dal volume perderebbe o no la traccia a seconda che ci sia un rientro);
- osservatore con la portata **maggiore** (o uguale, o l'altro senza sensore): il passaggio coincide con la finestra,
  quindi la fine resta `window.t_end` (invariato; il piano non ricalcola nulla per lui, per evitare differenze
  numeriche fra i tratti dello scheduler e del risolutore);
- **senza tratti** (chiamate dirette): passaggi non calcolabili, resta `window.t_end` come oggi;
- passaggio **ritagliato** dalla finestra (G4a, decollo/atterraggio): termina al massimo a `window.t_end` (`hi`);
- il candidato e' ammesso solo se `t_ready <= hi` (reazione completata prima dell'uscita);
- una salva **gia' lanciata** prima dell'uscita non cambia (la fine del candidato limita solo l'istante di lancio:
  `Logic/Engagement_Resolver.py:2475`, `:2928`, `:3057`, e la ricerca dell'ingresso in portata, `:3004-3008`
  [V]); si interrompe solo il lancio di salve **nuove** dopo l'uscita.

**Numeri di P-0** (§1.8): `salvos_after_next_pass_start` e `salvos_between_passes` 0 (nessuna direzione multi). Con
(a), nelle direzioni a **un** passaggio, 151 salve in **44 esecuzioni della fotografia** partono oggi dopo la fine
dell'unico passaggio di un osservatore con portata minore (S26-BINGO 32 esecuzioni e 121 salve, S21 6 e 19, S13 2 e 6,
S14 1 e 2, S28-CLASS 2 e 2, S24-ORBIT 1 e 1): con la regola **accesa** sono queste (al piu') le esecuzioni che cambiano
(~4 % della fotografia, concentrate su S26-BINGO); con la regola **spenta** nessuna. Quali armi sparano oltre la portata
del sensore e' un dato non raccolto da P-0: si legge sulle cambiate di P-1 (§4.3).

### 2.6 Istante di rilevamento per la regola R-INT (FP-5) — SOSPESA (2026-11-07)

**Stato: SOSPESA** in attesa di `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` (regola nuova dell'utente sui colpi
che una difesa aerea puo' considerare bersagli). Non e' decisa: le opzioni sotto restano tutte aperte.
**Ordine deciso dall'utente il 2026-11-07 (BI-11 della Proposta BI)**: prima si esegue la Proposta BI, poi FP-5 viene
riproposta illustrando in dettaglio e con esempi le scelte possibili.

**Ruoli nella regola R-INT** (chi fa cosa; esempio di §1.4 adattato):

| Ruolo | Chi, nell'esempio | Che cosa conta per R-INT |
|---|---|---|
| lanciatore | l'A-10C | il suo istante di lancio `t_launch` e la sua posizione a quell'istante (L1) |
| bersaglio del rilevamento | lo stesso A-10C, visto dall'intercettore | i `Detection` dell'intercettore sull'A-10C: se uno e' <= `t_launch` il lancio e' "visto" |
| intercettore | un SAM della forza attaccata con arma `Anti_Missile` (es. Tor, 9M331) | ferma il colpo solo se t_traccia + tau <= t_impatto (`Logic/Engagement_Resolver.py:3250-3274`) |
| osservatore | lo stesso SAM (il rilevamento e' **per asset**, non per forza: `_detection_time_of`, `:3187-3193`) | i suoi passaggi nel proprio volume, i suoi rilevamenti |
| colpo da intercettare | il missile M lanciato dall'A-10C contro un'unita' U | e' "intercettabile" solo se `ShotSpec.interceptable` (oggi: ogni missile e le bombe guidate, `Logic/Fire_Control.py:763-768`) |
| bersaglio dell'attacco | l'unita' U (es. un BMP-2 della stessa forza del SAM) | la sua posizione all'impatto e' la fine della traiettoria rettilinea del colpo (`_round_track_time`, `:3212-3248`) |

Regola L1 (precedente, invariata): un colpo lanciato **dentro** il volume d'intercettazione V_I dell'intercettore non si
intercetta mai (`_may_intercept`, `:3162-3185`): il lanciatore e' un bersaglio, non si inseguono i suoi colpi.
**Attenzione all'esempio con la ZSU** [V]: la ZSU-57-2 di S32/S33 **non** e' un intercettore (il suo S-68-57mm non ha il
task `Anti_Missile`, `Proposta_Dati_Anti_Missile.md` §1, regola D in `Asset/Mobile.py:1112-1117`): per lei R-INT non si
applica mai. Nell'esempio l'intercettore e' quindi un SAM con arma `Anti_Missile`; S33-PASSES, che usa la ZSU, **non**
puo' provare FP-5 in sessione.

| Opzione | Contenuto |
|---|---|
| (a) il primo istante con la regola accesa | "l'intercettore aveva gia' rilevato il lanciatore al lancio" = esiste un rilevamento <= `t_launch`; spento: l'ultimo in ordine di lista, come oggi |
| (b) invariato | con la regola accesa un rilevamento del secondo passaggio sostituisce quello del primo: un lancio nel primo passaggio diventa "non visto" (regressione introdotta dalla regola) |
| (c) correzione separata | difetto latente corretto in un'altra Proposta con un suo interruttore |
| (d) **legata al passaggio** (nuova, 2026-11-07, proposta dalla sessione principale) | il lancio e' "visto" solo se l'intercettore ha rilevato il lanciatore **nel passaggio che contiene `t_launch`** (rilevamento <= `t_launch` dentro lo stesso passaggio `[inizio, fine]` del lanciatore nel volume proprio dell'intercettore). Motivo: con FP-3 = (a), decisa, la traccia e' persa all'uscita dal volume; un rilevamento di un passaggio **precedente** non dovrebbe far "vedere il lancio". Lancio fuori da ogni passaggio: non visto (percorso geometrico, tau = `total`) |

**Esempio** (passaggi dell'A-10C nel volume proprio del SAM [200, 254] s e [380, 434] s; rilevamenti a **210** s nel
primo e a **390** s nel secondo; lancio a **300** s, fra i due passaggi, con l'A-10C fuori dal volume del SAM):

| Opzione | Rilevamento usato | Lancio a 300 s | Lancio a 385 s (secondo passaggio, prima del rilevamento a 390) | Lancio a 400 s |
|---|---|---|---|---|
| oggi / (b) | l'ultimo in lista: 390 | non visto (390 > 300) | non visto | visto |
| (a) | il primo: 210 | **visto** (210 <= 300), anche se la traccia e' persa dal 254 | visto (210) | visto |
| (d) | quello del passaggio che contiene il lancio | **non visto** (nessun passaggio contiene 300) | non visto (nel secondo passaggio il rilevamento e' a 390 > 385) | visto (390 <= 400, stesso passaggio) |

"Non visto" non vuol dire "non intercettato": l'intercettore scopre il colpo dalla geometria quando entra nel suo
raggio aereo e reagisce con tau = `total` (RIV+VAL+COM+ATT) invece di `refire_interval`; fallisce solo se il tempo non
basta prima dell'impatto.

**Nota (2026-11-07): la regola nuova sugli A2G potrebbe rendere FP-5 marginale.** Con la regola dell'utente in
`Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` i missili aria-superficie dei cacciabombardieri (Maverick & C.) non
sono piu' bersagli delle difese **terrestri**: R-INT resterebbe in uso solo per cruise/balistici e, contro le difese
navali, per gli antinave. Il caso "aereo che entra ed esce dal volume di un SAM terrestre e lancia fra due passaggi"
non produrrebbe piu' intercettazioni, quindi la scelta fra (a), (b), (c) e (d) conterebbe solo per lanciatori di
cruise/antinave che rientrano nel volume dell'intercettore, caso non presente nella fotografia (P-0:
`rint_last_not_earliest` 0). Per questo FP-5 e' sospesa: si decide dopo la Proposta nuova.

**Raccomandazione della prima stesura, scritta prima dell'opzione (d) e della sospensione: (a)**: corregge il difetto
proprio dove la regola lo renderebbe frequente; cambierebbe anche coppie a
piu' finestre, ma solo con l'interruttore acceso. P-0: `rint_last_not_earliest` 0, nessuna esecuzione `RINT`: nella
fotografia il difetto non si manifesta mai, quindi (a), (b) e (c) sono indistinguibili sul confronto; (a) resta la
scelta piu' economica (una funzione, coperta dal test unitario 13) e protegge S33 e le sessioni future con rientri.
Con FP-3 = (a) decisa, pero', (a) fa "vedere" lanci avvenuti dopo la perdita della traccia (esempio sopra, lancio a
300 s): la (d) e' la coerente con FP-3 (a), al costo di cercare il passaggio che contiene `t_launch` (i passaggi sono
gia' calcolati dalla regola, B-R). Da rivalutare alla ripresa di FP-5; il piano di §4 implementa ancora (a) e va
aggiornato se l'utente sceglie (d).

### 2.7 Interazione con la D-5 (FP-6)

- Con **FP acceso**, ogni occasione ha la permanenza **del suo passaggio** (`min(end, t_end) - start`, non tagliata
  all'inizio della finestra come in DW-4): la somma sparisce, **la B assorbe la A**.
- Con **FP spento e D-5 acceso** resta un'estrazione per finestra: la permanenza va comunque presa da **un**
  passaggio. Raccomandazione: **il passaggio che contiene `t_cpa`** della finestra (quello la cui distanza entra nella
  Pd), in subordine il piu' lungo. E' la (A) di §2.1, **dentro** l'interruttore della D-5: nessun interruttore nuovo,
  perche' la D-5 e' spenta e nessuna esecuzione della fotografia la accende; le 20 esecuzioni di S32 (un solo
  passaggio della ZSU e del P-18) restano uguali (verifica in §4.1.6). P-0 lo conferma sui dati: nelle 20 esecuzioni
  di S32-DWELL nessuna direzione ha piu' di un passaggio (`multi` 0 su tutte le 1029), quindi la permanenza "del
  passaggio che contiene `t_cpa`" coincide con la somma di oggi. Anche FP-6, come FP-3/4/5, si vede solo in S33
  (variante `dwell_off`).
- Alternativa: lasciare la somma con FP spento (la D-5 violerebbe la regola finche' FP non e' acceso). Non raccomandata.

### 2.8 Interruttore (FP-7)

| Opzione | Contenuto |
|---|---|
| **(a)** `Engagement_Resolver.FP_PER_PASS_DETECTION = False`, letto da `Session_Simulator.engage` che passa `pass_rng` solo se acceso; nel risolutore la regola e' attiva se e solo se `pass_rng` non e' None | stesso schema della D-5 (lettore passato solo se acceso): a interruttore spento la chiamata a `resolve_engagement` e' **letteralmente** quella di prima |
| (b) costante letta dentro `_detect_direction` | agisce anche sulle chiamate dirette; serve comunque uno stream per O3 |
| (c) in `Session_Simulator` come gli F*/G* | il risolutore non lo vede senza importare l'orchestratore |

**Raccomandazione (a), spento.** L'accensione si decide dopo la sonda P-1, non in questo piano; la fotografia **non** si
reinstalla senza decisione esplicita dell'utente.

P-0 rende l'esito di P-1 prevedibile: con FP-3 (a) decisa, accendere l'interruttore cambia **al piu' le 44
esecuzioni `AFTER_PASS`** della fotografia (salve dopo la fine dell'unico passaggio, §1.8, §2.5); le altre 965 e le 20
di S32 restano identiche (S32 non ha salve `AFTER_PASS`). Una futura accensione del default richiederebbe quindi una
fotografia nuova per quelle esecuzioni, su decisione esplicita dell'utente dopo la lettura delle cambiate di P-1 (le
varianti di S33 fissano l'interruttore con `patch.object` e non dipendono dal default). Il default resta spento in
questo piano per la regola di progetto (ogni regola nuova dietro un interruttore che riproduce il comportamento
precedente).

### 2.9 Scenario (FP-8)

| Opzione | Contenuto |
|---|---|
| **(a) S33-PASSES, 8 varianti x 5 semi = 40** | geometria di **rientro**: `off`, `on`, `dwell_off` (D-5 acceso, FP spento, dwell di test 600 s sulla ZSU), `dwell_on` (entrambi accesi); geometria **CAS** (richiesta dell'utente del 2026-11-07): `cas_off`, `cas_on`, `cas_dwell_off`, `cas_dwell_on`, stessi interruttori |
| (b) 2 varianti x 5 semi = 10 | solo `off`/`on`: non prova FP-6 in sessione |

**Raccomandazione (a).**
- Geometria di **rientro**: S32 (ZSU in (1000, -300), 3 BMP-2, 4 A-10C a 3000 m) con rotta di andata, uscita a 14 km e
  ritorno sulla linea: due passaggi nei 6 km della ZSU, sempre entro gli 80 km dell'A-10C (una finestra).
- Geometria **CAS** (caso operativo d'appoggio ravvicinato): gli stessi 4 A-10C attaccano in sequenza **3 bersagli a
  terra** lungo la rotta, due dentro la copertura visiva della ZSU (6 km) e uno fuori: punto sopra il primo bersaglio
  (dentro), proseguimento fino al secondo (fuori, 13 km dalla ZSU), virata e ritorno sopra il terzo (dentro), uscita.
  Per tutto l'attacco gli A-10C restano entro gli 80 km del proprio sensore (distanza massima 41 km alla partenza):
  **una** finestra per coppia A-10C/ZSU, **due passaggi non contigui** nel volume della ZSU (separati da ~104 s). E' la
  forma che il DES sa rappresentare (rotta a punti, §1.10): un tratto rettilineo unico non darebbe due passaggi.
  Dettagli in §4.2.1.

P-0 rafforza la (a): nessuna esecuzione esistente ha una direzione a piu' passaggi, quindi S33 e' l'**unico** banco di
prova in sessione della regola (FP-2/3/4/5 in `on`/`cas_on`, FP-6 in `dwell_*`/`cas_dwell_*`). Con la (b) FP-6 non
sarebbe provata in nessuna sessione. Le due geometrie si completano: il rientro e' il caso "torna sullo stesso
sito", la CAS il caso "attacco a piu' bersagli con un bersaglio fuori dal volume", con passaggi di durata diversa
(~50-54 s e ~61-67 s) [V: calcolo sui tratti, §4.2.1].

### 2.10 Pianificatore (FP-9)

`Path.compute_detection_metrics` (blocco B della D-5) da' la Pd **per attraversamento** e `max_detection_probability`
= massimo sui tratti. Con la regola accesa il DES da' un'occasione per attraversamento, quindi la probabilita' di
essere rilevati almeno una volta su due attraversamenti a 0,4 e' 1 - 0,6^2 = 0,64 contro 0,4 della metrica. Ma
anche oggi due attraversamenti dello stesso volume dell'osservatore con portata maggiore sono due finestre: la
divergenza esiste gia'. **Raccomandazione: nessun cambio**, limite dichiarato; una metrica cumulativa
(`cumulative_detection_probability`) e' un'estensione futura. P-0 non tocca questa decisione (misura il DES, non il
pianificatore); nelle esecuzioni della fotografia il caso "piu' attraversamenti dentro una finestra" non si presenta.

### 2.11 Passaggi molto ravvicinati: tolleranza di unione (FP-10)

Con B-R (FP-1) i passaggi sono gli intervalli di `range_intervals` con la portata propria, fusi solo entro `TIME_EPS`
(§1.11). Un A-10C che fra due bersagli vicini esce dal volume della ZSU per pochi secondi ha quindi **due** passaggi,
due estrazioni. Stesso limite del blocco B della D-5 nel pianificatore (`CROSSING_JOIN_TOLERANCE_S` = 1e-6 s,
numerica) e delle finestre di oggi per l'osservatore con la portata maggiore.

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| **(a) nessuna tolleranza di modello** | passaggi distinti se separati da piu' di `TIME_EPS` (come oggi `range_intervals`) | coerente con finestre di oggi e pianificatore (stessa regola in DES e metriche); nessuna costante inventata; nessun codice in piu' | un'uscita di pochi secondi raddoppia l'occasione: per traiettorie sul bordo del volume la Pd cumulativa e' sovrastimata |
| (b) tolleranza fissa nel risolutore | `FP_PASS_JOIN_GAP_S` = X s [S, stima]: passaggi separati da un'uscita < X si uniscono (una estrazione, CPA del passaggio unito, permanenza = dall'inizio del primo alla fine dell'ultimo) | toglie le occasioni "artificiali" sul bordo | costante di modello **senza dato** (va dichiarata stima); incoerente con le finestre (che restano due per l'osservatore con la portata maggiore) e con il pianificatore, se non si cambiano anche loro; un parametro in piu' sotto l'interruttore |
| (c) tolleranza legata al sensore | unione se la pausa e' minore di un tempo di "memoria della traccia" del sensore (per i radar con `dwell_time_s` il periodo di rivisita; per il visivo un valore da registro) | fisicamente piu' motivata (il sensore non "perde" il bersaglio fra due rivisite) | richiede un dato che il registro non ha per i sensori non EWR (DW-9: valori solo ai 10 EWR); di fatto rimanda a una ricerca di dati |
| (d) come (b), applicata anche a finestre e pianificatore | stessa X per `contact_windows`, `_own_passes` e `CROSSING_JOIN_TOLERANCE_S` | regola unica ovunque | cambia le finestre di tutte le coppie: fotografia da rifare; fuori dal perimetro di questa Proposta |

**Esempio numerico** (portata propria 6 km, fattore 1): passaggi [200, 254] s e [257, 300] s (uscita di 3 s), distanze
minime 5,5 km e 5,0 km.
- (a): due estrazioni, Pd 1 - 0,5 * (5,5/6)^4 = **0,647** e 1 - 0,5 * (5,0/6)^4 = **0,759**; almeno un rilevamento
  1 - 0,353 * 0,241 = **0,915**.
- (b) o (d) con X = 10 s [S]: un passaggio [200, 300], distanza minima 5,0 km: Pd **0,759**, una estrazione.
- Con un'uscita di 104 s (variante CAS di S33) (b) con X = 10 s non unisce: due estrazioni come in (a).

**Raccomandazione (a)**, senza interruttore aggiuntivo: e' il comportamento di oggi per finestre e pianificatore,
non introduce costanti senza dato e il caso non compare nella fotografia (P-0: 0 direzioni multi). Il limite si
dichiara (§5.2). Se in futuro servisse, la strada coerente e' (c) con dati di sensore, oppure (d) in una Proposta
dedicata. Sonda possibile prima di decidere (facoltativa, non nel piano): contare nella fotografia le coppie con due
finestre separate da meno di X secondi (misura quanto la stessa regola "uscita breve = nuova occasione" pesa gia' oggi).

### 2.12 Effetti delle decisioni e raccomandazioni (B-R, O3, FP-3 (a), FP-4 (a), FP-10 (a)) sugli altri pezzi [V sul codice letto]

| Pezzo | Effetto |
|---|---|
| `ContactWindow`, `contact_windows`, `_pair_windows`, `trim_contact_window`, `schedule_contacts` | **invariati** |
| `t_mutual_*` | invariati; usati solo dai ripieghi senza tratti |
| ordine canonico delle finestre, stream dell'ingaggio | invariati (numero e ordine delle estrazioni identici in ogni stato) |
| stream nuovo `pass_rng` | ordine: finestra canonica, a->b poi b->a, passaggio 2..n |
| `t_end` del candidato | fine del passaggio (FP-3 (a)) per l'osservatore con portata minore, anche a un passaggio; `window.t_end` per l'osservatore con portata maggiore e senza tratti |
| `distance_cpa` | per passaggio in `Detection` e `_Candidate` (FP-4) |
| `first_detector` | non letto dal risolutore: invariato |
| RWR | una percezione per passaggio rilevato (`rwr_class` accumula `(istante, classe)`, `_air_threat` filtra per istante) |
| percezione/identificazione (`seen_by`, `identified_by`) | minimo degli istanti: un rilevamento del secondo passaggio conta solo se e' il primo |
| R-INT | primo istante con la regola accesa (FP-5) |
| eventi di danno | estrazioni di danno nello stream dell'ingaggio, invariate se le salve sono le stesse; cambiano dove cambiano i lanci |
| episodi G4a/G4b, `busy_until`, `covered`, `counter` | invariati (finestre invariate) |
| `Detection` | 4 campi nuovi a `None` di default (`pass_index`, `pass_count`, `pass_start`, `pass_end`), valorizzati solo nelle direzioni multi con la regola accesa |
| pianificatore, `Weapon_Delivery`, adapter DCS | invariati |
| tolleranza di unione dei passaggi (FP-10 (a)) | nessuna oltre `TIME_EPS`: `_own_passes` usa gli intervalli di `range_intervals` come sono |

---

## 3. Decisioni per l'utente (una per volta)

Stato al 2026-11-07: **FP-1 DECISA** (B-R); **FP-2 DECISA** (O3); **FP-3 DECISA** ((a)); **FP-4 DECISA** ((a));
**FP-5 SOSPESA** (in attesa di `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`); **FP-6..FP-10 aperte**.
Premessa comune dalla sonda P-0 (§1.8): nessuna esecuzione della fotografia ha direzioni a piu' passaggi, quindi FP-1
(B-R), FP-2, FP-4, FP-5, FP-6, FP-9 e FP-10 non cambiano la fotografia in nessuna opzione raccomandata ne' alternativa
(salvo B-S1, che sdoppia le finestre; B-S2 non e' valutata in dettaglio [I]; FP-10 (d), che cambia le finestre).
L'unica scelta con impatto sulla fotografia a interruttore acceso e' FP-3 (a), decisa: al piu' 44 esecuzioni. Le
decisioni si giudicano sulla correttezza del modello e su S33, non sul confronto.

**FP-1 — Dove si calcolano i passaggi. DECISA dall'utente il 2026-11-07: B-R, nel risolutore** dai tratti (era la
raccomandazione; l'utente ha chiesto prima l'esame di B-S1, motivi del no in §2.2).
Esempio: un A-10C nella stessa finestra [0, 700] s con la ZSU entra nei suoi 6 km in [200, 254] e [380, 434]. B-S1
farebbe tre finestre (A-10C -> ZSU [0, 700]; ZSU -> A-10C [200, 254] e [380, 434]) e cambierebbe gli episodi; B-R
lascia la finestra [0, 700] e da' alla ZSU due estrazioni dentro la stessa finestra.

**FP-2 — Ordine delle estrazioni. DECISA dall'utente il 2026-11-07: O3, stream separato** (`pass_rng`) per i
passaggi dal secondo in poi (era la raccomandazione).
Esempio: stream dell'ingaggio 0,31 / 0,72 / 0,05 ... Oggi 0,31 va alla ZSU, 0,72 all'A-10C. Con O1 il secondo
passaggio della ZSU prende 0,72, l'A-10C prende 0,05 e tutto il resto slitta. Con O3 la ZSU ha ancora 0,31 nel primo
passaggio, l'A-10C ancora 0,72, e il secondo passaggio prende il primo numero dello stream `pass_event_id`.
P-0: `extra_draws` 0, sulla fotografia O1/O2/O3 sono equivalenti; O3 resta raccomandata per le sessioni con rientri e
per la verificabilita' di S33 (§2.3), O1 e' l'alternativa piu' semplice.

**FP-3 — Finestra d'ingaggio per passaggio. DECISA dall'utente il 2026-11-07: (a), fino alla fine del passaggio**
(traccia persa all'uscita dal volume proprio; al rientro serve un nuovo rilevamento), per tutte le direzioni con
passaggi calcolabili, anche a un passaggio; osservatore con la portata maggiore e chiamate senza tratti invariati
(`window.t_end`). La raccomandazione iniziale era (b), motivata solo dalla compatibilita' con la fotografia (§2.5).
Esempio: passaggi [200, 254] e [380, 434], fine finestra 700, ZSU che rileva a 205 con reazione 8 s (t_ready 213).
**(a) candidato fino a 254**; (b) fino a 380; (c), cioe' oggi, fino a 700. Con t_ready 260 (reazione di 55 s) il primo
passaggio non da' candidato in (a): la ZSU spara solo se rileva nel secondo passaggio. P-0: con la regola accesa (a)
cambia fino a 44 esecuzioni della fotografia (151 salve dopo l'unico passaggio, 32 esecuzioni su 44 in S26-BINGO);
spenta, nessuna.

**FP-4 — Distanza per passaggio. DECISA dall'utente il 2026-11-07: (a), CPA del passaggio** (era la
raccomandazione).
Esempio (§1.4): 5,5 km e 3,3 km. (a): Pd 0,647 e 0,954. (b): 0,954 e 0,954 (il passaggio lontano eredita la distanza
del vicino). (c): 0,954 nel primo (distanza del secondo), 0,954 nel secondo.

**FP-5 — Istante di rilevamento per R-INT. SOSPESA (2026-11-07)** in attesa di
`Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`: non decisa, opzioni (a), (b), (c) e la nuova (d) aperte (§2.6).
Ruoli (tabella completa in §2.6): l'A-10C e' **lanciatore** e **bersaglio del rilevamento**; il SAM (con arma
`Anti_Missile`, es. Tor: la ZSU-57-2 non intercetta, regola D) e' **intercettore** e **osservatore**; il missile M
lanciato contro un'unita' U e' il **colpo da intercettare**; L1: un lancio dentro V_I non si intercetta mai.
Esempio: il SAM rileva l'A-10C a 210 s (primo passaggio, [200, 254]) e a 390 s (secondo, [380, 434]); l'A-10C lancia
a 300 s, fra i due passaggi. Oggi (ultimo) vale 390 > 300: lancio "non visto", tempo di reazione pieno (`total`)
invece di `refire_interval`, e l'intercettazione puo' fallire. Con (a) vale 210 <= 300: lancio visto, anche se con
FP-3 (a) la traccia e' persa dal 254. Con (d) (legata al passaggio) nessun passaggio contiene 300: lancio non visto;
un lancio a 400 s sarebbe visto (rilevamento a 390 nello stesso passaggio). P-0: il difetto non si manifesta in
nessuna esecuzione della fotografia (`rint_last_not_earliest` 0), quindi nessuna opzione cambia il confronto. La
regola nuova sugli A2G (missili aria-superficie dei cacciabombardieri non piu' bersagli delle difese terrestri)
potrebbe rendere FP-5 marginale: R-INT resterebbe per cruise/balistici e per gli antinave contro le difese navali.

**FP-6 — D-5 senza FP.** Raccomandazione: **permanenza del passaggio che contiene `t_cpa`** (mai la somma), senza
interruttore nuovo. Esempio: dwell di test 600 s, passaggi di 54 s e 54 s. Oggi: g = 108/600 = 0,18 su un'estrazione.
FP spento con la raccomandazione: g = 54/600 = 0,09 su un'estrazione. FP acceso: g = 0,09 su ciascuna di due
estrazioni (almeno un rilevamento a distanza nulla: 1 - 0,91^2 = 0,172).

**FP-7 — Interruttore.** Raccomandazione: **`Engagement_Resolver.FP_PER_PASS_DETECTION = False`**, `pass_rng` passato
da `Session_Simulator` solo se acceso. Esempio di lettura: spento, `resolve_engagement` riceve gli stessi argomenti di
oggi (verificato dal test di §4.1.5 punto 15) e la fotografia resta 1009 identiche; acceso (sonda P-1), cambiano al
piu' le esecuzioni elencate `MULTI`/`RINT`/`AFTER_PASS` dalla sonda P-0: `MULTI` e `RINT` sono vuoti, `AFTER_PASS` ne
ha 44 (FP-3 (a)), quindi **al piu' 44 cambiate**, le altre 965 identiche (§2.8, §4.3).

**FP-8 — Scenario.** Raccomandazione: **S33-PASSES, 8 varianti x 5 semi = 40 esecuzioni nuove**: 4 con la geometria di
rientro (`off`, `on`, `dwell_off`, `dwell_on`) e 4 con la geometria CAS chiesta dall'utente (`cas_off`, `cas_on`,
`cas_dwell_off`, `cas_dwell_on`: 3 bersagli a terra in sequenza, 2 dentro i 6 km della ZSU e 1 fuori) (circa due
minuti di suite in piu' [I]). Esempio: per ogni seme la ZSU ha 4 estrazioni (una per A-10C) in `off`/`cas_off` e 8
(due per A-10C) in `on`/`cas_on`; la seconda di ogni A-10C viene dallo stream separato `pass_rng`, la prima ha lo
stesso numero di oggi. P-0: S33 sara' l'unico scenario in cui la regola agisce (nessuna direzione multi altrove).

**FP-9 — Pianificatore.** Raccomandazione: **nessun cambio**, limite dichiarato. Esempio: due attraversamenti a Pd 0,4:
metrica 0,4, DES con la regola 0,64.

**FP-10 — Tolleranza di unione dei passaggi ravvicinati (nuova, 2026-11-07).** Raccomandazione: **(a), nessuna
tolleranza di modello**: passaggi distinti se separati da piu' di `TIME_EPS` (1e-9 s), come oggi le finestre e gli
attraversamenti del pianificatore (§1.11, §2.11). Esempio: un A-10C esce dal volume della ZSU per 3 s fra due
bersagli vicini, distanze minime 5,5 e 5,0 km su 6 km. (a): due estrazioni, Pd 0,647 e 0,759, almeno un rilevamento
0,915. (b) con una tolleranza stimata di 10 s: un passaggio, Pd 0,759. (c): tolleranza = memoria della traccia del
sensore, dato oggi assente per il visivo. (d): stessa tolleranza anche per finestre e pianificatore, fotografia da
rifare. Il piano di §4 implementa (a) (nessun codice in piu'); con (b)/(c) va aggiornato prima dell'esecuzione.

---

## 4. Piano di intervento (FP-1 decisa = B-R; FP-2 decisa = O3; FP-3 decisa = (a); raccomandazioni FP-4..FP-10)

Se l'utente sceglie diversamente anche su una sola decisione, questo piano va aggiornato da chi pianifica **prima**
dell'esecuzione.

### 4.0 Precondizioni (l'esecutore le verifica e si ferma se mancano)

1. Branch dedicato creato dalla sessione principale; `git status` pulito (come BI §5.0.1 e VA §4.0.1).
2. Il blocco B della D-5 e' committato (`git log` mostra il commit; `git status` pulito su
   `Logic/Air_Route_Manager.py`, `Test/Test_Air_Route_Manager.py`, `Test/Test_Threat_AA_Factory.py`).
3. Base: suite `Ran 4795 tests`, `OK (skipped=7)` [V: `.ai-run/suite.log` del 2026-11-06 su osboxes, working tree con
   il blocco B]; confronto `compared 1029 runs: 20 difference lines` (20 NEW di S32-DWELL) [V:
   `.ai-run/confronto.log`].
4. La sonda P-0 e' stata eseguita (§1.8: fatto il 2026-11-07, numeri registrati), le decisioni FP-1..FP-10 sono
   prese (al 2026-11-07: FP-1, FP-2 e FP-3 decise, FP-4..FP-10 ancora aperte).
5. Copia della cattura di P-0 conservata: `.ai-run/sonde_passaggi/p0/capture.json` (serve alla verifica di S32 in
   §4.1.6) [V: presente sul ProArt il 2026-11-07, ~13,5 MB]. `.ai-run/` e' fuori dal versionamento (`.gitignore:37`):
   se l'esecutore lavora su un'altra macchina (osboxes) il file non c'e'; in quel caso si ferma e lo dice (la sessione
   principale lo copia o riesegue P-0 su quella macchina, ~20 minuti [S]).

### 4.1 Blocco 1 — risolutore e orchestratore

#### 4.1.1 `Logic/Engagement_Resolver.py`

1. **Import** (`:463-470`): aggiungere `clamp_legs` e `closest_point_of_approach` all'import da `Contact_Scheduler`
   (ordine alfabetico come oggi).
2. **Interruttore**, in coda, nell'ordine di esecuzione (BI, poi VA, poi FP), come dice la tabella di coordinamento di BI §6.1 (non subito dopo `D5_DWELL_TIME = False`, `:525`); testo esatto:

```python
# Rilevamento per passaggio nella portata propria (Proposta_Finestre_Per_Passaggio_Portata_Propria.md), interruttore
# dedicato:
#   * `FP_PER_PASS_DETECTION` (SPENTO): un'occasione di rilevamento per OGNI passaggio del bersaglio nel volume PROPRIO
#     dell'osservatore dentro una finestra di contatto (prima: una sola estrazione per finestra e direzione, con la
#     distanza minima dell'intera finestra). Lo legge Session_Simulator, che passa al risolutore lo stream separato
#     `pass_rng` solo se acceso. Spento: chiamata e comportamento di prima. Acceso: lo stream `rng` non cambia (stesse
#     estrazioni, stesso ordine); le estrazioni dei passaggi dal secondo in poi vengono da `pass_rng`; il candidato al
#     tiro dell'osservatore con la portata minore vale fino alla fine del passaggio (traccia persa all'uscita).
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
        candidate_end = window.t_end

        if self.pass_rng is not None:
            # FP (FP_PER_PASS_DETECTION, v. docstring del modulo): con >= 2 passaggi nel volume proprio dentro la
            # finestra, un'estrazione per passaggio. Con 0 o 1 passaggio, o senza tratti, l'estrazione di prima.
            passes = self._own_passes(window, observer.id, target.id, own_range)

            if passes is not None and len(passes) >= 2:
                self._detect_passes(window, observer, target, own_range, factor, passes)
                return

            # FP-3 (a): all'uscita dal volume proprio la traccia e' persa. Con un passaggio solo, per l'osservatore con
            # la portata MINORE, il candidato al tiro vale fino alla fine del passaggio (ritagliata alla finestra).
            # Portata maggiore o uguale (il passaggio coincide con la finestra) o senza tratti: fine della finestra.
            inner = other_range is not None and other_range > 0 and own_range < other_range

            if inner and passes:
                candidate_end = passes[0][1]
```

   Nel resto del metodo cambiano **solo due righe** del ramo `if detected:` (`:2134-2137`): la condizione
   `if t_ready <= window.t_end + TIME_EPS:` diventa `if t_ready <= candidate_end + TIME_EPS:` e l'argomento
   `t_end=window.t_end` di `_Candidate` diventa `t_end=candidate_end`. A interruttore spento (`pass_rng` None)
   `candidate_end` e' lo stesso oggetto `window.t_end`: stessi valori di prima. Nessuna estrazione nuova in questo ramo; la `Detection` di una direzione a un
   passaggio resta quella di prima (campi `pass_*` None).
7. **Metodi nuovi** di `_EngagementRun`, dopo `_exposure_time` (`:2250`), testo esatto del corpo:

```python
    def _own_intervals(self, observer_id: str, target_id: str, own_range: float,
                       radius: Optional[float] = None) -> Optional[List[Tuple[float, float]]]:
        """Intervalli in cui il bersaglio e' nel volume di rilevamento PROPRIO dell'osservatore: oggi la sfera di
        raggio `own_range`, o di raggio `radius` (raggio estratto, per l'istante di rilevamento) se dato. None senza
        i tratti di entrambi. UNICO punto di chiamata del volume proprio nel risolutore (decisione VA-6 (a),
        Proposta_Allineamento_Volumi_DES_Pianificatore.md §2.3): un volume di rilevamento diverso dalla sfera si
        sostituisce qui, senza toccare la logica dei passaggi; dovra' restare contenuto nella sfera di raggio
        `own_range` (le finestre dello scheduler sono costruite su quella) e ridursi per omotetia di fattore
        `radius / own_range` al posto del raggio estratto. Nessuna estrazione."""
        legs_observer = self.legs.get(observer_id)
        legs_target = self.legs.get(target_id)

        if not (legs_observer and legs_target):
            return None

        return range_intervals(legs_observer, legs_target, own_range if radius is None else radius)

    def _own_passes(self, window, observer_id: str, target_id: str,
                    own_range: float) -> Optional[List[Tuple[float, float, float, float]]]:
        """Passaggi del bersaglio nel volume PROPRIO dell'osservatore dentro la finestra (FP), in ordine di tempo.

        Ogni passaggio e' `(lo, hi, start, end)`: `(start, end)` e' un intervallo di `range_intervals` con la portata
        propria che tocca la finestra (stesso criterio di `_exposure_time`), `[lo, hi]` lo stesso ritagliato alla
        finestra. None senza i tratti di entrambi (chiamate dirette): il chiamante usa l'estrazione unica di prima.
        Nessuna estrazione.
        """
        intervals = self._own_intervals(observer_id, target_id, own_range)

        if intervals is None:
            return None

        passes = []

        for start, end in intervals:
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

    def _pass_detection_time(self, observer_id: str, target_id: str, own_range: float, lo: float, hi: float,
                             radius: float, t_cpa: float) -> float:
        """Istante del rilevamento dentro il passaggio `[lo, hi]`: primo istante in cui la distanza scende sotto il
        raggio estratto (come `_detection_time`, ma nel passaggio); ripiego il CPA del passaggio."""
        for start, end in self._own_intervals(observer_id, target_id, own_range, radius) or ():
            if end >= lo - TIME_EPS and start <= hi + TIME_EPS:
                return max(float(start), lo)

        return t_cpa

    def _detect_passes(self, window, observer: _Shadow, target: _Shadow, own_range: float, factor: float,
                       passes: List[Tuple[float, float, float, float]]) -> None:
        """Un'estrazione per passaggio nel volume proprio (FP, >= 2 passaggi). Il primo estrae dallo stream
        dell'ingaggio nella posizione dell'estrazione unica di prima; dal secondo in poi da `pass_rng`, nell'ordine
        (finestra canonica, a->b poi b->a, passaggio). Ogni passaggio ha la sua distanza minima (FP-4), la sua
        permanenza D-5 (FP-6) e un candidato al tiro valido fino alla FINE del passaggio (FP-3 (a): all'uscita dal
        volume proprio la traccia e' persa, al rientro serve un nuovo rilevamento). Due o piu' passaggi capitano
        solo all'osservatore con la portata minore (per l'altro il passaggio coincide con la finestra)."""
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
                time = self._pass_detection_time(observer.id, target.id, own_range, lo, hi, radius, t_cpa)
                self._perceive(observer.force_id, target.id, time)
                identified = self.identified_by.setdefault(self.domain_of[observer.force_id], {})
                identified[target.id] = min(identified.get(target.id, time), time)

                if not self._grounded_in(target.id, window) \
                        and ADE.rwr_perception(target.asset, observer.asset) == ADE.PERCEIVED_AT_DETECTION:
                    self._perceive_rwr(target, observer, time)

                t_ready = time + self._profile(observer.id).total
                # FP-3 (a): fine del passaggio (gia' ritagliata alla finestra: hi <= window.t_end).
                if t_ready <= hi + TIME_EPS:
                    self.candidates.setdefault(observer.id, []).append(
                        _Candidate(t_ready=t_ready, target_id=target.id, t_end=hi, t_cpa=t_cpa,
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
            touching = [(start, end) for start, end in self._own_intervals(observer_id, target_id, own_range)
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
8-bis. **Volume proprio in un solo punto (decisione VA-6 (a) del 2026-11-07,
   `Proposta_Allineamento_Volumi_DES_Pianificatore.md` §2.3)**: `_own_intervals` (testo al punto 7) e' l'**unico**
   punto del risolutore che chiama `range_intervals` sul volume di rilevamento proprio. Oltre ai metodi nuovi
   (`_own_passes`, `_pass_detection_time`) e a `_exposure_time` (punto 8), anche il metodo esistente
   `_detection_time` (`:2192-2218`) passa da li': nel suo ramo con i tratti, `for start, end in
   range_intervals(legs_observer, legs_target, radius):` diventa `for start, end in self._own_intervals(observer_id,
   target_id, own_range, radius):` (la condizione `legs_observer and legs_target and radius is not None` resta). Il
   raggio passa **invariato** (nessuna moltiplicazione per un fattore): stessi float, stessi intervalli, quindi
   comportamento identico in ogni stato degli interruttori. Le chiamate a `range_intervals` che restano nel modulo
   sono solo quelle dell'**ingaggio** (`engagement_intervals`, controllo di portata), fuori da questa regola.
   Verifica dell'esecutore: `grep -n "range_intervals(" Logic/Engagement_Resolver.py` deve dare solo
   `engagement_intervals` (e, se la Proposta VA e' gia' eseguita, le sue funzioni d'ingaggio) e `_own_intervals`.
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
    questo; il candidato al tiro dell'osservatore con la portata minore vale fino alla fine del passaggio, anche con
    un passaggio solo (FP-3 (a)). None (default) = un'estrazione per finestra e direzione, comportamento precedente. In sessione lo passa
    Session_Simulator (`pass_event_id`) solo con FP_PER_PASS_DETECTION acceso."
12. **Docstring del modulo**: (i) nel punto del contratto RNG (`:412-415`) la parentesi "(invariato dalla D-5)"
    diventa "(invariato dalla D-5 e dal rilevamento per passaggio: con `pass_rng` i passaggi dal secondo in poi
    estraggono da quello stream separato, nell'ordine canonico seguito dall'indice del passaggio, e lo stream `rng`
    resta identico)"; (ii) una sezione nuova, dopo quella della D-5, intitolata `## Rilevamento per passaggio nella
    portata propria (FP, interruttore FP_PER_PASS_DETECTION)`, con: la regola dell'utente (un'occasione per passaggio,
    mai la somma), i passaggi dai tratti (`_own_passes`), le quattro scelte FP-2/3/4/6 (FP-3 (a): candidato al tiro
    fino alla fine del passaggio, anche con un passaggio solo, per l'osservatore con la portata minore; le salve gia'
    lanciate non cambiano, si fermano solo i lanci nuovi dopo l'uscita), R-INT (FP-5), il ripiego senza tratti, la
    frase "spento (`pass_rng` None) il comportamento e' quello di prima".

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
- **Nessuna costante stimata nuova**; tolleranze = `TIME_EPS` esistente. In particolare nessuna tolleranza di unione
  dei passaggi ravvicinati (FP-10 (a)): `_own_passes` usa gli intervalli di `range_intervals` cosi' come sono. Il dwell di 600 s di S33 e' un valore
  **dichiarato di test** (come S32 `short`).
- Core indifferente al simulatore; import col percorso completo; logger mockato nei test come negli altri.

#### 4.1.5 Test del blocco 1 (20)

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
8. `test_a_pass_candidate_ends_with_its_pass` (FP-3 (a)): profilo di `b1` (120, 1), fire control `_kill()` per `b1` e
   None per `r1`; rng `[0.0, 0.99]`, pass_rng `[0.99]`. Senza `pass_rng`: una salva di `b1` a 170.0 (`places=6`;
   rilevamento a 50, candidato fino a 430). Con: nessuna salva di `b1` (t_ready 170 oltre la fine del primo passaggio,
   150, anche se il secondo comincia solo a 290; secondo passaggio mancato: 0.99 >= 0.9352).
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
18. `test_single_pass_candidate_ends_with_the_pass` (FP-3 (a) con un passaggio solo): geometria del test 10 (`r1` con
    il solo primo tratto, finestra [0, 200] con `t_cpa` 100, `distance_cpa` 0, portate 5000/20000, `t_mutual` 50/150),
    fire control `_kill()` per `b1` e None per `r1`, rng `[0.0, 0.99]`, pass_rng vuoto. Profilo di `b1` (120, 1):
    senza `pass_rng` una salva di `b1` a 170.0 (candidato fino a 200); con `pass_rng` nessuna salva di `b1`
    (passaggio [50, 150]: t_ready 170 dopo l'uscita), `pass_rng.calls == 0`. Profilo di `b1` (10, 1): in entrambi gli
    stati una salva di `b1` a 60.0 (`places=6`): il tiro dentro il passaggio non cambia.
19. `test_larger_range_observer_candidate_ends_with_the_window` (FP-3 (a), osservatore con la portata maggiore):
    stessa geometria del test 18; fire control `_kill()` per `r1` e None per `b1`, profilo di `r1` (180, 1), rng
    `[0.99, 0.0]`, pass_rng vuoto: in entrambi gli stati una salva di `r1` su `b1` a 180.0 (`places=6`; rilevamento a
    0, candidato fino a `window.t_end` = 200), `pass_rng.calls == 0`.

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

In `TestDetectionPerPass` (VA-6 (a)):
20. `test_own_intervals_is_the_single_volume_call`: sulla geometria comune, `run._own_intervals('b1', 'r1', 5000.0)`
    == `range_intervals(legs_b1, legs_r1, 5000.0)` e con `radius=3000.0` == `range_intervals(..., 3000.0)`; None senza
    tratti; con `patch.object(ER._EngagementRun, '_own_intervals', spia)` che chiama l'originale, una risoluzione con
    `pass_rng` e `dwell_time_for` dati passa per la spia da `_own_passes`, `_pass_detection_time` ed `_exposure_time`
    (almeno una chiamata da ciascuno: la spia registra il raggio), e la `Detection` e' identica a quella senza spia.

#### 4.1.6 Esito atteso del blocco 1

- Suite: **`Ran 4815 tests`** (4795 + 20), `OK (skipped=7)`.
- Confronto con la fotografia: **1009 identiche, 0 cambiate, 20 nuove** (`S32-DWELL`), cioe'
  `compared 1029 runs: 20 difference lines` come prima. Le 1009 restano identiche perche' l'interruttore e' spento:
  `engage` non passa `pass_rng`, `_detect_direction` esegue le stesse istruzioni (`candidate_end` e' `window.t_end`),
  `_exposure_time` non e' mai
  chiamato (D-5 spenta), `_detection_time_of` usa `earliest=False` (stesso dizionario di prima).
- **Verifica di S32** (le sue esecuzioni non sono nella fotografia: un cambio non si vedrebbe nel confronto):
  `<python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare .ai-run/sonde_passaggi/p0/capture.json
  --against .ai-run/confronto_capture.json --only 'S32-DWELL' --ignore probe_passes` -> `compared 20 runs:
  IDENTICAL` (attesa: in S32 la ZSU e il P-18 hanno un solo passaggio, quindi FP-6 non cambia la permanenza; P-0 lo
  conferma: nessuna direzione con piu' di un passaggio nelle 20 esecuzioni di S32-DWELL, §1.8).
  Se non e' IDENTICAL: fermarsi e riferire le righe.

### 4.2 Blocco 2 — scenario S33-PASSES

#### 4.2.1 `Test/Test_Session_Scenarios_S33.py` (nuovo, 14 test)

Docstring di modulo nello stile di S32 (`Test_Session_Scenarios_S32.py:1-28`) con la tabella delle 8 varianti (le due
geometrie) e la frase "600 s e' un periodo di rivisita DICHIARATO DI TEST sulla ZSU-57-2, non un dato". Costruzione:

```python
SEEDS = [f'S33-PASSES-{index}' for index in range(5)]
# variante -> (geometria, FP_PER_PASS_DETECTION, dwell DICHIARATO DI TEST sulla ZSU [s] con D5_DWELL_TIME acceso | None)
VARIANT_SPEC = {
    'off': ('reentry', False, None),
    'on': ('reentry', True, None),
    'dwell_off': ('reentry', False, 600.0),
    'dwell_on': ('reentry', True, 600.0),
    'cas_off': ('cas', False, None),
    'cas_on': ('cas', True, None),
    'cas_dwell_off': ('cas', False, 600.0),
    'cas_dwell_on': ('cas', True, 600.0),
}
VARIANTS = tuple(VARIANT_SPEC)
CAS_IDS = tuple(f'Blue-CAS/cas{index}' for index in range(4))
# Andata sulla linea Red, uscita a 14 km, ritorno, uscita: due passaggi nei 6 km della ZSU (visivo, quota 3000 m),
# sempre entro gli 80 km dell'A-10C contro bersagli a terra (una sola finestra per coppia A-10C/ZSU).
REENTRY = [(0.0, 0.0), (-14_000.0, 0.0), (0.0, 0.0), (-30_000.0, 0.0)]
# CAS: tre BMP-2 attaccati in sequenza lungo la rotta; A e C dentro i 6 km della ZSU, B fuori (13 km). Punto sopra A,
# proseguimento fino a B, virata e ritorno sopra C, uscita a ovest: due passaggi NON contigui nel volume della ZSU,
# sempre entro gli 80 km dell'A-10C (una sola finestra per coppia A-10C/ZSU).
CAS_TARGETS = {'ifvA': (0.0, 0.0), 'ifvB': (14_000.0, 0.0), 'ifvC': (2_000.0, -3_000.0)}
CAS_TARGET_IDS = tuple(f'Red-Line/{prefix}0' for prefix in CAS_TARGETS)
CAS_ROUTE = [CAS_TARGETS['ifvA'], CAS_TARGETS['ifvB'], CAS_TARGETS['ifvC'], (-30_000.0, -3_000.0)]
ZSU_VISUAL_RANGE_M = 6_000.0     # portata del registro della ZSU-57-2 contro bersagli aerei (§1.4), per i test di premessa
A10_GROUND_RANGE_M = 80_000.0    # portata del registro dell'A-10C contro bersagli a terra (§1.4)
```

Funzioni del modulo:
- `build` e `ZSU`, `ZSU_POSITION` importati da `Test_Session_Scenarios_S32` (geometria di rientro: `build(with_ewr=False)`).
- `build_cas()` nuova: forza `Red-Line` (lato 'Red') con, in quest'ordine, tre `F.Unit('vehicle', 'BMP-2', 1,
  origin=CAS_TARGETS[prefix], prefix=prefix, sensors=VISUAL)` per `prefix` in `('ifvA', 'ifvB', 'ifvC')` e
  `F.Unit('vehicle', 'ZSU-57-2', 1, origin=ZSU_POSITION, prefix='ad')`; forza `Blue-CAS` identica a quella di
  `Test_Session_Scenarios_S32.build` (stessa riga `F.Unit('aircraft', 'A-10C Thunderbolt II', 4, origin=(-40_000.0,
  0.0, 3_000.0), step=(0.0, 500.0), prefix='cas', loadout='Maverick/Gun CAS')`, `mil_category=F.AIR_UNIT`). `VISUAL`
  e `MAVERICK` importati da `Test_Session_Scenarios_S19_Air_Defence` come in S32. Restituisce `(red, cas)`.
- `run_variant(session_id, variant)` come quello di S32 (`:83-110`): geometria `'reentry'` = `build(with_ewr=False)`,
  rotta `REENTRY`, bersaglio GROUP `Red-Line` con `asset_ids=IFV_IDS`; geometria `'cas'` = `build_cas()`, rotta
  `CAS_ROUTE`, bersaglio GROUP `Red-Line` con `asset_ids=CAS_TARGET_IDS`; per entrambe `mission_type='CAS'`,
  `weapons=(MAVERICK,)`, `rules=MissionRules(roe='only_designated')`, nessun `attack_waypoint` (come S32: con
  `only_designated` il punto ATTACK non e' letto, §1.10). Attorno all'intera esecuzione
  `patch.object(ER_MODULE, 'FP_PER_PASS_DETECTION', switch)` e `patch.object(ER_MODULE, 'D5_DWELL_TIME', dwell is not
  None)`; `F.declare_dwell(red.assets[ZSU], {'air': dwell})` se `dwell` non e' None. La spia su
  `ER.resolve_engagement` salva, **prima** di chiamare l'originale, `copy.deepcopy(kwargs.get('pass_rng'))` (None se
  assente) e dopo la coppia `(risultato, copia)`. Restituisce `(outcome, results, pass_streams)`: le coppie con
  risultato non None, separate in due liste allineate.
- Ciclo esterno sui semi, interno sulle 8 varianti nell'ordine di `VARIANT_SPEC` (stesso `session_id` per le 8 varianti
  di un seme). Classe `TestS33DetectionPerPass(F.LoggerSilencer, unittest.TestCase)`; `_zsu(results, cas=None)` = le
  `Detection` con `observer_id == ZSU` (e `target_id == cas` se dato) di tutti i risultati; `_first_zsu(results, cas)`
  = le `Detection` della ZSU su `cas` nel **primo** risultato che ne contiene almeno una.

Nota per l'esecutore [V, calcolo del 2026-11-07 con `Scenario_Fixtures.missions_for`, `Mission_Adapter.movement_legs` e
`range_intervals` contro la ZSU ferma, senza sessione]: con entrambe le rotte `missions_for` crea **4 missioni**
(`Blue-CAS:CAS-1..4`, un A-10C ciascuna) perche' la formazione traslata non e' riducibile a un offset dopo le virate
(comportamento previsto dal fixture, `Test/Scenario_Fixtures.py:716-742`); velocita' 155,6 m/s. Per questo i test CAS
non assumono che i 4 A-10C stiano nello stesso `EngagementResult`.

Test 1-7 (geometria di **rientro**, varianti `off`, `on`, `dwell_off`, `dwell_on`):
1. `test_premise_two_passes_per_aircraft`: in `on`, per ogni seme e A-10C, esattamente 2 `Detection` della ZSU, con
   `pass_index` {0, 1}, `pass_count` 2 e `pass_end` del passaggio 0 < `pass_start` del passaggio 1.
2. `test_switch_off_one_draw_per_window`: in `off`, per ogni seme e A-10C, esattamente 1 `Detection` della ZSU, con
   `pass_index` None.
3. `test_the_engagement_stream_is_unchanged`: per ogni seme, nel PRIMO `EngagementResult`,
   `[d.draw for d in off.detections] == [d.draw for d in on.detections if d.pass_index in (None, 0)]`.
4. `test_no_launch_after_the_pass_without_a_new_detection` (FP-3 (a)): in `on`, per ogni salva della ZSU in un
   risultato esiste, nello stesso risultato, una `Detection` rilevata della ZSU sullo stesso bersaglio con `time <=
   t_launch + 1e-9` e `t_launch <= pass_end + 1e-6` (la salva parte dentro il passaggio del rilevamento; in `on` tutte
   le `Detection` della ZSU hanno `pass_end` valorizzato, test 1). In particolare nessuna salva della ZSU fra la fine
   del passaggio 0 e il rilevamento nel passaggio 1.
5. `test_dwell_exposure_is_the_own_pass`: in `dwell_on` ogni `Detection` della ZSU ha `dwell_time_s == 600`,
   `|exposure_s - (pass_end - pass_start)| < 1e-6` e `probability <= exposure_s / 600 + 1e-12`.
6. `test_dwell_single_draw_uses_one_pass_never_the_sum` (FP-6): per ogni seme e A-10C, nel primo risultato,
   l'`exposure_s` della `Detection` della ZSU in `dwell_off` e' uguale (entro 1e-6) a una delle due di `dwell_on` ed e'
   minore della loro somma di almeno 1e-6.
7. `test_premise_the_zsu_fires_without_the_switch`: in `off` la ZSU spara in almeno un seme.

Test 8-14 (geometria **CAS**, varianti `cas_off`, `cas_on`, `cas_dwell_off`, `cas_dwell_on`):

8. `test_cas_premise_geometry` (senza sessione): con `red, cas = build_cas()`: la distanza orizzontale dalla ZSU di
   `Red-Line/ifvA0` e `Red-Line/ifvC0` e' `< ZSU_VISUAL_RANGE_M` e quella di `Red-Line/ifvB0` e' `>
   ZSU_VISUAL_RANGE_M`; `CS.mutual_detection_ranges(red.assets[ZSU], cas.assets['Blue-CAS/cas0'])` e'
   `(ZSU_VISUAL_RANGE_M, A10_GROUND_RANGE_M)`; per ogni A-10C, il punto di partenza e i punti di `CAS_ROUTE` traslati
   della sua formazione (`dy = 500 * indice`, quota 3000 m) distano dalla ZSU meno di `A10_GROUND_RANGE_M` (la rotta e'
   una spezzata: il massimo e' su un vertice).
9. `test_cas_premise_two_separate_passes_per_aircraft`: in `cas_on`, per ogni seme e A-10C, `_first_zsu` ha
   esattamente 2 `Detection`, con `pass_index` {0, 1}, `pass_count` 2, `distance_cpa < ZSU_VISUAL_RANGE_M` per
   entrambe e `pass_start` del passaggio 1 - `pass_end` del passaggio 0 `> 60.0` s (uscita verso il bersaglio fuori
   volume; calcolata ~103-104 s, 60 s e' un margine del test, non un dato).
10. `test_cas_switch_off_one_draw_per_aircraft`: in `cas_off`, per ogni seme e A-10C, `_first_zsu` ha esattamente 1
    `Detection`, con `pass_index` None.
11. `test_cas_first_pass_keeps_the_engagement_stream`: per ogni seme, nel PRIMO `EngagementResult`,
    `[d.draw for d in cas_off.detections] == [d.draw for d in cas_on.detections if d.pass_index in (None, 0)]` (il
    primo passaggio prende l'estrazione di oggi, nella stessa posizione dello stream dell'ingaggio).
12. `test_cas_second_pass_draws_from_the_pass_stream`: in `cas_on`, per ogni seme e per ogni coppia (risultato, copia
    dello stream) con copia non None: `[d.draw for d in risultato.detections if d.pass_index not in (None, 0)] ==
    [copia.random() for _ in range(n)]` (n = lunghezza della lista di sinistra; ordine: finestra canonica, a->b poi
    b->a, passaggio); inoltre, sommando su tutti i risultati del seme, almeno una `Detection` della ZSU con
    `pass_index == 1` per ogni A-10C. Prova che le estrazioni dal secondo passaggio in poi vengono **solo** da
    `pass_rng`.
13. `test_cas_dwell_uses_the_own_pass_never_the_sum` (FP-6): per ogni seme e A-10C, in `cas_dwell_on` le 2 `Detection`
    di `_first_zsu` hanno `dwell_time_s == 600` e `|exposure_s - (pass_end - pass_start)| < 1e-6`; in `cas_dwell_off`
    l'unica `Detection` di `_first_zsu` ha `exposure_s` uguale (entro 1e-6) a una delle due di `cas_dwell_on` e minore
    della loro somma di almeno 1e-6.
14. `test_cas_no_launch_after_the_pass_without_a_new_detection` (FP-3 (a)): come il test 4, in `cas_on`: ogni salva
    della ZSU parte dentro il passaggio di una `Detection` rilevata della ZSU sullo stesso bersaglio nello stesso
    risultato (`time <= t_launch + 1e-9`, `t_launch <= pass_end + 1e-6`): dopo il passaggio 1 (bersaglio A) nessun tiro
    prima del rilevamento nel passaggio 2 (bersaglio C).

Valori attesi [V: calcolo sui tratti del 2026-11-07 (§4.2.1, nota), da leggere all'esecuzione, NON da scrivere come
asserzioni]:
- rientro: passaggi della ZSU [230, 284] s e [410, 464] s per `cas0` (49,8-53,8 s secondo l'A-10C), pausa 126-130 s;
- CAS: passaggi [230, 297] s e [401, 462] s per `cas0` (62,7-66,7 s e 60,8-66,7 s secondo l'A-10C), pausa 103-104 s;
  distanza massima dalla ZSU 41 km (partenza), dei bersagli dalla ZSU 1044 m (A), 13 003 m (B), 2879 m (C);
- 4 estrazioni della ZSU per seme in `off`/`cas_off`, 8 in `on`/`cas_on`.
Se (1) o (9) fallissero (la sessione non da' due passaggi in una finestra: per esempio un ritaglio G4a o una
ri-pianificazione G4b), l'esecutore **non** cambia la rotta: si ferma e riferisce `pass_count`, gli istanti e le
finestre osservate.

#### 4.2.2 `Test/Scenario_Baseline.py`

In `UNITS`, in coda, nell'ordine di esecuzione (BI, poi VA, poi FP), come dice la tabella di coordinamento di BI §6.1 (non dopo S32-DWELL, `:395-397`):

```python
    # ── S33 (FP: un'occasione di rilevamento per passaggio nel volume proprio) — in coda, nomi stabili ──
    ('S33-PASSES', 'Test_Session_Scenarios_S33', 'TestS33DetectionPerPass', None,
     _by_occurrence('off', 'on', 'dwell_off', 'dwell_on', 'cas_off', 'cas_on', 'cas_dwell_off', 'cas_dwell_on')),
```

(l'ordine dei nomi e' quello del ciclo interno sulle varianti, `VARIANT_SPEC`: la fotografia numera le esecuzioni per
occorrenza del `session_id` nell'unita', `Test/Scenario_Baseline.py:227-232`).

e nel docstring, dopo "## Permanenza nel volume dopo la D-5" (`:176-181`):

```
## Rilevamento per passaggio dopo la FP

Il rilevamento per passaggio nella portata propria (`Engagement_Resolver.FP_PER_PASS_DETECTION`, SPENTO,
`Proposta_Finestre_Per_Passaggio_Portata_Propria.md`) non cambia le esecuzioni esistenti (interruttore spento). Aggiunge
in coda l'unita' S33-PASSES (8 varianti: rientro e CAS, ciascuna con FP spento/acceso e con/senza dwell di test; 5
seed): 40 esecuzioni nuove; nessuna voce nuova nel riassunto (i `Detection` non sono registrati).
```

#### 4.2.3 Vincoli del blocco 2

- **Nomi stabili**: unita' `S33-PASSES`; varianti, nell'ordine, `off`, `on`, `dwell_off`, `dwell_on`, `cas_off`,
  `cas_on`, `cas_dwell_off`, `cas_dwell_on`; semi `S33-PASSES-0..4`; asset `Red-Line/ad0` (ZSU), `Red-Line/ifv0..2`
  (rientro), `Red-Line/ifvA0`, `Red-Line/ifvB0`, `Red-Line/ifvC0` (CAS), `Blue-CAS/cas0..3`; missioni
  `Blue-CAS:CAS-1..4` (generate dal fixture). Nessun nome esistente cambia (S33 e' tutta nuova).
- Valore di test 600 s dichiarato come tale nel codice (commento) e nel rapporto; il margine di 60 s del test 9 e' una
  soglia del test, dichiarata come tale.
- Nessuna modifica a `Test_Session_Scenarios_S32.py` (si importano `build`, `ZSU`, `ZSU_POSITION`; `build_cas` sta in
  S33).

#### 4.2.4 Esito atteso del blocco 2

- Suite: **`Ran 4829 tests`** (4815 + 14), `OK (skipped=7)`.
- Confronto: **1009 identiche, 0 cambiate, 60 nuove** (20 `S32-DWELL`, 40 `S33-PASSES/S33-PASSES-<k>/<variante>`),
  cioe' `compared 1069 runs: 60 difference lines`. Fra le nuove, `off` e `on` (e `cas_off` e `cas_on`) di un seme
  possono differire nel contenuto (e' l'effetto della regola); nessuna asserzione lo richiede.

### 4.3 Dopo i blocchi (sessione principale, non l'esecutore)

1. Sonda **P-1** (`probe_switch_on.py`, §1.8 e LEGGIMI): confronto con la regola accesa in memoria. Atteso: le
   esecuzioni cambiate sono un sottoinsieme delle righe `MULTI`, `RINT` e `AFTER_PASS` di P-0; `MULTI` e `RINT` sono
   vuote, `AFTER_PASS` elenca **44 esecuzioni** (§1.8) toccate da FP-3 (a): quindi **da 0 a 44 cambiate, tutte
   nell'elenco `AFTER_PASS`** (S13-2, S13-4, S14-4, 6 di S21, S24-ORBIT-0/full, 32 di S26-BINGO, 2 di S28-CLASS), le
   altre 965 identiche, le 20 di S32 identiche. Dopo il solo blocco 1: `compared 1029 runs`, righe di differenza = le
   20 `NEW S32-DWELL/...` piu' quelle delle esecuzioni cambiate; dopo il blocco 2: `compared 1069 runs`, le 60 righe
   NEW (20 `S32-DWELL`, 40 `S33-PASSES`) piu' le stesse cambiate. Le esecuzioni di S33 non dipendono dal default (ogni
   variante fissa l'interruttore con `patch.object`). Atteso [I, per induzione sul primo evento divergente: una
   esecuzione cambia solo se una salva lanciata dopo la fine dell'unico passaggio sparisce]: probabilmente quasi
   tutte le 44. Una cambiata **fuori** dall'elenco `AFTER_PASS` va diagnosticata (implementazione diversa dalla
   regola della sonda, o un effetto del candidato esaurito prima che il ragionamento non copre). Da leggere per
   gruppi: quali armi sparano oltre la portata del sensore (dato non raccolto da P-0).
2. Decisione dell'utente sull'accensione, sui numeri di P-1 e sulle esecuzioni di S33 (`off` contro `on`). Con
   FP-3 (a) accendere il default cambia le esecuzioni `AFTER_PASS` rilevate da P-1, quindi richiede una fotografia
   nuova (§2.8): **nessuna nuova fotografia** senza decisione esplicita dell'utente.

### 4.4 Tempi di verifica (ProArt, `tools/ai/verifica.sh`, mai in parallelo)

Per blocco: suite ~10 minuti, poi confronto ~10 minuti [AGENTS.md]; P-0 eseguita (484,4 s, ~8 minuti, contro la stima
di 11-13); P-1 ~8-10 minuti dopo [S, sulla durata di P-0]. Totale macchina restante ~50-55 minuti [S]. Le 40
sessioni di S33 aggiungono ~2 minuti alla suite e al confronto [I, per analogia con S32: 20 sessioni ~1 minuto].

### 4.5 Scelte minori lasciate all'esecutore (da elencare nel rapporto)

Nomi delle variabili locali e delle costanti di test, posizione dei metodi nuovi dentro la classe, testo dei
messaggi di log, struttura interna di `Test_Session_Scenarios_S33.py` (riuso o copia locale di `run_variant`), la
sessione minima dei test 15-16 (quella di `_Base`), il modo di raccogliere le salve nel test S33 4 (dai
`EngagementResult` catturati), la forma interna di `_first_zsu` e del calcolo della distanza orizzontale nel test 8.

---

## 5. Rischi e limiti

### 5.1 Rischi di esecuzione

- `_detect_direction` e' il punto piu' delicato del motore. La rete: test 2, 4, 10 (stream e percorso di prima),
  confronto **0 cambiate** a interruttore spento (una sola cambiata = errore d'implementazione), verifica di S32
  (§4.1.6).
- I test 4 e 14 di S33 e 8, 18, 19 del blocco 1 controllano FP-3 (a) (decisa): fine del candidato = fine del
  passaggio per l'osservatore con la portata minore, fine della finestra per l'altro.
- Il costo con la regola accesa: un `range_intervals` per direzione e un CPA (con `Point3D` di sympy) per passaggio
  multi; trascurabile rispetto a una sessione [I], da confermare con i tempi di P-1.
- `Test_Session_Scenarios_S33` aggiunge 40 sessioni (~2 minuti di suite [I]).
- La sonda P-0 misura con la stessa regola dei passaggi del piano: se l'implementazione se ne discostasse, P-1
  mostrerebbe cambiate fuori dall'elenco `AFTER_PASS` (gli elenchi `MULTI` e `RINT` sono vuoti): **qualunque**
  cambiata fuori da quelle 44 va diagnosticata.
- **FP-3 (a) cambia esecuzioni esistenti con la regola accesa** (fino a 44, ~4 % della fotografia, 32 in S26-BINGO):
  e' il primo effetto della Proposta visibile sulla fotografia. A interruttore spento resta 1009 identiche (test 18
  e 19 e confronto del blocco 1). Il bordo e' numerico: la fine del passaggio viene da `range_intervals` del
  risolutore; per l'osservatore con la portata maggiore non si usa (fine della finestra), per evitare differenze fra
  i tratti dello scheduler e del risolutore.
- **La fotografia non esercita la regola** (P-0: 0 direzioni multi su 33 910). Il confronto "1009 identiche" a
  interruttore spento prova solo che il percorso di prima non e' stato toccato; acceso, cambia solo per FP-3 (a) sulle
  direzioni a un passaggio. Il percorso dei passaggi multipli (`_detect_passes`, `pass_rng`, FP-3/4/5/6) e' coperto
  **solo** dai test unitari del blocco 1 (§4.1.5) e dai 14 test di S33. Un difetto del ramo multi passerebbe
  inosservato al confronto: per questo i test 3-9, 13, 18 e 19 di §4.1.5 e i test 1, 3-6 e 9-14 di S33 hanno
  asserzioni esatte e non vanno indeboliti.
- **Sessioni di S33 e G4a/G4b**: un ritaglio d'episodio o una ri-pianificazione (disingaggio, bingo) potrebbe spezzare
  la finestra o cambiare la rotta prima del secondo passaggio in qualche seme. Le asserzioni CAS usano il primo
  risultato che contiene la coppia (le estrazioni avvengono all'inizio del risolutore, prima degli eventi); se le
  premesse (1) o (9) falliscono l'esecutore si ferma (§4.2.1). Le 4 missioni separate generate dal fixture
  (`Blue-CAS:CAS-1..4`) sono previste.
- Le sessioni di campagna con rientri sullo stesso sito (non rappresentate nella fotografia) sono il caso d'uso reale
  della regola: il suo effetto quantitativo su di esse e' **ignoto** finche' non esiste uno scenario che le rappresenti
  [I].
- **FP-5 entro `TIME_EPS`** [I]: P-0 conta le coppie con rilevamenti a istanti diversi oltre `TIME_EPS`; coppie con due
  rilevamenti distanti meno di `TIME_EPS` non sono contate e con la regola accesa darebbero un istante diverso di meno
  di `TIME_EPS`. Effetto atteso nullo (decide solo un confronto `<= t_launch` al limite); P-1 lo rileverebbe come riga
  DIFF.

### 5.2 Limiti di modello (da dichiarare nel manuale)

- **Senza tratti** (chiamate dirette) nessun passaggio: un'estrazione per finestra e direzione, come prima.
- **Fine del tiro all'uscita dal volume** (FP-3 (a), decisa): con la regola accesa l'osservatore con la portata
  minore non lancia salve **nuove** dopo la fine del passaggio (traccia persa); una salva **gia' lanciata** prima
  dell'uscita prosegue fino all'impatto (la fine del candidato limita solo l'istante di lancio). Non e' modellata una
  memoria della traccia oltre l'uscita ne' una guida che richieda il sensore dopo il lancio. Con la regola spenta resta
  il limite di oggi: P-0 misura 151 salve in 44 esecuzioni della fotografia (32 in S26-BINGO) lanciate dopo la fine
  dell'unico passaggio. Senza tratti (chiamate dirette) e per l'osservatore con la portata maggiore la fine resta
  quella della finestra.
- **Passaggi tangenti o ritagliati a durata nulla** contano come passaggi (Pd sul bordo = 0,5 x fattore, legge di
  oggi); con la D-5 la permanenza nulla li annulla.
- **Passaggio diviso da un decollo/atterraggio** (`_pair_windows`): due finestre, due estrazioni, come oggi (stato a
  terra diverso nelle due parti).
- **Pianificatore** (FP-9): `max_detection_probability` e' per attraversamento, non cumulativa.
- **Detection non nella fotografia**: il numero di estrazioni non e' visibile nel confronto; lo verificano i test.
- **R-INT** con l'interruttore spento: resta il difetto latente "ultimo rilevamento" (§1.9), corretto solo con la
  regola accesa; P-0: oggi non si manifesta in nessuna esecuzione della fotografia.
- **Passaggi molto ravvicinati** (FP-10 (a)): un'uscita dal volume anche di pochi secondi crea un passaggio nuovo e
  un'estrazione in piu' (come oggi le finestre e gli attraversamenti del pianificatore); per traiettorie sul bordo del
  volume la Pd cumulativa e' sovrastimata (esempio in §2.11: 0,915 contro 0,759).
- **Attacchi CAS a piu' bersagli** (§1.10): il moto e' la spezzata dei punti di missione; nessuna manovra d'attacco
  (pop-up, giro sul bersaglio, riattacco) e' generata dal motore, l'ordine degli attacchi lo decidono priorita' e
  portate (non la sequenza dei punti), la rotta non cambia se i bersagli sono distrutti prima (salvo G4b). Un tratto
  rettilineo attraversa al piu' una volta il volume proprio, sfera nel DES e cilindro nel pianificatore (entrambi
  convessi): il caso multi-passaggio nasce solo da rotte con virate. Con forme non convesse (portata minima, cono di
  silenzio, unione di volumi) un solo tratto potrebbe dare due passaggi: v.
  `Proposta_Allineamento_Volumi_DES_Pianificatore.md` §2.3.
  La variante CAS di S33 rappresenta questa forma, non un profilo d'attacco reale.

---

## 6. Documenti da aggiornare dopo (non scritti qui)

- **Manuale DES** (`des-manual-writer`, insieme all'aggiornamento della D-5 ancora da fare): cap. 3 §3.5
  (`04_Strato1_Scheduler_Contatti.md:195-201`: `t_mutual_*` e' il **primo** intervallo nella portata minore; i
  passaggi successivi li conta il risolutore); cap. 4 §4.2 (Pd per passaggio, distanza del passaggio, FP-6), §4.11
  (stream `pass_rng`, `pass_event_id`), §4.26 (R-INT: primo istante con la regola accesa); cap. 6 (orchestratore,
  `07_Orchestratore_Session_Simulator.md`: `pass_event_id` fra gli stream); cap. 8 (`09_Validazione.md`: S33-PASSES,
  geometrie di rientro e CAS);
  cap. 9 (`10_Limiti_Estensioni_Divergenze.md`: il limite "una sola estrazione per finestra con piu' passaggi nel
  volume minore" come **storico** e i limiti di §5.2, compresi passaggi ravvicinati (FP-10) e attacchi CAS a piu'
  bersagli come spezzata di punti); atlante `11a_Atlante_Risolutore.md` (costante
  `FP_PER_PASS_DETECTION`, campi nuovi di `Detection` a `:1310`, metodi `_own_passes`, `_pass_cpa`,
  `_pass_detection_time`, `_detect_passes`, funzione `_detection_times`, sequenza di `_detect_direction`).
- **`F4_Differenze_Scenari.md`**: sezione "FP — rilevamento per passaggio (2026-11-xx)": il cambio, 1009 identiche,
  40 nuove di S33, esiti di P-0 e P-1 (con la regola accesa le esecuzioni `AFTER_PASS` cambiate da FP-3 (a), per
  gruppi), limiti.
- **`Piano_Implementazione_Missione.md`**: riga in §5 fuori dalla numerazione F, come D-4b/D-4c e D-5, con lo stato
  dell'interruttore.
- **`Proposta_Dwell_Time_Rilevamento.md`**: nota in §5.2 gia' scritta (rimando a questa Proposta); a lavoro fatto,
  l'esito.
- **`Rapporti/Sonde_Finestre_Passaggio/LEGGIMI.md`**: esiti di P-0 (noti dal 2026-11-07, §1.8: la frase "nessuna
  sonda e' stata ancora eseguita" e l'esito atteso di P-1 "sottoinsieme delle righe MULTI" vanno aggiornati: MULTI e
  RINT sono vuoti; con FP-3 (a) decisa l'atteso e' un sottoinsieme delle 44 righe AFTER_PASS) e, dopo, di P-1. Anche
  il docstring di `probe_switch_on.py` cita solo il "sottoinsieme delle esecuzioni MULTI (o RINT)": va completato con
  AFTER_PASS.
- **Memoria** (solo la sessione principale): decisioni FP, interruttore, esiti delle sonde.
