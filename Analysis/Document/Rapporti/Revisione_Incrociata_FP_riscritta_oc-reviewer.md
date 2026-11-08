# Revisione incrociata — Proposta FP riscritta (Finestre per Passaggio nella portata propria)

Revisione indipendente della versione riscritta il 2026-11-08 di
`Analysis/Document/Proposta_Finestre_Per_Passaggio_Portata_Propria.md` (1662 righe), sul commit
`8c440dba` (working tree: solo file non tracciati in `Analysis/Document/Bozze/`). Nessuna suite,
confronto o sonda eseguiti; nessun file di codice o documento modificato, come da mandato.

Convenzioni: **[V]** = verificato leggendo il file alla riga indicata; **[I]** = ipotesi;
**[S]** = stima. Acronimi alla prima comparsa: DES (*Discrete Event Simulation*), RNG (*Random
Number Generator*), CPA (*Closest Point of Approach*), R-INT (regola dell'intercettazione con
tempo di reazione), EWR (*Early Warning Radar*), BI (Proposta *Bersagli Intercettabili*), VA
(Proposta *Allineamento Volumi*), CAS (*Close Air Support*), ZSU (ZSU-57-2, semovente contraereo).

Stato: **completa** (2026-11-08, revisione del commit `8c440dba`; verdetto nella sezione 9).

## 1. Contesto e perimetro

- Decisioni utente da verificare nel piano: FP-1 B-R, FP-2 O3 `pass_rng`, FP-3 (a), FP-4 (a),
  FP-5 (d), FP-6 (a), FP-7 (a) interruttore TEMPORANEO `FP_PER_PASS_DETECTION`, FP-8 modificata
  (S33-PASSES 4 varianti x 5 semi = 20; `on`/`cas_on` con FP e D-5 accese, dwell ZSU 2 s [S]),
  FP-9 (a), FP-10 (c) con tre sotto-decisioni.
- Le revisioni del 2026-11-07 (Coerenza/BI/VA) sono sulla versione PRECEDENTE; ho letto i rilievi
  FP della revisione di coerenza (`Revisione_Incrociata_Coerenza_oc-reviewer.md`) per sapere cosa'
  doveva essere corretto.

## 2. Rilievi della revisione del 2026-11-07: tutti assorbiti? [V]

| Rilievo vecchio | Dove doveva essere corretto | Stato nel testo riscritto [V] |
|---|---|---|
| FP-6 fuori interruttore con opzione APERTA | FP-6 ora DECISA (a), dentro `D5_DWELL_TIME`; eccezione dichiarata nel commento dell'interruttore | [V] §2.7:437-441, commento punto 2 §4.1.1:719-721 |
| Punto 10 hardcodizzava FP-5 = (a) sospesa | FP-5 ora DECISA (d); punto 10 riscritto (`_detection_time_of(..., at)`, `_detection_time_in_pass`) | [V] §2.6:380-424, §4.1.1:1019-1053 |
| Precondizioni/esiti calcolati su "FP per prima" | §4.0/§4.0.1 riscritti sull'ordine BI 3-4 -> VA 1-2 -> FP con base reale `Ran 4829` | [V] §4.0:641-659, §4.0.1:661-682 |
| Ancore di posizione (interruttore prima di BI/VA; UNITS dopo S32) | Interruttore "in coda... subito dopo `VA_ENGAGEMENT_ALTITUDE_BAND`"; UNITS "dopo la riga S34-BAND di VA" | [V] §4.1.1:704-706, §4.2.2:1445 |
| Interazione FP-5/BI dichiarata solo "di riga" | Dichiarata interazione di logica (con BI acceso R-INT resta per cruise/balistici e antinave) | [V] §2.6:416-420, §5.2:1606-1609 |
| Branch dedicato non richiesto | §4.0 punto 1 lo richiede | [V] §4.0:641-643 |
| Test R-INT integrato mancante (Alta) | Nuovo test 21 | [V] §4.1.5:1208-1221 |
| Ripiego `next(..., longest)` senza test diretto (Media) | Nuovo test 23 | [V] §4.1.5:1257-1262 |
| Verifica S34/S35 a regola accesa (Media) | Facoltativa in §4.3 punto 1 | [V] §4.3:1513-1517 |

Nessuno dei rilievi vecchi resta scoperto nel testo; due dettagli numerici ereditati dal vecchio
contesto sono ancora da ricontrollare sui file (vedi sezione 4).

## 3. Fedelta' alle decisioni FP-1..FP-10 (punto A) — verifica del testo

