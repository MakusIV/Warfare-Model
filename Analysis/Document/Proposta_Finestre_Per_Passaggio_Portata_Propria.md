# Proposta: un'occasione di rilevamento per ogni passaggio nel volume di rilevamento PROPRIO dell'osservatore (FP)

**Stato aggiornato (2026-11-13): FP ESEGUITA, ACCESA E SENZA INTERRUTTORE.** Il testo che segue e' il piano storico
(scritto con l'interruttore `FP_PER_PASS_DETECTION`): l'interruttore e' stato eliminato dalla pulizia
(`Proposta_FP_Pulizia_Interruttore.md`, §4.3 punto 3); il codice di oggi non contiene piu' la costante.

**Stato: TUTTE LE DECISIONI PRESE (2026-11-08).** FP-1..FP-4 decise dall'utente il 2026-11-07 (**FP-1 = B-R**,
**FP-2 = O3**, **FP-3 = (a)**, **FP-4 = (a)**); FP-5..FP-10 decise dall'utente il 2026-11-08 (**FP-5 = (d)**, **FP-6 =
(a)**, **FP-7 = (a), interruttore TEMPORANEO**, **FP-8 modificata** a 4 varianti x 5 semi, **FP-9 = (a)**, **FP-10 =
(c)** con tre sotto-decisioni, la terza confermata la sera del 2026-11-08). Il piano di §4 implementa esattamente queste
scelte; **nessuna decisione resta aperta**. Ordine di esecuzione: **BI blocchi 3-4 -> VA blocchi 1-2 -> FP blocchi 1-2**
(§4.0.1).

**Modifiche rispetto alla versione del 2026-11-07** (riscrittura del 2026-11-08, `des-planner`):
1. Decisioni FP-5..FP-10 registrate (§2, §3); tolte le parole "aperta", "sospesa", "raccomandazione" residue; le
   opzioni scartate hanno una riga di motivazione; §3 e' ora l'elenco delle decisioni prese.
2. Riferimenti al codice ricontrollati sul checkout `97620f55` (BI blocchi 0-2 gia' integrati: `Engagement_Resolver.py`
   ha ~51 righe in piu', `Fire_Control.py` cambiato); ogni riga citata e' quella di oggi.
3. Blocco 1: **punto 10 riscritto per FP-5 (d)** (`_detection_time_of(..., at)`, funzione `_detection_time_in_pass`; la
   funzione `_detection_times` dell'opzione (a) e' tolta); **FP-10 (c)**: funzione `_join_passes`, metodo `_dwell_of`,
   `_own_passes(..., dwell)`, permanenza e CPA del passaggio unito; preambolo di `_detect_direction` riscritto;
   interruttore con il criterio di rimozione (FP-7 temporaneo); docstring D-5 del modulo allineata a FP-6.
4. Test del blocco 1 **da 20 a 30**: il 13 riscritto (FP-5 (d)), il 9 con dwell 125 s (con 400 s i passaggi si
   unirebbero, FP-10), il 10 e il 20 estesi, nuovi 21-30 (R-INT integrato, ripiego senza tratti, ripiego
   `next(..., longest)` di FP-6, sette test di FP-10).
5. Blocco 2: **S33-PASSES a 4 varianti x 5 semi = 20 esecuzioni nuove** (`off`, `on`, `cas_off`, `cas_on`), test **da
   14 a 11** (poi 13, punto 10), costante `ZSU_DWELL_S = 2.0` STIMA [S] dell'utente.
6. Precondizioni: branch dedicato (come BI §5.0.1 e VA §4.0.1), BI e VA eseguite, base reale, **cattura di base
   `.ai-run/fp_base_capture.json`** al posto della cattura di P-0 per la verifica a interruttore spento.
7. Numeri di suite e confronto riallineati all'ordine BI 3-4 -> VA 1-2 -> FP 1-2 partendo dalla base reale di oggi
   (`Ran 4829`, `compared 1029 runs: 20 difference lines`), tabella unica in §4.0.1.
8. §5.2: limiti di FP-9 (con la nota dell'utente su `Air_Route_Manager`), di FP-10 e delle tolleranze di finestre e
   pianificatore.
9. Sonda P-1 riscritta (`probe_switch_on.py`: passaggi di durata zero, decisioni R-INT cambiate da FP-5 (d)) e
   `LEGGIMI.md` corretto.
10. **2026-11-08 sera: conferme dell'utente (P-1 = 44 + RINT_D; S33 on/cas_on con D-5 accesa e dwell ZSU 2 s [S];
    FP-10 senza unione con FP spenta).** Di conseguenza: attesa di P-1 scritta ovunque come "al piu' le 44 `AFTER_PASS`
    piu' le eventuali `RINT_D`", NON misurata (§0, §1.8, §4.3, `LEGGIMI.md`, `probe_switch_on.py`); S33 `on`/`cas_on`
    accendono anche `D5_DWELL_TIME` e dichiarano `ZSU_DWELL_S` sulla ZSU (§2.9, §3, §3.1, §4.2), test S33 **da 11 a
    13** (nuovi 12 e 13, asserzioni in piu' nei test 1 e 7), suite dopo il blocco 2 **`B_FP + 43`** (§4.0.1); FP-10 a
    FP spenta e' la sotto-decisione 3 di §2.11 (tolta da §3.1); colonna FP della tabella di coordinamento in §4.0.2.

- **Regola dell'utente (vincolante, 2026-11-06)**: per una coppia di asset nemici il rilevamento di un osservatore si
  valuta **per singolo passaggio del bersaglio nel volume di rilevamento PROPRIO dell'osservatore**, indipendentemente
  dalla finestra dell'altro asset. Se il bersaglio esce e rientra nel volume dell'osservatore sono **due passaggi
  distinti**, ciascuno con la sua permanenza, la sua estrazione di rilevamento e (se differente) la sua finestra
  d'ingaggio; **mai la somma delle permanenze**. Precisazione del 2026-11-08 (FP-10 (c)): un'uscita non piu' lunga del
  periodo di aggiornamento del sensore (dwell) non interrompe la traccia: i due tratti sono **un** passaggio.
- **Esecutore**: `des-developer` (Claude Sonnet, sforzo alto: zona delicata RNG/interruttori). Alternativa:
  `oc-developer`. L'esecutore segue il piano di §4 cosi' com'e'; se il codice reale non corrisponde (righe, firme,
  esiti), si ferma e riferisce.
- **Nessun file di codice o di test modificato da questo documento.** Scritti: questo file e, in
  `Analysis/Document/Rapporti/Sonde_Finestre_Passaggio/`, gli script di sola lettura (P-0 del 2026-11-06, P-1 riscritta
  il 2026-11-08) e `LEGGIMI.md`.

**Convenzioni**: **[V]** = verificato leggendo il codice sul checkout del 2026-11-08 (`97620f55`, branch
`analysis/dce-dcs-persistence`) o eseguendolo (calcoli di geometria con `range_intervals`, log di `.ai-run/`); **[I]** =
ipotesi o conoscenza generale, non verificata nel repository; **[S]** = stima o scelta di progetto, mai dato tarato.
Percorsi di codice relativi a `Code/Dynamic_War_Manager/Source/`. Sonde **P-0, P-1**; decisioni **FP-1, FP-2, ...**.

**Termini**: **finestra** = solo la finestra di contatto (`ContactWindow`, intervallo entro la portata MAGGIORE delle
due parti); **passaggio** = intervallo continuo in cui il bersaglio e' entro la portata PROPRIA dell'osservatore, dopo
l'unione di FP-10; **passaggio unito** = due o piu' intervalli consecutivi della portata propria separati da uscite
<= dwell del sensore, trattati come un passaggio solo (dall'inizio del primo alla fine dell'ultimo); **finestra
d'ingaggio** = intervallo di validita' del candidato al tiro (`_Candidate.t_end`).

**Glossario delle sigle** (significato verificato dove indicato):

| Sigla | Significato | Fonte / verifica |
|---|---|---|
| DES | *Discrete Event Simulation*: il motore delle sessioni virtuali, a coda di eventi | `Logic/Session_Simulator.py:1-45` |
| CPA / TCPA | *Closest Point of Approach* (punto e distanza di massimo avvicinamento fra due mobili) / *Time to CPA* (istante del massimo avvicinamento) | `Logic/Contact_Scheduler.py:181`, `:804` [V] |
| RNG | *Random Number Generator*: nel motore solo l'RNG di sessione, uno stream per chiave (missione, evento, contatore) | `Utility/Session_Rng.py`, `Command/Session_Types.py:388-390` |
| Pd | probabilita' di rilevamento di un sensore contro un bersaglio a distanza d | `Logic/Engagement_Resolver.py:1119-1146` (`detection_probability`) [V] |
| D-5 | decisione D-5 di `Proposta_Volumi_Rilevamento_Intercettazione.md` §9, opzione 2: Pd dipendente dalla permanenza (`Proposta_Dwell_Time_Rilevamento.md`, interruttore `D5_DWELL_TIME`, spento) | `Logic/Engagement_Resolver.py:522-529` [V] |
| dwell (`dwell_time_s`) | periodo di rivisita (aggiornamento) del sensore [s]: con la D-5 la Pd e' moltiplicata per min(1, permanenza / dwell); con la FP e la D-5 accese e' anche la soglia di unione dei passaggi (FP-10). Oggi dichiarato solo dai 10 EWR del registro | `Logic/Engagement_Resolver.py:1181-1203` (`dwell_factor`), `:1206-1221` (`registry_dwell_time`); `Asset/Vehicle_Data.py:4659-5058` (10 voci) [V] |
| DW-1..DW-9 | decisioni della Proposta D-5 (tutte prese il 2026-11-06); DW-9 = estensione dei dwell a SAM/AAA, da fare | `Proposta_Dwell_Time_Rilevamento.md:3-8` |
| FP | questa Proposta: "finestre per passaggio", un'occasione di rilevamento per passaggio nel volume proprio; decisioni FP-1..FP-10 | questo documento |
| BI | `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`: quali colpi una difesa aerea puo' considerare bersagli; interruttore `BI_AD_TARGET_RULE` (spento), blocchi 0-2 integrati | `Logic/Engagement_Resolver.py:531-535`, `:3196-3202` (`_admissible`) [V] |
| VA | `Proposta_Allineamento_Volumi_DES_Pianificatore.md`: quota nel volume d'ingaggio; interruttore `VA_ENGAGEMENT_ALTITUDE_BAND`; decisione VA-6 (a) (`_own_intervals`) scritta in questo piano | quella Proposta, §2.3, §4 |
| EWR | *Early Warning Radar*: radar di scoperta lontana (es. P-18-Terek, FPS-117) | `Proposta_Dwell_Time_Rilevamento.md` |
| SAM | *Surface-to-Air Missile*: sistema missilistico superficie-aria | conoscenza generale [I] |
| AAA | *Anti-Aircraft Artillery*: artiglieria contraerea (cannoni) | conoscenza generale [I] |
| ZSU | ZSU-57-2, semovente contraereo a cannoni da 57 mm (S-68-57mm, task `Anti_Air` e `Infantry_Support`, non `Anti_Missile`); nel registro solo sensore visivo, portata 6000 m contro bersagli aerei | `Asset/Ground_Weapon_Data.py:2254-2266` [V]; §1.4 |
| R-INT | regola dell'intercettazione con tempo di reazione (2026-09-30, `Proposta_Intercettazione_Reazione.md`): un intercettore ferma i colpi solo se ne ha una traccia e il tempo di reagire; se aveva gia' rilevato il lanciatore "vede il lancio" (reazione breve) | `Logic/Engagement_Resolver.py:49-55`, `:3292-3316` (`_in_time`) [V] |
| G4a | raggruppamento delle finestre in **episodi d'ingaggio** (sovrapposte entro `EPISODE_GAP`), un `resolve_engagement` per episodio; finestre successive ritagliate | `Logic/Session_Simulator.py:919`, `:1222-1293` [V] |
| G4b | **ri-pianificazione degli aerei dopo l'episodio** (bingo, rientro dopo disingaggio) e ricalcolo dei contatti non ancora risolti | `Logic/Session_Simulator.py:2832` (`reschedule`) [V] |
| B-R / B-S1 / B-S2 | opzioni di FP-1: passaggi calcolati nel **R**isolutore / nello **S**cheduler con finestre per direzione / nello Scheduler come campo della finestra | §2.2 |
| O1 / O2 / O3 | opzioni di FP-2 per l'ordine delle estrazioni: in linea / in coda / stream separato | §2.3 |
| S32 | scenario S32-DWELL (D-5): ZSU, 3 BMP-2, 4 A-10C in sorvolo; 5 varianti x 4 semi = 20 esecuzioni nuove, non nella fotografia | `Test/Test_Session_Scenarios_S32.py:1-28` [V] |
| S33 | scenario nuovo S33-PASSES di questa Proposta (FP-8): rientro e CAS, 4 varianti x 5 semi = 20 esecuzioni nuove; `off`/`cas_off` tutto spento, `on`/`cas_on` FP e D-5 accese con il dwell della ZSU 2 s [S] | §2.9, §4.2 |
| S34 / S35 | scenari nuovi di VA (S34-BAND, 32 esecuzioni) e della BI (S35-ADTGT, 32 esecuzioni), eseguiti prima della FP | VA §4.2, BI §5.4 |
| P-0 / P-1 | sonde di sola lettura: P-0 prima del codice (conta i passaggi; FATTA), P-1 dopo il blocco 1 (regola accesa in memoria) | §1.8, §4.3, `Rapporti/Sonde_Finestre_Passaggio/` |
| `ContactWindow` | finestra di contatto fra due asset: `t_start/t_end`, CPA, portate delle due parti, primo intervallo nella portata minore | `Logic/Contact_Scheduler.py:196-240` [V] |
| `TIME_EPS` | 1e-9 s: due istanti piu' vicini sono lo stesso istante; serve anche a fondere intervalli contigui fra tratti consecutivi | `Logic/Contact_Scheduler.py:88-92`, `:938-952` [V] |
| CAS | *Close Air Support*: tipo di missione aerea d'appoggio ravvicinato (`mission_type='CAS'` negli scenari) | `Test/Test_Session_Scenarios_S32.py:103` [V] |

---

## 0. Sintesi

Oggi il DES fa **una sola estrazione di rilevamento per finestra di contatto e direzione**, con la distanza minima
dell'intera finestra. La finestra e' l'intervallo in cui la distanza e' entro la portata **maggiore** delle due
parti. Per l'osservatore che ha la portata maggiore la regola e' gia' rispettata (uscita e rientro dal suo volume =
due finestre). Per l'osservatore con la portata **minore** (tipicamente un SAM o un'AAA contro un aereo, che vede i
bersagli a terra fino a 80 km) una finestra puo' contenere **piu' passaggi** nel suo volume, ma riceve **una sola**
occasione; con la D-5 accesa, in piu', la permanenza e' la **somma** dei passaggi. Il limite e' **precedente alla
D-5** e **non e' dichiarato** nel manuale.

| Tema | Decisione | Effetto sulla fotografia (interruttore spento) |
|---|---|---|
| Dove si calcolano i passaggi (FP-1, DECISA 2026-11-07: **B-R**) | nel **risolutore**, dai tratti (`range_intervals` con la portata propria, tramite `_own_intervals`), come la permanenza D-5; `ContactWindow` e scheduler invariati | nessuno |
| Ordine delle estrazioni (FP-2, DECISA 2026-11-07: **O3**) | primo passaggio dallo stream dell'ingaggio, nella posizione di oggi; dal secondo in poi uno **stream separato** (`pass_rng`, `pass_event_id`, come la tempra) | nessuno |
| Finestra d'ingaggio per passaggio (FP-3, DECISA 2026-11-07: **(a)**) | il candidato al tiro vale fino alla **fine del passaggio** (uscita dal volume proprio: traccia persa), per l'osservatore con la portata minore, anche con un passaggio solo | nessuno spento; **acceso (con FP-5 (d)): al piu' le 44 esecuzioni `AFTER_PASS` di P-0 piu' le eventuali `RINT_D`**, attesa NON misurata (la misura P-1, §4.3) |
| Distanza per passaggio (FP-4, DECISA 2026-11-07: **(a)**) | **CPA del passaggio** | nessuno |
| Istante di rilevamento per R-INT (FP-5, DECISA 2026-11-08: **(d)**) | regola accesa: il lancio e' "visto" solo se l'intercettore ha rilevato il lanciatore **nel passaggio che contiene il lancio**; spenta: l'ultimo rilevamento in ordine di lista, come oggi | nessuno spento; acceso: da misurare in P-1 (`RINT_D`, §4.3) |
| D-5 senza FP (FP-6, DECISA 2026-11-08: **(a)**) | con la D-5 accesa la permanenza e' **il passaggio che contiene `t_cpa`** (in subordine il piu' lungo), mai la somma, in ogni stato dell'interruttore FP; con FP acceso la permanenza del proprio passaggio | nessuno (D-5 spenta nella fotografia; S32 a un passaggio) |
| Interruttore (FP-7, DECISA 2026-11-08: **(a), TEMPORANEO**; **ELIMINATO il 2026-11-13**, v. §4.3 punto 3) | `Engagement_Resolver.FP_PER_PASS_DETECTION = False`; `Session_Simulator` passa `pass_rng` solo se acceso; si elimina con un blocco di pulizia dopo P-1 e la fotografia nuova installata dall'utente | **1009 identiche** |
| Scenario (FP-8, DECISA 2026-11-08, **modificata**; D-5 in S33 confermata la sera) | S33-PASSES, 4 varianti x 5 semi = **20 nuove** (`off`, `on` rientro; `cas_off`, `cas_on` CAS); `off`/`cas_off` tutto spento (stato precedente); `on`/`cas_on` = configurazione finale, **FP e D-5 accese** con il dwell della ZSU 2 s [S] (g = 1, nessuna unione FP-10); niente varianti con dwell lunghi | +20 nuove |
| Pianificatore (FP-9, DECISA 2026-11-08: **(a)**) | nessun cambio; limite dichiarato: `max_detection_probability` e' il peggiore degli attraversamenti, non la probabilita' cumulativa del DES | nessuno |
| Passaggi ravvicinati (FP-10, DECISA 2026-11-08: **(c)**) | passaggi separati da un'uscita **<= dwell** del sensore osservatore si **uniscono** (una estrazione, CPA e permanenza del passaggio unito); solo con FP e D-5 accese e il dwell dichiarato | nessuno |

**Esito della sonda P-0 (2026-11-07, §1.8)** [V: `Rapporti/Sonde_Finestre_Passaggio/esito_p0.txt`]: nelle 1029
esecuzioni (1009 della fotografia e 20 di S32-DWELL) nessuna direzione ha piu' di un passaggio nel volume proprio e
nessuna coppia ha rilevamenti a istanti diversi nello stesso ingaggio. A interruttore **spento** la fotografia resta
**1009 identiche**; a interruttore **acceso** (sonda P-1) l'attesa e' che cambino **al piu' le 44 esecuzioni
`AFTER_PASS`** di P-0 (FP-3 (a)) **piu' le eventuali `RINT_D`** (esecuzioni in cui FP-5 (d) cambia una decisione R-INT):
attesa **NON misurata** [I], P-0 ha contato solo le `AFTER_PASS`; la misura e' P-1 (§4.3). Le altre parti della regola
(passaggi multipli, FP-4, permanenza per passaggio, FP-10) sono provabili **solo** sul nuovo scenario S33-PASSES e nei
test unitari; in sessione S33 percorre il ramo "FP e D-5 accese, nessuna unione, g = 1", l'unione effettiva e g < 1
restano ai test unitari (§5.1).

**Dimensione stimata** [S]: blocco 1 ~210 righe di codice + ~620 di test (30 test); blocco 2 ~340 righe di test (13
test) + 4 righe nella tabella della fotografia. Suite e confronto lungo la sequenza in §4.0.1: dopo il blocco 1
`Ran B_FP + 30`, dopo il blocco 2 `Ran B_FP + 43`, con `B_FP` letto dall'ESITO all'avvio (stima `4876` [S], §4.0.1);
confronto finale atteso `compared 1113 runs: 104 difference lines` [I: dipende dai blocchi BI 3 e VA 2 non ancora
eseguiti].