- **FP-1 B-R** [V]: §2.2:338, §3.581, applicato in §4.1.1 punto 7 (`_own_intervals` su tratti,
  None senza tratti con estrazione unica).
- **FP-2 O3** [V]: §2.3:346, applicato: `pass_rng` stream separato, primo passaggio nella
  posizione di oggi (`_detect_passes` indice 0 usa `self._draw()`, §4.1.1:949), ordine
  (finestra canonica, a->b poi b->a, passaggio) §2.12:560.
- **FP-3 (a)** [V]: §2.5:360-374, applicato: `candidate_end = hi` per l'osservatore con portata
  minore (§4.1.1:834-835), `_Candidate(t_end=hi)` in `_detect_passes` (:971), salve gia' lanciate
  non cambiate (:373-374). Da verificare in codice le righe citate `:2502/:2955/:3035/:3084`.
- **FP-4 (a)** [V]: §2.4:352, `_pass_cpa` sui tratti ritagliati al passaggio unito (:906-916).
- **FP-5 (d)** [V]: §2.6:401, `_detection_time_in_pass` + `_detection_time_of(..., at)` +
  `_in_time` passa `salvo.t_launch` (:1049-1053). Ripiego senza tratti = ultimo in lista
  (§3.1:618-620).
- **FP-6 (a)** [V]: §2.7:430, `_exposure_time` punto 8 (passaggio che contiene `t_cpa`, in
  subordine il piu' lungo, mai la somma), incondizionato dentro `D5_DWELL_TIME` (nessun nuovo
  interruttore); con FP acceso permanenza del proprio passaggio (:946).
- **FP-7 (a)** [V]: §2.8:447, `FP_PER_PASS_DETECTION = False` letto da `Session_Simulator.engage`,
  attivo se e solo se `pass_rng` non e' None; TEMPORANEO con criterio di rimozione a 4 passi
  (:451-455) ripetuto nel commento del codice (:722-724) e in §4.3:1520.
- **FP-8 modificata** [V]: §2.9:463, 4 varianti x 5 semi = 20; `off`/`cas_off` stato precedente,
  `on`/`cas_on` FP + D-5 accese con `ZSU_DWELL_S = 2.0` dichiarata STIMA [S] nel codice
  (§4.2.1:1323-1327) e nel vincolo §4.2.3:1474.
- **FP-9 (a)** [V]: §2.10:502, nessun cambio al pianificatore; limite dichiarato in §5.2:1624-1629.
- **FP-10 (c)** [V]: §2.11:521 con le tre sotto-decisioni (:524-532), confine `<= dwell + TIME_EPS`
  (:534-536), unione a valle di `_own_intervals` (:538-543), ordine unione-prima-del-filtro
  (§3.1:614-617), estremi veri per FP-5 (§3.1:619-620).

## 4. Verifica del codice citato (punto B) [V, checkout `8c440dba`]

Righe citate dal piano contro il codice reale (il piano dichiara righe del checkout `97620f55`;
il checkout attuale `8c440dba` contiene solo la Proposta BI in piu', nessun cambio di codice):
tutte le ancore verificate coincidono.

`Logic/Engagement_Resolver.py`:
- import da `Contact_Scheduler` :467-474 (contiene `range_intervals`, `TIME_EPS`,
  `GROUNDED_DETECTION_MODE`, `detection_mode_for`) [V]; `clamp_legs` (:469) e
  `closest_point_of_approach` (:804) esistono in `Contact_Scheduler` [V].
- interruttori: `D5_DWELL_TIME = False` :529 (blocco :524-529), `BI_AD_TARGET_RULE` :531-535,
  `AD_DOMAINS` :537-538 [V]; nessun `VA_ENGAGEMENT_ALTITUDE_BAND` ancora (VA blocco 1 non
  eseguito, coerente con l'ordine §4.0.1).
- `Detection` :674-692, docstring "una per finestra e direzione", campi fino a
  `dwell_time_s` :692 [V] — i 4 campi nuovi vanno in coda come dice il punto 3.
- `dwell_factor` :1181-1203 (`min(1.0, exposure/dwell)`) [V]; `registry_dwell_time`
  :1206-1221 (lettura pura, nessuna estrazione) [V].
- `engagement_intervals` :1731, `range_intervals(` chiamato a :1738 (dentro
  `engagement_intervals`), :2233 (`_detection_time`), :2265 (`_exposure_time`) [V]: il grep
  di verifica del punto 8-bis quadrava ieri e quadra oggi; dopo il blocco 1 restera' solo
  :1738 piu' `_own_intervals` [V sul piano].
- `_EngagementRun.__init__` :1765-1769 con `dwell_time_for=None` ultimo parametro;
  `self.dwell_time_for = dwell_time_for` :1838 [V]; esiste gia' `self.detected_at` :1828 e
  `in_time_cache` :1830 usati dal nuovo `_detection_time_of` [V].
- `_detect` :2091-2110: finestre in ordine canonico `(t_start, id_a, id_b, t_end)`, per ogni
  finestra a->b poi b->a [V] — l'ordine di `pass_rng` (O3) e' cosi' ben definito.
- `_detect_direction` :2112-2169: `exposure = dwell = None` :2127, blocco D-5 :2129-2137
  (solo letture e aritmetica, nessuna estrazione) [V]; le due righe da cambiare sono esattamente
  `if t_ready <= window.t_end + TIME_EPS:` :2161 e `t_end=window.t_end` :2163; la costruzione
  della `Detection` :2166-2169 resta [V].
- `_detection_time` :2219-2245 (ramo tratti :2233) [V]; `_exposure_time` :2247-2277, somma
  nel ramo tratti :2262-2269, docstring "somma, sugli intervalli..." da correggere come dice
  il punto 8 [V]; `_draw` :2285-2291, firma attuale `def _draw(self) -> float:` con
  `value = self.rng.random()` [V] — la firma nuova `def _draw(self, rng=None)` e' compatibile
  con tutte le chiamate esistenti `self._draw()` [V].
- `_admissible` :3196-3202, `_may_intercept` :3204-3227 (L1) [V];
  `_detection_time_of` :3229-3235 (il dizionario `{(obs, tgt): d.time}` in ordine di lista
  prende l'ultimo: e' la regola precedente che FP-5 (d) spento deve mantenere) [V];
  `_round_track_time` :3254-3290 [V]; `_in_time` :3292-3316, `seen = self._detection_time_of(shadow.id,
  salvo.shooter_id)` :3307, soglia `seen <= salvo.t_launch + TIME_EPS` :3309 [V] — la
  modifica "cambia una riga" del punto 10 e' corretta: la semantica "visto" resta decisa da
  `_in_time`, come dichiara la docstring di `_detection_time_in_pass`.
- usi di `candidate.t_end`: :2502, :2955, :3035, :3084 [V] — le salve gia' lanciate non
  cambiano; `candidate_end` limita solo il `_Candidate` nuovo, come dice §2.5.
- `resolve_engagement` :3809-3828 (`dwell_time_for` ultimo), validazione :3943-3944 (forma
  uguale a `breakpoint_rng` :3936-3937, dove il punto 11 la copia), chiamata `_EngagementRun`
  :3965-3972, voce docstring :3906-3908 [V].
- docstring del modulo: catena punto 4 (R-INT) :49-55, sezione D-5 "Permanenza" :143-167 con
  la frase da correggere a :157-158, "## Scorta per arma" :169, contratto RNG :416-421 con
  "(invariato dalla D-5)" a :419 [V] — tutte le ancore del punto 12 esistono.

`Logic/Session_Simulator.py`:
- `TEMPER_EVENT_TAG` :798, `temper_event_id` :1022-1032 (chiamata a `engagement_event_id`
  per la validazione e `json.dumps` col proprio tag) [V] — `pass_event_id` proposta e' la
  copia esatta di questo schema; il test 17 (`ValueError` con un solo id) e' coerente con
  `engagement_event_id` :1009-1010 [V].
- `engage` :2707, `counter` = ordinale G4a dell'episodio :2711, `extra = {}` :2715, blocco
  D-5 :2770-2772 (`if ER.D5_DWELL_TIME: extra['dwell_time_for'] = ER.registry_dwell_time`),
  chiamata con `**extra` :2790 [V] — lo snippet del punto 3 si innesta esattamente li' e usa
  la stessa forma di `order.rng(mission_id=None, event_id=..., counter=counter)` di :2775/:2783 [V].
- `all_legs` :2397-2409 [V] (citato in §2.2); docstring D-5 :730-733 [V].
- `D5_DWELL_TIME` letto in questo modulo solo a :2770 [V, grep]; manca da verificare
  `Air_Route_Manager.py:1132` (v. sotto).

`Logic/Contact_Scheduler.py`:
- `range_intervals` :874-935 [V]: **intervalli degeneri s1 == s2 esistono** — il ramo a un
  solo breakpoint produce `(t, t)` :907 e la tangente `s2 == s1` NON e' scartata (`if s2 < s1:
  continue` :930-931) [V]; la dichiarazione del piano sui "passaggi di durata nulla" (§5.2)
  e' corretta e la tolleranza di P-1 (`ZERO_PASSES`) e' pertinente.
- `_merge_intervals` :938-952, confine `start <= merged[-1][1] + TIME_EPS` :947 [V] — il
  confine di FP-10 (`<= dwell + TIME_EPS`, §2.11) usa la stessa tolleranza, come dichiara.

`Test/Scenario_Fixtures.py`:
- `declare_dwell` :306-338 [V]: sostituisce `detection_dwell_time` solo sull'istanza (il
  probe del test S33 13 la legge sull'istanza della ZSU della variante) e valida modo/valore
  (`'air'` e' un modo valido) [V]; e' una lettura pura, coerente con "la D-5 non fa
  estrazioni" (§2.9).

`Test/Test_Session_Scenarios_S32.py` (schema su cui poggia S33) [V]:
- docstring :1-28, `ER_MODULE` :43, `ZSU = 'Red-Line/ad0'` :56, `ZSU_POSITION` :58,
  `build` :67-80 (ZSU in (1000, -300), 3 BMP-2, 4 A-10C a 3000 m con
  `loadout='Maverick/Gun CAS'`), `run_variant` :83-110 con `patch.object` :95 attorno alla
  costruzione delle forze :96 e `F.run` :107 con `[red]` terzo argomento posizionale,
  `mission_type='CAS'` :103 [V]. S33 importa da qui `build`, `ZSU`, `ZSU_POSITION`,
  `ER_MODULE` (tutti esistenti) [V]; `IFV_IDS`, `VISUAL`, `MAVERICK`, `OVERFLIGHT`, `DURATION`
  arrivano da `Test_Session_Scenarios_S19_Air_Defence` (importati in S32 :38-40) [V].
- La spia di S32 (:90-93) cattura il risultato DOPO la chiamata; la spia di S33 (deepcopy di
  `pass_rng` PRIMA della chiamata) e' un'estensione dichiarata del piano, coerente con lo
  schema.

`Asset/Vehicle_Data.py`: 10 voci `dwell_time_s` fra :4688 e :5058 [V, grep: 4688, 4737,
4764, 4788, 4814, 4841, 4866, 4952, 4980, 5058]; un radar a antenna fissa :4925 senza dwell
— "solo i 10 EWR dichiarano il dwell" [V].

Le funzioni nuove (`_join_passes`, `_detection_time_in_pass`, `_dwell_of`, `_own_intervals`,
`_own_passes`, `_pass_cpa`, `_pass_detection_time`, `_detect_passes`) NON esistono nel
checkout [V, grep] come atteso; le firme proposte sono coerenti con i chiamanti reali
(dettagli nella sezione 6).

## 5. Completamento delle verifiche di codice (resto del punto B) [V]

Riferimenti citati dal piano rimasti da verificare, tutti letti sul checkout `8c440dba`:

- `Logic/Air_Route_Manager.py`: `D5_DWELL_TIME` letto a :1132 (`dwell_enabled`, dentro
  `compute_detection_metrics` :1098, usato da `calcRoute` :1520; la sessione non lo chiama) [V];
  `CROSSING_JOIN_TOLERANCE_S = 1e-6` :38 (citate in §1.3:178 e §5.2:1622) [V].
- `Asset/Mobile.py`: `INTERCEPTOR_TASK = 'Anti_Missile'` :203-208 [V] — la ZSU non e'
  intercettore e S33 non prova FP-5 in sessione, come dice §2.6:392-394.
- `Logic/Fire_Control.py`: `interceptable` :836-842 (missili e bombe guidate True, resto
  False) [V].
- `Test/Test_Engagement_Resolver.py`: helper `_ScriptedRng` :77-87 (valori prefissati e
  `calls`), `_window` :90-96, `_profiles` :105, `_kill` :113, `_always` :123 [V];
  schema `_EngagementRun` diretto :2406/:2435/:2522/:2623/:2688 [V]; `_TrackingInterceptor`
  :1730-1738 (per il test 21) e `TestInterceptionReaction._run` :1751-1771 (schema citato
  dal test 21; `_ScriptedRng([0.0] * 20)`, profili `{'b1': (2.0, 1.0)}` con default) [V];
  `TestDwellTimeInTheResolver` :3736-3755: `setUp` mocka il logger :3739-3742 e `_run`
  chiama `ER.resolve_engagement(..., dwell_time_for=reader, **kwargs)` [V] — la classe
  esiste ed e' la sede dei test 14 e 23; il confronto `dataclasses.replace(..., exposure_s=None,
  dwell_time_s=None)` :3779 resta valido con i campi nuovi a None [V]; i suoi test esistenti
  usano finestre senza tratti o a un intervallo: nessuno asserisce la somma (§4.1.3:1126) [V].
- `Test/Test_Session_Simulator.py`: `TestDwellTimeSwitch(_Base)` :235 (modello del test
  15-16) [V].
- `Test/Scenario_Baseline.py`: `_by_occurrence` :227, CLI `--compare/--against/--save/
  --only/--quiet/--ignore` :904-916, uscita "IDENTICAL"/"difference lines" :948 (per §4.1.6
  e i comandi di §4.5) [V]; la coda di `UNITS` termina con S32-DWELL :397 (S35/S34 arriveranno
  con BI/VA, coerente con §4.0.1) [V].
- Registro: ZSU-57-2 solo visivo, `acquisition_range` 6 km contro bersagli aerei
  (`Vehicle_Data.py:3729-3736`) e niente contro terra [V]; A-10C TVD `ground`
  `acquisition_range` 80 km (`Aircraft_Data.py:1786`) [V]; il cannone S-68-57mm della ZSU
  dichiara i task `Anti_Air` e `Infantry_Support`, non `Anti_Missile`
  (`Ground_Weapon_Data.py:2266`) [V] — le premesse di S33 (§4.2.1:1321-1322, §2.9) sono vere.
- S32 importa `DURATION, IFV_IDS, MAVERICK, OVERFLIGHT, VISUAL` da
  `Test_Session_Scenarios_S19_Air_Defence` (:38-40) [V]: tutto cio' che serve a S33 esiste
  (v. rilievo MINORE 3 sugli import non nominati).

## 6. Determinismo (punto C) [V]

- **Nessuna estrazione nuova a interruttore spento**: `engage` non passa `pass_rng` (guard
  `if ER.FP_PER_PASS_DETECTION`, §4.1.2 punto 3); nel risolutore `self.pass_rng is None` salta
  l'intero ramo FP (§4.1.1:811); `_dwell_of` ripete le stesse due istruzioni del blocco D-5
  attuale (modo + `_check_dwell`, codice :2132-2133) senza estrarre; `candidate_end` si
  riduce allo stesso oggetto `window.t_end` (:808, :844); `_detection_time_of` a spento
  costruisce `detected_at` con lo stesso dizionario e lo stesso ordine del codice attuale
  (:1030-1037 contro :3231-3235). L'unica modifica attiva a spento e' FP-6, dentro
  `D5_DWELL_TIME` e dichiarata come tale: il commento dell'interruttore (:719-721) NON
  promette "spento = tutto come prima" senza l'eccezione, coerente con §2.7:437-441 [V].
- **Stream dell'ingaggio identico in ogni stato**: `_detect_passes` estrae il passaggio di
  indice 0 da `self._draw()` (posizione dell'estrazione unica di oggi) e gli indici 1..n da
  `pass_rng` (:949); con 0 o 1 passaggio l'estrazione resta una sola dallo stream dell'ingaggio;
  con i passaggi uniti (FP-10) la direzione ha comunque una sola estrazione dallo stream
  dell'ingaggio, quindi nemmeno l'unione sposta `rng` (§4.1.4:1133-1135). I test 4 (blocco 1)
  e 3/9 (S33) lo asseriscono direttamente.
- **Ordine di `pass_rng` ben definito** (O3): finestre in ordine canonico `(t_start, id_a,
  id_b, t_end)` (:2092-2093), per ognuna a->b poi b->a (:2109-2110), dentro la direzione
  passaggio per passaggio in ordine di tempo (`range_intervals` restituisce intervalli
  ordinati da `_merge_intervals`, `Contact_Scheduler.py:943-952`; `_join_passes` preserva
  l'ordine) [V]. Il contratto RNG del docstring viene aggiornato di conseguenza (punto 12
  (i), :416-421) [V].
- **Nessuna estrazione nelle funzioni nuove**: `_dwell_of` (letture), `_join_passes`
  (aritmetica), `_own_intervals`/`_own_passes` (`range_intervals`, deterministico),
  `_pass_cpa`/`_pass_detection_time` (geometria), `_detection_time_in_pass`/
  `_detection_time_of` (dizionari): nessuna chiama `_draw` [V piano]; la sonda P-1 avvolge
  `_own_passes` e `_in_time` misurando dopo l'originale, senza consumare RNG (probe:68-112) [V].
- **D-5 con g = 1 senza estrazioni**: il blocco D-5 del risolutore fa solo letture di
  registro e aritmetica PRIMA di `_draw` (:2129-2137) [V]; `dwell_factor` = `min(1.0,
  permanenza/dwell)` (:1203) restituisce esattamente `1.0` per permanenza >= dwell e
  `factor * 1.0 == factor` al bit: con g = 1 la D-5 non cambia Pd, raggio estratto, istanti
  ne' candidati (premessa del test S33 12 e di §2.9:474-484) [V]. Nessuna estrazione in
  nessuno stato della D-5.

## 7. Conteggi e attese calcolabili (punto D)

- **Blocco 1 = 30** [V §4.1.5:1272-1273]: `TestDetectionPerPass` 25 (1-13, 18-22, 24-30),
  `TestDwellTimeInTheResolver` 2 (14, 23), `TestPerPassDetectionSwitch` 3 (15-17); l'elenco
  numerato non ha buchi (14-17 assegnati alle altre classi) e i conteggi per classe tornano.
- **S33 = 13** [V §4.2.1]: test 1-5 (rientro), 6-11 (CAS), 12-13 (D-5 e scope); "da 11 a 13"
  (§0:35-36) coerente.
- **§4.0.1** [V]: base reale `Ran 4829` (`suite.log:17409-17411`) e `compared 1029 runs:
  20 difference lines` (`confronto.log:1186-1187`) letti dai log; FP blocco 1 = B_FP + 30
  (:676, §4.1.6:1277), blocco 2 = B_FP + 43 (:677, §4.2.4:1486); finale 1113 = 1029 + 32 (S35)
  + 32 (S34) + 20 (S33) e 104 = 20 + 32 + 32 + 20 (:679-680), identico in §0:129-133 e
  §4.2.4:1487-1488. Coerenza interna completa; i valori non ancora misurabili sono marcati
  [S]/[I] come richiede AGENTS.md.
- **§4.0.2 contro BI §6.1** [V]: la colonna FP (20 esecuzioni, 13 test, B_FP + 43, 1113/104)
  coincide con la tabella di coordinamento attuale di BI (`...Difesa_Aerea.md:1138` e `:1161`).
  **Rilievo**: §4.0.2:686-689 afferma che BI §6.1 riporta ancora "S33-PASSES (40)" e che la
  riga "va corretta da chi aggiorna quella Proposta": il commit `8c440dba` (contenuto nel
  checkout) l'ha gia' corretta — affermazione resa stantia (v. ESITO, IMPORTANTE 1).
- **Esempio FP-5 (d) calcolabile senza indovinare** [V tabella §2.6:406-411]: passaggi
  [200, 254] e [380, 434], rilevamenti 210 e 390: lancio a 230 -> passaggio [200, 254],
  rilevamento 210 <= 230 -> **visto**; 300 -> nessun passaggio lo contiene -> **non visto**;
  385 -> passaggio [380, 434], rilevamento 390 > 385 -> **non visto**; 400 -> 390 <= 400 ->
  **visto**. La funzione proposta `_detection_time_in_pass` (:769-786) implementa esattamente
  questa semantica: primo passaggio (in ordine di tempo) che contiene `at` entro TIME_EPS,
  `min` dei rilevamenti dentro il passaggio (robusto a `times` disordinati), None altrimenti;
  la decisione "visto" resta in `_in_time` (:3309 nel codice attuale), che il punto 10 modifica
  solo nell'argomento `at`. Il test 13 copre tutti e quattro i casi piu' `times` invertito e
  `passes = []` (:1187-1190). Coerente con FP-3 (a) (traccia persa all'uscita) e, con BI
  acceso, il perimetro dichiarato (cruise/balistici e antinave, §2.6:416-420) e' corretto
  perche' il filtro `_admissible` precede L1 e R-INT (:3196-3202) [V].
- **Altre attese calcolabili verificate a mano** [V/calcolo]: Pd del secondo passaggio della
  geometria comune 0,9352 = 1 - 0,5 * (3000/5000)^4; test 9: 0,8 = 100/125 e 0,64 * 0,9352
  (80/125 x Pd del passaggio); test 14/23: 0,25 = 100/400; test 24: permanenza 320 s con
  dwell 140 -> g = 1 -> probability 1,0; test 28: 0,99 >= 0,9352 * 80/139 ~ 0,538 -> salvo
  mancato; test 21: passaggi [0, 1,5] (1000 m/s su 1500 m) e [0, 3,0] (500 m/s), salva a
  2,0, impatto a 5,0, tau 1 visto / 5 non visto -> 3/0/3 come atteso (:1219-1221).
- **S33, estrazioni attese** [V :1434]: 4 della ZSU per seme in `off`/`cas_off` (4 A-10C x 1),
  8 in `on`/`cas_on` (x 2 passaggi): coerente con i test 1/2/7/8 e con la nota delle 4
  missioni (:1372-1376).
- **Sonda P-1** [V, letta senza eseguirla]: docstring e logica di `probe_switch_on.py` e
  `LEGGIMI.md` corrispondono al piano: richiede esattamente i simboli del blocco 1
  (`FP_PER_PASS_DETECTION`, `_own_passes`, `_in_time`, `_detection_time_of`, probe:44-50) e
  si rifiuta altrimenti; misura `rint_seen_changed` ricalcolando la regola precedente
  (ultimo rilevamento in ordine di lista) contro FP-5 (d) senza estrazioni (probe:90-112);
  l'attesa "al piu' le 44 AFTER_PASS (FP-3 (a)) piu' le eventuali RINT_D (FP-5 (d))" e'
  dichiarata **NON misurata** [I] ovunque (probe:8-11, LEGGIMI:49-55, §0:119-127, §4.3:1499-1512),
  coerente con la conferma dell'utente; `MULTI`/`RINT` di P-0 vuote e D-5 spenta nella
  fotografia: FP-6 e FP-10 non agiscono (LEGGIMI:53-55). **L'accensione globale di P-1 non
  cambia S33**: `run_variant` fissa da se' i due interruttori con `patch.object` attorno
  all'intera esecuzione (§4.2.1:1349), come conferma LEGGIMI:69-72 [V]. I comandi di
  LEGGIMI sono compatibili con l'interfaccia reale di `Scenario_Baseline` (:904-916, :948) [V].

## 8. Completezza per l'esecutore (punto E)

- **Criterio di rimozione di FP-7 completo** e scritto in tre posti coerenti: commento
  dell'interruttore (:722-724), §2.8:451-455, §4.3 punto 3:1520-1526 — (1) sonda P-1 eseguita,
  (2) lettura delle esecuzioni cambiate da parte dell'utente, (3) fotografia nuova installata
  **dall'utente**, (4) blocco di pulizia dedicato che elimina interruttore e rami spenti
  (con l'elenco di cosa riscrivere: test 1/2/15, meta' "senza pass_rng", varianti off di S33);
  default spento fino ad allora [V].
- **Limiti dichiarati** [V §5.2]: senza tratti (un'estrazione, candidato fino alla fine della
  finestra, R-INT ultimo in lista: 1600-1601); FP-9 (metrica del peggiore degli attraversamenti,
  nota dell'utente non verificata riportata come tale, 1624-1629); finestre e pianificatore con
  la tolleranza numerica nonostante FP-10 (1620-1623); passaggi tangenti/di durata nulla
  (1610-1612); FP-5 non esercitato in sessione, coperto dai test 13/21/22/29 e da P-1
  (1579-1582).
- **Istruzioni di fermata** precise dove l'esecutore potrebbe essere tentato di "aggiustare":
  premesse S33 1/7 fallite -> fermarsi e riferire pass_count/istanti/finestre (:1435-1436);
  g < 1 nel test 12 -> fermarsi e riferire seme/A-10C/exposure/pass_start/pass_end/finestra,
  senza toccare `ZSU_DWELL_S` ne' la rotta (:1437-1441); confronto non IDENTICAL a spento ->
  fermarsi e riferire le righe (§4.1.6:1287) [V].
- **Scelte minori dichiarate** a §4.6: nomi, posizioni dei metodi, struttura di S33, sessione
  minima dei test 15-16, raccolta delle salve nei test 4/11, forma interna di `_first_zsu` e
  del test 6, forma di `probe` nel test 13 [V].
- **Due punti dove l'esecutore deve scegliere** (nessuna decisione di modello; v. ESITO
  MINORE 2 e 3): la via del `TypeError` del test 12 e gli import di S33 non nominati
  (`DURATION`, `IFV_IDS`).

## 9. ESITO (punto F)

**BLOCCANTI: nessuno.**

**IMPORTANTE**

1. `Proposta...Portata_Propria.md` §4.0.2 (righe 686-689): affermazione resa stantia dal
   commit `8c440dba`. Il piano dice che la riga "scenari" di BI §6.1 riporta ancora
   "S33-PASSES (40)" (valore della prima stesura di FP-8) e che "la riga di BI va corretta da
   chi aggiorna quella Proposta"; ma BI §6.1 e' stata gia' allineata (BI:1138 dice "4 varianti
   x 5 semi = 20 esecuzioni, 13 test"; BI:1161 dice "B_FP + 43" e "compared 1113 runs: 104
   difference lines") [V]. Scenario: un esecutore diligente che verifichi il coordinamento
   trova il testo BI gia' corretto e la frase del piano falsa; la sessione principale
   potrebbe "ricorreggere" una tabella gia' giusta. Correzione suggerita, dal pianificatore,
   nel passaggio separato che aggiorna gli altri punti stanti di BI/VA (i "FP-5 sospesa" e
   il conto B + 27 gia' segnalati come GIA' NOTO): riscrivere la frase come "gia' allineata
   dal commit 8c440dba" o toglierla. Non blocca l'esecuzione: per l'esecutore vale la colonna
   FP di §4.0.2, identica a BI.

**MINORE**

2. Test 12 del blocco 1 (§4.1.5, riga 1186): la via del `TypeError` non e' esplicita. La
   validazione di `pass_rng` e' pianificata solo in `resolve_engagement` (punto 11, righe
   1054-1056), mentre la geometria comune dei test dice di costruire `ER._EngagementRun`
   direttamente dove si chiamano metodi privati; il test 12 non chiama metodi privati, quindi
   la strada coerente col piano e' `ER.resolve_engagement(..., pass_rng=object())`, schema
   gia' usato da `TestDwellTimeInTheResolver._run` (`Test_Engagement_Resolver.py:3750-3755`,
   che inoltra `**kwargs`) [V]. Correzione suggerita: una riga in §4.1.5, oppure dichiararla
   in §4.6. Da: chi pianifica; l'esecutore puo' comunque risolverla senza decisioni di design.

3. Import di S33 (§4.2.1, righe 1333-1341): la lista nomina `build`, `ZSU`, `ZSU_POSITION`,
   `ER_MODULE` (da S32) e `VISUAL`, `MAVERICK` (da S19) ma non `DURATION` (usato a riga
   1355) ne' `IFV_IDS` (usato a riga 1343), entrambi importati da S19 nello schema S32
   (`Test_Session_Scenarios_S32.py:38-40) [V]. Correzione suggerita: nominarli. Da: chi
   pianifica; l'esecutore li aggiunge da se' senza ambiguita' (§4.6).

**Verdetto: pronto per l'esecutore.** I tre rilievi non toccano istruzioni operative dei
blocchi: il primo e' una frase di coordinamento da correggere nel passaggio separato gia'
previsto per BI/VA; gli altri due sono chiarimenti minimi che l'esecutore puo' risolvere
entro §4.6. Sul resto il piano e' eseguibile senza decisioni di design nuove: le decisioni
FP-1..FP-10 sono realizzate fedelmente (sezione 3), tutte le ancore di codice verificate
coincidono sul checkout `8c440dba` (sezione 4-5), le firme delle funzioni nuove sono coerenti
con i chiamanti, i 30 + 13 test hanno attese calcolabili (sezione 7), il determinismo e'
salvo in ogni stato dell'interruttore (sezione 6), il criterio di rimozione di FP-7 e'
completo e la rete di verifiche (0 cambiate, cattura IDENTICAL su 1093, fermate con rapporto)
e' costruita.

**Non ho controllato (limiti della revisione):**

- §1.9-§1.11 del piano (righe 279-323) riletti solo in parte; i riferimenti li contenuti
  (es. `_pair_windows` :1492-1524, `Weapon_Delivery._evaluate_exposure` :433) non riverificati.
- `probe_passes.py` (P-0) non riletto riga per riga: i suoi numeri (44 AFTER_PASS, 151 salve,
  multi 0, istogramma) sono stati confrontati con `LEGGIMI.md` e `esito_p0.txt` citati dal
  piano, non ricalcolati.
- La geometria di S33 (passaggi [230, 284]/[410, 464], pause 126-130/103-104 s, 4 missioni,
  155,6 m/s) non ricalcolata da me: mi sono affidato alle marcature [V] del piano (calcolo del
  2026-11-07, dichiarato "non ripetuto il 2026-11-08"); le fermate previste ai test 1/7
  coprono l'eventuale discrepanza.
- I numeri dipendenti dai blocchi non ancora eseguiti (N_BI3 ~15, B_VA, le righe NEW
  S35/S34, `~4876` [S]) non verificabili oggi: il piano li marca [S]/[I] e rimanda all'ESITO.
- Suite, confronto e sonde non eseguiti (vietato dal mandato): gli ESITO citati come [V]
  sono quelli letti dai log esistenti in `.ai-run/` dell'8 novembre.
- La versione precedente del piano (riscrittura del 2026-11-08) e le revisioni BI/VA del
  2026-11-07 non rilette direttamente: per i rilievi precedenti ho usato solo l'estratto FP
  della revisione di coerenza.