---

## 1. Problema e comportamento attuale

### 1.1 La finestra di contatto usa la portata maggiore [V]

- `Logic/Contact_Scheduler.py` `contact_windows` (`:1023-1100`): `outer = max(portate)` (`:1067`), `inner = min`
  (`:1068`); **una finestra per ogni intervallo** di `range_intervals(legs_a, legs_b, outer)` (`:1070`, ciclo
  `:1083-1098`). Gli intervalli entro la portata minore (`mutual_intervals`, `:1075`) sono calcolati ma nella finestra
  entra solo il **primo** contenuto (`_first_contained`, `:1086`, `:1117-1126`) come `t_mutual_start/t_mutual_end`.
- `ContactWindow` (`:196-240`): `t_start/t_end`, `t_cpa/distance_cpa` (massimo avvicinamento dell'**intera**
  finestra), `range_a/range_b`, `t_mutual_*`, `first_detector`. **Non porta il sensore** ne' gli intervalli
  successivi al primo nella portata minore.
- Le finestre sono spezzate agli istanti di decollo/atterraggio (`_pair_windows`, `:1492-1524`), ritagliate dal G4a
  (`trim_contact_window`, `:1129-1172`, chiamata da `Session_Simulator._trim_busy`, `Logic/Session_Simulator.py:1296-1329`,
  e da `reschedule`, `:2832-2842`), ordinate per `(t_start, id_a, id_b)` (`:1487`).

### 1.2 Una estrazione per finestra e direzione [V]

- `Logic/Engagement_Resolver.py` `_detect` (`:2091-2110`): finestre in ordine `(t_start, id_a, id_b, t_end)`, per
  ognuna `_detect_direction` a->b poi b->a.
- `_detect_direction` (`:2112-2169`): esce **senza estrarre** solo se l'osservatore non ha portata (`:2114-2115`) o e'
  un aereo a terra (`:2117-2120`); altrimenti **una** estrazione (`self._draw()`, `:2139`) anche quando il bersaglio non
  entra mai nella portata propria (Pd 0, `:2141`); `distance = window.distance_cpa` (`:2140`): la distanza minima
  **dell'intera finestra**, anche se cade in un passaggio diverso da quello del rilevamento.
- Istante (`_detection_time`, `:2219-2245`): con i tratti, il primo istante in cui la distanza scende sotto il raggio
  estratto, nel **primo** intervallo che tocca la finestra (`range_intervals` a `:2233`).
- Candidato al tiro (`:2159-2164`): `t_ready = istante + profilo.total`, ammesso se `t_ready <= window.t_end`, con
  `_Candidate.t_end = window.t_end`: un rilevamento nel primo passaggio fa sparare anche nel secondo (traccia
  mantenuta fra i passaggi), finche' l'arma e' a portata (`_range_entry`, `:3011`; usi di `candidate.t_end` a
  `:2502`, `:2955`, `:3035`, `:3084`).
- Contratto RNG scritto nel modulo (`:416-421`, la parentesi "(invariato dalla D-5)" a `:419`): prima tutte le
  estrazioni di rilevamento nell'ordine canonico, a->b poi b->a, una per direzione; poi una per colpo non intercettato.
  La tempra usa lo stream separato `breakpoint_rng` (`Session_Simulator.py:2783-2785`).

### 1.3 Dove la regola e' gia' rispettata e dove no [V]

| Caso | Oggi | Regola |
|---|---|---|
| osservatore con la portata **maggiore** (o uguale, o unica) | una finestra per ogni ingresso nel suo volume: un'estrazione per passaggio | rispettata |
| osservatore con la portata **minore**, un solo passaggio nella finestra | un'estrazione, distanza della finestra = distanza del passaggio (il minimo cade nell'unico passaggio) | rispettata |
| osservatore con la portata **minore**, **>= 2 passaggi** nella stessa finestra | **una** estrazione, con la distanza minima fra tutti i passaggi; candidato valido fino alla fine della finestra | **violata** |
| come sopra con la D-5 accesa | permanenza = **somma** dei passaggi (`_exposure_time`, `:2247-2277`, somma a `:2262-2269`) | **violata** |
| pianificatore (`Path.compute_detection_metrics`) | raggruppa per minaccia i tratti **contigui** (`CROSSING_JOIN_TOLERANCE_S` = 1e-6 s, `Logic/Air_Route_Manager.py:35-38`, uso `:1190`): tratti non contigui = attraversamenti distinti | rispettata (attraversamento per attraversamento) |

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
- La D-5 (blocco A, `8943b292`, interruttore `D5_DWELL_TIME` spento, `:522-529`) lo **aggrava** nel solo caso
  multi-passaggio: `_exposure_time` somma i passaggi (`:2262-2269`). Con un passaggio solo e' corretta.
- Il lettore del dwell [V]: `Session_Simulator.engage` (`:2707`) passa `dwell_time_for=ER.registry_dwell_time` solo con
  `D5_DWELL_TIME` acceso (`:2770-2772`); nel risolutore e' `self.dwell_time_for` (`:1838`), letto in `_detect_direction`
  con `_check_dwell(self.dwell_time_for(observer.asset, target.asset, mode))` e il modo `GROUNDED_DETECTION_MODE` o
  `detection_mode_for(target.asset)` (`:2129-2133`). `registry_dwell_time` (`:1206-1221`) chiama
  `observer.detection_dwell_time(mode)` (`Asset/Mobile.py:1692`), lettura pura del registro (nessuna estrazione); None
  se il sensore vincente non dichiara `dwell_time_s` (oggi lo dichiarano solo i 10 EWR, `Asset/Vehicle_Data.py:4659-5058`).
- Il blocco B della D-5 (`Logic/Air_Route_Manager.py`, committato `effb0dcf`) e' gia' per attraversamento.

### 1.6 Altri chiamanti [V]

- `contact_windows`/`schedule_contacts`/`trim_contact_window`/`ContactWindow` sono usati **solo** da
  `Logic/Session_Simulator.py` (`:1314`, `:2390`, `:2841`) e dai test; nessun altro modulo del core li importa
  (`Mission_Adapter`, `Session_Validator`, `Session_Types` usano altre funzioni o solo `TIME_EPS`).
- `Logic/Weapon_Delivery.py` **non** usa ne' finestre ne' estrazioni: `_evaluate_exposure` (`:433`) e' una stima
  deterministica di pianificazione. Non tocca.
- `Logic/Air_Route_Manager.py` usa solo `detection_probability`/`dwell_factor` del risolutore (metriche). Non tocca
  (FP-9). Nessun codice di produzione fuori da `Air_Route_Manager.py` legge `max_detection_probability` o
  `detection_tracts` (ricerca del 2026-11-08: solo `Logic/Air_Route_Manager.py:1073-1220` e i test).
- `first_detector` e `is_mutual` **non** sono letti fuori dallo scheduler; `t_mutual_*` solo dai ripieghi senza tratti
  del risolutore (`:2239-2245`, `:2271-2277`).
- `EngagementResult.detections` e' letto in produzione solo da `_detection_time_of` (`:3229-3235`, regola R-INT,
  chiamato solo da `_in_time`, `:3307`) e nei test (`Test_Session_Scenarios.py:1249`, `:1375-1380`,
  `Test_Session_Scenarios_S32.py:122`); **non** e' nella fotografia (`Test/Scenario_Baseline.py`, nessun riferimento ai
  `Detection`).
- `_exposure_time` e `_detection_time` sono chiamati solo da `_detect_direction` (`:2136`, `:2147`); nessun test li
  chiama direttamente (ricerca del 2026-11-08).
- Adapter DCS: nessun riferimento. Il core resta indifferente al simulatore.

### 1.7 Il manuale non dichiara il limite [V]

Ricerca in `Analysis/Document/Manuale_Motore_DES/`: nessun passo dichiara "una sola estrazione per finestra anche con
piu' passaggi nel volume minore". Il capitolo 3 §3.5 (`04_Strato1_Scheduler_Contatti.md:195-201`) dice che
`[t_mutual_start, t_mutual_end]` e' l'intervallo "da quel momento entrambi si vedono", senza dire che e' solo il
**primo**; il capitolo 4 §4.2 (`05_Strato2_Risolutore_Ingaggio.md:144-147`) descrive "una sola estrazione" come pregio;
l'atlante (`11a_Atlante_Risolutore.md:1310`) dice "una per finestra e direzione". Il limite va aggiunto al capitolo 9
(`10_Limiti_Estensioni_Divergenze.md`) come storico.

### 1.8 Sonda P-0 (sola lettura) — ESEGUITA il 2026-11-07 sul ProArt

Script versionato: `Analysis/Document/Rapporti/Sonde_Finestre_Passaggio/probe_passes.py` (istruzioni in `LEGGIMI.md`).
Avvolge `_detect_direction` e `run` del risolutore **senza cambiarne il comportamento**, aggiunge al riassunto di ogni
esecuzione una voce `probe_passes` e riesegue `Scenario_Baseline --compare` con `--ignore probe_passes`.

**Esito (2026-11-07, ProArt)** [V: `esito_p0.txt`; `.ai-run/sonde_passaggi/p0/stats.json` sul ProArt]:

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

- **Confronto invariato**: le 20 righe di differenza sono tutte `NEW S32-DWELL/...`, **0 righe DIFF**.
- **Nessuna direzione a piu' passaggi**: `multi` 0 su 33 910 direzioni con estrazione (1258 ingaggi, 28 214 salve).
- **Istogramma**: 32 964 direzioni con un passaggio (97,2 %), 946 con **zero** passaggi (2,8 %: il bersaglio non entra
  mai nella portata propria dentro la finestra, estrazione a Pd 0). `without_legs` 0: in sessione i tratti ci sono
  sempre. P-0 **non** distingue i passaggi di durata zero (rotta tangente: `range_intervals` tiene gli intervalli con
  s1 == s2: scarta solo `s2 < s1`, `Contact_Scheduler.py:926-930` [V]): un passaggio tangente conta come 1. Li conta P-1 (§4.3).
- **R-INT**: `rint_last_not_earliest` 0: nessuna coppia con rilevamenti a istanti diversi. P-0 **non** misura la
  differenza introdotta da FP-5 (d) (lancio fuori dal passaggio del rilevamento): la misura P-1.
- **Salve dopo il passaggio (FP-3 (a))**: 151 salve, in **44 esecuzioni tutte della fotografia**, di un osservatore
  con portata minore e un solo passaggio, partite dopo la fine di quel passaggio: S13 (`S13-2` 2, `S13-4` 4), S14
  (`S14-4` 2), S21 (`S21-3/control` 3, `S21-3/parked` 8, `S21-5/control` 4, `S21-5/parked` 1, `S21-7/control` 2,
  `S21-7/parked` 1), S24-ORBIT (`S24-ORBIT-0/full` 1), S26-BINGO (32 esecuzioni: tutti gli 8 semi per le 4 varianti
  `engagement_fuel_off`, `none`, `switch_off`, `transfer_continue`, 121 salve), S28-CLASS (`S28-CLASS-2/self_defence` 1,
  `S28-CLASS-2/self_defence_off` 1).

**Lettura.** L'attesa qualitativa scritta prima della sonda [I] ("direzioni multi probabili dove un aereo torna su un
sito") e' **smentita**: in nessuno scenario della fotografia un bersaglio rientra nel volume proprio dell'osservatore
con la portata minore restando nella stessa finestra. Conseguenze: (1) con la regola accesa la parte "passaggi
multipli" non cambia nessuna esecuzione della fotografia; (2) il comportamento dei passaggi multipli e' provabile
**solo** su S33-PASSES e nei test unitari; (3) FP-3 (a) vale anche per le direzioni a un passaggio: con la regola
accesa cambiano, per FP-3 (a), **al piu' le 44 esecuzioni** elencate (probabilmente quasi tutte [I]); a queste si
aggiungono le eventuali `RINT_D` di FP-5 (d), che P-0 non misura (attesa complessiva NON misurata, §4.3).

### 1.9 Precisazioni [V]

- Un'estrazione avviene anche se il bersaglio non entra mai nella portata propria (Pd 0): con zero passaggi la
  regola nuova non cambia nulla (resta un'estrazione).
- **Difetto latente R-INT, precedente**: `_detection_time_of` (`:3229-3235`) costruisce un dizionario
  `{(osservatore, bersaglio): istante}` in cui vince l'**ultimo** rilevamento in ordine di lista (il dizionario
  sovrascrive), non il primo. Con un'estrazione per passaggio diventerebbe frequente. Trattato da FP-5 (d) a regola
  accesa (§2.6); a regola spenta resta.
- `_pair_windows` divide gia' oggi un passaggio fisico a cavallo di un decollo/atterraggio in due finestre (due
  estrazioni): limite precedente, con stato a terra diverso nelle due parti; non cambia (§5.2).

### 1.10 Come il DES rappresenta un attacco CAS a piu' bersagli [V, verifica del 2026-11-07]

- **Il moto di un aereo e' la spezzata dei punti della missione**, a velocita' costante per arco: `Mission_Adapter`
  prende la rotta di riferimento (`Mission.route` o la spezzata dei `MissionWaypoint`), applica l'offset di formazione e
  la scompone in tratti con `Contact_Scheduler.route_legs` (`Logic/Contact_Scheduler.py:383`), piu' i tratti fermi
  delle attese e della presenza prima/dopo. Dopo un bingo o un disingaggio i tratti sono sostituiti dal rientro
  (`_legs_after_bingo`, `Logic/Session_Simulator.py:1628`; G4b).
- **Nessun modulo genera manovre d'attacco** (pop-up, giro sul bersaglio, riattacco): i tratti passano sopra un
  bersaglio **solo se** il pianificatore della missione ha messo un punto li'. Il bersaglio di una missione e' **uno**
  (`Mission.target`); i punti ATTACK possono essere piu' d'uno ma il motore ne legge solo l'ultimo, e solo per la ROE
  `priority_designated`; il fixture ne ammette uno solo (`attack_waypoint`, `Test/Scenario_Fixtures.py:710-734`).
- **Il tiro non dipende dalla rotta**: il controllo del fuoco spara quando l'arma e' a portata lungo la spezzata
  (`_range_entry`); l'ordine degli attacchi lo decidono priorita' e portate.
- **Geometria**: nel DES il volume proprio e' una **sfera** (`range_intervals` risolve |Δr + Δv s|^2 = R^2 in 3D,
  `Contact_Scheduler.py:874-935`); nel pianificatore e' un **cilindro**. Entrambi **convessi**: un tratto rettilineo li
  attraversa al piu' una volta. Due passaggi non contigui richiedono almeno un cambio di direzione. Forme **non
  convesse** (portata minima, cono di silenzio) darebbero due passaggi su un solo tratto: v.
  `Proposta_Allineamento_Volumi_DES_Pianificatore.md` §2.3 (con FP-10 (c) un'uscita <= dwell si unirebbe).

Conseguenza per la variante CAS di S33 (§4.2): la geometria usa una rotta a punti con un punto sopra ciascun bersaglio
e una virata dopo il bersaglio fuori volume, la forma che il DES sa rappresentare.

### 1.11 Intervalli adiacenti oggi [V]

- `range_intervals` (`Logic/Contact_Scheduler.py:874-935`) fonde gli intervalli con `_merge_intervals` (`:938-952`)
  **solo** se si toccano entro `TIME_EPS` = 1e-9 s (`:88-92`). Due intervalli separati da un'uscita di qualunque durata
  maggiore di 1e-9 s restano distinti.
- Le **finestre** (`contact_windows`, `:1070`) usano gli stessi intervalli con la portata maggiore: l'osservatore con la
  portata maggiore riceve gia' oggi **due estrazioni** per un'uscita di pochi secondi (due finestre).
- Il pianificatore unisce due tratti dello stesso volume solo se il secondo entra entro `CROSSING_JOIN_TOLERANCE_S` =
  1e-6 s dall'uscita del primo (`Logic/Air_Route_Manager.py:35-38`, uso `:1190`): tolleranza **numerica**.
- Con FP-10 (c) **decisa**, nel solo risolutore, con la FP e la D-5 accese e il dwell dichiarato dal sensore, un'uscita
  <= dwell unisce i passaggi; finestre e pianificatore restano con la tolleranza numerica (limite dichiarato, §5.2).

---

## 2. Alternative e decisioni

### 2.1 (A) Minimo: un solo passaggio nella permanenza, una estrazione come oggi

`_exposure_time` usa il passaggio che contiene `t_cpa` (in subordine il piu' lungo) invece della somma; nessuna
estrazione nuova. Non e' la regola dell'utente (resta una sola occasione per finestra): **assorbita** come
comportamento della D-5 in ogni stato dell'interruttore FP (FP-6 (a), §2.7).

### 2.2 Dove calcolare i passaggi (FP-1) — DECISA dall'utente il 2026-11-07: B-R

| Opzione | Dove | Esito |
|---|---|---|
| B-S1 | scheduler, finestre per direzione/sensore | scartata: cambia numero e ordine delle finestre per tutte le coppie con portate asimmetriche (episodi G4a `_episodes`, `_trim_busy`, `counter` degli stream, stream dell'ingaggio): fotografia da rifare senza beneficio misurabile (P-0: 0 direzioni multi, 32 964 a un passaggio da sdoppiare) |
| B-S2 | scheduler, campo `ContactWindow.mutual_intervals` | scartata: tocca `ContactWindow` (uguaglianza e `repr` di tutte le finestre), `contact_windows`, `trim_contact_window`; due calcoli di tratti da tenere allineati; le finestre costruite a mano nei test non hanno il campo |
| **B-R** | **risolutore**: per la direzione, gli intervalli di `range_intervals(tratti_oss, tratti_bers, portata_propria)` che toccano la finestra (tramite `_own_intervals`, VA-6 (a)) | **DECISA**: modifica locale allo strato 2 (come la D-5, DW-4); finestre, episodi, scheduler invariati; in sessione i tratti ci sono sempre (`all_legs`, `Session_Simulator.py:2397-2409`; P-0 `without_legs` 0). Limite: senza tratti (chiamate dirette) i passaggi non si calcolano, un'estrazione come oggi |

### 2.3 Ordine delle estrazioni nuove (FP-2) — DECISA dall'utente il 2026-11-07: O3

| Opzione | Contenuto | Esito |
|---|---|---|
| O1 in linea | nello stream dell'ingaggio: per finestra, a->b passaggi 1..n, poi b->a | scartata: ogni estrazione successiva slitta, il confronto con la regola accesa diventa illeggibile nelle sessioni con rientri |
| O2 in coda | primo passaggio nella posizione di oggi; dal secondo dopo tutte le estrazioni di rilevamento | scartata: le estrazioni di danno slittano comunque; codice in due giri |
| **O3 stream separato** | primo passaggio dallo stream dell'ingaggio, **nella posizione di oggi**; passaggi 2..n da `pass_rng`, nell'ordine (finestra canonica, a->b poi b->a, passaggio) | **DECISA**: lo stream dell'ingaggio resta **identico in ogni stato dell'interruttore**; precedenti nel progetto (tempra: `breakpoint_rng`); rende verificabili S33 e il test 4 |

### 2.4 Distanza per passaggio (FP-4) — DECISA dall'utente il 2026-11-07: (a)

| Opzione | Contenuto | Esito |
|---|---|---|
| **(a) CPA del passaggio** | `closest_point_of_approach` sui tratti ritagliati al passaggio (unito, FP-10), per ogni passaggio | **DECISA**; con un solo passaggio il risolutore usa il percorso di oggi (distanza della finestra), identico al bit |
| (b) distanza della finestra per tutti | come oggi | scartata: un passaggio lontano "eredita" la distanza del passaggio migliore |
| (c) finestra per il primo, propria per gli altri | continuita' col passato | scartata: incoerente, il primo passaggio usa la distanza di un altro |

### 2.5 Finestra d'ingaggio per passaggio (FP-3) — DECISA dall'utente il 2026-11-07: (a)

| Opzione | Candidato di un passaggio valido fino a | Esito |
|---|---|---|
| **(a) fine del passaggio** | `hi` del passaggio (al piu' `window.t_end`), anche con un solo passaggio | **DECISA**: all'uscita dal volume proprio la traccia e' persa; al rientro serve un nuovo rilevamento |
| (b) inizio del passaggio successivo | `lo` del passaggio successivo; l'ultimo fino a `window.t_end` | scartata: lascia la traccia valida fuori dal volume fino al rientro; motivata solo dalla compatibilita' con la fotografia |
| (c) fine della finestra | `window.t_end` per tutti (oggi) | scartata: il rilevamento del primo passaggio continua a far sparare nel secondo |

**Applicazione** (vincolante per il piano, §4.1.1):
- **tutte le direzioni con passaggi calcolabili** dell'osservatore con la portata **minore**, anche con un passaggio
  solo; con FP-10 il passaggio e' quello unito (il candidato vale fino alla fine del passaggio unito);
- osservatore con la portata **maggiore** (o uguale, o l'altro senza sensore): il passaggio coincide con la finestra,
  la fine resta `window.t_end` (nessun ricalcolo, per evitare differenze numeriche fra tratti dello scheduler e del
  risolutore);
- **senza tratti** (chiamate dirette): resta `window.t_end`;
- passaggio **ritagliato** dalla finestra: termina al massimo a `window.t_end` (`hi`);
- il candidato e' ammesso solo se `t_ready <= hi` (reazione completata prima dell'uscita);
- una salva **gia' lanciata** prima dell'uscita non cambia (la fine del candidato limita solo l'istante di lancio,
  `:2502`, `:2955`, `:3035`, `:3084`); si interrompe solo il lancio di salve **nuove** dopo l'uscita.

**Numeri di P-0**: 151 salve in **44 esecuzioni della fotografia** partono oggi dopo la fine dell'unico passaggio di un
osservatore con portata minore (S26-BINGO 32 esecuzioni e 121 salve, S21 6 e 19, S13 2 e 6, S14 1 e 2, S28-CLASS 2 e 2,
S24-ORBIT 1 e 1): con la regola **accesa** sono queste (al piu') le esecuzioni che cambiano per FP-3 (a).

### 2.6 Istante di rilevamento per la regola R-INT (FP-5) — DECISA dall'utente il 2026-11-08: (d)

**Ruoli nella regola R-INT**:

| Ruolo | Chi, nell'esempio | Che cosa conta per R-INT |
|---|---|---|
| lanciatore | un aereo (o una nave) che lancia un colpo intercettabile | istante di lancio `t_launch` e posizione a quell'istante (L1) |
| bersaglio del rilevamento | lo stesso lanciatore, visto dall'intercettore | i `Detection` dell'intercettore sul lanciatore |
| intercettore | un asset della forza attaccata con arma `Anti_Missile` (regola D, `Asset/Mobile.py:203-208`) | ferma il colpo solo se t_traccia + tau <= t_impatto (`_in_time`, `Logic/Engagement_Resolver.py:3292-3316`) |
| osservatore | lo stesso intercettore (rilevamento **per asset**: `_detection_time_of`, `:3229-3235`) | i suoi passaggi nel proprio volume e i suoi rilevamenti |
| colpo da intercettare | il colpo M lanciato contro un'unita' U | "intercettabile" se `ShotSpec.interceptable` (`Logic/Fire_Control.py:836-842`) e, con `BI_AD_TARGET_RULE` acceso, ammesso dal dominio dell'intercettore (`_admissible`, `:3196-3202`, filtro prima di L1 e R-INT, `:3396-3397`) |

Regola L1 (precedente, invariata): un colpo lanciato **dentro** il volume d'intercettazione V_I dell'intercettore non si
intercetta mai (`_may_intercept`, `:3204-3227`). La ZSU-57-2 di S32/S33 **non** e' un intercettore (nessun
`Anti_Missile`): S33 non puo' provare FP-5 in sessione; la prova e' nei test unitari 13, 21, 22, 29.

| Opzione | Contenuto | Esito |
|---|---|---|
| (a) il primo istante | "rilevato entro il lancio" = esiste un rilevamento <= `t_launch` | scartata: con FP-3 (a) fa "vedere" lanci avvenuti dopo la perdita della traccia (esempio sotto, lancio a 300 s) |
| (b) invariato | l'ultimo in ordine di lista anche con la regola accesa | scartata: un rilevamento del secondo passaggio sostituisce quello del primo, un lancio nel primo passaggio diventa "non visto" |
| (c) correzione separata | difetto latente corretto in un'altra Proposta | scartata: la regola accesa renderebbe il difetto frequente proprio qui |
| **(d) legata al passaggio** | il lancio e' "visto" solo se l'intercettore ha rilevato il lanciatore (rilevamento <= `t_launch`) **nel passaggio che contiene `t_launch`** (passaggi dopo l'unione di FP-10); nessun passaggio che contiene `t_launch` = non visto (percorso geometrico, tau = `total`). Spento l'interruttore: l'ultimo rilevamento in ordine di lista, come oggi | **DECISA**: coerente con FP-3 (a) (traccia persa all'uscita dal volume) |

**Esempio** (da usare nei test, §4.1.5 test 13): passaggi del lanciatore nel volume proprio dell'intercettore
[200, 254] s e [380, 434] s; rilevamenti a **210** s e **390** s.

| Lancio a | Passaggio che lo contiene | Rilevamento nel passaggio | (d), decisa | oggi / (b) (ultimo = 390) | (a) (primo = 210) |
|---|---|---|---|---|---|
| 230 s | [200, 254] | 210 | **visto** (210 <= 230) | non visto (390 > 230) | visto |
| 300 s | nessuno | — | **non visto** | non visto | visto |
| 385 s | [380, 434] | 390 | **non visto** (390 > 385) | non visto | visto |
| 400 s | [380, 434] | 390 | **visto** (390 <= 400) | visto | visto |

"Non visto" non vuol dire "non intercettato": l'intercettore scopre il colpo dalla geometria quando entra nel suo
raggio aereo (`_round_track_time`, `:3254-3290`) e reagisce con tau = `total` invece di `refire_interval`.

**Interazione con la BI** [V sul codice integrato]: con `BI_AD_TARGET_RULE` acceso i missili aria-superficie tattici
(Maverick & C.) non arrivano a `_in_time` contro le difese terrestri (filtro `_admissible` prima di L1/R-INT): R-INT, e
con essa FP-5 (d), resta in uso per **cruise/balistici** e, contro i **navali**, per gli **antinave**. A interruttori
BI e FP accesi entrambi l'istante usato da "vede il lancio" e' quello di FP-5 (d): e' un'interazione di logica, non
solo di riga (rilievo 5 della revisione di coerenza), dichiarata qui e in §5.2.

**Ripiego senza tratti** (conseguenza del limite di B-R, non una regola nuova): se per la coppia i passaggi non sono
calcolabili (chiamate dirette senza `legs`), R-INT usa la regola precedente (ultimo in lista), come ogni altra parte
della FP senza tratti.

### 2.7 Interazione con la D-5 (FP-6) — DECISA dall'utente il 2026-11-08: (a)

> **Dopo la pulizia (2026-11-13)**: la scelta "passaggio che contiene `t_cpa`, in subordine il piu' lungo" valeva solo
> a FP spenta ed e' stata tolta con il ramo spento. Oggi, con i tratti, ogni estrazione ha la permanenza del proprio
> passaggio (unito, FP-10) e 0 se nessun passaggio tocca la finestra; `_exposure_time(window, own_range,
> other_range)` resta solo come ripiego senza tratti. La tabella sotto e' il testo storico della decisione.

| Opzione | Contenuto | Esito |
|---|---|---|
| **(a) un passaggio, incondizionata dentro la D-5** | con la D-5 accesa e FP spento la permanenza e' quella del **passaggio che contiene `t_cpa`** della finestra (in subordine il piu' lungo, il primo a pari durata), **mai la somma**; nessun interruttore nuovo (vale in ogni stato di `FP_PER_PASS_DETECTION`, dentro `D5_DWELL_TIME`). Con FP acceso ogni occasione ha la permanenza del proprio passaggio (unito, FP-10) | **DECISA**: la somma viola la regola dell'utente; nessuna esecuzione della fotografia accende la D-5; le 20 di S32 hanno un passaggio per direzione (P-0), quindi restano uguali (verifica in §4.1.6) |
| (b) somma finche' FP e' spento | lasciare la somma con FP spento | scartata: la D-5 violerebbe la regola finche' FP non e' acceso |
| (c) dietro `FP_PER_PASS_DETECTION` | la correzione solo con FP acceso | scartata: lega una correzione della D-5 a un interruttore temporaneo |

Esempio: dwell di 600 s, passaggi di 54 s e 54 s (CPA nel primo). Oggi: g = 108/600 = 0,18 su un'estrazione. FP
spento, FP-6 (a): g = 54/600 = 0,09 su un'estrazione. FP acceso: g = 0,09 su ciascuna di due estrazioni.

Il punto 8 del blocco 1 resta come scritto nella versione del 2026-11-07 (ramo con i tratti di `_exposure_time`); in
piu' un test diretto del ripiego `next(..., longest)` (test 23, rilievo della revisione) e l'allineamento del docstring
D-5 del modulo (che oggi dice "somma", `:156-160`). **Nota**: questa e' l'unica parte del blocco 1 che cambia un
comportamento gia' committato **senza** l'interruttore FP; e' dentro l'interruttore della D-5 (spento) per decisione
dell'utente. Il commento dell'interruttore FP non dice quindi "spento = tutto come prima" senza questa eccezione.

### 2.8 Interruttore (FP-7) — DECISA dall'utente il 2026-11-08: (a), TEMPORANEO

> **Interruttore eliminato il 2026-11-13** (`Proposta_FP_Pulizia_Interruttore.md`): `FP_PER_PASS_DETECTION` e i rami
> `pass_rng is None` non esistono piu'; `Session_Simulator` passa sempre `pass_rng`. La tabella sotto e' storica.

| Opzione | Contenuto | Esito |
|---|---|---|
| **(a)** | `Engagement_Resolver.FP_PER_PASS_DETECTION = False`, letto da `Session_Simulator.engage` che passa `pass_rng` solo se acceso; nel risolutore la regola e' attiva se e solo se `pass_rng` non e' None | **DECISA**: stesso schema della D-5; a interruttore spento la chiamata a `resolve_engagement` e' letteralmente quella di prima |
| (b) costante letta dentro `_detect_direction` | agisce anche sulle chiamate dirette | scartata: serve comunque uno stream per O3 |
| (c) in `Session_Simulator` come gli F*/G* | il risolutore non lo vede senza importare l'orchestratore | scartata |

**Temporaneo** (criterio dell'utente del 2026-11-08: un interruttore si tiene solo se lo stato precedente e' un'alternativa
valida; la regola FP sostituisce una soluzione superata). **Criterio di rimozione**, scritto anche nel commento
dell'interruttore: (1) sonda P-1 eseguita; (2) lettura delle esecuzioni cambiate da parte dell'utente; (3) fotografia
nuova installata **dall'utente**; (4) un **blocco di pulizia** dedicato (§4.3, descritto in breve, non pianificato qui)
che elimina interruttore e vecchio ramo. Fino ad allora il default resta spento.

### 2.9 Scenario (FP-8) — DECISA dall'utente il 2026-11-08, MODIFICATA; D-5 nelle varianti accese confermata la sera

| Opzione | Contenuto | Esito |
|---|---|---|
| prima stesura | 8 varianti x 5 semi = 40 (con `dwell_*` e `cas_dwell_*`, dwell di test 600 s) | scartata: con il dwell stimato della ZSU (2 s [S]) e passaggi di 50-67 s il fattore D-5 e' g = 1: le varianti con dwell sarebbero identiche a quelle senza |
| (b) 2 varianti x 5 semi | solo `off`/`on` | scartata: non prova la geometria CAS chiesta dall'utente |
| **4 varianti x 5 semi = 20** | `off`, `on` (geometria di **rientro**), `cas_off`, `cas_on` (geometria **CAS**); `off`/`cas_off` = stato precedente (FP e D-5 spente, nessun dwell dichiarato); `on`/`cas_on` = **configurazione finale** (FP **e D-5** accese, dwell della ZSU 2 s [S] dichiarato) | **DECISA** |

- **Dwell della ZSU in S33: 2 s, STIMA [S] dell'utente** (osservatore umano piu' ottica: la "predizione" del cervello
  aggiorna la traccia in continuo). Da dichiarare [S] nel codice dello scenario (costante `ZSU_DWELL_S`) e nel
  rapporto. **Conferma dell'utente (2026-11-08 sera)**: nelle varianti `on` e `cas_on` lo scenario accende **anche** la
  D-5 (`Engagement_Resolver.D5_DWELL_TIME = True`, con `patch.object`, ripristinato all'uscita anche in caso di errore)
  e dichiara il dwell sulla ZSU (`F.declare_dwell(zsu, {'air': ZSU_DWELL_S})`), per esercitare in sessione la
  configurazione finale: lettore del dwell (`registry_dwell_time` -> `_dwell_of`), unione FP-10 valutata (e **non**
  applicata: uscite fra i passaggi 126-130 s nel rientro e 103-104 s nella CAS, molto maggiori di 2 s) e fattore
  **g = 1** (passaggi di 50-67 s > 2 s). Le varianti `off` e `cas_off` restano come prima (FP e D-5 spente, nessun dwell
  dichiarato): sono il confronto con lo stato precedente.
- **Perche' gli esiti attesi `on` contro `off` non cambiano** [V sul codice, 2026-11-08 sera]: la D-5 non fa estrazioni
  (`_detect_direction`, blocco `:2129-2137`: solo letture di registro e aritmetica; `registry_dwell_time`, `:1206-1221`,
  e `declare_dwell`, `Test/Scenario_Fixtures.py:306-338`, sono letture pure); con g = 1 `dwell_factor` restituisce
  esattamente `1.0` (`min(1.0, permanenza / dwell)`, `:1181-1203`) e `factor * 1.0 == factor` al bit, quindi Pd, raggio
  estratto, istanti e candidati sono quelli di FP accesa senza D-5. In sessione `D5_DWELL_TIME` e' letto **solo** da
  `Session_Simulator.engage` (`:2770-2772`); l'altro lettore (`Air_Route_Manager.compute_detection_metrics`, `:1132`) e'
  nel pianificatore delle rotte (`calcRoute`), che la sessione non chiama. Unica differenza visibile: le `Detection`
  della ZSU in `on`/`cas_on` portano `dwell_time_s` = 2.0 e `exposure_s` valorizzata (campi non nella fotografia).
  Premessa da asserire (test S33 12): g = 1 in **ogni** direzione della ZSU con distanza minima entro la portata; se
  una finestra spezzata o un passaggio di durata quasi nulla desse g < 1, la Pd di quella direzione cambierebbe per
  effetto della D-5 e l'esecutore si ferma (§4.2.1).
- Lettore del dwell sugli asset di S33 [V, sonda di sola lettura del 2026-11-08 sera]: senza `declare_dwell`
  `registry_dwell_time` restituisce None per ZSU-57-2 (modo `air`), A-10C (modo `ground`) e BMP-2 (modo `air`): nel
  registro dichiarano `dwell_time_s` solo i 10 EWR (`Asset/Vehicle_Data.py:4659-5058`); dopo `declare_dwell(zsu,
  {'air': 2.0})` la ZSU da' 2.0 nel modo `air` e None nel modo `ground`; un asset ricostruito non eredita la
  dichiarazione (attributo d'istanza).
- Geometria di **rientro**: S32 (ZSU in (1000, -300), 3 BMP-2, 4 A-10C a 3000 m) con rotta di andata, uscita a 14 km e
  ritorno: due passaggi nei 6 km della ZSU, sempre entro gli 80 km dell'A-10C (una finestra).
- Geometria **CAS**: gli stessi 4 A-10C attaccano in sequenza **3 bersagli a terra**, due dentro la copertura visiva
  della ZSU e uno fuori (13 km): **una** finestra per coppia A-10C/ZSU, **due passaggi non contigui** (uscita ~104 s).
- S33 e' l'**unico** banco di prova in sessione dei passaggi multipli (FP-2, FP-3, FP-4) e della configurazione finale
  FP + D-5 nel ramo "nessuna unione, g = 1". **Non** prova FP-5 (la ZSU non ha `Anti_Missile`), l'unione FP-10
  effettiva ne' una permanenza per passaggio con g < 1: queste sono coperte dai test unitari (§5.1).

### 2.10 Pianificatore (FP-9) — DECISA dall'utente il 2026-11-08: (a)

| Opzione | Contenuto | Esito |
|---|---|---|
| **(a) nessun cambio** | `Path.compute_detection_metrics` resta per attraversamento; `max_detection_probability` = massimo sui tratti | **DECISA**, limite dichiarato in §5.2 |
| metrica cumulativa ora | `cumulative_detection_probability` = 1 - prodotto(1 - Pd) sugli attraversamenti | rinviata: si aggiunge in una Proposta dedicata quando ci sara' un consumatore (oggi nessun codice di produzione fuori da `Air_Route_Manager.py` legge `max_detection_probability` o `detection_tracts` [V, §1.6]) |

Esempio: due attraversamenti a Pd 0,4: metrica 0,4 (il peggiore), DES con la regola 1 - 0,6^2 = 0,64. La divergenza
esiste gia' oggi per l'osservatore con la portata maggiore (due attraversamenti = due finestre).

**Nota dell'utente (2026-11-08), NON verificata nel codice da chi pianifica, riportata come tale**: `Air_Route_Manager`
pianifica con 3 criteri: (1) evita ogni volume con segmenti tangenti ai cilindri di minaccia/rilevamento; (2) come (1)
con modifica di quota; (3) attraversa il cilindro solo per un tempo massimo inferiore al tempo di risposta della
minaccia. Vicino al waypoint iniziale e al target non considera le minacce. Col criterio 3 una rotta puo' avere piu'
edge che attraversano lo stesso volume in momenti distinti (caso raro). Moduli futuri useranno quelle API: la metrica
cumulativa si aggiunge allora.

### 2.11 Passaggi molto ravvicinati: unione (FP-10) — DECISA dall'utente il 2026-11-08: (c)

| Opzione | Contenuto | Esito |
|---|---|---|
| (a) nessuna tolleranza di modello | passaggi distinti se separati da piu' di `TIME_EPS` | scartata: un'uscita di pochi secondi raddoppia l'occasione anche quando la traccia non si perde |
| (b) tolleranza fissa nel risolutore | `FP_PASS_JOIN_GAP_S` = X s [S] | scartata: costante di modello senza dato |
| **(c) tolleranza legata al sensore** | passaggi separati da un'uscita **<= dwell del sensore osservatore** si **uniscono** in un passaggio: una estrazione, CPA del passaggio unito, permanenza dall'inizio del primo alla fine dell'ultimo, candidato valido fino alla fine del passaggio unito (FP-3 (a)) | **DECISA**. Motivazione dell'utente: il tracciamento e' "predittivo", una perdita di segnale piu' breve del tempo di aggiornamento (dwell) non interrompe la traccia |
| (d) come (b) anche per finestre e pianificatore | stessa X ovunque | scartata: cambia le finestre di tutte le coppie, fotografia da rifare |

**Sotto-decisioni** (DECISE dall'utente il 2026-11-08):
1. **Sensore senza dwell dichiarato** (oggi tutti tranne i 10 EWR; DW-9 estendera' ad altri): **nessuna unione** (come
   la vecchia (a), sola `TIME_EPS`); nessun valore inventato.
2. L'unione usa **il lettore di dwell della D-5** (`registry_dwell_time` in sessione; in generale il lettore
   `dwell_time_for` passato al risolutore): e' attiva **solo con la D-5 accesa** e solo se il sensore dichiara il dwell.
   Finestre e pianificatore restano con la tolleranza numerica (limite dichiarato, §5.2).
3. **Con la FP spenta nessuna unione** (confermata dall'utente la sera del 2026-11-08): l'unione esiste solo nel calcolo
   dei passaggi della FP; la permanenza D-5 a FP spenta (FP-6 (a), `_exposure_time`, punto 8 di §4.1.1) sceglie un
   passaggio fra gli intervalli **non** uniti. Le altre sezioni rimandano a questa.

**Confine** (scelta di chi pianifica, dichiarata): si uniscono due intervalli consecutivi se
`inizio_successivo - fine_precedente <= dwell + TIME_EPS`: l'uguaglianza unisce, con la stessa tolleranza con cui
`_merge_intervals` fonde gli intervalli che si toccano (`Contact_Scheduler.py:947`).

**Dove agisce l'unione** [V sul codice e sul piano]: solo nel calcolo dei passaggi della FP (`_own_passes`), sugli
intervalli restituiti da `_own_intervals` (VA-6 (a)): l'unione e' **a valle** del volume proprio, quindi un volume di
rilevamento futuro diverso dalla sfera (VA §2.3) si sostituisce in `_own_intervals` e l'unione continua a valere sui
suoi intervalli (anche sui due intervalli che un volume non convesso darebbe su un solo tratto). `_pass_detection_time`
e `_detection_time` usano `_own_intervals` con il raggio estratto (nessuna unione: servono solo a trovare il primo
istante dentro il passaggio). `_exposure_time` (FP spento) non unisce (sotto-decisione 3).

**Esempio numerico** (portata propria 6 km, fattore 1): passaggi [200, 254] s e [257, 300] s (uscita di 3 s), distanze
minime 5,5 km e 5,0 km.
- sensore con dwell 6 s (es. P-18, dato di fonte), D-5 accesa: 3 <= 6, **un** passaggio [200, 300], distanza minima
  5,0 km: Pd **0,759**, una estrazione, permanenza 100 s;
- sensore senza dwell (es. la ZSU nel registro, visivo), oppure D-5 spenta: due estrazioni, Pd **0,647** e **0,759**, almeno un
  rilevamento **0,915**;
- uscita di 104 s (variante CAS di S33) con un dwell di 6 s: due passaggi.

### 2.12 Effetti delle decisioni sugli altri pezzi [V sul codice letto]

| Pezzo | Effetto |
|---|---|
| `ContactWindow`, `contact_windows`, `_pair_windows`, `trim_contact_window`, `schedule_contacts` | **invariati** |
| `t_mutual_*` | invariati; usati solo dai ripieghi senza tratti |
| ordine canonico delle finestre, stream dell'ingaggio | invariati (numero e ordine delle estrazioni identici in ogni stato) |
| stream nuovo `pass_rng` | ordine: finestra canonica, a->b poi b->a, passaggio 2..n |
| `t_end` del candidato | fine del passaggio (unito) per l'osservatore con portata minore, anche a un passaggio (FP-3 (a)); `window.t_end` per l'osservatore con portata maggiore e senza tratti |
| `distance_cpa` | per passaggio in `Detection` e `_Candidate` (FP-4) nelle direzioni a >= 2 passaggi |
| `first_detector` | non letto dal risolutore: invariato |
| RWR | una percezione per passaggio rilevato (`rwr_class` accumula `(istante, classe)`) |
| percezione/identificazione (`seen_by`, `identified_by`) | minimo degli istanti: un rilevamento del secondo passaggio conta solo se e' il primo |
| R-INT | regola accesa: rilevamento nel passaggio che contiene il lancio (FP-5 (d)); spenta: ultimo in lista |
| permanenza D-5 | un passaggio, mai la somma, in ogni stato di FP (FP-6 (a)); con FP acceso, il proprio passaggio (unito) |
| eventi di danno | estrazioni di danno nello stream dell'ingaggio, invariate se le salve sono le stesse |
| episodi G4a/G4b, `busy_until`, `covered`, `counter` | invariati (finestre invariate) |
| `Detection` | 4 campi nuovi a `None` (`pass_index`, `pass_count`, `pass_start`, `pass_end`), valorizzati solo nelle direzioni a >= 2 passaggi con la regola accesa |
| pianificatore, `Weapon_Delivery`, adapter DCS | invariati |
| unione dei passaggi (FP-10 (c)) | solo nel risolutore, solo con FP e D-5 accese e dwell dichiarato; finestre e pianificatore invariati |

---

## 3. Decisioni prese (tutte; nessuna aperta)

Premessa comune dalla sonda P-0 (§1.8): nessuna esecuzione della fotografia ha direzioni a piu' passaggi; le decisioni
si giudicano sulla correttezza del modello, su S33 e sui test unitari, non sul confronto.

1. **FP-1 = B-R** (2026-11-07): passaggi calcolati nel risolutore dai tratti. Motivo: regola dentro lo strato 2,
   nessun cambio di finestre ed episodi.
2. **FP-2 = O3** (2026-11-07): stream separato `pass_rng` per i passaggi dal secondo in poi. Motivo: lo stream
   dell'ingaggio resta identico in ogni stato.
3. **FP-3 = (a)** (2026-11-07): candidato al tiro fino alla fine del passaggio, anche con un passaggio solo, per
   l'osservatore con la portata minore. Motivo dell'utente: all'uscita dal volume proprio la traccia e' persa.
4. **FP-4 = (a)** (2026-11-07): CPA del passaggio. Motivo: nessun passaggio "eredita" la distanza di un altro.
5. **FP-5 = (d)**, DECISA dall'utente il 2026-11-08: con la regola accesa il lancio e' "visto" solo con un
   rilevamento (<= `t_launch`) nel passaggio che contiene `t_launch` (passaggi dopo l'unione FP-10); nessun passaggio
   che lo contiene = non visto. Spenta: ultimo rilevamento in ordine di lista. Motivo: coerenza con FP-3 (a).
6. **FP-6 = (a)**, DECISA dall'utente il 2026-11-08: con la D-5 accesa e FP spento la permanenza e' quella del
   passaggio che contiene `t_cpa` (in subordine il piu' lungo), mai la somma, incondizionata dentro l'interruttore D-5;
   con FP acceso il proprio passaggio. Motivo: la somma viola la regola dell'utente.
7. **FP-7 = (a)**, DECISA dall'utente il 2026-11-08: `Engagement_Resolver.FP_PER_PASS_DETECTION = False`, letto da
   `Session_Simulator.engage`, che passa `pass_rng` solo se acceso. **Temporaneo**: si elimina dopo P-1, la lettura
   delle cambiate da parte dell'utente, una fotografia nuova installata dall'utente e un blocco di pulizia.
8. **FP-8 MODIFICATA**, DECISA dall'utente il 2026-11-08: S33-PASSES a 4 varianti (`off`, `on`, `cas_off`, `cas_on`)
   x 5 semi = 20 esecuzioni nuove; tolte le varianti con dwell lunghi (dwell della ZSU 2 s, STIMA [S] dell'utente:
   g = 1). **Confermato la sera del 2026-11-08**: `on` e `cas_on` accendono FP **e D-5** e dichiarano il dwell di 2 s
   sulla ZSU (configurazione finale: lettore del dwell, unione FP-10 valutata senza unire, g = 1); `off` e `cas_off`
   tutto spento, nessun dwell dichiarato (stato precedente).
9. **FP-9 = (a)**, DECISA dall'utente il 2026-11-08: pianificatore non toccato; limite dichiarato; metrica cumulativa
   in una Proposta dedicata quando ci sara' un consumatore.
10. **FP-10 = (c)**, DECISA dall'utente il 2026-11-08: passaggi separati da un'uscita <= dwell del sensore osservatore
    si uniscono; (1) senza dwell dichiarato nessuna unione; (2) l'unione usa il lettore di dwell della D-5, quindi solo
    con la D-5 accesa; finestre e pianificatore restano con la tolleranza numerica; (3) con la FP spenta nessuna unione
    (confermata la sera del 2026-11-08; §2.11).

### 3.1 Scelte di attuazione di chi pianifica (non di modello, dichiarate)

Non sono decisioni di design nuove: precisano come il piano applica le decisioni sopra. Se l'utente ne vuole una
diversa, il piano va aggiornato prima dell'esecuzione.
- **Confine di FP-10**: uscita `<= dwell + TIME_EPS` unisce (§2.11).
- **Ordine unione/filtro**: l'unione si applica alla lista completa degli intervalli di `_own_intervals`, poi si
  tengono i passaggi che toccano la finestra (come `range_intervals`, che fonde prima di ogni filtro; e come la DW-4,
  per cui la permanenza conta dall'inizio vero del passaggio). Differisce dall'ordine inverso solo se un intervallo
  fuori dalla finestra (ritaglio G4a, decollo) dista <= dwell da uno dentro.
- **FP-5 (d) senza tratti**: regola precedente (ultimo in lista), come ogni parte della FP senza tratti (limite di B-R).
- **FP-5 (d), "passaggio che contiene `t_launch`"**: si usano gli estremi veri del passaggio (unito) `(start, end)`,
  non quelli ritagliati alla finestra, cosi' un passaggio fisico diviso fra due finestre della stessa run resta uno.
- **S33 e la D-5** (attuazione della conferma dell'utente, §2.9): `on` e `cas_on` sostituiscono `D5_DWELL_TIME` con
  True e `FP_PER_PASS_DETECTION` con True, `off` e `cas_off` entrambi con False (valore esplicito, uguale al default),
  con due `patch.object` annidati attorno all'intera esecuzione della variante, come S32 (`Test_Session_Scenarios_S32.py:95`):
  all'uscita, anche per un'eccezione, i valori di prima tornano al loro posto. Il dwell `ZSU_DWELL_S` e' dichiarato
  con `F.declare_dwell` sull'istanza della ZSU costruita in quella variante (nessuno stato globale). Nessuna variante
  con una sola delle due regole accesa: le varianti sono lo stato precedente e la configurazione finale.
- **Verifica a interruttore spento**: confronto della cattura di base (prima del blocco 1) con quella dopo, su tutte le
  esecuzioni (fotografia e nuove), al posto della sola cattura di P-0 su S32 (§4.1.6).
- **Sonda P-1**: conta in piu' le decisioni R-INT cambiate da FP-5 (d) (`RINT_D`), perche' P-0 non le ha misurate;
  attesa confermata dall'utente: al piu' le 44 `AFTER_PASS` piu' le eventuali `RINT_D`, NON misurata (§4.3).

---

## 4. Piano di intervento (tutte le decisioni prese)

Se il codice reale non corrisponde a questo piano (funzione inesistente, firma diversa, esito diverso dall'atteso),
l'esecutore si ferma e riferisce.

### 4.0 Precondizioni (l'esecutore le verifica e si ferma se mancano)

1. **Branch dedicato** creato dalla sessione principale (come BI §5.0.1 e VA §4.0.1): `git branch --show-current`
   mostra il branch del compito; `git status` pulito; `git stash list` vuota. Nessun altro esecutore lavora su
   `Logic/Engagement_Resolver.py`, `Logic/Session_Simulator.py` o `Test/Scenario_Baseline.py`.
2. **BI e VA eseguite e integrate** (ordine BI 3-4 -> VA 1-2 -> FP, §4.0.1), controllate per contenuto:
   `BI_AD_TARGET_RULE` e `VA_ENGAGEMENT_ALTITUDE_BAND` esistono in `Logic/Engagement_Resolver.py`; `ShotSpec` ha in coda
   `intercept_domains`, `min_altitude`, `max_altitude`, `max_target_z`; `Scenario_Baseline.UNITS` termina con
   `S35-ADTGT` e poi `S34-BAND`; `Logic/Contact_Scheduler.py` ha `altitude_intervals`. Se manca qualcosa, fermarsi.
3. **Decisioni**: questa Proposta riporta in testa "TUTTE LE DECISIONI PRESE (2026-11-08)" (soddisfatta).
4. **Base**: `bash tools/ai/verifica.sh suite` -> annotare `Ran B_FP` e `OK (skipped=7)` dall'ESITO; `bash
   tools/ai/verifica.sh confronto` -> atteso `UNCHANGED (1009)` e `compared 1093 runs: 84 difference lines` (84 NEW:
   20 S32-DWELL, 32 S35-ADTGT, 32 S34-BAND; nessuna DIFF ne' MISSING). Se diverso, fermarsi e riferire. Subito dopo il
   confronto della base, **conservare la cattura**: `cp .ai-run/confronto_capture.json .ai-run/fp_base_capture.json`
   (serve a §4.1.6, §4.2.4 e a P-1).
5. **Righe**: quelle citate sono del checkout `97620f55` (2026-11-08). BI blocco 3 (solo test e scenario) e VA blocco 1
   (che tocca `_range_entry`, `_schedule_next`, `_in_range_at`, `_call_fire_control`, `ShotSpec`, `__init__`) le
   spostano: l'esecutore cerca **per nome** (`_detect`, `_detect_direction`, `_detection_time`, `_exposure_time`,
   `_draw`, `_detection_time_of`, `_in_time`, `registry_dwell_time`, `Detection`, `_EngagementRun.__init__`,
   `resolve_engagement`, `D5_DWELL_TIME`, `VA_ENGAGEMENT_ALTITUDE_BAND`; in `Session_Simulator.py` `TEMPER_EVENT_TAG`,
   `temper_event_id`, `engage`). Se una firma e' diversa da quella citata in §4.1, fermarsi.

### 4.0.1 Ordine di esecuzione e numeri attesi (tabella unica)

Base reale di oggi [V: `.ai-run/suite.log` e `.ai-run/confronto.log` dell'8 novembre, merge `4803424b`]: `Ran 4829
tests`, `OK (skipped=7)`; `UNCHANGED (1009)`, `compared 1029 runs: 20 difference lines` (20 NEW S32-DWELL). Il
blocco 2 della BI ha aggiunto 28 test (4801 + 28 = 4829, `Rapporti/Rapporto_BI_blocco2_des-developer.md:41`), non i
"circa 21" del piano BI: i conteggi dei blocchi non ancora eseguiti sono stime [S] o attese [I] e il numero vero si
legge sempre dall'ESITO.

| Passo | `Ran` prima | `Ran` dopo | Confronto atteso (sempre `UNCHANGED (1009)`, 0 DIFF/MISSING) | Note |
|---|---|---|---|---|
| oggi (BI blocchi 0-2 fatti) | — | **4829** [V] | `compared 1029 runs: 20 difference lines` [V] | 20 NEW S32 |
| BI blocco 3 (S35-ADTGT) | 4829 | 4829 + N_BI3, con N_BI3 "circa 15" (BI §5.4) -> **~4844** [S] | `compared 1061 runs: 52 difference lines` [I] | + 32 NEW S35 |
| BI blocco 4 (documenti) | = | = | invariato | nessun test |
| VA blocco 1 | B_VA = 4829 + N_BI3 | B_VA + 23 -> **~4867** [S] | `compared 1061 runs: 52` [I] | VA §4.1.7 |
| VA blocco 2 (S34-BAND) | B_VA + 23 | B_VA + 32 -> **~4876** [S] | `compared 1093 runs: 84 difference lines` [I] | + 32 NEW S34 |
| **FP blocco 1** | B_FP (letto all'avvio; ~4876 [S]) | **B_FP + 30** -> ~4906 [S] | `compared 1093 runs: 84 difference lines` (invariato) | cattura di base IDENTICAL su 1093 (§4.1.6); poi P-1 dalla sessione principale |
| **FP blocco 2** (S33-PASSES) | B_FP + 30 | **B_FP + 43** -> ~4919 [S] | **`compared 1113 runs: 104 difference lines`** [I] | + 20 NEW S33 (13 test) |

Il confronto finale atteso deriva da 1029 + 32 (S35) + 32 (S34) + 20 (S33) = 1113 esecuzioni e 20 + 32 + 32 + 20 = 104
righe NEW; i 32 di S35 (8 varianti x 4 semi, BI §5.4) e i 32 di S34 (8 varianti x 4 semi, VA §4.2) sono quelli dei
piani BI e VA ricontrollati il 2026-11-08 [V sui testi]. Le esecuzioni NEW non cambiano con BI, VA e FP spenti. La D-5
accesa in S33 `on`/`cas_on` (§2.9) non cambia ne' il numero delle esecuzioni ne' quello delle righe NEW.

### 4.0.2 Coordinamento con BI e VA: colonna FP

La tabella di coordinamento e' in BI §6.1 (`Proposta_Bersagli_Intercettabili_Difesa_Aerea.md:1127-1140`, riga `:1138`), che questo
piano non modifica; BI §6.1 e' gia' allineata alla colonna FP (commit `8c440dba`: riga "scenari" con S33-PASSES a 20
esecuzioni e 13 test, righe FP blocco 1/2 della sequenza). Per l'esecutore della FP vale la colonna seguente.

| Punto di contatto | FP (questo piano) |
|---|---|
| interruttori del risolutore | `FP_PER_PASS_DETECTION` in coda, dopo `VA_ENGAGEMENT_ALTITUDE_BAND` (§4.1.1 punto 2); `D5_DWELL_TIME` **non** modificato nel codice (S33 lo sostituisce solo durante le proprie esecuzioni `on`/`cas_on`) |
| scenari | **S33-PASSES** (`Test_Session_Scenarios_S33.py`, 4 varianti x 5 semi = **20** esecuzioni, **13** test); `on`/`cas_on` con FP e D-5 accese e dwell della ZSU 2 s [S] |
| `Scenario_Baseline.UNITS` | riga S33-PASSES in coda, dopo S34-BAND (§4.2.2) |
| `Scenario_Fixtures.py`, `Test_Session_Scenarios_S32.py` | non modificati (S33 usa `F.declare_dwell` e importa da S32) |

### 4.1 Blocco 1 — risolutore e orchestratore

#### 4.1.1 `Logic/Engagement_Resolver.py`

1. **Import** (`:467-474`): aggiungere `clamp_legs` e `closest_point_of_approach` all'import da `Contact_Scheduler`,
   in ordine alfabetico con i nomi gia' presenti (compresi quelli eventualmente aggiunti da VA).
2. **Interruttore**, in coda agli interruttori esistenti, nell'ordine di esecuzione: subito dopo il blocco di
   `VA_ENGAGEMENT_ALTITUDE_BAND` (commento e assegnazione), come dice la tabella di coordinamento di BI §6.1 (oggi gli
   interruttori sono `D5_DWELL_TIME`, `:522-529`, e `BI_AD_TARGET_RULE`, `:531-535`, seguiti da `AD_DOMAINS`, `:537-538`);
   testo esatto:

```python
# Rilevamento per passaggio nella portata propria (Proposta_Finestre_Per_Passaggio_Portata_Propria.md, FP),
# interruttore dedicato e TEMPORANEO:
#   * `FP_PER_PASS_DETECTION` (SPENTO): un'occasione di rilevamento per OGNI passaggio del bersaglio nel volume PROPRIO
#     dell'osservatore dentro una finestra di contatto (prima: una sola estrazione per finestra e direzione, con la
#     distanza minima dell'intera finestra). Lo legge Session_Simulator, che passa al risolutore lo stream separato
#     `pass_rng` solo se acceso. Acceso: lo stream `rng` non cambia (stesse estrazioni, stesso ordine); le estrazioni
#     dei passaggi dal secondo in poi vengono da `pass_rng`; il candidato al tiro dell'osservatore con la portata
#     minore vale fino alla fine del passaggio (traccia persa all'uscita); R-INT "vede il lancio" solo con un
#     rilevamento nel passaggio che contiene il lancio; con la D-5 accesa i passaggi separati da un'uscita non piu'
#     lunga del dwell del sensore si uniscono. Spento: chiamata e rilevamento di prima (la permanenza D-5 di un solo
#     passaggio, mai la somma, vale in ogni stato: e' dentro D5_DWELL_TIME). Nessuna estrazione nello stream `rng` in
#     piu' ne' in ordine diverso in nessuno dei due stati.
#   TEMPORANEO (criterio dell'utente del 2026-11-08: la regola sostituisce una soluzione superata). Si elimina, con il
#   ramo "spento", in un blocco di pulizia dopo: la sonda P-1, la lettura delle esecuzioni cambiate da parte
#   dell'utente e una fotografia nuova installata dall'utente.
FP_PER_PASS_DETECTION = False
```

3. **`Detection`** (`:674-692`): la prima riga del docstring diventa "Esito di un'estrazione di rilevamento (una per
   finestra e direzione; con il rilevamento per passaggio, FP, una per passaggio)."; quattro campi in coda, con
   default None, e una frase nel docstring ("`pass_index`, `pass_count`, `pass_start`, `pass_end` (FP): indice del
   passaggio nel volume proprio, numero di passaggi della direzione nella finestra, estremi del passaggio (unito, FP-10)
   ritagliati alla finestra; None se l'estrazione e' l'unica della direzione, come prima"):

```python
    pass_index: Optional[int] = None       # FP: indice del passaggio (0 = primo); None = estrazione unica della direzione
    pass_count: Optional[int] = None       # FP: passaggi della direzione nella finestra; None = estrazione unica
    pass_start: Optional[float] = None     # FP: inizio del passaggio [s], ritagliato alla finestra
    pass_end: Optional[float] = None       # FP: fine del passaggio [s], ritagliata alla finestra
```

4. **Funzioni di modulo nuove**, subito dopo `registry_dwell_time` (`:1206-1221`), testo esatto:

```python
def _join_passes(intervals: Sequence[Tuple[float, float]],
                 max_gap: Optional[float]) -> List[Tuple[float, float]]:
    """Unione dei passaggi ravvicinati (FP-10 (c), Proposta_Finestre_Per_Passaggio_Portata_Propria.md).

    `intervals`: intervalli ORDINATI e disgiunti (uscita di `range_intervals`). Due intervalli consecutivi separati da
    un'uscita `inizio_successivo - fine_precedente <= max_gap` (con la tolleranza TIME_EPS: l'uguaglianza unisce)
    diventano un passaggio solo, dall'inizio del primo alla fine dell'ultimo: il tracciamento e' predittivo, una
    perdita di segnale non piu' lunga del periodo di aggiornamento del sensore (dwell) non interrompe la traccia.
    `max_gap` None = nessuna unione (sensore senza dwell dichiarato, o legge D-5 non applicata). Nessuna estrazione,
    nessuna costante nuova.
    """
    if max_gap is None or not intervals:
        return [(float(start), float(end)) for start, end in intervals]

    joined = [(float(intervals[0][0]), float(intervals[0][1]))]

    for start, end in intervals[1:]:
        if float(start) - joined[-1][1] <= max_gap + TIME_EPS:
            joined[-1] = (joined[-1][0], max(joined[-1][1], float(end)))
        else:
            joined.append((float(start), float(end)))

    return joined


def _detection_time_in_pass(passes: Sequence[Tuple[float, float]], times: Sequence[float],
                            at: float) -> Optional[float]:
    """Regola R-INT con il rilevamento per passaggio (FP-5 (d), Proposta_Finestre_Per_Passaggio_Portata_Propria.md).

    `passes`: passaggi `(start, end)` del lanciatore nel volume proprio dell'intercettore (dopo l'unione FP-10);
    `times`: istanti dei rilevamenti dell'intercettore sul lanciatore. Restituisce il PRIMO istante di rilevamento
    dentro il primo passaggio (in ordine di tempo) che contiene `at` (estremi entro TIME_EPS); None se nessun
    passaggio contiene `at` o se in quel passaggio non c'e' rilevamento. Il lancio a `at` e' "visto" se il risultato
    non e' None ed e' <= at (+ TIME_EPS): lo decide il chiamante (`_in_time`). Nessuna estrazione.
    """
    for start, end in sorted(passes):
        if start - TIME_EPS <= at <= end + TIME_EPS:
            inside = [time for time in times if start - TIME_EPS <= time <= end + TIME_EPS]

            return min(inside) if inside else None

    return None
```

5. **`_EngagementRun.__init__`** (firma `:1765-1769`): parametro in coda `pass_rng=None` (dopo `dwell_time_for=None`);
   subito dopo `self.dwell_time_for = dwell_time_for` (`:1838`), testo esatto:

```python
        # FP (FP_PER_PASS_DETECTION): stream separato dei passaggi dal secondo in poi; None = un'estrazione per finestra
        # e direzione, comportamento precedente. Passaggi `(start, end)` (uniti, FP-10) per (osservatore, bersaglio) e
        # istanti di rilevamento per coppia, per la regola R-INT legata al passaggio (FP-5 (d), `_detection_time_of`).
        self.pass_rng = pass_rng
        self.own_passes_of: Dict[Tuple[str, str], List[Tuple[float, float]]] = {}
        self.detection_times_of: Optional[Dict[Tuple[str, str], List[float]]] = None
```

6. **`_detect_direction`** (`:2112-2169`): sostituire il blocco che va da `exposure = dwell = None` (`:2127`) alla fine
   del blocco D-5 (`:2137`, `factor = factor * dwell_factor(exposure, dwell)`) con, testo esatto:

```python
        exposure = None
        # D-5 (D5_DWELL_TIME, v. docstring del modulo): periodo di rivisita del sensore; None senza lettore (interruttore
        # spento) o senza dato. Nessuna estrazione: numero e ordine delle estrazioni restano quelli di prima.
        dwell = self._dwell_of(window, observer, target)
        candidate_end = window.t_end
        pass_exposure = None

        if self.pass_rng is not None:
            # FP (FP_PER_PASS_DETECTION, v. docstring del modulo): passaggi del bersaglio nel volume proprio dentro la
            # finestra, uniti se separati da un'uscita <= dwell (FP-10). Con >= 2 passaggi un'estrazione per passaggio;
            # con 0 o 1 passaggio, o senza tratti, l'estrazione di prima.
            passes = self._own_passes(window, observer.id, target.id, own_range, dwell)

            if passes is not None:
                # FP-5 (d): passaggi della coppia, per la regola R-INT (`_detection_time_of`).
                self.own_passes_of.setdefault((observer.id, target.id), []).extend(
                    (start, end) for _, _, start, end in passes)

            if passes is not None and len(passes) >= 2:
                self._detect_passes(window, observer, target, own_range, factor, dwell, passes)
                return

            if passes:
                _, hi, start, end = passes[0]
                # D-5 con FP: permanenza dell'unico passaggio (unito, FP-10), come in `_detect_passes`.
                pass_exposure = max(0.0, min(end, window.t_end) - start)

                # FP-3 (a): all'uscita dal volume proprio la traccia e' persa. Per l'osservatore con la portata MINORE il
                # candidato al tiro vale fino alla fine del passaggio (ritagliata alla finestra). Portata maggiore o
                # uguale (il passaggio coincide con la finestra) o senza tratti: fine della finestra, come prima.
                if other_range is not None and other_range > 0 and own_range < other_range:
                    candidate_end = hi

        if dwell is not None:
            exposure = self._exposure_time(window, observer.id, target.id, own_range, other_range) \
                if pass_exposure is None else pass_exposure
            factor = factor * dwell_factor(exposure, dwell)
```

   Nel resto del metodo cambiano **solo due righe** del ramo `if detected:` (`:2161-2164`): la condizione
   `if t_ready <= window.t_end + TIME_EPS:` diventa `if t_ready <= candidate_end + TIME_EPS:` e l'argomento
   `t_end=window.t_end` di `_Candidate` diventa `t_end=candidate_end`. La costruzione della `Detection` (`:2166-2169`)
   resta com'e' (campi `pass_*` None). Equivalenza a interruttori spenti: `_dwell_of` esegue le stesse due istruzioni
   del vecchio blocco D-5 (`:2132-2133`) e restituisce None senza lettore; `pass_rng` None salta il ramo FP;
   `candidate_end` e' lo stesso oggetto `window.t_end`; con la D-5 accesa `pass_exposure` e' None e la permanenza viene
   da `_exposure_time` come prima. Con FP acceso e un solo passaggio **non unito**, `pass_exposure` coincide al bit con
   il risultato di `_exposure_time` (stesso intervallo, stessa espressione `max(0.0, min(end, window.t_end) - start)`).
7. **Metodi nuovi** di `_EngagementRun`, dopo `_exposure_time` (`:2247-2277`), testo esatto del corpo:

```python
    def _dwell_of(self, window, observer: _Shadow, target: _Shadow) -> Optional[float]:
        """Periodo di rivisita [s] del sensore dell'osservatore contro il bersaglio (D-5, v. "Permanenza nel volume"):
        None senza lettore (`dwell_time_for` None, cioe' D5_DWELL_TIME spento in sessione) o se il sensore non lo
        dichiara. Usato dalla legge di permanenza e dall'unione dei passaggi (FP-10). Nessuna estrazione."""
        if self.dwell_time_for is None:
            return None

        mode = GROUNDED_DETECTION_MODE if self._grounded_in(target.id, window) else detection_mode_for(target.asset)

        return _check_dwell(self.dwell_time_for(observer.asset, target.asset, mode))

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

    def _own_passes(self, window, observer_id: str, target_id: str, own_range: float,
                    dwell: Optional[float] = None) -> Optional[List[Tuple[float, float, float, float]]]:
        """Passaggi del bersaglio nel volume PROPRIO dell'osservatore dentro la finestra (FP), in ordine di tempo.

        Gli intervalli di `_own_intervals` (portata propria) separati da un'uscita <= `dwell` si UNISCONO prima di
        tutto (FP-10 (c), `_join_passes`; `dwell` None = nessuna unione oltre TIME_EPS). Ogni passaggio e'
        `(lo, hi, start, end)`: `(start, end)` e' un passaggio (unito) che tocca la finestra (stesso criterio di
        `_exposure_time`), `[lo, hi]` lo stesso ritagliato alla finestra. None senza i tratti di entrambi (chiamate
        dirette): il chiamante usa l'estrazione unica di prima. Nessuna estrazione.
        """
        intervals = self._own_intervals(observer_id, target_id, own_range)

        if intervals is None:
            return None

        passes = []

        for start, end in _join_passes(intervals, dwell):
            if end >= window.t_start - TIME_EPS and start <= window.t_end + TIME_EPS:
                lo = max(float(start), float(window.t_start))
                passes.append((lo, max(lo, min(float(end), float(window.t_end))), float(start), float(end)))

        return passes

    def _pass_cpa(self, window, observer_id: str, target_id: str, lo: float, hi: float) -> Tuple[float, float]:
        """`(t_cpa, distanza)` del massimo avvicinamento dentro il passaggio `[lo, hi]` (FP-4; passaggio unito compreso).
        Ripiego (non atteso: il passaggio viene dagli stessi tratti) il CPA della finestra, con un log."""
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
                       dwell: Optional[float], passes: List[Tuple[float, float, float, float]]) -> None:
        """Un'estrazione per passaggio nel volume proprio (FP, >= 2 passaggi dopo l'unione FP-10). Il primo estrae
        dallo stream dell'ingaggio nella posizione dell'estrazione unica di prima; dal secondo in poi da `pass_rng`,
        nell'ordine (finestra canonica, a->b poi b->a, passaggio). Ogni passaggio ha la sua distanza minima (FP-4), la
        sua permanenza D-5 (FP-6; `dwell` None = legge non applicata) e un candidato al tiro valido fino alla FINE del
        passaggio (FP-3 (a): all'uscita dal volume proprio la traccia e' persa, al rientro serve un nuovo
        rilevamento). Due o piu' passaggi capitano solo all'osservatore con la portata minore (per l'altro il
        passaggio coincide con la finestra)."""
        count = len(passes)

        for index, (lo, hi, start, end) in enumerate(passes):
            pass_factor = factor
            exposure = None

            if dwell is not None:
                # Permanenza del PROPRIO passaggio (unito: dall'inizio del primo intervallo alla fine dell'ultimo), non
                # tagliata all'inizio della finestra (DW-4); mai la somma.
                exposure = max(0.0, min(end, window.t_end) - start)
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

8. **`_exposure_time`** (`:2247-2277`, FP-6 (a), invariato rispetto alla versione del 2026-11-07): sostituire il ramo
   con i tratti (`:2262-2269`, dall'`if legs_observer and legs_target:` al `return exposure`) con:

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

   Docstring del metodo: "somma, sugli intervalli ..." diventa "con i tratti di entrambe le rotte: la permanenza del
   passaggio (intervallo di `range_intervals` con la portata propria che tocca la finestra) che contiene `t_cpa`, in
   mancanza del piu' lungo, `min(end, t_end) - start`; MAI la somma dei passaggi (regola dell'utente del 2026-11-06,
   FP-6). Nessuna unione dei passaggi (FP-10 vale solo con il rilevamento per passaggio)". Il ramo senza tratti non
   cambia. **Docstring del modulo, sezione D-5** (`:156-160`, punto "Permanenza"): "somma degli intervalli in portata
   PROPRIA che toccano la finestra" diventa "il passaggio in portata PROPRIA (intervallo che tocca la finestra) che
   contiene il CPA della finestra, in subordine il piu' lungo; mai la somma (FP-6, Proposta_Finestre_Per_Passaggio_
   Portata_Propria.md); con il rilevamento per passaggio acceso, la permanenza del proprio passaggio, unito se
   separato da uscite <= dwell (FP-10)"; il resto del punto invariato.
8-bis. **Volume proprio in un solo punto (VA-6 (a))**: `_own_intervals` (punto 7) e' l'**unico** punto del risolutore
   che chiama `range_intervals` sul volume di rilevamento proprio. Oltre ai metodi nuovi e a `_exposure_time` (punto 8),
   anche `_detection_time` (`:2219-2245`) passa da li': nel suo ramo con i tratti, `for start, end in
   range_intervals(legs_observer, legs_target, radius):` (`:2233`) diventa `for start, end in
   self._own_intervals(observer_id, target_id, own_range, radius):` (la condizione `legs_observer and legs_target and
   radius is not None` resta). Il raggio passa **invariato**: stessi float, stessi intervalli. Verifica
   dell'esecutore: `grep -n "range_intervals(" Logic/Engagement_Resolver.py` deve dare solo `engagement_intervals`
   (oggi `:1738`), le funzioni d'ingaggio aggiunte da VA (se ne chiamano) e `_own_intervals`.
9. **`_draw`** (`:2285-2291`): firma `def _draw(self, rng=None) -> float:`, prima riga
   `value = (self.rng if rng is None else rng).random()`; il resto invariato.
10. **`_detection_time_of`** (`:3229-3235`, FP-5 (d)): sostituire il metodo con, testo esatto:

```python
    def _detection_time_of(self, observer_id: str, target_id: str, at: Optional[float] = None) -> Optional[float]:
        """Istante in cui `observer_id` ha rilevato `target_id` (None = mai rilevato), per la regola R-INT.

        Rilevamento per passaggio spento (`pass_rng` None), `at` None o passaggi della coppia non calcolati (senza
        tratti): l'ULTIMO rilevamento in ordine di lista, come prima. Acceso (FP-5 (d),
        Proposta_Finestre_Per_Passaggio_Portata_Propria.md): il rilevamento NEL passaggio dell'osservatore che contiene
        `at` (`_detection_time_in_pass`); None se nessun passaggio lo contiene. Nessuna estrazione.
        """
        if self.detected_at is None:
            self.detected_at = {(d.observer_id, d.target_id): d.time
                                for d in self.detections if d.detected and d.time is not None}

        key = (observer_id, target_id)

        if self.pass_rng is None or at is None or key not in self.own_passes_of:
            return self.detected_at.get(key)

        if self.detection_times_of is None:
            self.detection_times_of = {}

            for d in self.detections:
                if d.detected and d.time is not None:
                    self.detection_times_of.setdefault((d.observer_id, d.target_id), []).append(float(d.time))

        return _detection_time_in_pass(self.own_passes_of[key], self.detection_times_of.get(key, ()), at)
```

    In `_in_time` (`:3292-3316`) cambia **una** riga: `seen = self._detection_time_of(shadow.id, salvo.shooter_id)`
    (`:3307`) diventa `seen = self._detection_time_of(shadow.id, salvo.shooter_id, salvo.t_launch)`; nel docstring,
    dopo "Lancio osservato (...)", la frase "Con il rilevamento per passaggio (FP-5 (d)) il lancio e' osservato solo se
    il rilevamento e' nel passaggio del lanciatore che contiene il lancio." A interruttore spento `_detection_time_of`
    restituisce lo stesso valore di prima (stesso dizionario, stesso ordine di costruzione).
11. **`resolve_engagement`** (firma `:3809-3828`): parametro in coda `pass_rng=None`; validazione accanto a quella di
    `dwell_time_for` (`:3943-3944`): `if pass_rng is not None and not callable(getattr(pass_rng, 'random', None)):
    raise TypeError("pass_rng must expose a random() method returning a float in [0, 1)")`; passato a
    `_EngagementRun(..., dwell_time_for=dwell_time_for, pass_rng=pass_rng)` (`:3965-3972`). Voce nel docstring degli
    argomenti, dopo `dwell_time_for` (`:3906-3908`): "pass_rng: flusso casuale SEPARATO (oggetto con `.random()`) per
    il rilevamento per passaggio (FP, v. "Rilevamento per passaggio"): se dato, una direzione con >= 2 passaggi nel
    volume proprio dentro una finestra ha un'estrazione per passaggio, la prima dallo stream `rng` nella posizione di
    prima, le altre da questo; il candidato al tiro dell'osservatore con la portata minore vale fino alla fine del
    passaggio, anche con un passaggio solo (FP-3 (a)); R-INT vede il lancio solo con un rilevamento nel passaggio che
    lo contiene (FP-5 (d)); con `dwell_time_for` i passaggi separati da un'uscita <= dwell si uniscono (FP-10). None
    (default) = un'estrazione per finestra e direzione, comportamento precedente. In sessione lo passa
    Session_Simulator (`pass_event_id`) solo con FP_PER_PASS_DETECTION acceso."
12. **Docstring del modulo**: (i) contratto RNG (`:416-421`): la parentesi "(invariato dalla D-5)" diventa "(invariato
    dalla D-5 e dal rilevamento per passaggio: con `pass_rng` i passaggi dal secondo in poi estraggono da quello stream
    separato, nell'ordine canonico seguito dall'indice del passaggio, e lo stream `rng` resta identico)"; (ii) punto 4
    della catena (R-INT, `:49-55`): una frase "Con il rilevamento per passaggio acceso (FP-5 (d)) 'aveva gia' rilevato il
    lanciatore' vale solo per un rilevamento nel passaggio che contiene il lancio."; (iii) una sezione nuova dopo
    quella della D-5 (prima di "## Scorta per arma", `:169`), intitolata `## Rilevamento per passaggio nella portata
    propria (FP, interruttore FP_PER_PASS_DETECTION, temporaneo)`, con: la regola dell'utente (un'occasione per
    passaggio, mai la somma), i passaggi dai tratti (`_own_passes`, `_own_intervals`), le scelte FP-2/3/4/5/6/10 (FP-3
    (a): candidato fino alla fine del passaggio per l'osservatore con la portata minore, le salve gia' lanciate non
    cambiano; FP-5 (d); FP-10 (c): unione entro il dwell del sensore, solo con la D-5 accesa), il ripiego senza tratti,
    la frase "spento (`pass_rng` None) il rilevamento e' quello di prima" e il criterio di rimozione dell'interruttore.

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

3. In `engage` (`:2707`), subito dopo il blocco D-5 (`:2770-2772`):

```python
        if ER.FP_PER_PASS_DETECTION:
            # FP: un'occasione di rilevamento per passaggio nel volume proprio (v. Engagement_Resolver.FP_PER_PASS_DETECTION),
            # stream separato con lo stesso `counter` dell'episodio. Spento: chiamata di prima.
            extra['pass_rng'] = order.rng(mission_id=None, event_id=pass_event_id(*force_ids), counter=counter)
```

4. Docstring del modulo, dopo "## Permanenza nel volume (D-5)" (`:730-733`), sezione `## Rilevamento per passaggio
   (FP)`: "Interruttore del risolutore, temporaneo: `Engagement_Resolver.FP_PER_PASS_DETECTION` (SPENTO). Acceso,
   `engage` passa a `resolve_engagement` lo stream separato `pass_rng = order.rng(mission_id=None,
   event_id=pass_event_id(*forze), counter=ordinale dell'episodio)`; spento, la chiamata e' quella di prima."

#### 4.1.3 Effetti sui chiamanti [V]

- Chiamate dirette a `resolve_engagement` e a `_EngagementRun` (test: `Test_Engagement_Resolver.py:2406`, `:2435`,
  `:2522`, `:2623`, `:2688`; `Test_Aircraft.py:345`; `Test_Mission_Adapter.py:605`): parametro in coda con default,
  nessun cambio.
- `Detection` costruite in produzione solo da `_detect_direction` (`:2166`) e, dopo, da `_detect_passes`; nei test il
  confronto di `Test_Engagement_Resolver.py:3779` (`dataclasses.replace(..., exposure_s=None, dwell_time_s=None)`)
  resta valido (campi nuovi None da entrambe le parti).
- `_exposure_time`, `_detection_time`: chiamati solo da `_detect_direction` (`:2136`, `:2147`); nessun test esistente
  asserisce la somma (`TestDwellTimeInTheResolver`, `:3736`: un solo intervallo, o finestre senza tratti).
- `_detection_time_of`: chiamato solo da `_in_time` (`:3307`); parametro nuovo con default.
- `_in_time`: dopo `_admissible` e `_may_intercept` (`:3396-3397`): ordine invariato.
- Nessun altro modulo del core cambia (§1.6). Adapter DCS: nessun riferimento.

#### 4.1.4 Vincoli

- **RNG**: con `pass_rng` None nessuna istruzione nuova che estragga; con `pass_rng` dato lo stream `rng` ha lo stesso
  numero e lo stesso ordine di estrazioni (il primo passaggio prende la posizione dell'estrazione unica, anche quando
  i passaggi sono uniti da FP-10). `_dwell_of`, `_join_passes`, `_own_passes`, `_detection_time_in_pass`,
  `_detection_time_of` non estraggono. Vietato il modulo `random`.
- **Interruttore**: `FP_PER_PASS_DETECTION = False`, letto a ogni chiamata di `engage` (globale di modulo, sostituibile
  con `patch.object`); commento con il criterio di rimozione (punto 2).
- **Nessuna costante stimata nuova nel motore**; tolleranze = `TIME_EPS` esistente; la soglia di unione e' il dwell
  del sensore (dato di registro o lettore), mai un valore inventato. I dwell nei test unitari (125, 139, 140, 400 s)
  sono valori **dichiarati di test**.
- Core indifferente al simulatore; import col percorso completo; logger mockato nei test come negli altri.

#### 4.1.5 Test del blocco 1 (30)

**Geometria comune** dei test 2-12, 18-20, 24-30 (`Test/Test_Engagement_Resolver.py`), da definire come costanti della
classe nuova: osservatore `b1` fermo in (0, 0, 0): `Leg(0.0, 430.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))`; bersaglio `r1`
con tre tratti `Leg(0, 200, (-10000, 0, 0), (10000, 0, 0))`, `Leg(200, 230, (10000, 0, 0), (10000, 3000, 0))`,
`Leg(230, 430, (10000, 3000, 0), (-10000, 3000, 0))`. Finestra `ContactWindow('b1', 'r1', t_start=0.0, t_end=430.0,
t_cpa=100.0, distance_cpa=0.0, range_a=5000.0, range_b=20000.0, t_mutual_start=50.0, t_mutual_end=150.0)`; i tratti
passati con `legs={'b1': [...], 'r1': [...]}`. Passaggi di `b1` (portata 5 km): **[50, 150]** (CPA 0 m a 100 s) e
**[290, 370]** (CPA 3000 m a 330 s; Pd 1 - 0,5 * 0,6^4 = **0,9352**), uscita fra i due **140 s**; `r1` (20 km) ha un
solo passaggio [0, 430] [V: `range_intervals` eseguito il 2026-11-08]. Forze `_Force('blue', 'Blue', [_Asset('b1')])`,
`_Force('red', 'Red', [_Asset('r1')])`, `reaction_profile_for=_profiles({...})`, RNG `_ScriptedRng`. Fire control
`lambda s, t: None` salvo dove indicato. Dove il test chiama metodi privati si costruisce `ER._EngagementRun(...)`
direttamente e si chiama `.run()` (schema di `Test_Engagement_Resolver.py:2406-2411`), con `dwell_time_for=` e
`pass_rng=` come parole chiave.

Classe nuova `TestDetectionPerPass(unittest.TestCase)` (logger mockato in `setUp` come `TestDwellTimeInTheResolver`):
1. `test_switch_is_off_by_default`: `ER.FP_PER_PASS_DETECTION is False`.
2. `test_without_pass_rng_one_draw_per_window`: senza `pass_rng`, una `Detection` di `b1` su `r1`, campi `pass_*`
   None; `rng.calls == 2`.
3. `test_with_pass_rng_one_draw_per_pass`: rng `[0.3, 0.6]`, pass_rng `[0.7]`: due `Detection` di `b1` con
   `pass_index` 0 e 1, `pass_count` 2, `(pass_start, pass_end)` ~ (50, 150) e (290, 370) (`places=6`); la `Detection`
   di `r1` ha i campi `pass_*` None.
4. `test_the_engagement_stream_is_unchanged`: stessa sequenza nei due stati: `rng.calls` uguale (2), draw della
   `Detection` di `b1` con `pass_index` 0 uguale a quello dell'estrazione unica (0.3), `pass_rng.calls == 1`.
5. `test_each_pass_uses_its_own_cpa`: `distance_cpa` 0 e 3000 (`places=6`), `probability` 1.0 e 0.9352 (`places=9`).
6. `test_detection_time_is_inside_its_pass`: rng `[0.0, 0.9]`, pass_rng `[0.0]`: istanti 50.0 e 290.0 (`places=6`).
7. `test_the_second_pass_is_a_new_occasion`: `detection_factor=lambda o, t: 0.9`, profilo di `b1` (10, 1), fire
   control `_kill()` per `b1` e None per `r1`; rng `[0.95, 0.99]`, pass_rng `[0.1]`. Senza `pass_rng`: nessuna salva di
   `b1` (0.95 >= 0.9). Con: una salva di `b1` su `r1` con `t_launch` 300.0 (`places=6`).
8. `test_a_pass_candidate_ends_with_its_pass` (FP-3 (a)): profilo di `b1` (120, 1), fire control `_kill()` per `b1` e
   None per `r1`; rng `[0.0, 0.99]`, pass_rng `[0.99]`. Senza `pass_rng`: una salva di `b1` a 170.0 (`places=6`). Con:
   nessuna salva di `b1` (t_ready 170 oltre la fine del primo passaggio, 150; secondo passaggio mancato).
9. `test_dwell_exposure_is_per_pass` (FP-6 con FP): `dwell_time_for=lambda o, t, m: 125.0` (125 < uscita di 140 s:
   nessuna unione), pass_rng dato: `pass_count` 2, `exposure_s` 100.0 e 80.0, `probability` 0.8 e 0.64 * 0.9352
   (`places=9`), `dwell_time_s` 125.0.
10. `test_single_pass_direction_is_unchanged`: `r1` con il solo primo tratto e finestra [0, 200] (`t_cpa` 100,
    `distance_cpa` 0, portate 5000/20000, `t_mutual` 50/150): `Detection` uguali (osservatore, bersaglio, probabilita',
    draw, rilevato, istante, `exposure_s`, `dwell_time_s`) con e senza `pass_rng`, `pass_rng.calls == 0`; ripetuto con
    `dwell_time_for=lambda o, t, m: 400.0`: stesse uguaglianze, `exposure_s` 100.0 per `b1` e 200.0 per `r1` in entrambi
    gli stati.
11. `test_without_legs_one_draw`: finestra `_window('b1', 'r1', range_a=1000.0, range_b=2000.0)` senza `legs`, con
    `pass_rng`: una `Detection` per direzione, `pass_rng.calls == 0`.
12. `test_pass_rng_must_expose_random`: `ER.resolve_engagement(..., pass_rng=object())` -> `TypeError`: si chiama
    `resolve_engagement`, non `_EngagementRun`, secondo lo schema di `TestDwellTimeInTheResolver._run` (che inoltra
    `**kwargs` a `ER.resolve_engagement`), perche' la validazione di `pass_rng` e' in `resolve_engagement` (punto 11).
13. `test_detection_time_in_pass` (FP-5 (d), funzione pura, esempio di §2.6): con `passes = [(200.0, 254.0), (380.0,
    434.0)]` e `times = [210.0, 390.0]`, `ER._detection_time_in_pass(passes, times, t)` vale 210.0 per t = 230.0, None
    per 300.0, 390.0 per 385.0, 390.0 per 400.0; l'esito "visto" (`x is not None and x <= t + ER.TIME_EPS`) e' True,
    False, False, True; con `times = [390.0, 210.0]` stessi risultati; con `passes = []` None.
18. `test_single_pass_candidate_ends_with_the_pass` (FP-3 (a) con un passaggio solo): geometria del test 10, fire
    control `_kill()` per `b1` e None per `r1`, rng `[0.0, 0.99]`, pass_rng vuoto. Profilo di `b1` (120, 1): senza
    `pass_rng` una salva di `b1` a 170.0 (candidato fino a 200); con `pass_rng` nessuna salva di `b1` (passaggio
    [50, 150]), `pass_rng.calls == 0`. Profilo di `b1` (10, 1): in entrambi gli stati una salva di `b1` a 60.0
    (`places=6`).
19. `test_larger_range_observer_candidate_ends_with_the_window` (FP-3 (a), portata maggiore): geometria del test 18;
    fire control `_kill()` per `r1` e None per `b1`, profilo di `r1` (180, 1), rng `[0.99, 0.0]`, pass_rng vuoto: in
    entrambi gli stati una salva di `r1` su `b1` a 180.0 (`places=6`; candidato fino a `window.t_end` = 200),
    `pass_rng.calls == 0`.
20. `test_own_intervals_is_the_single_volume_call` (VA-6 (a)): su un `_EngagementRun` diretto, (i)
    `run._own_intervals('b1', 'r1', 5000.0) == CS.range_intervals(legs_b1, legs_r1, 5000.0)` e con `radius=3000.0` ==
    `CS.range_intervals(..., 3000.0)`; (ii) None senza tratti; (iii) con `patch.object(ER._EngagementRun,
    '_own_intervals', spia)` che chiama l'originale e registra il nome del chiamante (`sys._getframe(1).f_code.co_name`):
    una risoluzione con `pass_rng=_ScriptedRng([0.7])`, rng `[0.3, 0.6]` e `dwell_time_for` 125 s registra
    `_own_passes` e `_pass_detection_time` (e `_detection_time` per la direzione di `r1`); una risoluzione **senza**
    `pass_rng` con `dwell_time_for` 400 s registra `_exposure_time` e `_detection_time`; (iv) in entrambe le risoluzioni
    le `Detection` sono identiche a quelle ottenute senza spia.
21. `test_rint_launch_seen_only_inside_its_pass` (FP-5 (d) integrato, rilievo "Alta" della revisione di coerenza):
    schema di `TestInterceptionReaction._run` (`:1751-1771`). Forze: blu `[_Asset('b1')]`; rossa `[_Asset('r1'), r2]`
    con `r2 = _TrackingInterceptor('r2', (0.0, 0.0, 0.0), 50_000.0)` e `interceptors=[(r2, 3)]`. Tratti: `r1` e `r2`
    fermi in (0, 0, 0) per [0, 100]; `b1` in moto da (0, 0, 0) lungo +x: **veloce** `Leg(0.0, 100.0, (0.0, 0.0, 0.0),
    (100_000.0, 0.0, 0.0))` (1000 m/s) oppure **lento** `Leg(0.0, 100.0, (0.0, 0.0, 0.0), (50_000.0, 0.0, 0.0))`
    (500 m/s). Finestre: `ContactWindow('b1', 'r1', t_start=0.0, t_end=2.9, t_cpa=0.0, distance_cpa=0.0,
    range_a=50_000.0, range_b=None)` e `ContactWindow('r2', 'b1', t_start=0.0, t_end=T, t_cpa=0.0, distance_cpa=0.0,
    range_a=1_500.0, range_b=None)` con T = 1.5 (veloce) o 3.0 (lento) [V: passaggi di `r2` su `b1` con portata 1500 m
    = [0, 1.5] e [0, 3.0]]. Spec di `b1`: `_miss(rounds=5, interceptable=True, time_of_flight=3.0)`; fire control: la
    spec per `b1`, None per gli altri; profili `{'b1': (2.0, 1.0)}` con default (5.0, 1.0); rng
    `_ScriptedRng([0.0] * 20)`. La salva di `b1` parte a t = 2.0 (rilevamento a 0 + reazione 2), impatto a 5.0.
    Atteso (`resolutions[0].intercepted`): **veloce senza `pass_rng` 3** (rilevamento di `r2` a 0 <= 2: lancio visto,
    tau = 1 s), **veloce con `pass_rng=_ScriptedRng([])` 0** (2.0 fuori dal passaggio [0, 1.5]: non visto, tau = 5 s,
    2 + 5 > 5); **lento 3 in entrambi gli stati** (2.0 dentro [0, 3.0]).
22. `test_rint_without_passes_keeps_the_previous_rule` (ripiego senza tratti): `_EngagementRun` diretto, forze blu
    `[_Asset('l')]` e rossa `[_Asset('i')]`, finestre `_window('i', 'l', t_start=0.0, t_end=100.0, range_a=1000.0,
    range_b=None)` e `_window('i', 'l', t_start=200.0, t_end=300.0, range_a=1000.0, range_b=None)`, **senza** `legs`, rng
    `[0.0, 0.0]`, fire control None, `pass_rng=_ScriptedRng([])`: dopo `.run()`, `run._detection_time_of('i', 'l',
    50.0) == 200.0` (l'ultimo in lista, come prima: istanti 0 e 200 dal ripiego `t_start`), uguale a quello di un run
    senza `pass_rng`; `pass_rng.calls == 0`.
24. `test_passes_join_when_the_gap_is_within_the_dwell` (FP-10, confine compreso): `_EngagementRun` diretto sulla
    geometria comune, `dwell_time_for=lambda o, t, m: 140.0` (uscita = 140 s esatti), rng `[0.3, 0.6]`, pass_rng
    `[0.7]`: `run._own_passes(WINDOW, 'b1', 'r1', 5000.0, 140.0)` ~ `[(50.0, 370.0, 50.0, 370.0)]` (`places=6`);
    `run._pass_cpa(WINDOW, 'b1', 'r1', 50.0, 370.0)` ~ (100.0, 0.0) (`places=6`); dopo `.run()` una sola `Detection` di
    `b1`, con `pass_index` None, `exposure_s` 320.0 (`places=6`), `dwell_time_s` 140.0, `probability` 1.0;
    `rng.calls == 2`, `pass_rng.calls == 0`.
25. `test_passes_stay_apart_when_the_gap_exceeds_the_dwell`: come il 24 con dwell 139.0: due `Detection` di `b1`
    (`pass_index` 0 e 1), `exposure_s` 100.0 e 80.0, `dwell_time_s` 139.0; `pass_rng.calls == 1`.
26. `test_passes_stay_apart_without_a_declared_dwell` (sotto-decisione 1): come il 24 con
    `dwell_time_for=lambda o, t, m: None`: due `Detection` di `b1`, `exposure_s` e `dwell_time_s` None.
27. `test_passes_stay_apart_with_the_dwell_law_off` (sotto-decisione 2): come il 24 senza `dwell_time_for`: due
    `Detection` di `b1`, `exposure_s` None.
28. `test_joined_pass_keeps_the_candidate_across_the_gap` (FP-10 con FP-3 (a)): fire control `_kill()` per `b1` e None
    per `r1`, profilo di `b1` (120, 1), rng `[0.0, 0.99]`, pass_rng `[0.99]`. Dwell 140: una salva di `b1` su `r1` con
    `t_launch` 170.0 (`places=6`; rilevamento a 50, candidato fino a 370, fine del passaggio unito). Dwell 139: nessuna
    salva di `b1` (170 oltre la fine del passaggio [50, 150]; secondo passaggio mancato: 0.99 >= 0.9352 * 80/139).
29. `test_launch_in_a_joined_gap_is_inside_the_pass` (FP-10 con FP-5 (d)): `_EngagementRun` diretto, rng `[0.0, 0.99]`,
    pass_rng `[0.99]`, fire control None. Dwell 140: `run._detection_time_of('b1', 'r1', 200.0) == 50.0` (200 e' nel
    passaggio unito [50, 370]); dwell 139: `None` (200 fra [50, 150] e [290, 370]); in entrambi
    `run._detection_time_of('b1', 'r1', 100.0) == 50.0`.
30. `test_join_passes_boundary` (funzione pura): `ER._join_passes([(0.0, 10.0), (12.0, 20.0), (30.0, 40.0)], 2.0) ==
    [(0.0, 20.0), (30.0, 40.0)]`; con 1.999 la lista e' invariata; con None invariata; `[(0.0, 10.0), (12.0 + 5e-10,
    20.0)]` con 2.0 -> `[(0.0, 20.0)]` (entro TIME_EPS); `[(0.0, 10.0), (12.0 + 2e-9, 20.0)]` con 2.0 -> invariata;
    `ER._join_passes([], 2.0) == []`.

Nella classe esistente `TestDwellTimeInTheResolver` (`:3736`):
14. `test_exposure_is_the_pass_containing_the_cpa` (FP-6, FP spento): geometria comune, `dwell` 400, **senza**
    `pass_rng`: una `Detection` di `b1` con `exposure_s` 100.0 (passaggio che contiene `t_cpa` = 100; la somma sarebbe
    180) e `probability` 0.25.
23. `test_exposure_falls_back_to_the_longest_pass` (FP-6, ripiego `next(..., longest)`, rilievo della revisione):
    tratti di `r1` scambiati `Leg(0, 200, (-10000, 3000, 0), (10000, 3000, 0))`, `Leg(200, 230, (10000, 3000, 0),
    (10000, 0, 0))`, `Leg(230, 430, (10000, 0, 0), (-10000, 0, 0))` (passaggi di `b1` [60, 140], 80 s, e [280, 380],
    100 s [V: `range_intervals` eseguito il 2026-11-08]); finestra come la comune ma con `t_cpa=200.0` (fra i due
    passaggi), `distance_cpa=0.0`, `t_mutual` 60/140; `dwell` 400, **senza** `pass_rng`: `exposure_s` della `Detection`
    di `b1` = 100.0 (il piu' lungo, non il primo 80 ne' la somma 180), `probability` 0.25.

`Test/Test_Session_Simulator.py`, classe nuova `TestPerPassDetectionSwitch(_Base)` modellata su `TestDwellTimeSwitch`
(`:235-266`):
15. `test_switch_off_passes_no_pass_rng`: nessuna chiamata a `resolve_engagement` riceve `pass_rng`.
16. `test_switch_on_passes_the_pass_stream`: con `patch.object(ER, 'FP_PER_PASS_DETECTION', True)` ogni chiamata
    riceve `pass_rng` con un metodo `random` chiamabile.
17. `test_pass_event_id_is_distinct_and_order_free`: `pass_event_id('a', 'b') == pass_event_id('b', 'a')`, diverso
    da `engagement_event_id('a', 'b')` e da `temper_event_id('a', 'b')`; `ValueError` con un solo id.

Conteggio: `TestDetectionPerPass` 25 (1-13, 18-22, 24-30), `TestDwellTimeInTheResolver` 2 (14, 23),
`TestPerPassDetectionSwitch` 3 (15-17): **30**.

#### 4.1.6 Esito atteso del blocco 1

- Suite: **`Ran B_FP + 30`** (~4906 [S]), `OK (skipped=7)`.
- Confronto con la fotografia: `UNCHANGED (1009)`, **0 cambiate**, `compared 1093 runs: 84 difference lines` (le
  stesse 84 NEW della base). Le 1009 restano identiche perche' l'interruttore e' spento (`engage` non passa
  `pass_rng`, `_detect_direction` esegue le stesse istruzioni, `_detection_time_of` usa il dizionario di prima) e la
  D-5 e' spenta (FP-6 non agisce).
- **Verifica di tutte le esecuzioni, nuove comprese** (S32, S35, S34 non sono nella fotografia: un loro cambio non si
  vedrebbe nel confronto): `<python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare
  .ai-run/fp_base_capture.json --against .ai-run/confronto_capture.json` -> **`compared 1093 runs: IDENTICAL`**.
  Copre anche FP-6 (punto 8), l'unica parte che agisce a FP spento: le varianti `long`, `short`, `ewr_on` di S32 hanno
  la D-5 accesa e un solo passaggio per direzione (P-0), quindi la permanenza non cambia. Se non e' IDENTICAL:
  fermarsi e riferire le righe.

### 4.2 Blocco 2 — scenario S33-PASSES

#### 4.2.1 `Test/Test_Session_Scenarios_S33.py` (nuovo, 13 test)

Docstring di modulo nello stile di S32 (`Test_Session_Scenarios_S32.py:1-28`) con la tabella delle 4 varianti (due
geometrie x {tutto spento, FP e D-5 accese}) e le frasi: "Le varianti `off` e `cas_off` sono lo stato precedente: FP e
D-5 spente, nessun dwell dichiarato. Le varianti `on` e `cas_on` sono la configurazione finale: FP e D-5 accese, e la
ZSU dichiara (`declare_dwell`, modo 'air') un periodo di aggiornamento di 2 s, STIMA [S] dell'utente (2026-11-08:
osservatore umano piu' ottica), non un dato. Con passaggi di 50-67 s il fattore di permanenza e' g = 1 e con uscite di
100-130 s l'unione dei passaggi (FP-10) non unisce: la D-5 non cambia ne' estrazioni ne' Pd; per questo non ci sono
varianti con dwell lunghi." Costruzione:

```python
SEEDS = [f'S33-PASSES-{index}' for index in range(5)]
# variante -> (geometria, interruttori FP_PER_PASS_DETECTION e D5_DWELL_TIME, con il dwell ZSU_DWELL_S sulla ZSU)
VARIANT_SPEC = {
    'off': ('reentry', False),
    'on': ('reentry', True),
    'cas_off': ('cas', False),
    'cas_on': ('cas', True),
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
# STIMA [S] dell'utente (2026-11-08): periodo di aggiornamento della traccia della ZSU-57-2 (osservatore umano piu'
# ottica, "predizione" del cervello). NON e' un dato. Dichiarato sulla ZSU (F.declare_dwell, modo 'air') solo nelle
# varianti con FP e D-5 accese: soglia di unione FP-10 (le uscite fra i passaggi sono molto piu' lunghe: nessuna unione)
# e dwell della legge D-5 (passaggi molto piu' lunghi: g = 1).
ZSU_DWELL_S = 2.0
```

Nota: il secondo elemento di `VARIANT_SPEC` e' **un solo booleano** per i due interruttori (la conferma dell'utente
esclude varianti con una sola delle due regole accesa, §3.1); se acceso, si dichiara anche il dwell.

Funzioni del modulo:
- `build` e `ZSU`, `ZSU_POSITION`, `ER_MODULE` importati da `Test_Session_Scenarios_S32` (geometria di rientro:
  `build(with_ewr=False)`, `:67-80`).
- `build_cas()` nuova: forza `Red-Line` (lato 'Red') con, in quest'ordine, tre `F.Unit('vehicle', 'BMP-2', 1,
  origin=CAS_TARGETS[prefix], prefix=prefix, sensors=VISUAL)` per `prefix` in `('ifvA', 'ifvB', 'ifvC')` e
  `F.Unit('vehicle', 'ZSU-57-2', 1, origin=ZSU_POSITION, prefix='ad')`; forza `Blue-CAS` identica a quella di
  `Test_Session_Scenarios_S32.build` (stessa riga `F.Unit('aircraft', 'A-10C Thunderbolt II', 4, origin=(-40_000.0,
  0.0, 3_000.0), step=(0.0, 500.0), prefix='cas', loadout='Maverick/Gun CAS')`, `mil_category=F.AIR_UNIT`). `DURATION`,
  `IFV_IDS`, `VISUAL` e `MAVERICK` importati da `Test_Session_Scenarios_S19_Air_Defence` come in S32 (`:38-40`). Restituisce `(red, cas)`.
- `run_variant(session_id, variant)` come quello di S32 (`:83-110`): geometria `'reentry'` = `build(with_ewr=False)`,
  rotta `REENTRY`, bersaglio GROUP `Red-Line` con `asset_ids=IFV_IDS`; geometria `'cas'` = `build_cas()`, rotta
  `CAS_ROUTE`, bersaglio GROUP `Red-Line` con `asset_ids=CAS_TARGET_IDS`; per entrambe `mission_type='CAS'`,
  `weapons=(MAVERICK,)`, `rules=MissionRules(roe='only_designated')`, nessun `attack_waypoint`. Con `geometry, switch =
  VARIANT_SPEC[variant]`, attorno all'intera esecuzione (costruzione delle forze compresa, come S32 `:95-108`):

  ```python
  with patch.object(ER_MODULE, 'FP_PER_PASS_DETECTION', switch), patch.object(ER_MODULE, 'D5_DWELL_TIME', switch):
      red, cas = build(with_ewr=False) if geometry == 'reentry' else build_cas()

      if switch:
          F.declare_dwell(red.assets[ZSU], {'air': ZSU_DWELL_S})
      ...
      outcome = F.run(session_id, [cas], [red], make_registry_fire_control(), duration=DURATION,
                      missions=missions, thresholds=BOTH_HOLD)
  ```

  `F.run` si chiama **attraverso il modulo** `F` e con le forze rosse come terzo argomento posizionale `[red]`, come
  S32 (`:107`): il test 13 lo sostituisce. I due `patch.object` ripristinano i valori precedenti all'uscita dal blocco
  anche se l'esecuzione solleva un'eccezione (contesto di `unittest.mock`); `declare_dwell` agisce sull'istanza della
  ZSU costruita dentro la variante (`Test/Scenario_Fixtures.py:306-338`: sostituisce `detection_dwell_time` solo
  sull'istanza), quindi nessuno stato resta fra varianti o fra test. La spia su `ER.resolve_engagement` salva, **prima**
  di chiamare l'originale,
  `copy.deepcopy(kwargs.get('pass_rng'))` (None se assente) e dopo la coppia `(risultato, copia)`. Restituisce
  `(outcome, results, pass_streams)`: le coppie con risultato non None, separate in due liste allineate.
- Ciclo esterno sui semi, interno sulle 4 varianti nell'ordine di `VARIANT_SPEC` (stesso `session_id` per le 4
  varianti di un seme). Classe `TestS33DetectionPerPass(F.LoggerSilencer, unittest.TestCase)`; `_zsu(results,
  cas=None)` = le `Detection` con `observer_id == ZSU` (e `target_id == cas` se dato) di tutti i risultati;
  `_first_zsu(results, cas)` = le `Detection` della ZSU su `cas` nel **primo** risultato che ne contiene almeno una.

Nota per l'esecutore [V, calcolo del 2026-11-07 con `Scenario_Fixtures.missions_for`, `Mission_Adapter.movement_legs` e
`range_intervals` contro la ZSU ferma, senza sessione; non ripetuto il 2026-11-08, codice dei moduli coinvolti non
cambiato dalla BI]: con entrambe le rotte `missions_for` crea **4 missioni** (`Blue-CAS:CAS-1..4`, un A-10C ciascuna)
perche' la formazione traslata non e' riducibile a un offset dopo le virate; velocita' 155,6 m/s. Per questo i test
non assumono che i 4 A-10C stiano nello stesso `EngagementResult`.

Test 1-5 (geometria di **rientro**, varianti `off`, `on`):
1. `test_premise_two_passes_per_aircraft`: in `on`, per ogni seme e A-10C, esattamente 2 `Detection` della ZSU, con
   `pass_index` {0, 1}, `pass_count` 2, `dwell_time_s == ZSU_DWELL_S` per entrambe e `pass_start` del passaggio 1 -
   `pass_end` del passaggio 0 `> ZSU_DWELL_S` (il lettore del dwell e' attivo, l'unione FP-10 e' stata valutata con il
   dwell stimato e non ha unito).
2. `test_switch_off_one_draw_per_window`: in `off`, per ogni seme e A-10C, esattamente 1 `Detection` della ZSU, con
   `pass_index` None.
3. `test_the_engagement_stream_is_unchanged`: per ogni seme, nel PRIMO `EngagementResult`,
   `[d.draw for d in off.detections] == [d.draw for d in on.detections if d.pass_index in (None, 0)]`.
4. `test_no_launch_after_the_pass_without_a_new_detection` (FP-3 (a)): in `on`, per ogni salva della ZSU in un
   risultato esiste, nello stesso risultato, una `Detection` rilevata della ZSU sullo stesso bersaglio con `time <=
   t_launch + 1e-9` e `t_launch <= pass_end + 1e-6`. In particolare nessuna salva della ZSU fra la fine del passaggio 0
   e il rilevamento nel passaggio 1.
5. `test_premise_the_zsu_fires_without_the_switch`: in `off` la ZSU spara in almeno un seme.

Test 6-11 (geometria **CAS**, varianti `cas_off`, `cas_on`):
6. `test_cas_premise_geometry` (senza sessione): con `red, cas = build_cas()`: la distanza orizzontale dalla ZSU di
   `Red-Line/ifvA0` e `Red-Line/ifvC0` e' `< ZSU_VISUAL_RANGE_M` e quella di `Red-Line/ifvB0` e' `>
   ZSU_VISUAL_RANGE_M`; `CS.mutual_detection_ranges(red.assets[ZSU], cas.assets['Blue-CAS/cas0'])` e'
   `(ZSU_VISUAL_RANGE_M, A10_GROUND_RANGE_M)`; per ogni A-10C, il punto di partenza e i punti di `CAS_ROUTE` traslati
   della sua formazione (`dy = 500 * indice`, quota 3000 m) distano dalla ZSU meno di `A10_GROUND_RANGE_M`.
7. `test_cas_premise_two_separate_passes_per_aircraft`: in `cas_on`, per ogni seme e A-10C, `_first_zsu` ha
   esattamente 2 `Detection`, con `pass_index` {0, 1}, `pass_count` 2, `distance_cpa < ZSU_VISUAL_RANGE_M` e
   `dwell_time_s == ZSU_DWELL_S` per entrambe e `pass_start` del passaggio 1 - `pass_end` del passaggio 0 `> 60.0` s
   (calcolata ~103-104 s; 60 s e' un margine del test, non un dato; implica anche `> ZSU_DWELL_S`: nessuna unione).
8. `test_cas_switch_off_one_draw_per_aircraft`: in `cas_off`, per ogni seme e A-10C, `_first_zsu` ha esattamente 1
   `Detection`, con `pass_index` None.
9. `test_cas_first_pass_keeps_the_engagement_stream`: per ogni seme, nel PRIMO `EngagementResult`,
   `[d.draw for d in cas_off.detections] == [d.draw for d in cas_on.detections if d.pass_index in (None, 0)]`.
10. `test_cas_second_pass_draws_from_the_pass_stream`: in `cas_on`, per ogni seme e per ogni coppia (risultato, copia
    dello stream) con copia non None: `[d.draw for d in risultato.detections if d.pass_index not in (None, 0)] ==
    [copia.random() for _ in range(n)]` (n = lunghezza della lista di sinistra); inoltre, sommando su tutti i risultati
    del seme, almeno una `Detection` della ZSU con `pass_index == 1` per ogni A-10C.
11. `test_cas_no_launch_after_the_pass_without_a_new_detection` (FP-3 (a)): come il test 4, in `cas_on`.

Test 12-13 (D-5 nelle varianti accese, conferma dell'utente del 2026-11-08 sera; tutte e due le geometrie):
12. `test_d5_reads_the_dwell_and_leaves_the_probability_unchanged`: (i) in `on` e `cas_on`, per ogni seme, ogni
    `Detection` della ZSU con `distance_cpa < ZSU_VISUAL_RANGE_M` ha `dwell_time_s == ZSU_DWELL_S`, `exposure_s >=
    ZSU_DWELL_S` e `ER.dwell_factor(d.exposure_s, d.dwell_time_s) == 1.0` (g = 1 esatto: la D-5 non cambia la Pd), e
    ce n'e' almeno una per seme (premessa non vacua); (ii) in `on` e `cas_on` ogni `Detection` con osservatore diverso
    dalla ZSU (A-10C, BMP-2) ha `dwell_time_s is None` ed `exposure_s is None` (il lettore restituisce None: nel registro
    il dwell lo dichiarano solo i 10 EWR); (iii) in `off` e `cas_off` ogni `Detection` (tutti gli osservatori) ha
    `dwell_time_s is None` ed `exposure_s is None` (D-5 spenta: nessun lettore passato al risolutore).
13. `test_variant_switches_are_scoped` (senza sessione): per ogni variante, letti prima `before =
    (ER.FP_PER_PASS_DETECTION, ER.D5_DWELL_TIME)`, `run_variant('S33-PASSES-0', variant)` con `patch.object(F, 'run',
    side_effect=probe)`, dove `probe(*args, **kwargs)` registra `(ER_MODULE.FP_PER_PASS_DETECTION,
    ER_MODULE.D5_DWELL_TIME, args[2][0].assets[ZSU].detection_dwell_time('air'))` e solleva `RuntimeError`; la chiamata
    sta in `assertRaises(RuntimeError)`. Atteso registrato: `(True, True, ZSU_DWELL_S)` per `on` e `cas_on`, `(False,
    False, None)` per `off` e `cas_off`; dopo ogni chiamata `(ER.FP_PER_PASS_DETECTION, ER.D5_DWELL_TIME) == before`
    (ripristino anche con l'eccezione). Il confronto con `before` e non con `(False, False)` lascia il test valido se un
    chiamante (per esempio una sonda) ha cambiato i valori globali prima della suite.

Valori attesi [V: calcolo sui tratti del 2026-11-07, da leggere all'esecuzione, NON da scrivere come asserzioni]:
- rientro: passaggi della ZSU [230, 284] s e [410, 464] s per `cas0` (49,8-53,8 s secondo l'A-10C), pausa 126-130 s;
- CAS: passaggi [230, 297] s e [401, 462] s per `cas0` (62,7-66,7 s e 60,8-66,7 s secondo l'A-10C), pausa 103-104 s;
  distanza massima dalla ZSU 41 km (partenza), dei bersagli dalla ZSU 1044 m (A), 13 003 m (B), 2879 m (C);
- 4 estrazioni della ZSU per seme in `off`/`cas_off`, 8 in `on`/`cas_on`.
Se (1) o (7) fallissero (la sessione non da' due passaggi in una finestra: per esempio un ritaglio G4a o una
ri-pianificazione G4b), l'esecutore **non** cambia la rotta: si ferma e riferisce `pass_count`, gli istanti e le
finestre osservate. Se fallisse il punto (i) del test 12 (una direzione della ZSU entro la portata con permanenza
< 2 s, quindi g < 1: per esempio una finestra spezzata o un passaggio di durata quasi nulla), l'esecutore **non**
cambia `ZSU_DWELL_S` ne' la rotta: si ferma e riferisce seme, A-10C, `exposure_s`, `pass_start/pass_end` e la finestra;
in quel caso la D-5 cambierebbe la Pd di quella direzione e gli esiti `on` non sarebbero piu' "FP sola" (decisione
dell'utente).

#### 4.2.2 `Test/Scenario_Baseline.py`

In `UNITS`, in coda, dopo la riga `S34-BAND` di VA (nell'ordine di esecuzione, tabella di BI §6.1):

```python
    # ── S33 (FP: un'occasione di rilevamento per passaggio nel volume proprio) — in coda, nomi stabili ──
    ('S33-PASSES', 'Test_Session_Scenarios_S33', 'TestS33DetectionPerPass', None,
     _by_occurrence('off', 'on', 'cas_off', 'cas_on')),
```

(l'ordine dei nomi e' quello del ciclo interno sulle varianti, `VARIANT_SPEC`: la fotografia numera le esecuzioni per
occorrenza del `session_id` nell'unita', `_by_occurrence`, `Test/Scenario_Baseline.py:227`).

e nel docstring, dopo la sezione di VA ("## Quota nel volume d'ingaggio (VA)"):

```
## Rilevamento per passaggio dopo la FP

Il rilevamento per passaggio nella portata propria (`Engagement_Resolver.FP_PER_PASS_DETECTION`, SPENTO, temporaneo;
`Proposta_Finestre_Per_Passaggio_Portata_Propria.md`) non cambia le esecuzioni esistenti (interruttore spento).
Aggiunge in coda l'unita' S33-PASSES (4 varianti: rientro e CAS, ciascuna con tutto spento e con FP e D-5 accese,
dwell della ZSU 2 s, stima; 5 seed): 20 esecuzioni nuove; nessuna voce nuova nel riassunto (i `Detection` non sono
registrati).
```

#### 4.2.3 Vincoli del blocco 2

- **Nomi stabili**: unita' `S33-PASSES`; varianti, nell'ordine, `off`, `on`, `cas_off`, `cas_on`; semi
  `S33-PASSES-0..4`; asset `Red-Line/ad0` (ZSU), `Red-Line/ifv0..2` (rientro), `Red-Line/ifvA0`, `Red-Line/ifvB0`,
  `Red-Line/ifvC0` (CAS), `Blue-CAS/cas0..3`; missioni `Blue-CAS:CAS-1..4` (generate dal fixture). Nessun nome esistente
  cambia.
- `ZSU_DWELL_S = 2.0` dichiarato STIMA [S] dell'utente nel codice (commento) e nel rapporto; il margine di 60 s del test
  7 e' una soglia del test, dichiarata come tale.
- Nessuna modifica a `Test_Session_Scenarios_S32.py` (si importano `build`, `ZSU`, `ZSU_POSITION`, `ER_MODULE`;
  `build_cas` sta in S33).
- Interruttori e dwell come in §4.2.1 (`run_variant`): `FP_PER_PASS_DETECTION` e `D5_DWELL_TIME` sostituiti insieme,
  con `patch.object` sul modulo `ER_MODULE`, solo durante la variante; `F.declare_dwell` solo in `on`/`cas_on`, sulla
  ZSU di quella variante. Nessuna variante con una sola delle due regole accesa (criterio dell'utente del 2026-11-08:
  niente scenari sulle combinazioni di interruttori che il modello scarta; le varianti sono lo stato precedente e la
  configurazione finale). Nessuna modifica al valore di default di `D5_DWELL_TIME` nel codice.

#### 4.2.4 Esito atteso del blocco 2

- Suite: **`Ran B_FP + 43`** (~4919 [S]; 30 del blocco 1 + 13 di S33), `OK (skipped=7)`.
- Confronto: `UNCHANGED (1009)`, 0 cambiate, **`compared 1113 runs: 104 difference lines`** (104 NEW: 20 `S32-DWELL`,
  32 `S35-ADTGT`, 32 `S34-BAND`, 20 `S33-PASSES/S33-PASSES-<k>/<variante>`).
- Verifica sulla cattura di base: `--compare .ai-run/fp_base_capture.json --against .ai-run/confronto_capture.json` ->
  `compared 1113 runs: 20 difference lines`, tutte `NEW S33-PASSES/...` (nessuna DIFF ne' MISSING).
- Fra le nuove, `off` e `on` (e `cas_off` e `cas_on`) di un seme possono differire nel contenuto (e' l'effetto della
  regola FP: occasioni per passaggio e fine del candidato); nessuna asserzione lo richiede. La D-5 accesa in `on`/`cas_on`
  non contribuisce alla differenza finche' vale la premessa g = 1 del test 12 (nessuna estrazione, fattore 1.0
  esatto, §2.9); le sole differenze dovute alla D-5 sono i campi `dwell_time_s`/`exposure_s` delle `Detection`, fuori
  dalla fotografia.

### 4.3 Dopo i blocchi (sessione principale, non l'esecutore)

1. Sonda **P-1** (`probe_switch_on.py`, riscritta il 2026-11-08; comandi e lettura in `LEGGIMI.md`): accende la regola
   in memoria e riesegue il confronto con la fotografia, contando i passaggi di durata zero (`ZERO_PASSES`, righe
   `ZERO`) e le decisioni R-INT in cui "lancio visto" cambia con FP-5 (d) (righe `RINT_D`). **Atteso** (confermato
   dall'utente la sera del 2026-11-08): righe `DIFF` **al piu' fra le 44 `AFTER_PASS` di P-0 piu' le eventuali
   `RINT_D`**. E' un'attesa **NON misurata** [I]: P-0 ha contato le 44 `AFTER_PASS` ma non sa quali cambieranno, e non
   ha contato le `RINT_D`; i numeri veri sono quelli di P-1. In dettaglio:
   - righe `DIFF` (esecuzioni della fotografia cambiate) fra le 44 `AFTER_PASS` di P-0 (S13-2, S13-4, S14-4,
     6 di S21, S24-ORBIT-0/full, 32 di S26-BINGO, 2 di S28-CLASS), effetto di FP-3 (a); probabilmente quasi tutte [I];
   - **in piu'**, possibili cambiate fra le esecuzioni `RINT_D` (FP-5 (d): lancio fuori dal passaggio del
     rilevamento), che P-0 non ha misurato: atteso [I] poche o nessuna, perche' un lanciatore lancia di solito dentro il
     volume dell'intercettore che lo ha appena rilevato; da leggere a parte;
   - FP-6 e FP-10 non agiscono (D-5 spenta in tutta la fotografia); `MULTI` e `RINT` di P-0 sono vuote;
   - una cambiata che non e' ne' `AFTER_PASS` ne' `RINT_D` va diagnosticata;
   - `ZERO_PASSES`: nessun atteso, conteggio informativo (§5.2).
   Facoltativo (rilievo della revisione di coerenza): le esecuzioni nuove (S32, S35, S34, S33) con la regola accesa
   contro `.ai-run/fp_base_capture.json` (comando in `LEGGIMI.md`); atteso [I] S32 identica (nessuna salva
   `AFTER_PASS` in S32 per P-0, nessun intercettore `Anti_Missile`), S35/S34 informative. S33 fissa da se' i due
   interruttori in ogni variante (`patch.object` in `run_variant`, §4.2.1): l'accensione globale di P-1 non la cambia,
   e nella cattura di base non c'e' (righe NEW).
   **Esito di P-1 (2026-11-11, ProArt; estratto in `Rapporti/Sonde_Finestre_Passaggio/esito_p1.txt`)**: `compared 1113
   runs: 1060 difference lines`; **44 esecuzioni della fotografia cambiate = esattamente le 44 `AFTER_PASS` di P-0**
   (insiemi identici); `RINT_D` 0 (0 decisioni R-INT cambiate su 407); `ZERO_PASSES` 0 su 34116 passaggi; 0 cambiate
   fra le nuove S32/S34/S35; S33 20 NEW. Effetto (solo FP-3 (a)): in tutte e 44 la difesa spara meno (153 salve in meno,
   mai in aumento); in 11 cambiano esito o perdite a favore dell'attaccante (S13-2, S13-4, S14-4, 6 di S21, 2 di
   S28-CLASS-2); S26-BINGO (32) e S24-ORBIT: solo salve e danni (S26 `transfer_continue`: l'istante di fine movimento
   passa da 1200 s a ~1163-1169 s, perche' l'episodio con Red-Site finisce all'uscita dal sensore). Le attese sono
   confermate (nessuna cambiata fuori da `AFTER_PASS`/`RINT_D`).
2. **Decisione dell'utente (2026-11-12): `FP_PER_PASS_DETECTION` ACCESO** (default `True`) dopo la lettura dei numeri di
   P-1 e delle esecuzioni cambiate. Verifica dopo l'accensione (osboxes): suite `Ran 4919` (un solo test da aggiornare in
   `Test_Session_Scenarios_S26`, `test_transfer_continue_runs_dry_after_the_engagement`: l'istante di perdita non e' piu'
   la fine rotta ma la fine dell'episodio, fra l'uscita dal sensore a 1160 s e la fine rotta a 1200 s; altri 3 test che
   assumevano il default spento sono ora espliciti), confronto `UNCHANGED (965)` + 44 `CHANGED` (le stesse 44 di P-1) e
   `compared 1113 runs: 1060 difference lines`. **Fotografia nuova installata il 2026-11-12 su richiesta dell'utente**
   (`Test/baseline/scenario_baseline.json`, **1113 esecuzioni**, 0 errori di unita', catturata con la regola accesa in 1186 s;
   rispetto alla precedente differisce esattamente per le 44 cambiate di P-1 e per le 104 nuove di S32-S35).
3. **ESEGUITO il 2026-11-13** (`Proposta_FP_Pulizia_Interruttore.md`, 4 blocchi di `oc-developer` su `ai/oc-fp-pulizia`,
   merge `f46e3982`): suite `Ran 4914`, `OK (skipped=7)`; confronto `UNCHANGED (1103)`, 0 `CHANGED`, `compared 1103 runs:
   10 difference lines` = le 10 `MISSING` di S33 (`off`/`cas_off`). **Fotografia di 1103 esecuzioni installata il
   2026-11-13 su richiesta dell'utente** (commit `3b5edf49`). Con i tratti e >= 2 passaggi `pass_rng` e' obbligatorio
   (`ValueError`). Descrizione di progetto originale: **Blocco di pulizia** (dopo i punti 1-2 e la fotografia nuova; da pianificare a parte): elimina
   `FP_PER_PASS_DETECTION` e i rami `pass_rng is None` (in `_detect_direction` i passaggi si calcolano sempre; in
   `_detection_time_of` resta solo FP-5 (d) con il ripiego senza tratti; `Session_Simulator` passa sempre `pass_rng`);
   riscrive i test che provano lo stato spento (1, 2, 15 e le meta' "senza `pass_rng`" degli altri) e toglie le
   varianti `off`/`cas_off` di S33 (nomi della fotografia da aggiornare con la fotografia nuova); il ramo con i tratti
   di `_exposure_time` (FP-6) diventa il solo ripiego per le direzioni a zero passaggi e si semplifica; manuale
   aggiornato.

### 4.4 Tempi di verifica (ProArt, `tools/ai/verifica.sh`, mai in parallelo)

Per blocco: suite ~10 minuti, poi confronto ~10 minuti [AGENTS.md]; il confronto della cattura di base contro la nuova
dura secondi (nessuna esecuzione). P-1 ~8-10 minuti [S, sulla durata di P-0, 484 s]. Le 20 sessioni di S33 aggiungono
~1 minuto alla suite e al confronto [I, per analogia con S32: 20 sessioni ~1 minuto].

### 4.5 Comandi di verifica (dalla root del repo)

    bash tools/ai/verifica.sh suite start          # poi: bash tools/ai/verifica.sh suite wait   (fino a ESITO)
    bash tools/ai/verifica.sh confronto start      # poi: bash tools/ai/verifica.sh confronto wait
    <python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Engagement_Resolver
    <python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Simulator
    <python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S33
    <python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare .ai-run/fp_base_capture.json \
        --against .ai-run/confronto_capture.json
    <python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline \
        --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json \
        --against .ai-run/confronto_capture.json | grep -cE '^NEW'          # 84 dopo il blocco 1, 104 dopo il 2
    grep -n "range_intervals(" Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py   # punto 8-bis

`<python>` = l'interprete che `verifica.sh` stampa nell'ESITO. Suite e confronto mai in parallelo; numeri riportati
dall'ESITO, mai stimati. **Non installare mai una fotografia nuova.**

### 4.6 Scelte minori lasciate all'esecutore (da elencare nel rapporto)

Nomi delle variabili locali e delle costanti di test, posizione dei metodi nuovi dentro la classe, testo dei
messaggi di log, aiuti di costruzione dei test (un `_run`/`_direct` locale), struttura interna di
`Test_Session_Scenarios_S33.py` (riuso o copia locale di `run_variant`), la sessione minima dei test 15-16 (quella di
`_Base`), il modo di raccogliere le salve nei test S33 4 e 11, la forma interna di `_first_zsu` e del calcolo della
distanza orizzontale nel test S33 6, la forma interna di `probe` nel test S33 13.

---

## 5. Rischi e limiti

### 5.1 Rischi di esecuzione

- `_detect_direction` e' il punto piu' delicato del motore; il blocco 1 ne riscrive il preambolo (lettura del dwell
  spostata in `_dwell_of`, ramo FP). La rete: test 2, 4, 10 (stream e percorso di prima, anche con dwell), 14 e 23
  (D-5 a FP spento), confronto **0 cambiate** e cattura di base **IDENTICAL su 1093** a interruttore spento (§4.1.6).
- **FP-6 agisce a FP spento** (decisione dell'utente, dentro `D5_DWELL_TIME`): e' l'unica modifica del blocco 1 a un
  comportamento gia' committato senza l'interruttore FP. Oggi non cambia nulla (D-5 spenta; S32 a un passaggio per
  direzione); cambierebbe le sessioni con la D-5 accesa e direzioni a piu' passaggi.
- **FP-10 con unione effettiva e la permanenza per passaggio con g < 1 (FP-6 con FP acceso) non sono esercitati in
  sessione**: S33 `on`/`cas_on` accende FP e D-5 con il dwell di 2 s [S] e percorre solo il ramo "nessuna unione,
  g = 1" (lettore del dwell, `_dwell_of`, `_join_passes` che non unisce, permanenza per passaggio calcolata e
  registrata in `exposure_s` ma senza effetto sulla Pd). L'unione e g < 1 sono coperti **solo** dai test unitari 9, 10,
  24-30. Asserzioni esatte, da non indebolire.
- **Premessa g = 1 di S33** (test 12): se in qualche seme una direzione della ZSU entro la portata avesse permanenza
  < 2 s (finestra spezzata da G4a/G4b, passaggio quasi tangente), la D-5 ne ridurrebbe la Pd e gli esiti `on` non
  sarebbero piu' quelli della sola FP; il test 12 lo rileva e l'esecutore si ferma (§4.2.1).
- **FP-5 (d) non e' esercitato in sessione** (nessuno scenario con intercettore che rileva un lanciatore in rientro):
  coperto dai test 13, 21, 22, 29; il suo effetto sulla fotografia a regola accesa si legge in P-1 (`RINT_D`). P-0 non
  lo aveva misurato: l'attesa e' "al piu' le 44 `AFTER_PASS` (FP-3 (a)) piu' le eventuali `RINT_D` (FP-5 (d))", NON
  misurata [I].
- I test 4 e 11 di S33 e 8, 18, 19, 28 del blocco 1 controllano FP-3 (a): fine del candidato = fine del passaggio
  (unito) per l'osservatore con la portata minore, fine della finestra per l'altro.
- Il costo con la regola accesa: un `range_intervals` per direzione e un CPA (con `Point3D` di sympy) per passaggio
  multi; trascurabile rispetto a una sessione [I], da confermare con i tempi di P-1.
- **La fotografia non esercita la regola** (P-0: 0 direzioni multi su 33 910): il percorso dei passaggi multipli
  (`_detect_passes`, `pass_rng`, FP-3/4/6/10) e' coperto **solo** dai test unitari e dai 13 test di S33.
- **Sessioni di S33 e G4a/G4b**: un ritaglio d'episodio o una ri-pianificazione potrebbe spezzare la finestra o
  cambiare la rotta prima del secondo passaggio in qualche seme: se le premesse (1) o (7) falliscono l'esecutore si
  ferma (§4.2.1).
- **Coordinamento con BI e VA**: righe spostate dai loro blocchi (ricerca per nome, §4.0 punto 5); posizione
  dell'interruttore e della riga `UNITS` in coda (tabella di BI §6.1); numeri dipendenti da BI 3 e VA 2 non ancora
  eseguiti (§4.0.1, [S]/[I]).
- **FP-5 entro `TIME_EPS`** [I]: rilevamenti e lanci a meno di `TIME_EPS` dal bordo di un passaggio sono considerati
  dentro; effetto atteso nullo.

### 5.2 Limiti di modello (da dichiarare nel manuale)

- **Senza tratti** (chiamate dirette) nessun passaggio: un'estrazione per finestra e direzione, candidato fino alla
  fine della finestra e R-INT con l'ultimo rilevamento, come prima. **Con i tratti e una direzione a >= 2 passaggi,
  `pass_rng` e' obbligatorio** (`ValueError` altrimenti, dopo la pulizia del 2026-11-13).
- **Fine del tiro all'uscita dal volume** (FP-3 (a)): con la regola accesa l'osservatore con la portata minore non
  lancia salve **nuove** dopo la fine del passaggio (unito); una salva **gia' lanciata** prosegue fino all'impatto. Non
  e' modellata una guida che richieda il sensore dopo il lancio. Con la regola spenta resta il limite di oggi (P-0: 151
  salve in 44 esecuzioni lanciate dopo la fine dell'unico passaggio).
- **R-INT** (FP-5 (d)): con la regola accesa un lancio fuori da ogni passaggio dell'intercettore sul lanciatore e'
  "non visto" anche se l'intercettore lo aveva rilevato in un passaggio precedente (traccia persa); con la regola
  spenta resta il difetto latente "ultimo rilevamento" (§1.9). Con `BI_AD_TARGET_RULE` acceso la regola conta solo per
  cruise/balistici e, contro i navali, per gli antinave.
- **Passaggi tangenti o ritagliati a durata nulla** contano come passaggi (Pd sul bordo = 0,5 x fattore, legge di
  oggi; con FP-3 (a) nessun candidato se la reazione non e' nulla); con la D-5 la permanenza nulla li annulla. Il loro
  numero nella fotografia lo conta P-1 (`ZERO_PASSES`).
- **Passaggio diviso da un decollo/atterraggio** (`_pair_windows`): due finestre, due estrazioni, come oggi.
- **Unione dei passaggi (FP-10)**: solo nel risolutore, solo con la D-5 accesa e il dwell dichiarato dal sensore (oggi i
  10 EWR; DW-9 estendera'). Sensori senza dwell, o D-5 spenta: un'uscita di pochi secondi crea un passaggio nuovo e
  un'estrazione in piu' (per traiettorie sul bordo del volume la Pd cumulativa e' sovrastimata: esempio di §2.11,
  0,915 contro 0,759). Con FP spento nessuna unione (§2.11, sotto-decisione 3). **Copertura**: in sessione (S33
  `on`/`cas_on`) l'unione e' valutata ma non unisce (uscite >> 2 s) e la D-5 da' g = 1; l'unione effettiva e la
  permanenza per passaggio con g < 1 sono provate solo dai test unitari.
- **Finestre e pianificatore restano con la tolleranza numerica** (FP-10, sotto-decisione 2): l'osservatore con la
  portata maggiore riceve ancora due finestre (due estrazioni) per un'uscita breve dal volume anche se e' <= dwell; il
  pianificatore conta due attraversamenti (`CROSSING_JOIN_TOLERANCE_S` = 1e-6 s). Incoerenza dichiarata fra DES (FP
  accesa) e finestre/pianificatore.
- **Pianificatore** (FP-9): `Path.max_detection_probability` e' il **peggiore** degli attraversamenti, non la
  probabilita' cumulativa di essere rilevati almeno una volta che il DES da' con la regola accesa (due attraversamenti
  a 0,4: metrica 0,4, DES 0,64). La metrica cumulativa (`cumulative_detection_probability`) si aggiungera' in una
  Proposta dedicata quando ci sara' un consumatore. Nota dell'utente non verificata nel codice (§2.10): con il criterio
  3 di `Air_Route_Manager` una rotta puo' attraversare piu' volte lo stesso volume (caso raro), vicino a partenza e
  bersaglio le minacce non sono considerate.
- **Detection non nella fotografia**: il numero di estrazioni non e' visibile nel confronto; lo verificano i test.
- **Attacchi CAS a piu' bersagli** (§1.10): il moto e' la spezzata dei punti di missione; nessuna manovra d'attacco
  generata dal motore; l'ordine degli attacchi lo decidono priorita' e portate; la rotta non cambia se i bersagli sono
  distrutti prima (salvo G4b). Un tratto rettilineo attraversa al piu' una volta un volume convesso: il caso
  multi-passaggio nasce solo da rotte con virate (o, in futuro, da volumi non convessi, VA §2.3).

---

## 6. Documenti da aggiornare dopo (non scritti qui)

- **Manuale DES** (`des-manual-writer`): cap. 3 §3.5 (`04_Strato1_Scheduler_Contatti.md:195-201`: `t_mutual_*` e' il
  **primo** intervallo nella portata minore; i passaggi li conta il risolutore); cap. 4 §4.2 (Pd per passaggio,
  distanza del passaggio, permanenza a un passaggio FP-6, unione FP-10), §4.11 (stream `pass_rng`, `pass_event_id`),
  §4.26 (R-INT: FP-5 (d)); cap. 6 (`07_Orchestratore_Session_Simulator.md`: `pass_event_id`); cap. 8 (`09_Validazione.md`:
  S33-PASSES, con `on`/`cas_on` a FP e D-5 accese e dwell della ZSU 2 s [S]); cap. 9
  (`10_Limiti_Estensioni_Divergenze.md`: il limite "una sola estrazione per finestra con piu' passaggi nel volume
  minore" come **storico** e i limiti di §5.2); atlante `11a_Atlante_Risolutore.md` (costante
  `FP_PER_PASS_DETECTION`, campi nuovi di `Detection` a `:1310`, funzioni `_join_passes`, `_detection_time_in_pass`,
  metodi `_dwell_of`, `_own_intervals`, `_own_passes`, `_pass_cpa`, `_pass_detection_time`, `_detect_passes`,
  `_detection_time_of(..., at)`, sequenza di `_detect_direction`).
- **`F4_Differenze_Scenari.md`**: sezione "FP — rilevamento per passaggio (2026-11-xx)": il cambio, 1009 identiche,
  20 nuove di S33 (varianti accese con FP e D-5), esiti di P-0 e P-1 (cambiate `AFTER_PASS` e `RINT_D`, per gruppi),
  passaggi di durata zero, limiti.
- **`Piano_Implementazione_Missione.md`**: riga in §5 fuori dalla numerazione F, come D-4b/D-4c e D-5, con lo stato
  dell'interruttore (temporaneo) e il criterio di rimozione.
- **`Proposta_Dwell_Time_Rilevamento.md`** (chi pianifica quella Proposta): la permanenza non e' piu' la somma (FP-6);
  il dwell e' anche la soglia di unione dei passaggi con la FP accesa (FP-10); DW-9 (dwell a SAM/AAA) estende
  l'unione a quei sensori.
- **`Proposta_Allineamento_Volumi_DES_Pianificatore.md`** §2.3 (chi pianifica): la nota "FP-10 andrebbe rivista con un
  dato di memoria della traccia" e' superata da FP-10 (c) (dwell del sensore).
- **`Rapporti/Sonde_Finestre_Passaggio/LEGGIMI.md`**: aggiornato il 2026-11-08 (P-0 eseguita, attese di P-1); dopo P-1
  i suoi numeri.
- **Memoria** (solo la sessione principale): decisioni FP-5..FP-10, interruttore temporaneo, esiti delle sonde.
