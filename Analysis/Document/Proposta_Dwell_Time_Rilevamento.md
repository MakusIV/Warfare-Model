# Proposta: tempo di permanenza `dwell_time_s` e Pd dipendente dalla permanenza nel DES (D-5, opzione 2)

**Stato: DEFINITIVA (decisioni DW-1..DW-9 prese dall'utente il 2026-11-06).** Bozza scritta il 2026-11-05,
completata il 2026-11-06.
- **Decisioni**: tutte prese (§3): DW-1 (a), DW-2 "regime normale se citato, altrimenti rotazione piu' veloce"
  (diversa dalla raccomandazione iniziale: **AMES-Type-80 = 15 s**), DW-3 L1, DW-4 nel risolutore, DW-5
  `D5_DWELL_TIME` spento, DW-6 blocco B si', DW-7 blocco C rimandato, DW-8 S32-DWELL 5 x 4, DW-9 (nuova) solo il
  meccanismo: valori ai soli 10 EWR.
- **Sonde**: **S-1, S-2 e S-3 complete** (§1.9). S-3 conferma la geometria di S32-DWELL: nessun ritocco ai test di
  §4.A.7.
- **Da eseguire**: blocchi A e B (§4). Il blocco C e' descritto ma **non** si esegue (DW-7).

Nessun file di codice o di test modificato da questo documento. Le sonde di §1.9 sono script di sola lettura:
accendono la legge **in memoria** e rieseguono il confronto con la fotografia, senza installare nulla e senza
toccare il repository; copia versionata degli script e dell'esito di S-1 in
`Analysis/Document/Rapporti/Sonde_Dwell_D5/`, log di S-2 e S-3 in `.ai-run/sonde_dwell/` (fuori dal versionamento).
**Origine**: `Proposta_Volumi_Rilevamento_Intercettazione.md` §3.3 e §9 D-5 ("Non rilevato" a corda limitata).
L'utente ha scelto **esplicitamente l'opzione 2**: `dwell_time_s` per sensore e una Pd del DES che dipende dalla
permanenza nel volume, perche' l'aggiramento puro allungherebbe troppo le rotte e annullare missioni per
l'impossibilita' di evitare il rilevamento sarebbe eccessivo in un contesto Guerra Fredda. Il "se" non si riapre:
questo documento discute il "come".
**Fonte dei dati**: `Ricerca_EWR_2026_10_29.md` §3 (righe "Antenna/mobilita'", giri al minuto), riletta per i 15 EWR
dei registri.
**Esecutore**: `des-developer` (Claude Sonnet, sforzo alto). Alternativa: `oc-developer`. L'esecutore segue il
piano di §4 cosi' com'e': nessuna decisione di design resta aperta; se il codice reale non corrisponde (righe,
firme, esiti), si ferma e riferisce.
**Convenzioni**: **[V]** = verificato leggendo il codice (`file:riga`) o eseguendolo; **[I]** = ipotesi o
conoscenza generale, non verificata nel repository; **[S]** = stima o scelta di progetto, mai dato tarato;
**F/D/S** = Fonte / Dedotto / Stima, come nella ricerca. Percorsi di codice relativi a
`Code/Dynamic_War_Manager/Source/`. Sonde numerate **S-1, S-2, ...**; decisioni numerate **DW-1, DW-2, ...**.

---

## 0. Sintesi

**Risultato principale, da leggere prima delle decisioni.** Con i dati di fonte (periodo di rotazione degli EWR,
6-60 s) la legge "Pd ridotta se la permanenza e' piu' breve del periodo di scansione" ha un effetto **quasi nullo
sulle rotte**: la corda che un aereo puo' percorrere dentro un volume EWR con Pd ridotta e' al piu' `v * dwell`,
cioe' 1,5-3,75 km a 250 m/s contro raggi di 120-440 km, e la penetrazione corrispondente nel volume e' di pochi metri
(§1.8). La legge e' fisicamente corretta e utile (contatti radenti, esposizioni brevi, sensori lenti come lo
SCR-270 o la scoperta a vista, futuri radar SAM), ma **da sola non accorcia le rotte contro una copertura EWR in
quota**: per quello servono l'orizzonte radar nel DES (oggi assente, §1.6) o l'accettazione del rilevamento come
costo. Per questo DW-7 ha rimandato il blocco C e l'orizzonte radar nel DES resta un'attivita' separata.

| Tema | Decisione presa (2026-11-06) | Effetto sulla fotografia |
|---|---|---|
| Che cos'e' `dwell_time_s` (DW-1) | (a) **periodo di rivisita** del sensore = 60 / giri al minuto; nessun fattore di conferma (la conferma e' gia' nella RIV) | — |
| Valori (DW-2) | 10 EWR con giri/min di fonte; regola "**regime normale se citato, altrimenti rotazione piu' veloce**" (AMES-Type-80 = 15 s, [S]); 5 EWR senza dato -> nessuna permanenza | — |
| Legge (DW-3) | L1: `Pd = g * Pd(d_cpa)`, `g = min(1, permanenza / dwell)`: SOLO riduzione, si riduce alla legge attuale per permanenza >= dwell o dwell assente; legge unica per ogni sensore | — |
| Permanenza e RNG (DW-4) | calcolata nel risolutore dai tratti (`range_intervals` con la portata propria), **non tagliata** all'inizio della finestra; stessa unica estrazione per coppia e direzione, stesso ordine | — |
| Interruttore (DW-5) | `Engagement_Resolver.D5_DWELL_TIME = False` (spento di default); l'accensione si decide dopo la verifica | spento: **1009 identiche** |
| Pianificatore (DW-6) | blocco B: `DetectionThreat.dwell_time_s` e metriche di `Path` con la stessa legge; `AVOID_DETECTION` invariato (aggiramento puro) | nessuna (il pianificatore non e' nella fotografia) |
| Attraversamento a corda limitata nel pianificatore (DW-7) | **rimandato** (blocco C descritto, non eseguito): con i dati di fonte non accorcia nessuna rotta | — |
| Scenario (DW-8) | S32-DWELL: 5 varianti x 4 semi = **20 esecuzioni nuove** (geometria confermata dalla sonda S-3) | +20 |
| Estensione ad altri sensori (DW-9) | **solo il meccanismo ora**: la legge vale per ogni osservatore, ma i valori si danno ai soli 10 EWR; SAM, AAA, radar d'aereo, navi, TVD e vista senza valore finche' manca una fonte | — |
| Con l'interruttore ACCESO e i soli dati di fonte (sonda S-1) | — | **1009 identiche** (nessuno scenario usa un sensore con dwell di fonte) |
| Sensibilita': dwell fittizio di 10 s a OGNI osservatore (sonda S-2) | — | 1007 identiche, **2 cambiate** (S21-5 e S21-7 `control`) |

**Dimensione stimata**: blocco A ~170 righe di codice + ~330 righe di test (31 test); blocco B ~60 righe + ~110 di
test (7 test). Blocco C (rimandato, DW-7) ~120 righe + ~150 di test. Suite attesa: `Ran 4788` dopo A, `Ran 4795`
dopo B (base 4757). La scelta DW-2 (Type-80 15 s invece di 10 s) cambia un valore, non il numero dei test.

---

## 1. Problema e comportamento attuale

### 1.1 La catena del rilevamento nel DES [V]

1. **Finestre di contatto** (`Logic/Contact_Scheduler.py`). `contact_windows` (`:1023-1100`) calcola gli
   intervalli in cui la distanza 3D fra due asset e' entro la portata **maggiore** delle due (`outer`, `:1067`,
   `:1070`); per ognuno registra `t_start/t_end`, il massimo avvicinamento `t_cpa/distance_cpa`, le due portate
   `range_a/range_b` e il **primo** intervallo dentro la portata minore (`t_mutual_start/t_mutual_end`,
   `_first_contained`, `:1117-1126`). Le portate vengono da `mutual_detection_ranges` (`:972-1020`), che chiede a
   ogni osservatore `detection_range(modo del bersaglio)`. Le finestre sono spezzate agli istanti di decollo e
   atterraggio (`_pair_windows`, `:1492-1524`) e, dal G4a, ritagliate quando una forza e' occupata in un
   episodio (`trim_contact_window`, `:1129-1172`): **una finestra puo' cominciare dopo l'ingresso reale nella
   portata**. Il `ContactWindow` (`:196-240`) **non porta il sensore** che ha prodotto la portata.
2. **Portata** (`Asset/Mobile.py`). `detection_range(mode, sensor=None, range_type)` (`:1570-1652`) restituisce il
   **massimo** fra `radar`, `TVD` e `visual` (`DETECTION_SENSORS`, `:83`; il visivo e' escluso con
   `D4C_VISUAL_SENSOR` spento, `:86-92`, `:1638-1640`). `_sensor_range_km` (`:1532-1568`) legge
   `record.<sensore>['capabilities'][mode][1][range_type]`.
3. **Pd e istante** (`Logic/Engagement_Resolver.py`). `_detect` (`:1965-1984`) ordina le finestre per
   `(t_start, id_a, id_b, t_end)` e chiama `_detect_direction` prima a->b poi b->a. `_detect_direction`
   (`:1986-2031`):
   - esce **prima dell'estrazione** se l'osservatore non ha portata (`:1988-1989`) o e' un aereo a terra
     (`:1991-1994`);
   - calcola il fattore iniettato `detection_factor(observer, target)` (`:1996-1999`, meteo, notte, nebbia);
   - estrae **un** numero (`self._draw()`, `:2001`, `:2115-2121`);
   - `probability = detection_probability(d_cpa, own_range, factor)` (`:2003`), rilevato se `draw < probability`;
   - l'istante e' quello in cui la distanza scende sotto `detection_radius(draw, own_range, factor)` (`:2008-2009`,
     inversa della legge, `:1071-1100`), calcolato esattamente sui tratti (`_detection_time`, `:2081-2107`); senza
     tratti: `t_start` se la propria portata e' la maggiore, altrimenti `t_mutual_start`, ultimo ripiego `t_cpa`;
   - se rilevato: percezione del dominio (`_perceive`, `:2033-2037`), identificazione, RWR (`:2017-2019`) e
     candidato al tiro se `t_ready = time + profilo.total <= t_end` (`:2021-2026`);
   - registra un `Detection` (`:614-628`, `:2028-2031`), che **non** e' nella fotografia [V: nessun riferimento in
     `Test/Scenario_Baseline.py`].
4. **Legge** `detection_probability` (`:1041-1068`): `Pd(d) = f * (1 - (1 - 0,5) * (d/R)^4)` per `d <= R`, 0 oltre;
   `PD_AT_ACQUISITION_RANGE = 0.5` (`:451-454`, STIMA dichiarata), `PD_RANGE_EXPONENT = 4` (`:456-459`). Dipende
   **solo** dalla distanza minima della finestra, non dal tempo passato nel volume (lo dice gia' la Proposta
   d'origine §3.3 e il manuale, `Manuale_Motore_DES/05_Strato2_Risolutore_Ingaggio.md` §4.2).
5. **Fattori** notte/meteo (`NIGHT_DETECTION_FACTOR = 0.7`, `ADVERSE_WEATHER_DETECTION_FACTOR = 0.8`,
   `:461-473`) e nebbia (`:475-488`): moltiplicativi, unici per tutti i sensori.

### 1.2 Ordine e numero delle estrazioni [V]

Il contratto e' scritto nel modulo (`Logic/Engagement_Resolver.py:385-390`): **prima tutte le estrazioni di
rilevamento**, nell'ordine canonico delle finestre e per ognuna a->b poi b->a, **una per direzione** (salvo le
uscite anticipate di `:1988-1994`, che non estraggono); poi un'estrazione per colpo non intercettato. La tempra
usa uno stream separato (`breakpoint_rng`, `:3356-3391`). Lo stream e' `Session_Rng.session_rng(...)`
(`Utility/Session_Rng.py:105-113`), passato da `Session_Simulator` (`Logic/Session_Simulator.py:2765-2780`).

Conseguenza per il disegno: **qualunque legge che cambi solo la soglia dell'estrazione** (come gia' fa
`detection_factor`) lascia invariati numero e ordine delle estrazioni, e con la stessa estrazione `u` la decisione
nuova e' monotona rispetto a quella vecchia se la nuova Pd e' <= della vecchia.

### 1.3 Nessun dato di permanenza nei registri [V]

- La forma del sensore e' `record.<sensore> = {'model', 'capabilities': {modo: (bool, {...})}, 'reliability', ...}`
  (`Asset/Mobile.py:61-80`). I record possono gia' portare chiavi opzionali: `antenna_height` e
  `acquisition_profile` negli EWR (`Asset/Vehicle_Data.py:4682-4683`, `:4906`, `:4956`, `:4982-4983`), lette solo
  dal pianificatore (`Logic/Air_Route_Manager.py:705-729`) o da nessuno (`acquisition_profile`).
- Nessuna chiave `dwell`, `scan`, `rpm`, `rotation`, `revisit` in `Vehicle_Data`, `Ship_Data`, `Aircraft_Data`
  [V: ricerca testuale senza risultati]. `min_detection_time` di `ThreatAA` e la RIV di `Reaction_Profile` sono
  **latenze dopo il contatto**, non permanenza (Proposta d'origine §1.4 punto 2; `Context/Reaction_Profile.py:7-36`:
  RIV = "rilevazione", residuo fino al totale documentato rilevamento -> lancio).

### 1.4 Il pianificatore replica la legge [V]

`Path.compute_detection_metrics` (`Logic/Air_Route_Manager.py:1081-1150`) calcola, per ogni **edge** e ogni
`DetectionThreat`, il tratto dentro il cilindro (`_segment_cylinder_interval`, `:813-859`), la distanza minima dal
sito (`_min_distance_to_site`, `:862-871`) e `pd = detection_probability(min_distance, acquisition_range)`
(`:1103`, `:1131-1132`), importata dal risolutore: **una sola fisica**. Ne derivano `detection_exposure_s`,
`first_detection_time_s`, `warning_time_s`, `max_detection_probability` e `detection_tracts` (`:1053-1057`).
Il tratto e' **per edge**: un attraversamento che si estende su due edge produce due tratti, ciascuno con la sua
`pd` (nel DES e' una sola finestra con una sola estrazione). `ThreatMode.AVOID_DETECTION` (`:37-57`,
`:1403-1427`) aggira i `DetectionThreat` con il motore di evitamento esistente e attraversa a corda limitata i soli
volumi d'intercettazione (`_cross_interception_while_avoiding`, `:1800-1908`); la chiave di scelta e'
`(detection_exposure_s, total_danger, total_length)` (`:1240-1248`). `DetectionThreat` (`:280-307`) porta
`sensor`, `acquisition_range`, `reference_altitude`, `source_id`; `build_detection_threat` (`:732-787`) sceglie il
sensore con il raggio **effettivo** (dopo l'orizzonte) maggiore.

Chi usa il pianificatore [V]: `Logic/Weapon_Delivery.py` (transiti con `ThreatMode.AVOID` di default, `:635`;
esposizione di rilevamento deterministica dall'ingresso nel volume, `_evaluate_exposure`, `:433-460`) e
`Block/Military.air_detection_threats` (`Block/Military.py:584-611`). **Nessun chiamante del core usa
`AVOID_DETECTION`** e nessun codice annulla oggi una missione perche' il rilevamento non e' evitabile [V: ricerca
di `AVOID_DETECTION` fuori da `Air_Route_Manager.py` e dai test].

### 1.5 Chi consuma un rilevamento nel DES: perche' un EWR oggi cambia solo la percezione [V]

Un rilevamento crea un **candidato al tiro solo per l'osservatore stesso** (`:2024-2026`); il dominio di
coordinamento condivide la **percezione** (`seen_by`, `identified_by`, `:2033-2037`, `:2011-2012`), non il tiro
(`Piano_Implementazione_Missione.md` decisione 7: "un tiratore spara solo ai bersagli che ha rilevato lui"; il
cueing EWR -> SAM e' fuori perimetro, D-7). Quindi la Pd di un EWR, che non ha armi, entra nel motore **solo**
attraverso la percezione: rapporto di forze percepito e fuoco senza risposta della soglia di rottura
(`_perceived_ratio`, `_unanswered_fraction`), e nulla con dottrina "ad oltranza". La legge di permanenza cambia gli
esiti di tiro solo se la applica il sensore **di un tiratore**.

### 1.6 Limiti gia' dichiarati che interagiscono [V]

- **Nessun orizzonte radar nel DES** (`Manuale_Motore_DES/10_Limiti_Estensioni_Divergenze.md:598-600`): un EWR vede
  un aereo radente a piena `acquisition_range`; il pianificatore invece taglia il volume con l'orizzonte
  (`Logic/Air_Route_Manager.py:671-683`, `:768-770`). E' il limite che rende il volo basso inutile nel DES.
- **Fattore notte unico** per tutti i sensori (`10_Limiti...md:605`; `Engagement_Resolver.py:461-473`).
- **Nessuna copertura angolare** (`04_Strato1_Scheduler_Contatti.md:177`): Mammut e Chain-Home omnidirezionali.
- **La finestra non porta il sensore** (`Engagement_Resolver.py:463-467`): il risolutore non sa se la portata e'
  radar, TVD o visiva.

### 1.7 Dati di fonte per la permanenza: i giri al minuto degli EWR [V sulla ricerca]

La ricerca EWR riporta il regime di rotazione dell'antenna (colonna "Antenna/mobilita'", tutti **F**, confidenza
media salvo dove indicato). Periodo di rivisita = 60 / giri al minuto (**D**, conversione).

| Record (chiave) | Giri/min nella fonte | Riga ricerca | Periodo [s] con la regola di DW-2 ("normale" se citato, altrimenti "piu' veloce") |
|---|---|---|---|
| `SCR-270` | 1 | `:203` | **60** |
| `P-12-Yenisei` | 10 (2-6 secondo [AC-P12]: contraddizione) | `:231` | **6** |
| `P-18-Terek` | 10 | `:263` | **6** |
| `P-37-Mech` | 3-6 | `:291` | **10** |
| `1L13-Nebo-SV` | 3-6 | `:309` | **10** |
| `55Zh6-Nebo` | 6 (conf. media-bassa) | `:325` | **10** |
| `AN-TPS-43` | 6 | `:363` | **10** |
| `AMES-Type-7` | 0,5-8 | `:217` | **7,5** |
| `AMES-Type-80` | 4 (fino a 6) | `:338` | **15** [S]: "4 (fino a 6)" letto come regime base 4 giri/min (= "normale") e massimo 6; la fonte non dice "normale", e' un'interpretazione |
| `P-14-Lena` | 2-6 | `:246` | **10** |
| `Chain-Home` | antenna fissa a illuminazione continua (cortina trasmittente, 150 gradi) | `:128` | **nessuna** (nessun intervallo fra le occasioni di rilevamento: legge attuale) |
| `FuMG-80-Freya` | schiera orientabile 360 gradi, velocita' non data | `:154` | nessuna (dato mancante) |
| `Wassermann` | traliccio "ruotabile", velocita' non data | `:166` | nessuna (dato mancante) |
| `Mammut` | scansione elettronica su 100 gradi, cadenza non data | `:179` | nessuna (dato mancante) |
| `AN-FPS-117` | array planare, rotazione non riportata | `:377` | nessuna (dato mancante: **non** si usa il valore che si "sa" da fuori ricerca) |

Nessun dato per radar SAM, radar d'aereo, TVD e visivo: per loro `dwell_time_s` resta assente (legge attuale;
DW-9). Nella ricerca EWR la parola "normale" accanto ai giri al minuto compare solo per l'AN/FPS-20 (`:351`,
"3,3/5/10 giri/min (normale 5)"), radar assente dai registri: con la regola di DW-2 l'unico record che usa il
ramo "regime normale" e' l'AMES-Type-80, per interpretazione della dicitura "4 (fino a 6)".

### 1.8 I numeri della corda: cosa la legge puo' e non puo' dare [calcolo, I per le velocita']

Con la legge L1 (DW-3, §2.3) la Pd di un attraversamento e' `<= permanenza / dwell`. La corda percorsa in un
tempo pari al periodo e' `L = v * dwell`; la massima profondita' di penetrazione di una corda `L` in un cerchio di
raggio `R` e' circa `L^2 / (8 R)`.

| Caso | v [m/s] | dwell [s] | L = v*dwell | R [km] | penetrazione |
|---|---|---|---|---|---|
| P-18 / P-12, caccia | 250 [I] | 6 | 1,5 km | 180-200 | ~1,5 m |
| 1L13, P-37, 55Zh6, TPS-43, P-14, caccia | 250 [I] | 10 | 2,5 km | 250-440 | 2-3 m |
| AMES Type 80, caccia | 250 [I] | 15 [S] (DW-2) | 3,75 km | 390 | ~4,5 m |
| AMES Type 7, bombardiere WWII | 100 [I] | 7,5 | 0,75 km | 140 | ~0,5 m |
| SCR-270, bombardiere WWII | 100 [I] | 60 | 6 km | 160 | ~28 m |
| A-10C (`Mobile.speed['nominal']` = 155,6 m/s [V]) vs volume visivo 6 km a 3000 m | 155,6 | 30 (stima di test) | 4,7 km | 5,2 (sezione a 3000 m) | ~0,5 km |

Lettura: contro un EWR a rotazione (6-15 s) "attraversare senza essere visti" equivale a sfiorarne il bordo per
qualche secondo; un attraversamento vero dura minuti e ha Pd invariata. **E' fisica, non un difetto della
legge**: la portata pubblicata di un EWR e' per una singola scansione (es. AN/FPS-117: Pd 80 % contro 1 m2 a 330 km,
ricerca `:374`), e qualunque modello cumulativo darebbe Pd **ancora piu' alta** per permanenze lunghe. Cio' che in
Guerra Fredda permetteva la penetrazione non vista era il **volo basso sotto l'orizzonte** (e il terreno): nel
pianificatore c'e', nel DES no (§1.6). La legge serve davvero dove il volume e' piccolo o il sensore e' lento:
contatti radenti, pop-up, sensori a vista, radar WWII lenti, e in futuro radar SAM con dati di scansione e volumi
ridotti dall'orizzonte.

### 1.9 Sonde eseguite (sola lettura) — S-1, S-2, S-3 complete

Script `probe_dwell.py`: sostituisce in memoria `_EngagementRun._detect_direction` con la legge
di §2.3 e la permanenza di §2.4 (stesso codice del piano), poi chiama
`Scenario_Baseline.main(['--compare', <fotografia>, '--save', <cartella_uscita>, '--quiet'])`. Per ogni estrazione
registra anche la decisione **controfattuale** per dwell ipotetici di 2, 6, 10, 30, 60, 120 s (stessa estrazione,
nessun effetto sull'esito).

**S-1 — legge accesa con i soli dati di fonte** (dwell dei 10 EWR della tabella §1.7, nessun altro sensore).
Esito letto: `compared 1009 runs: IDENTICAL (1137.8 s)`. Nessun osservatore della fotografia dichiara un dwell
(`dwell_applied = 0`): nessuno scenario usa un EWR. **Accendere l'interruttore non cambia nessuna delle 1009
esecuzioni.** S-1 e' stata eseguita il 2026-11-05 con il valore di allora dell'AMES-Type-80 (10 s); l'esito vale
anche con i 15 s di DW-2, perche' nessun osservatore della fotografia ha un dwell (nessuno scenario usa un EWR;
l'AMES-Type-80 compare solo in `Test/Test_EWR_Data.py`) [V: `dwell_applied = 0`, `models_with_dwell` vuoto in
`s1/stats.json`].

Statistiche raccolte nella stessa esecuzione, su tutte le estrazioni di rilevamento delle 1009 sessioni (tutte con
i tratti: `with_legs = 33446`, `without_legs = 0`):

| Permanenza `tau` [s] | < 1 | 6-10 | 10-30 | 30-60 | 60-120 | 120-300 | 300-600 | 600-1800 | >= 1800 | totale |
|---|---|---|---|---|---|---|---|---|---|---|
| direzioni | 946 | 7 | 53 | 198 | 1315 | 1903 | 9228 | 1553 | 18243 | **33446** |

(nessuna direzione fra 1 e 6 s). Le 946 con `tau < 1 s` non erano rilevate gia' con la legge attuale (zero
rilevamenti persi anche con dwell 2 s, tabella sotto): presumibilmente osservatori con portata minore della
distanza minima, che hanno gia' Pd 0 [I].

Decisione **controfattuale** con la stessa estrazione, se TUTTI gli osservatori avessero lo stesso dwell (29 483
rilevamenti su 33 446 con la legge attuale):

| dwell ipotetico per tutti [s] | 2 | 6 | 10 | 30 | 60 | 120 |
|---|---|---|---|---|---|---|
| direzioni con `g < 1` | 946 | 946 | 953 | 1006 | 1204 | 2519 |
| rilevamenti persi | 0 | 0 | 3 | 17 | 45 | 464 |

Lettura: negli scenari esistenti le permanenze sono lunghe (29 024 su 33 446, l'87 %, da 5 minuti in su); con periodi di 6-10 s, cioe'
quelli di fonte di 8 EWR su 10, la legge cambierebbe al piu' 3 rilevamenti su 29 483 anche se la si desse a
**ogni** sensore. Il valore 15 s (AMES-Type-80, DW-2) non e' fra i controfattuali: con la stessa estrazione i
rilevamenti persi crescono con il dwell, quindi a 15 s sono fra 3 e 17 (non misurato).

**S-2 — sensibilita' a livello di esecuzione**: dwell uniforme di 10 s per **ogni** osservatore (valore fittizio di
sonda, non un dato; `probe_dwell.py uniform:10`), eseguita il 2026-11-06. Esito letto:
`compared 1009 runs: 44 difference lines (946.5 s)` (44 = righe stampate nel riepilogo, due intestazioni `DIFF` con
le loro righe accorciate). **2 esecuzioni cambiate, 1007 identiche**:

| Esecuzione | Valori differenti | Cosa cambia (letto dal log) |
|---|---|---|
| `S21/S21-5/control` | 42 | il SAM di `Red-Airbase/sam0` spara 2 colpi invece di 4; un colpo SAM diventa un colpo AAA (`aaa0`), gli istanti successivi slittano |
| `S21/S21-7/control` | 56 | il SAM `sam0` non spara (2 colpi -> nessuno); due colpi SAM diventano AAA; il bersaglio Blue `Blue-Strike/str1` **sopravvive** invece di essere distrutto |

Coerente con il controfattuale di S-1 (3 rilevamenti persi a 10 s su 29 483): pochi rilevamenti persi bastano a
cambiare un'esecuzione quando l'osservatore e' un **tiratore** (qui un SAM di S21). Il confronto e' valido. Lo
script `probe_dwell.py` fallisce poi nel salvataggio finale di `stats.json` (`TypeError: '<' not supported between
instances of 'NoneType' and 'str'` in `json.dump(..., sort_keys=True)`: una chiave `None` in un dizionario di
statistiche), quindi lo `stats.json` di S-2 e' **parziale**: e' un difetto dello script di sonda, non del
repository; non va corretto per questo piano. Implicazione per DW-9 in §2.8.

**S-3 — prova della geometria di S32-DWELL** (5 varianti x 4 semi, in memoria; `probe_s32.py`, rc = 0), eseguita
il 2026-11-06. **Tutte le asserzioni di §4.A.7 confermate**, nessun ritocco ai test necessario:

| Seme | `long` == `off` (munizioni) | `ewr_on` == `ewr_off` (munizioni) | colpi ZSU `off` / `short` | ZSU rilevati `off` / `short` (primo episodio = totale; sottoinsieme) | esposizioni ZSU in `long` [s] | P-18 in `ewr_on`: esposizione minima, probabilita' |
|---|---|---|---|---|---|---|
| 0 | si' | si' | 150 / 0 | 4 / 0, si' | 62,7; 64,7; 66,0; 66,7 | 385,7 s, uguale a `ewr_off` |
| 1 | si' | si' | 150 / 0 | 4 / 0, si' | idem | idem |
| 2 | si' | si' | 150 / 0 | 4 / 0, si' | idem | idem |
| 3 | si' | si' | 150 / 150 | 3 / 2, si' | idem | idem |

Ogni seme ha un solo episodio per variante. Totale dei rilevamenti della ZSU sui 4 semi: `off` 15, `short` 2 (la
stima di §4.A.7 era ~15,5 contro ~1,7). La premessa "la ZSU spara in `off`" vale in **tutti** i semi; il limite
`probability <= exposure/600` e' rispettato in ogni seme. Le esposizioni della ZSU (62,7-66,7 s) sono uguali in
`long` e `short` (dipendono dalla geometria, non dal dwell): >= 30 s in `long` (g = 1), < 600 s in `short`.

**Dove sono le sonde**: copia versionata degli script e dell'esito di S-1 in
`Analysis/Document/Rapporti/Sonde_Dwell_D5/` (`probe_dwell.py` per S-1 e S-2:
`<python> probe_dwell.py source|uniform:<s> <cartella_uscita> [regex --only]`; `probe_s32.py` per S-3;
`s1/log.txt`, `s1/stats.json`). I log di S-2 (`s2/log.txt`, `s2/capture.json`, `s2/stats.json` parziale) e di S-3
(`s3_log.txt`) sono in `.ai-run/sonde_dwell/` (fuori dal versionamento, solo sulla macchina osboxes). Le sonde non
vanno rieseguite per eseguire questo piano: restano riferimento. Il `LEGGIMI.md` della cartella versionata descrive
ancora S-2 come incompleta e S-3 come mai eseguita (scritto il 2026-11-05): fa fede questa sezione.

---

## 2. Alternative e raccomandazione

### 2.1 Che cos'e' `dwell_time_s` (domanda 1)

| Opzione | Significato | Pro | Contro |
|---|---|---|---|
| **(a) periodo di rivisita** | tempo fra due occasioni di rilevamento dello stesso punto: 60 / giri al minuto per un'antenna rotante | dato di fonte per 10 EWR; nessuna stima nuova; la conferma della traccia e' gia' nella RIV del profilo di reazione (`Reaction_Profile.py:7-36`), quindi non si conta due volte | ignora il numero di colpi per la conferma (M su N): un plot non e' una traccia |
| (b) periodo x colpi di conferma M | tempo per una traccia confermata | piu' vicino al "tracciato" dei sistemi automatici | M non e' nella ricerca: STIMA nuova (2-3 [I]); si somma alla RIV, che gia' copre rilevamento -> lancio |
| (c) permanenza minima per un rilevamento certo | soglia deterministica: sotto non si vede, sopra Pd(d) | semplice da pianificare | toglie la casualita' proprio dove la fisica e' casuale (fase dell'antenna); salto discontinuo |

**Raccomandazione: (a). DECISIONE DW-1 (presa il 2026-11-06): (a)**, nessun fattore di conferma. Unita': secondi, `float > 0`. **Dove vive**: chiave opzionale `dwell_time_s` nel
dizionario del sensore (`record.radar['dwell_time_s']`), accanto ad `antenna_height`: e' un dato **del sensore**,
non del modo. **Default**: assente (o `None`) = nessuna permanenza dichiarata = legge attuale, in qualunque stato
dell'interruttore. Il valore `0` e' trattato come assente (illuminazione continua, Chain-Home); valori negativi,
non numerici o booleani sono **ignorati** dal lettore del registro (come `_sensor_range_km`), mai un'eccezione.

### 2.2 Valori: quale regola per gli intervalli (DW-2)

La fonte da' spesso un intervallo (3-6, 2-6, 0,5-8 giri/min). Opzioni considerate: (i) **rotazione piu' veloce**
(periodo piu' breve); (ii) punto medio; (iii) valore "normale" quando citato, altrimenti punto medio.
La raccomandazione iniziale era (i): una regola sola, senza giudizi caso per caso, prudente per chi attacca (la
permanenza che riduce la Pd e' la piu' breve).

**DECISIONE DW-2 (presa il 2026-11-06), diversa dalla raccomandazione: "regime normale se citato, altrimenti
rotazione piu' veloce"** (variante di (iii) con il ramo di (i)). Effetti sui 10 record:
- **AMES-Type-80 = 15 s** (60/4): la fonte dice "4 giri/min (fino a 6)" (`Ricerca_EWR_2026_10_29.md:338`); 4 e'
  letto come regime base, cioe' "normale", e 6 come massimo. La parola "normale" non c'e': e' una **stima/
  interpretazione [S]**, dichiarata nel commento del record e nel rapporto dell'esecutore.
- Tutti gli altri valori **invariati** rispetto alla regola (i), perche' nessuna loro fonte cita un regime normale:
  SCR-270 60 s; P-12 6 s (la contraddizione 10 / 2-6 si risolve con il ramo "piu' veloce", a favore di 10 giri/min);
  P-18 6 s; AMES-Type-7 7,5 s; P-37, 1L13, 55Zh6, TPS-43, P-14 10 s.
- Chain-Home, Freya, Wassermann, Mammut, AN-FPS-117: nessun valore (come prima).
- Nella ricerca EWR "normale" compare solo per l'AN/FPS-20 (`:351`), che non e' nei registri.

[S] scelta di progetto, dichiarata nel commento di ogni record.

### 2.3 Forma della legge (domanda 2)

| Opzione | Legge | Pro | Contro |
|---|---|---|---|
| **L1 riduzione lineare** | `Pd = g * Pd(d_cpa)`, `g = min(1, tau / dwell)` | e' la probabilita' che almeno un'occasione cada nella permanenza con fase dell'antenna uniforme [I, argomento geometrico]; **si riduce esattamente** alla legge attuale per `tau >= dwell` o dwell assente; Pd sempre <= attuale (monotonia, §1.2); si applica come fattore, quindi `detection_radius` resta la sua inversa esatta; nessuna costante nuova | per permanenze lunghe non cresce oltre `Pd(d_cpa)` (non e' cumulativa) |
| L2 cumulativa | `Pd = 1 - prod_k (1 - p(d(t_k)))` sulle occasioni `t_k` ogni `dwell` | fisicamente completa anche per permanenze lunghe | cambia il significato di `PD_AT_ACQUISITION_RANGE` (diventa per scansione) e quindi va ritarata **tutta** la legge; rende i sensori con dwell molto piu' "vedenti" di quelli senza (incoerenza fra record); inversione numerica per l'istante; nessuna riduzione all'attuale |
| L3 a gradino | `Pd = Pd(d_cpa)` se `tau >= dwell`, altrimenti 0 | semplice | discontinua; = opzione (c) di §2.1 |

**Raccomandazione: L1. DECISIONE DW-3 (presa il 2026-11-06): L1**, motivata dall'utente con la semplicita' della
prima versione e con lo stesso criterio di Pd per ogni sensore di rilevamento (legge unica generica). Si realizza
come funzione pubblica e pura `dwell_factor(exposure_s, dwell_time_s)` composta con la
legge esistente attraverso il fattore: `detection_probability(d, R, factor * dwell_factor(tau, dwell))`.

Composizione e limiti:
- **con la distanza**: invariata, `d = distance_cpa` della finestra, `R` = portata propria;
- **notte, meteo, nebbia**: moltiplicativi e indipendenti, `P = f_notte * f_meteo * f_nebbia * g * Pd(d)`;
- **permanenza breve**: `g` lineare fino a 0; `tau = 0` (contatto tangente) => Pd 0;
- **finestre spezzate** (decollo/atterraggio, ritaglio G4a): la permanenza **non** si taglia all'inizio della
  finestra (§2.4), altrimenti lo spezzare finestre ridurrebbe la Pd per un artefatto di calcolo;
- **piu' finestre della stessa coppia**: una estrazione per finestra, come oggi; ogni finestra ha la sua
  permanenza;
- **piu' sensori sullo stesso bersaglio**: osservatori diversi = estrazioni indipendenti, come oggi; dentro lo
  stesso asset vale la permanenza del sensore che da' la portata (il piu' lontano, `detection_range`): un TVD senza
  dwell con portata minore non entra (limite, §5).

### 2.4 Dove si calcola la permanenza, RNG e interruttore (domanda 3)

| Opzione | Dove | Pro | Contro |
|---|---|---|---|
| **(a) nel risolutore** | `_EngagementRun._exposure_time`, dai tratti (`range_intervals` con la portata propria) | modifica locale; costo nullo quando la legge e' spenta o il sensore non dichiara dwell; puo' guardare prima dell'inizio della finestra | ricalcola un `range_intervals` per direzione con dwell |
| (b) nello scheduler | campi `exposure_a/exposure_b` di `ContactWindow` | lo scheduler calcola gia' gli intervalli interni (`:1075`) | tocca `ContactWindow`, `contact_windows`, `trim_contact_window`, `_pair_windows`; la finestra resta tagliata ai suoi estremi |

**Raccomandazione (a). DECISIONE DW-4 (presa il 2026-11-06): (a), nel risolutore dai tratti.** Regola della
permanenza `tau` per la direzione osservatore -> bersaglio:
- **con i tratti di entrambi** (sempre in sessione): somma, sugli intervalli di `range_intervals(tratti_oss,
  tratti_bers, portata_propria)` che toccano la finestra (`end >= t_start - TIME_EPS` e `start <= t_end +
  TIME_EPS`), di `min(end, t_end) - start`. L'intervallo che contiene l'inizio della finestra **conta dal suo
  inizio vero** (il sensore guardava gia').
- **senza tratti** (chiamate dirette dei test): `t_end - t_start` se la portata propria e' la maggiore (o l'altra
  e' None); altrimenti `t_mutual_end - t_mutual_start` se l'intervallo reciproco esiste; altrimenti 0.

**RNG**: il calcolo di `dwell` e `tau` avviene **prima** di `self._draw()` e non estrae nulla; l'estrazione resta
una, nella stessa posizione; le uscite anticipate (`:1988-1994`) restano prima di tutto. **Numero e ordine delle
estrazioni invariati in ogni stato dell'interruttore**; cambia solo la soglia, come per `detection_factor`.

**Interruttore** (domanda 3, DW-5): opzioni
- **(a) `Engagement_Resolver.D5_DWELL_TIME = False`**, letto a ogni chiamata da `Session_Simulator` (che passa al
  risolutore il lettore `dwell_time_for` solo se acceso) e da `Path.compute_detection_metrics` (che importa gia'
  localmente dal risolutore, `Air_Route_Manager.py:1103`). Una sola leva per DES e pianificatore, accanto alla
  legge che governa.
- (b) in `Session_Simulator` come gli F*/G*: il pianificatore non lo vede senza importare l'orchestratore.
- (c) in `Mobile` come `D4C_VISUAL_SENSOR`, spegnendo il **dato** (`detection_dwell_time` -> None): una leva sola,
  ma governa una regola del motore attraverso l'accessore di un dato.

**Raccomandazione (a), spento di default. DECISIONE DW-5 (presa il 2026-11-06): (a), `D5_DWELL_TIME = False`**;
l'eventuale accensione si decide dopo la verifica del lavoro, non in questo piano. "Identico con interruttore
spento" significa: `Session_Simulator` non passa `dwell_time_for` (la chiamata a `resolve_engagement` e'
**letteralmente** quella di prima), `_detect_direction` esegue le stesse istruzioni, il `Detection` ha due campi in
piu' a `None` (non registrati nella fotografia), le metriche del pianificatore sono quelle di prima: **1009
identiche**. Una chiamata diretta a `resolve_engagement` senza `dwell_time_for` usa la legge attuale anche con
l'interruttore acceso: la legge e' attiva solo se il chiamante passa il lettore.

### 2.5 Coerenza fra pianificatore e risolutore, `AVOID_DETECTION` (domanda 4)

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| P0 | pianificatore invariato | zero lavoro | con l'interruttore acceso la metrica `max_detection_probability` diverge dal DES (promessa "una sola fisica" della Proposta d'origine §2.1 rotta) |
| **P1 (blocco B)** | `DetectionThreat.dwell_time_s`; `compute_detection_metrics` raggruppa i tratti contigui dello stesso volume in un **attraversamento** (come la finestra del DES) e, con l'interruttore acceso, ne calcola la Pd con la stessa legge; `AVOID_DETECTION` invariato (aggiramento puro) | coerenza, poco codice, nessun cambio di rotte | le metriche cambiano solo per attraversamenti piu' brevi del periodo (rari, §1.8) |
| P2 (blocco C) | P1 + in `AVOID_DETECTION` un volume di rilevamento con dwell si **attraversa** se la Pd dell'attraversamento e' <= una soglia del chiamante (`detection_pd_max`), invece di aggirarlo | e' la "corda limitata" della D-5 | con i dati di fonte la corda ammessa e' 1,5-6 km (§1.8): nessuna rotta si accorcia contro un EWR; tocca la ricerca del percorso e la chiave di scelta |

**Raccomandazione: P1 ora, P2 rimandato** finche' non esistono sensori con dwell e volumi piccoli (radar SAM con
dati di scansione, orizzonte nel DES). **DECISIONI DW-6 e DW-7 (prese il 2026-11-06): P1 si' (blocco B); P2
rimandato (blocco C descritto in §4 ma non eseguito; l'orizzonte radar nel DES resta un'attivita' separata).** Il vincolo "**rilevamento != intercettazione**" resta per costruzione in
ogni opzione: P1 non tocca la ricerca; in P2 l'attraversamento di un volume di rilevamento non esenta il tratto dal
controllo dei volumi d'intercettazione (`cross_threats`, `Air_Route_Manager.py:1755-1765`), che restano attraversati
solo con la loro corda di sicurezza.

### 2.6 Scenari (domanda 5)

Un'unita' nuova **S32-DWELL**, stile S31: geometria di S31 'zsu' (linea Red di 3 BMP-2 e una ZSU-57-2 in
(1000, -300), 4 A-10C a 3000 m in sorvolo, bersaglio ristretto ai BMP-2, `only_designated`, `BOTH_HOLD`), 4 semi,
5 varianti:

| Variante | Interruttore | dwell della ZSU (dichiarato di test, **non dato**) | Con P-18 | Cosa prova |
|---|---|---|---|---|
| `off` | spento | — | no | riferimento (legge attuale) |
| `long` | acceso | 30 s (permanenza 62-67 s: `g = 1`) | no | riduzione esatta alla legge attuale: **stessi eventi di `off`** |
| `short` | acceso | 600 s (`g` ~0,10-0,11) | no | Pd ridotta: rilevamenti della ZSU **sottoinsieme** di quelli di `off` per ogni seme, e meno in totale |
| `ewr_off` | spento | — | si' (P-18 in (30 000, 0), dwell di **fonte** 6 s) | riferimento con EWR |
| `ewr_on` | acceso | — | si' | con i dati di fonte e permanenza di minuti **nulla cambia**: stessi eventi di `ewr_off` |

Sul visivo della ZSU non c'e' un dato di permanenza: 30 s e 600 s sono **valori di test** scelti per stare
chiaramente sopra e sotto la permanenza calcolata (§4.A.7), dichiarati come tali nel test, mai nei registri.
Esecuzioni nuove: **20**. Un'unita' con un sensore di registro a dwell che faccia sparare un tiratore non esiste
oggi (nessun tiratore ha dati di scansione): e' il motivo dei valori dichiarati di test.

**DECISIONE DW-8 (presa il 2026-11-06): S32-DWELL con 5 varianti x 4 semi = 20 esecuzioni nuove**, come in tabella.
La sonda S-3 (§1.9) ha confermato la geometria: esposizioni della ZSU 62,7-66,7 s in ogni seme, rilevamenti della
ZSU 15 in `off` e 2 in `short` sui 4 semi.

### 2.7 Dimensione e blocchi (domanda 6)

| Blocco | Contenuto | File | Righe (stima) | Test | Fotografia |
|---|---|---|---|---|---|
| **A** | dato, lettori, legge, interruttore, scenario | `Asset/Vehicle_Data.py`, `Asset/Mobile.py`, `Logic/Engagement_Resolver.py`, `Logic/Session_Simulator.py`, `Test/Scenario_Fixtures.py`, `Test/Scenario_Baseline.py`, 5 file di test (1 nuovo) | ~170 + ~330 test | 31 | 1009 identiche + 20 nuove |
| **B** | pianificatore coerente (P1) | `Logic/Air_Route_Manager.py`, 2 file di test | ~60 + ~110 test | 7 | invariata |
| C (rimandato, DW-7: NON eseguire) | attraversamento a corda limitata | `Logic/Air_Route_Manager.py`, `Test/Test_Air_Route_Manager.py` | ~120 + ~150 test | 6 | invariata |

**Organizzazione (conseguenza di DW-6 e DW-7)**: A e B in un solo branch `ai/oc-dwell-time` (o di
`des-developer`), due commit; A per primo, perche' B importa `dwell_factor` e `D5_DWELL_TIME` da A. Il rischio e'
basso: la legge e' spenta di default e, anche accesa, tocca solo i 10 record EWR, assenti dalla fotografia.

### 2.8 Estensione ad altri sensori (DW-9)

La legge e' **gia' generica**: `_detect_direction` (`Logic/Engagement_Resolver.py:1986-2031`) e' lo stesso codice
per ogni osservatore del DES (SAM, AAA, aerei, navi, EWR), e il lettore di default `registry_dwell_time` ->
`Mobile.detection_dwell_time` (§4.A.2-A.3) legge `dwell_time_s` da qualunque dizionario di sensore (`radar`, `TVD`,
`visual`) di qualunque record di `Vehicle_Data`, `Ship_Data`, `Aircraft_Data`. Il blocco B fa lo stesso per
`DetectionThreat` (`sensor_dwell_time`). Dare un dwell a un'altra classe di sensori e' quindi **solo un dato**.

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| **(a) solo il meccanismo ora** | valori ai soli 10 EWR (§1.7); nessun valore per SAM, AAA, radar d'aereo, navi, TVD, vista | nessun numero senza fonte; con l'interruttore acceso la fotografia resta identica (S-1) | la legge non agisce su nessun tiratore finche' mancano i dati |
| (b) valori stimati ora per le altre classi | `dwell_time_s` [S] per SAM/AAA/aerei | la legge agirebbe subito | SAM e AAA sono **tiratori**: una Pd ridotta cambia gli esiti di tiro (§1.5); numeri senza fonte che cambiano la fotografia con l'interruttore acceso |

**DECISIONE DW-9 (nuova, presa il 2026-11-06): (a) solo il meccanismo ora.** Motivi: SAM e AAA sono tiratori, quindi
nessun valore stimato senza fonte; la sonda S-2 mostra che un dwell uniforme di 10 s a **ogni** osservatore cambia
gia' 2 esecuzioni su 1009 (i SAM di S21-5 e S21-7, §1.9) e il controfattuale di S-1 da' 17, 45 e 464 rilevamenti
persi su 29 483 a 30, 60 e 120 s: estendere i valori a SAM e AAA **cambiera' la fotografia con l'interruttore
acceso**, e quel confronto andra' riletto esecuzione per esecuzione. Con l'interruttore spento la fotografia resta
identica in ogni caso (`Session_Simulator` non passa il lettore).

Un agente di ricerca sta raccogliendo i dati per classe di sensore in `Ricerca_Dwell_Sensori_2026_11_06.md`. **Quel
documento NON e' un ingresso di questo piano**: l'esecutore non lo legge e non ne usa i valori. Quando i dati
arriveranno, l'estensione sara' un intervento separato e senza cambi di codice (procedura in "Estensioni future").

---

## 3. Decisioni dell'utente (tutte prese il 2026-11-06)

1. **DW-1 Significato di `dwell_time_s`**: **(a)** periodo di rivisita = 60 / giri al minuto, senza colpi di
   conferma (come raccomandato). Scartate: (b) periodo x M colpi; (c) soglia deterministica.
2. **DW-2 Valori e regola sugli intervalli**: **"regime normale se citato, altrimenti rotazione piu' veloce"**
   (diversa dalla raccomandazione "rotazione piu' veloce"). 10 EWR con dato di fonte (tabella §1.7), con
   **AMES-Type-80 = 15 s** [S, interpretazione di "4 (fino a 6)"] e gli altri 9 valori invariati; Chain-Home senza
   permanenza (illuminazione continua, D); Freya, Wassermann, Mammut e AN-FPS-117 senza dato (nessun valore inventato).
3. **DW-3 Forma della legge**: **L1** `Pd = min(1, tau/dwell) * Pd(d_cpa)` (come raccomandato), per semplicita' della
   prima versione e stesso criterio di Pd per ogni sensore. Scartate: L2 cumulativa; L3 a gradino.
4. **DW-4 Permanenza**: **nel risolutore dai tratti**, non tagliata all'inizio della finestra (come raccomandato).
5. **DW-5 Interruttore**: **`Engagement_Resolver.D5_DWELL_TIME`, default False** (come raccomandato). L'eventuale
   accensione si decide dopo la verifica del lavoro (fuori da questo piano; S-1: accenderlo con i soli dati di
   fonte non cambia nessuna delle 1009 esecuzioni).
6. **DW-6 Pianificatore**: **P1, blocco B** (metriche coerenti, `AVOID_DETECTION` invariato), come raccomandato.
7. **DW-7 Attraversamento a corda limitata (P2, blocco C)**: **rimandato** (come raccomandato): il blocco C resta
   descritto in §4 ma non si esegue. L'orizzonte radar nel DES resta un'attivita' separata da pianificare.
8. **DW-8 Scenario S32-DWELL**: **5 varianti x 4 semi = 20 esecuzioni nuove** (come raccomandato), con i valori di
   permanenza dichiarati di test sulla ZSU (30 s, 600 s) e il P-18 con il dato di fonte (6 s).
9. **DW-9 Estensione ad altri sensori (nuova)**: **solo il meccanismo ora** (§2.8): valori ai soli 10 EWR; nessun
   valore per SAM, AAA, radar d'aereo, navi, TVD, vista finche' non c'e' una fonte.

**Decisioni ancora aperte per l'esecuzione**: nessuna. Restano fuori da questo piano, da decidere dopo:
l'accensione di `D5_DWELL_TIME` (dopo la verifica); i valori per le altre classi di sensori (DW-9, dopo la
ricerca); l'orizzonte radar nel DES e il blocco C (DW-7).

---

## 4. Piano di intervento (decisioni DW-1..DW-9 prese)

Il piano realizza le decisioni di §3 (blocchi A e B; il blocco C **non** si esegue). Se il codice reale non
corrisponde al piano (righe, firme, esiti dei test o del confronto), l'esecutore **non** adatta il piano: si ferma
e lo riferisce.

### Blocco A — dato, legge, interruttore, scenario

#### A.1 `Asset/Vehicle_Data.py`: chiave `dwell_time_s` nei 10 record EWR

Nel dizionario `'radar'` di ciascun record, dopo `'reliability'` (e dopo `antenna_height`/`acquisition_profile` se
presenti), aggiungere la chiave e una riga di commento nel formato del blocco:

| Record (variabile) | Riga attuale del record | Valore | Commento da scrivere (testo esatto) |
|---|---|---|---|
| `SCR270_data` | `:4660` | `60.0` | `# dwell_time_s 60: FONTE 1 giro/min (conversione D: 60/1), conf. media. D-5.` |
| `P12_Yenisei_data` | `:4710` | `6.0` | `# dwell_time_s 6: FONTE 10 giri/min (2-6 secondo [AC-P12], CONTRADDIZIONE; nessun regime normale citato, regola: rotazione piu' veloce) -> 60/10 (D). D-5.` |
| `P18_Terek_data` | `:4733` | `6.0` | `# dwell_time_s 6: FONTE 10 giri/min -> 60/10 (D), conf. media. D-5.` |
| `P37_Mech_data` | `:4758` | `10.0` | `# dwell_time_s 10: FONTE 3-6 giri/min (nessun regime normale citato, regola: rotazione piu' veloce) -> 60/6 (D). D-5.` |
| `Nebo_SV_1L13_data` | `:4780` | `10.0` | `# dwell_time_s 10: FONTE 3-6 giri/min (nessun regime normale citato, regola: rotazione piu' veloce) -> 60/6 (D). D-5.` |
| `Nebo_55Zh6_data` | `:4804` | `10.0` | `# dwell_time_s 10: FONTE 6 giri/min -> 60/6 (D), conf. media-bassa. D-5.` |
| `AN_TPS43_data` | `:4829` | `10.0` | `# dwell_time_s 10: FONTE 6 giri/min -> 60/6 (D), conf. media. D-5.` |
| `AMES_Type7_data` | `:4910` | `7.5` | `# dwell_time_s 7.5: FONTE 0,5-8 giri/min (nessun regime normale citato, regola: rotazione piu' veloce) -> 60/8 (D). D-5.` |
| `AMES_Type80_data` | `:4935` | `15.0` | `# dwell_time_s 15: FONTE 4 giri/min (fino a 6); 4 letto come regime normale = STIMA/interpretazione [S] (la fonte non dice 'normale'; regola: regime normale se citato) -> 60/4 (D). D-5.` |
| `P14_Lena_data` | `:5011` | `10.0` | `# dwell_time_s 10: FONTE 2-6 giri/min (nessun regime normale citato, regola: rotazione piu' veloce) -> 60/6 (D). D-5.` |

Nei 5 record senza dato (`FuMG80_Freya_data`, `AN_FPS117_data`, `Chain_Home_data`, `Wassermann_data`,
`Mammut_data`) **nessuna chiave**; nel solo `Chain_Home_data` aggiungere il commento
`# nessun dwell_time_s: antenna fissa a illuminazione continua (D), nessun intervallo fra le occasioni. D-5.`
Sopra il blocco "Nuovi EWR (D-4b)" (`:4653-4658`) aggiungere al commento esistente due righe:
`# D-5 (Proposta_Dwell_Time_Rilevamento.md): 'dwell_time_s' [s] nel radar = periodo di rivisita 60/giri al minuto`
`# (FONTE la rotazione, D la conversione); assente = nessuna permanenza dichiarata (legge di Pd invariata).`

e una terza riga con la regola sugli intervalli (DW-2):
`# Intervalli di giri/min (scelta [S], DW-2): regime normale se la fonte lo cita, altrimenti rotazione piu' veloce.`

Il testo dei commenti della tabella e' quello da scrivere, compreso il marcatore [S] del Type-80: l'esecutore puo'
solo andare a capo per rispettare la larghezza di riga del file, senza cambiare le parole.

#### A.2 `Asset/Mobile.py`: due lettori

Dopo `_sensor_range_km` (`:1532-1568`) aggiungere:

```python
@staticmethod
def _sensor_dwell_s(data_record, sensor: str) -> Optional[float]:
    """`dwell_time_s` [s] del dizionario `sensor` del record (D-5), o None.

    None se il sensore manca, non e' un dizionario, la chiave manca, o il valore non e' un numero
    (bool escluso) finito e > 0. Mai un'eccezione: e' un dato opzionale.
    """
```

e dopo `detection_range` (`:1570-1652`) due metodi pubblici:

```python
def sensor_dwell_time(self, sensor: str) -> Optional[float]:
    """Periodo di rivisita [s] del sensore `sensor` ('radar'/'TVD'/'visual') del modello, o None (D-5).

    Raises:
        ValueError: `sensor` fuori da DETECTION_SENSORS.
    """

def detection_dwell_time(self, mode: str, range_type: str = DEFAULT_DETECTION_RANGE_TYPE) -> Optional[float]:
    """Periodo di rivisita [s] del sensore che da' `detection_range(mode, range_type=range_type)` (D-5).

    Stesso dispatch di registro e stessa esclusione del visivo (D4C_VISUAL_SENSOR) di detection_range; il
    sensore e' quello con la portata MASSIMA, a parita' il primo di DETECTION_SENSORS (come
    Air_Route_Manager.build_detection_threat). None se il modello non e' noto, nessun sensore ha portata sul
    modo, o il sensore vincente non dichiara `dwell_time_s`.

    Raises:
        ValueError: `mode` o `range_type` fuori dominio.
    """
```

Comportamento: stesse validazioni d'argomento di `detection_range`; stesso lookup `_VehicleData._registry.get(model)
or _ShipData... or _AircraftData...`; per `detection_dwell_time` si scorrono i sensori ammessi in ordine,
`_sensor_range_km(record, s, mode, range_type)`, si tiene il primo con il valore massimo (confronto stretto `>`),
e si restituisce `_sensor_dwell_s(record, vincente)`. Nessun warning per dati mancanti (solo `logger.debug`).

#### A.3 `Logic/Engagement_Resolver.py`: interruttore, legge, lettore

1. **Costanti** (dopo `RECON_EFFICIENCY_FOG_RELIEF`, `:488`):

```python
# D-5 opzione 2 (Proposta_Dwell_Time_Rilevamento.md), interruttore dedicato:
#   * `D5_DWELL_TIME` (SPENTO): Pd ridotta dalla PERMANENZA nel volume quando l'osservatore dichiara un periodo di
#     rivisita (`dwell_time_s` del sensore nel registro): Pd = min(1, permanenza/dwell) * Pd(d_cpa). Lo leggono
#     Session_Simulator (passa `dwell_time_for` al risolutore solo se acceso) e Air_Route_Manager (metriche di
#     rilevamento). Spento: legge di sola distanza, come prima. Nessuna estrazione in piu' ne' in ordine diverso in
#     nessuno dei due stati.
D5_DWELL_TIME = False
```

2. **Funzioni pubbliche** dopo `detection_radius` (`:1071-1100`):

```python
def dwell_factor(exposure_s: float, dwell_time_s: Optional[float]) -> float:
    """Fattore di permanenza g in [0, 1] della legge di Pd (D-5): min(1, exposure_s / dwell_time_s).

    E' la probabilita' che almeno un'occasione di rilevamento (un passaggio del fascio, periodo dwell_time_s, fase
    uniforme) cada nella permanenza. Forma: scelta di progetto [S] con giustificazione geometrica, nessuna costante.
    dwell_time_s None o 0 -> 1.0 (nessuna permanenza dichiarata: legge di sola distanza).

    Raises:
        TypeError: argomenti non numerici o booleani.
        ValueError: exposure_s negativo o non finito; dwell_time_s negativo o non finito.
    """

def registry_dwell_time(observer, target, mode: Optional[str]) -> Optional[float]:
    """Lettore di default per `resolve_engagement(dwell_time_for=...)`: `observer.detection_dwell_time(mode)`.

    None se `mode` e' None o l'osservatore non espone `detection_dwell_time` (stub, adapter); `target` non e' letto
    (firma uniforme con detection_factor, per lettori futuri che dipendano dal bersaglio).
    """
```

3. **`Detection`** (`:614-628`): due campi in coda, docstring aggiornata:

```python
    exposure_s: Optional[float] = None      # permanenza [s] usata dalla legge D-5; None = legge non applicata
    dwell_time_s: Optional[float] = None    # periodo di rivisita [s] dell'osservatore; None = legge non applicata
```

4. **`_EngagementRun.__init__`** (`:1645-1649`): parametro keyword in coda `dwell_time_for=None`, salvato in
   `self.dwell_time_for` accanto a `self.detection_factor` (`:1712`).

5. **Metodo nuovo** `_exposure_time(self, window, observer_id, target_id, own_range, other_range) -> float`, dopo
   `_detection_time` (`:2081-2107`), con la regola di §2.4 (tratti: `range_intervals(legs_obs, legs_tgt,
   own_range)`, intervalli che toccano la finestra, contributo `max(0.0, min(end, window.t_end) - start)`; senza
   tratti: il ripiego di §2.4). Docstring che dica perche' non si taglia all'inizio della finestra.

6. **`_detect_direction`** (`:1986-2031`). Dopo il calcolo di `factor` (`:1996-1999`) e **prima** di
   `draw = self._draw()` (`:2001`), inserire:

```python
        exposure = dwell = None

        if self.dwell_time_for is not None:
            # D-5 (D5_DWELL_TIME, v. docstring del modulo): permanenza nel volume proprio. Nessuna estrazione qui:
            # numero e ordine delle estrazioni restano quelli di prima.
            mode = GROUNDED_DETECTION_MODE if self._grounded_in(target.id, window) else detection_mode_for(target.asset)
            dwell = _check_dwell(self.dwell_time_for(observer.asset, target.asset, mode))

            if dwell is not None:
                exposure = self._exposure_time(window, observer.id, target.id, own_range, other_range)
                factor = factor * dwell_factor(exposure, dwell)
```

   Il resto invariato (stessa `probability`, stesso `detection_radius(draw, own_range, factor)` con il fattore
   composto); nel `Detection` aggiungere `exposure_s=exposure, dwell_time_s=dwell`. Funzione privata
   `_check_dwell(value) -> Optional[float]` accanto a `_check_factor` (`:1031-1038`): `None` o `0` -> None;
   bool o non numerico -> `TypeError`; negativo o non finito -> `ValueError`; altrimenti `float(value)`.
   Import da `Contact_Scheduler` (`:436-441`): aggiungere `GROUNDED_DETECTION_MODE` e `detection_mode_for`.

7. **`resolve_engagement`** (`:3619-3779`): parametro keyword `dwell_time_for: Optional[Callable] = None` dopo
   `target_rules`; validazione `if dwell_time_for is not None and not callable(dwell_time_for): raise
   TypeError("dwell_time_for must be callable")`; passaggio a `_EngagementRun`. Voce nella docstring:
   `dwell_time_for: (observer, target, mode) -> float | None, periodo di rivisita [s] del sensore dell'osservatore
   (D-5, v. "Permanenza nel volume"); None (default) = legge di sola distanza. In sessione lo passa
   Session_Simulator (registry_dwell_time) solo con D5_DWELL_TIME acceso.`

8. **Docstring del modulo**: nuova sezione `## Permanenza nel volume (D-5, 2026-11-xx)` dopo "Controllo di
   portata" con: la legge, il significato del dato, la regola della permanenza (non tagliata), l'invarianza di
   numero e ordine delle estrazioni, l'interruttore, i limiti (§5.2). Al punto 1 della catena (`:14-19`) una frase:
   "con `dwell_time_for` (D-5) la soglia e' moltiplicata per il fattore di permanenza". In "L'ordine delle
   estrazioni fa parte del contratto" (`:385-390`) nessun cambio di testo salvo "(invariato dalla D-5)".

#### A.4 `Logic/Session_Simulator.py`: passaggio del lettore

In `engage`, dopo il blocco `if target_rules:` (`:2743-2763`) e prima della chiamata (`:2765`):

```python
        if ER.D5_DWELL_TIME:
            # D-5: Pd dipendente dalla permanenza (v. Engagement_Resolver.D5_DWELL_TIME). Spento: chiamata di prima.
            extra['dwell_time_for'] = ER.registry_dwell_time
```

Nessun interruttore nuovo in `Session_Simulator` (la leva e' nel risolutore, DW-5). Una riga nel docstring del
modulo nell'elenco degli interruttori: "D-5: `Engagement_Resolver.D5_DWELL_TIME` (SPENTO)".

#### A.5 `Test/Scenario_Fixtures.py`: permanenza dichiarata di test

Dopo `declare_sensor` (`:271-303`):

```python
def declare_dwell(asset, dwell_by_mode: Mapping[str, float]):
    """Periodo di rivisita DICHIARATO DI TEST [s] per modo (D-5): NON un dato, serve agli scenari che devono
    mostrare la legge su un tiratore (nessun tiratore del registro ha dati di scansione).

    Scavalca `detection_dwell_time` SOLO sull'istanza e SOLO per i modi indicati; per gli altri delega al registro.
    Restituisce l'asset.

    Raises:
        ValueError: modo fuori da DETECTION_MODES o valore non positivo.
    """
```

Stessa struttura di `declare_sensor`; l'override accetta `(mode, range_type=DEFAULT_DETECTION_RANGE_TYPE)`.

#### A.6 Test unitari del blocco A (25)

Logger mockati come negli altri file: `_ER_LOGGER` in `Test_Engagement_Resolver.py` (`:43`), `_MOBILE_LOGGER` in
`Test_Mobile.py` (`:37`). Nessuna classe base condivisa nuova.

`Test/Test_Engagement_Resolver.py`, classe nuova **`TestDwellFactor`** (6):
1. `test_no_dwell_is_neutral`: `dwell_factor(5.0, None) == 1.0`, `dwell_factor(5.0, 0.0) == 1.0`.
2. `test_exposure_at_least_the_dwell_is_neutral`: `(10, 10) -> 1.0`, `(30, 10) -> 1.0`.
3. `test_short_exposure_is_proportional`: `(5, 10) -> 0.5` (assertAlmostEqual).
4. `test_zero_exposure_gives_zero`: `(0, 10) -> 0.0`.
5. `test_invalid_arguments_raise`: esposizione negativa e `dwell` negativo o `inf` -> `ValueError`; `dwell=True`,
   `dwell='x'` -> `TypeError`.
6. `test_switch_is_off_by_default`: `ER.D5_DWELL_TIME is False`.

Classe nuova **`TestDwellTimeInTheResolver`** (11), con gli stub del file (`_Asset`, `_Force`, `_ScriptedRng`,
`_window`, `_profiles`, `_always`):
1. `test_without_the_reader_the_detections_are_unchanged`: stessa run con e senza `dwell_time_for=None` -> tuple
   di `(observer_id, target_id, probability, draw, detected, time)` uguali; `exposure_s`/`dwell_time_s` None.
2. `test_long_exposure_reproduces_the_previous_law`: finestra 0-1000 s senza tratti, lettore che restituisce 5 s
   -> stesse Detection (salvo i due campi nuovi) e stesso esito di tiro della run senza lettore.
3. `test_short_exposure_scales_the_probability`: finestra 0-10 s, `distance=0`, portate uguali, dwell 40 s ->
   `probability == 0.25`; con `_ScriptedRng([0.3, ...])` non rilevato (senza lettore: rilevato), con
   `[0.2, ...]` rilevato.
4. `test_draw_count_and_order_are_unchanged`: due finestre, `_ScriptedRng` con valori distinti; il numero di
   chiamate e il `draw` di ogni Detection, nell'ordine, sono uguali con e senza lettore.
5. `test_exposure_from_legs_is_not_cut_at_the_window_start`: tratti rettilinei (`Leg`) di un bersaglio che
   attraversa la portata di un osservatore fermo in 0-100 s; finestra costruita con `t_start=60` (come dopo
   `trim_contact_window`) -> `Detection.exposure_s == 100` (non 40), entro 1e-6.
6. `test_inner_observer_without_legs_uses_the_mutual_interval`: `range_a=2000`, `range_b=1000`, finestra 0-100 con
   `t_mutual_start=40`, `t_mutual_end=60` -> la Detection di b ha `exposure_s == 20`.
7. `test_inner_observer_without_a_mutual_interval_never_detects`: come sopra con `t_mutual_start=None` (costruire
   il `ContactWindow` a mano: l'helper `_window` lo valorizza sempre) e dwell 10 -> Detection di b con
   `probability == 0.0`, `detected` False, estrazione comunque consumata (conteggio delle chiamate invariato).
8. `test_detection_records_exposure_and_dwell`: con lettore 40 s, `exposure_s == 10`, `dwell_time_s == 40`.
9. `test_reader_must_be_callable`: `dwell_time_for=5` -> `TypeError`.
10. `test_invalid_dwell_from_the_reader_raises`: lettore che restituisce `-1` -> `ValueError`; `'x'` ->
    `TypeError`; `0` -> legge non applicata (Detection con `dwell_time_s` None).
11. `test_registry_dwell_time_reads_the_observer`: stub con `detection_dwell_time(mode)` -> valore; stub senza
    metodo -> None; `mode=None` -> None.

`Test/Test_Mobile.py`, classe nuova **`TestDetectionDwellTime`** (4), Vehicle reali come nei test esistenti:
1. `test_ewr_dwell_from_the_registry`: P-18-Terek -> `detection_dwell_time('air') == 6.0`,
   `sensor_dwell_time('radar') == 6.0`.
2. `test_records_without_dwell_give_none`: 9K331-Tor -> `detection_dwell_time('air') is None`; AN-FPS-117 ->
   None.
3. `test_dwell_follows_the_sensor_of_detection_range`: con `patch.dict` in memoria su un record con `radar` e
   `TVD` aria (scelta del modello all'esecutore), dare al TVD portata maggiore e `dwell_time_s` diverso dal radar
   -> si legge quello del TVD; ripristinare.
4. `test_invalid_values_are_ignored`: `patch.dict` sul radar del P-18 con `0`, `-3`, `True`, `'6'` -> None.

`Test/Test_EWR_Data.py`, classe nuova **`TestEWRDwellTime`** (2):
1. `test_source_dwell_values`: i 10 valori della tabella A.1 (`subTest` per modello), letti da
   `Vehicle_Data._registry[model].radar['dwell_time_s']`. Costante di modulo da scrivere nel test (valori di DW-2):

```python
# D-5, DW-2: periodo di rivisita [s] = 60 / giri al minuto; regime normale se citato, altrimenti rotazione piu'
# veloce. AMES-Type-80 15: 4 giri/min letto come regime normale di "4 (fino a 6)", interpretazione [S].
EWR_DWELL_S = {
    'SCR-270': 60.0, 'P-12-Yenisei': 6.0, 'P-18-Terek': 6.0, 'P-37-Mech': 10.0, '1L13-Nebo-SV': 10.0,
    '55Zh6-Nebo': 10.0, 'AN-TPS-43': 10.0, 'AMES-Type-7': 7.5, 'AMES-Type-80': 15.0, 'P-14-Lena': 10.0,
}
```

2. `test_records_without_rotation_data_have_no_dwell`: i 5 record senza chiave (`FuMG-80-Freya`, `AN-FPS-117`,
   `Chain-Home`, `Wassermann`, `Mammut`: `assertNotIn('dwell_time_s', radar)`).

Le chiavi del registro sono quelle che il file usa gia' in `EWR_MODELS` e `FIXED_SITE_MODELS`
(`Test_EWR_Data.py`); se una chiave scritta qui non coincide, l'esecutore usa quella del file e lo riferisce.

`Test/Test_Session_Simulator.py`, classe nuova **`TestDwellTimeSwitch(_Base)`** (2) (`_Base` esistente, `:160`):
1. `test_switch_off_passes_no_reader`: spia su `ER.resolve_engagement` (`patch.object(..., side_effect=...)` che
   chiama l'originale) in una sessione minima esistente (scelta all'esecutore fra quelle di `TestEndToEnd`):
   `'dwell_time_for' not in kwargs` di ogni chiamata.
2. `test_switch_on_passes_the_registry_reader`: con `patch.object(ER, 'D5_DWELL_TIME', True)`:
   `kwargs['dwell_time_for'] is ER.registry_dwell_time`.

Totale unitari blocco A: 6 + 11 + 4 + 2 + 2 = **25**; con i 6 di S32 (A.7) **31** test nuovi.

#### A.7 Scenario S32-DWELL: `Test/Test_Session_Scenarios_S32.py` (nuovo, 6 test)

Docstring di modulo nello stile di S31 (`Test_Session_Scenarios_S31.py:1-23`), con la tabella delle varianti di
§2.6 e la frase: "30 s e 600 s sono periodi di rivisita DICHIARATI DI TEST sulla ZSU-57-2, non dati: il visivo non
ha dati di scansione; il P-18 usa il dato di fonte del registro (6 s)".

Costruzione: riusare `Test_Session_Scenarios_S31.build('ZSU-57-2', 3_000.0)`; per le varianti EWR aggiungere alla
forza Red un `P-18-Terek` (costruire la forza con `F.build_force('Red-Line', 'Red', [...])` replicando le Unit di
S31 piu' `F.Unit('vehicle', 'P-18-Terek', 1, origin=(30_000.0, 0.0), prefix='ewr')`); dwell dichiarato con
`F.declare_dwell(red.assets['Red-Line/ad0'], {'air': <valore>})`. Missioni, ROE, bersaglio, durata, fire control e
soglie identici a S31 `run_variant`. L'interruttore con
`patch.object(sys.modules[ER.__name__], 'D5_DWELL_TIME', <bool>)` attorno all'intera esecuzione, i risultati
d'ingaggio catturati con la spia di S9 (`Test_Session_Scenarios.py:1235-1241`: `patch.object(ER,
'resolve_engagement', side_effect=spy)` che chiama l'originale e conserva l'`EngagementResult`).

```python
SEEDS = [f'S32-DWELL-{index}' for index in range(4)]
# variante -> (dwell dichiarato di test sulla ZSU [s] | None, interruttore D5_DWELL_TIME, con P-18)
VARIANT_SPEC = {
    'off': (None, False, False),
    'long': (30.0, True, False),
    'short': (600.0, True, False),
    'ewr_off': (None, False, True),
    'ewr_on': (None, True, True),
}
```

Ciclo esterno sui semi, interno sulle varianti (stesso `session_id` per le 5 varianti di un seme), come S31
(`setUpClass`, `Test_Session_Scenarios_S31.py:116-124`). Classe `TestS32DwellTime(F.LoggerSilencer, unittest.TestCase)`, test:
1. `test_premise_the_zsu_fires_with_the_previous_law`: in `off` la ZSU (`Red-Line/ad0`) spara in almeno un seme.
2. `test_long_dwell_reproduces_the_previous_law`: per ogni seme, `[(e.asset_id, e.weapon, e.rounds, e.time) for e
   in outcome.ammunition_events]` uguale fra `long` e `off`, e lo stesso per i `damage_events`
   (`(asset_id, time)` o i campi che l'esecutore trova nel tipo; scelta minore); le Detection della ZSU in `long`
   hanno `dwell_time_s == 30` ed `exposure_s >= 30`.
3. `test_short_dwell_never_adds_a_detection`: per ogni seme, nel **primo** `EngagementResult` catturato (primo
   episodio: stesse finestre e stesso stream nelle due varianti, quindi stessa estrazione per direzione),
   l'insieme `{(observer_id, target_id)}` delle Detection rilevate dalla ZSU in `short` e' sottoinsieme di quello
   in `off`. Gli episodi successivi possono avere finestre diverse (esiti diversi del primo): non si confrontano.
4. `test_short_dwell_reduces_the_aaa_detections`: totale sui 4 semi delle Detection rilevate dalla ZSU: `short` <
   `off` (stretto).
5. `test_short_dwell_probability_is_bounded_by_the_exposure`: ogni Detection della ZSU in `short` ha
   `dwell_time_s == 600`, `exposure_s < 600` e `probability <= exposure_s / 600 + 1e-12`; in `off` i due campi sono
   None.
6. `test_ewr_source_dwell_changes_nothing_at_medium_altitude`: per ogni seme eventi di munizioni uguali fra
   `ewr_on` e `ewr_off`; ogni Detection del P-18 (`Red-Line/ewr0`) in `ewr_on` ha `dwell_time_s == 6.0`,
   `exposure_s >= 6.0` e la stessa `probability` della Detection corrispondente in `ewr_off`.

**Valori attesi, misurati dalla sonda S-3** (§1.9; stessa legge e stessa permanenza, in memoria): esposizioni
della ZSU 62,7 / 64,7 / 66,0 / 66,7 s in ogni seme (stesse in `long` e `short`); Detection rilevate della ZSU
`off` / `short` = 4 / 0 nei semi 0-2 e 3 / 2 nel seme 3 (totale 15 / 2); colpi della ZSU `off` = 150 in ogni seme
(premessa del test 1 vera in tutti i semi); un solo episodio per variante e seme; esposizione minima del P-18 in
`ewr_on` 385,7 s, probabilita' uguale a `ewr_off`. Nessuno di questi numeri va scritto come asserzione esatta:
le asserzioni restano quelle dei test 1-6 (relazioni, non valori), che S-3 ha confermato tutte. I numeri servono
all'esecutore per riconoscere un'esecuzione anomala. Il P-18 ha dwell 6 s: la scelta DW-2 sull'AMES-Type-80 non
tocca S32-DWELL.

Se (2), (4) o (6) fallissero, l'esecutore **non** cambia i valori dichiarati ne' la geometria: si ferma e
riferisce i conteggi e le `exposure_s` osservate, confrontandoli con i valori di S-3 qui sopra.

#### A.8 `Test/Scenario_Baseline.py`: unita' in coda

In `UNITS` (`:258-388`), dopo S31-VISUAL (`:385-387`):

```python
    # ── S32 (D-5: Pd dipendente dalla permanenza nel volume, dwell_time_s) — in coda, nomi stabili ──
    ('S32-DWELL', 'Test_Session_Scenarios_S32', 'TestS32DwellTime', None,
     _by_occurrence('off', 'long', 'short', 'ewr_off', 'ewr_on')),
```

e nel docstring, dopo "Sensore visivo dopo la D-4c" (`:170-174`), la sezione:

```
## Permanenza nel volume dopo la D-5

La D-5 opzione 2 (`Engagement_Resolver.D5_DWELL_TIME`, SPENTO; `dwell_time_s` dei radar EWR,
`Proposta_Dwell_Time_Rilevamento.md`) non cambia le esecuzioni esistenti (interruttore spento; acceso, nessuno
scenario precedente usa un sensore con `dwell_time_s`). Aggiunge in coda l'unita' S32-DWELL (5 varianti, 4 seed):
20 esecuzioni nuove; nessuna voce nuova nel riassunto (i `Detection` non sono registrati).
```

#### A.9 Vincoli del blocco A

- **RNG**: nessuna estrazione nuova, nessuno spostamento; il codice D-5 sta **prima** di `self._draw()` in
  `_detect_direction` e non chiama `self.rng`. Vietato usare `random` di modulo.
- **Interruttore**: `D5_DWELL_TIME = False`, letto a ogni chiamata (globale di modulo, sostituibile nei test con
  `patch.object`).
- **Nomi stabili**: unita' `S32-DWELL`, varianti `off`, `long`, `short`, `ewr_off`, `ewr_on`, semi `S32-DWELL-0..3`,
  asset `Red-Line/ad0` (ZSU), `Red-Line/ewr0` (P-18), `Blue-CAS/cas0..3`. Nessun nome esistente cambia.
- **Costanti**: nessuna costante stimata nuova nel motore. I `dwell_time_s` sono dati di fonte convertiti (D) con
  una regola dichiarata [S] (DW-2); il valore dell'AMES-Type-80 (15 s) e' in piu' un'interpretazione [S] della
  fonte, da dichiarare nel commento del record (testo di A.1) e nel rapporto; 30 s e 600 s sono dichiarazioni di
  test, commentate come tali.
- **DW-9**: `dwell_time_s` **solo** nei 10 record EWR di A.1. Nessun valore in record di SAM, AAA, aerei, navi, ne'
  in dizionari `TVD`/`visual`, nemmeno se l'esecutore trovasse dati in altri documenti (es.
  `Ricerca_Dwell_Sensori_2026_11_06.md`, che non e' un ingresso di questo piano).
- **Core indifferente al simulatore**: nessun import dall'adapter DCS; i lettori stanno in `Mobile` e nel
  risolutore.
- **Import** con il percorso completo.

#### A.10 Esito atteso del blocco A

- Suite: `Ran 4788 tests` (4757 + 31), `OK (skipped=7)` [base verificata: ultima suite `Ran 4757 tests`,
  `OK (skipped=7)`, in `.ai-run/suite.log` del 2026-11-05]. Il valore 15 s dell'AMES-Type-80 entra solo come
  `subTest` di `TestEWRDwellTime.test_source_dwell_values`: il numero dei test non cambia.
- Confronto con la fotografia: **1009 identiche, 0 cambiate, 20 nuove** (`S32-DWELL/S32-DWELL-<k>/<variante>`).
  Le 1009 restano identiche perche' l'interruttore e' spento (nessun `dwell_time_for` passato); restano identiche
  anche con l'interruttore acceso (sonda S-1; vale anche con l'AMES-Type-80 a 15 s, perche' nessuno scenario usa
  un EWR). Le 20 nuove non dipendono dall'AMES-Type-80 (il P-18 di S32 ha 6 s). Fra le nuove, per costruzione e
  come misurato da S-3: `long` = `off` e `ewr_on` = `ewr_off` nel contenuto (chiavi diverse).

### Blocco B — pianificatore coerente (P1)

#### B.1 `Logic/Air_Route_Manager.py`

1. **`DetectionThreat.__init__`** (`:302-307`): parametro in coda `dwell_time_s: Optional[float] = None`, salvato
   come `self.dwell_time_s = float(dwell_time_s) if dwell_time_s else None`. Docstring (`:294-300`): voce
   `dwell_time_s: periodo di rivisita [s] del sensore (D-5), None = non dichiarato`. `__repr__`/`__str__` invariati.
2. **`build_detection_threat`** (`:732-787`): dopo la scelta di `sensor` (`:780`):
   `dwell = asset.sensor_dwell_time(sensor) if callable(getattr(asset, 'sensor_dwell_time', None)) else None`,
   passato come `dwell_time_s=dwell`. Docstring: il dwell e' quello del sensore scelto qui (raggio effettivo),
   che puo' differire da quello del DES (portata nominale) solo se un TVD supera il radar dopo l'orizzonte (§5.2).
3. **`Path.compute_detection_metrics`** (`:1081-1150`):
   - importare il modulo localmente (`from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER`)
     accanto all'import esistente di `detection_probability` (`:1103`) e leggere `ER.D5_DWELL_TIME` una volta;
   - durante il ciclo esistente, tenere in una lista locale parallela `owners` l'indice della minaccia di ogni
     tratto (non nel dizionario);
   - dopo il ciclo, raggruppare per minaccia i tratti **contigui** (`entry_s` del successivo - `exit_s` del
     precedente <= `CROSSING_JOIN_TOLERANCE_S`, costante di modulo nuova `= 1e-6`, tolleranza numerica, non una
     stima di modello) in un **attraversamento**: `exposure = exit_s ultimo - entry_s primo`,
     `d_min = min(min_distance)`;
   - ogni tratto riceve due chiavi nuove: `'crossing_exposure_s'` (sempre) e `'dwell_time_s'` (quello della
     minaccia, None se assente);
   - **solo** con `ER.D5_DWELL_TIME` acceso **e** `dwell_time_s` della minaccia non None: la
     `'detection_probability'` di ogni tratto dell'attraversamento diventa
     `detection_probability(d_min, R, ER.dwell_factor(exposure, dwell))`; altrimenti resta quella di oggi per
     tratto (identica);
   - `max_detection_probability` = massimo delle `'detection_probability'` finali; `detection_exposure_s`,
     `first_detection_time_s`, `warning_time_s` invariati.
   - Docstring: il paragrafo "nessuna modifica al risolutore" (`:1091-1098`) diventa "stessa legge del DES,
     compresa la permanenza D-5 con l'interruttore acceso; un attraversamento che si estende su piu' edge e' una
     sola permanenza, come una finestra del DES".
4. `ThreatMode`, `calcRoute`, `best_path_key`, la ricerca: **invariati**. Una frase nel docstring di
   `ThreatMode.AVOID_DETECTION` (`:44-50`): "Con la D-5 la Pd di un attraversamento dipende anche dalla
   permanenza (metrica), ma la modalita' resta aggiramento puro (Proposta_Dwell_Time_Rilevamento.md DW-7)".
5. `Weapon_Delivery._evaluate_exposure` (`:433-460`): **non** si tocca (esposizione deterministica dall'ingresso,
   gia' dichiarata come stima di pianificazione).

#### B.2 Test del blocco B (7)

`Test/Test_Air_Route_Manager.py`, classe nuova **`TestDetectionMetricsWithDwell`** (5), helper locale come
`_detection` di `:1769-1772` con `dwell_time_s`:
1. `test_switch_off_metrics_are_unchanged`: minaccia con `dwell_time_s=100`, edge che la attraversa in 5 s:
   `max_detection_probability == detection_probability(d_min, R)` come oggi.
2. `test_crossing_split_over_two_edges_is_one_exposure`: due edge consecutivi dentro lo stesso cilindro:
   `crossing_exposure_s` uguale nei due tratti e pari alla somma delle durate; con l'interruttore acceso, stessa
   `'detection_probability'` nei due tratti.
3. `test_short_crossing_reduces_the_probability`: interruttore acceso, permanenza 5 s, dwell 20 s:
   `max_detection_probability == detection_probability(d_min, R, 0.25)` (places=9).
4. `test_long_crossing_keeps_the_previous_probability`: permanenza >= dwell -> uguale allo stato spento.
5. `test_threat_without_dwell_is_unchanged_with_the_switch_on`: `dwell_time_s=None` -> uguale allo stato spento.

`Test/Test_Threat_AA_Factory.py`, classe esistente **`TestBuildDetectionThreat`** (`:389`), 2 test nuovi:
6. `test_ewr_detection_threat_carries_the_dwell`: P-18-Terek a quota di rotta 10 000 m -> `dwell_time_s == 6.0`.
7. `test_sensor_without_dwell_gives_none`: 9K331-Tor -> `dwell_time_s is None`.

#### B.3 Esito atteso del blocco B

Suite `Ran 4795 tests`, `OK (skipped=7)`; confronto **1009 identiche + 20 nuove** (le stesse del blocco A: il
pianificatore non entra in nessuna sessione della fotografia).

### Blocco C — attraversamento a corda limitata del rilevamento (RIMANDATO, DW-7: NON eseguire)

Descritto solo come riferimento per un piano futuro; l'esecutore dei blocchi A e B non lo implementa.

1. `calcRoute(..., detection_pd_max: Optional[float] = None)` (`:1309`): valido in (0, 1], altrimenti
   `ValueError`. Con `mode == AVOID_DETECTION`, `detection_pd_max` non None **e** `ER.D5_DWELL_TIME` acceso, a ogni
   copia profonda di `detections` (`:1349`, le copie sono locali alla chiamata) si assegna l'attributo
   `max_crossing_pd = detection_pd_max`; altrimenti nulla (ricerca identica).
2. Metodo nuovo `_detection_crossable(self, edge, threat, aircraft_speed) -> bool`: True solo se `threat` e' un
   `DetectionThreat` con `dwell_time_s` e `max_crossing_pd`, l'intersezione con l'edge e' **completa** (due punti
   sulla superficie laterale, come `firstThreatIntersected`), e
   `detection_probability(d_min, acquisition_range, dwell_factor(L / aircraft_speed, dwell_time_s)) <=
   max_crossing_pd`, con `L` la lunghezza dell'intersezione e `d_min` la distanza minima dal sito sul tratto
   (`_min_distance_to_site`).
3. In `calcPathWithoutThreat` (`:1748`), dopo `firstThreatIntersected`: finche' la minaccia trovata e'
   attraversabile, la si salta per questo edge (`firstThreatIntersected(edge, [t for t in threats if t not in
   saltate])`); il resto invariato (il controllo `cross_threats` dei volumi d'intercettazione resta, `:1755-1765`).
   Nessuna corda accorciata con `find_chord_coordinates`: se l'intersezione non e' attraversabile si aggira come
   oggi.
4. `PathCollection.best_path_key` (`:1240-1248`): con `AVOID_DETECTION` e `detection_pd_max` non None la chiave
   diventa `(total_danger, total_length)` (i percorsi prodotti rispettano gia' la soglia per costruzione; con la
   chiave attuale vincerebbe sempre l'aggiramento, che ha meno esposizione). `get_best_path` riceve
   `detection_pd_max` come argomento keyword (default None = chiave attuale).
5. Test (6): soglia invalida -> `ValueError`; interruttore spento -> rotta identica a senza soglia; corda breve con
   dwell lungo -> rotta diritta attraverso il volume; corda lunga -> aggiramento come oggi; volume di
   intercettazione sulla corda di rilevamento -> attraversato solo con la sua corda (rilevamento !=
   intercettazione); chiave di scelta con soglia -> il percorso piu' corto.
6. Esito: suite +6; fotografia invariata. Rischio: medio (ricerca ricorsiva, `Test_Air_Route_Manager` ampio).

---

## 5. Rischi e limiti

### 5.1 Valori deboli che entrano nel codice

- I 10 `dwell_time_s` sono **dati di fonte** di confidenza media (55Zh6 media-bassa), con una **regola di progetto**
  [S] sugli intervalli (DW-2: regime normale se citato, altrimenti rotazione piu' veloce). Il P-12 ha una
  contraddizione di fonte (10 contro 2-6 giri/min). L'AMES-Type-80 (15 s) poggia in piu' su un'**interpretazione**
  [S] della fonte ("4 (fino a 6)" letto come regime normale 4): con la lettura "piu' veloce" sarebbe 10 s.
- La **forma** L1 e' una scelta di progetto [S] con giustificazione geometrica [I], non tarata; non modella la
  conferma M su N (assorbita nella RIV, dichiarato).
- Nessuna costante stimata nuova nel motore; `CROSSING_JOIN_TOLERANCE_S` (blocco B) e' una tolleranza numerica.
- Valori di test di S32 (30 s, 600 s): dichiarati di test, mai nei registri.
- **Dati mancanti per i tiratori (DW-9)**: SAM, AAA, radar d'aereo, navi, TVD e vista non hanno `dwell_time_s`.
  Finche' mancano, la legge non agisce su nessun tiratore, quindi non cambia nessun esito di tiro dei registri; e'
  la scelta voluta (nessun valore senza fonte), ma significa che la D-5 oggi non produce effetti visibili nelle
  sessioni della fotografia. Quando i dati arriveranno (ricerca in corso), estenderli a SAM e AAA **cambiera' la
  fotografia con l'interruttore acceso** (S-2: gia' 10 s a tutti cambiano 2 esecuzioni su 1009; S-1: 17, 45, 464
  rilevamenti persi su 29 483 a 30, 60, 120 s) e il confronto andra' riletto; con l'interruttore spento resta
  identica.

### 5.2 Limiti di modello (da dichiarare nel manuale)

- **La legge non accorcia le rotte contro gli EWR** (§1.8), rischio principale e invariato dopo le decisioni: con
  periodi di 6-60 s la corda a Pd ridotta e' di pochi km (al piu' 3,75 km a 250 m/s per i periodi fino a 15 s).
  L'effetto "volo basso non visto" richiede l'orizzonte nel DES, assente (attivita' separata, DW-7).
- **Solo riduzione**: per permanenze lunghe la Pd resta quella della distanza minima (nessun cumulo di scansioni).
- **Sensore unico per asset**: la permanenza e' quella del sensore che da' la portata massima; un secondo sensore
  piu' corto senza dwell non entra.
- **Permanenza sui tratti, non sullo stato**: l'intervallo che precede l'inizio della finestra conta anche se in
  quella parte l'osservatore o il bersaglio erano a terra (finestre spezzate al decollo): spinge verso la legge
  attuale (conservativo).
- **Nessun dwell sul tracciamento dei colpi** (regola R-INT, `_round_track_time`, `Engagement_Resolver.py:3069`):
  l'intercettore scopre un colpo all'ingresso nella sua portata, come oggi.
- **Fixture**: `declare_sensor` non dichiara una permanenza; un modo dichiarato di test legge il dwell del
  registro (oggi sempre None fuori dagli EWR).
- **Pianificatore**: il dwell della `DetectionThreat` e' quello del sensore col raggio effettivo maggiore, il DES
  usa quello con la portata nominale maggiore: divergono solo se un TVD supera un radar dopo l'orizzonte (nessun
  EWR ha TVD).
- **Copertura angolare, notte unica, nessun orizzonte**: invariati.
- **Permanenza sommata su piu' passaggi** (trovato il 2026-11-06): se il bersaglio esce e rientra nel volume
  dell'osservatore con la portata minore dentro la stessa finestra, `_exposure_time` somma i passaggi, contro la regola
  dell'utente (un'occasione per passaggio, mai la somma). Il limite di fondo (una sola estrazione per finestra) e'
  precedente alla D-5. Piano in `Proposta_Finestre_Per_Passaggio_Portata_Propria.md` (FP-6: con FP spento il solo
  passaggio che contiene il CPA; con FP acceso un'estrazione e una permanenza per passaggio).

### 5.3 Rischi di esecuzione

- Toccare `_detect_direction` e' il punto piu' delicato del motore: il test A.6-4 (conteggio e ordine delle
  estrazioni) e il confronto con la fotografia sono la rete. Il confronto deve dare **0 cambiate**: una sola
  esecuzione cambiata con l'interruttore spento e' un errore d'implementazione, non un effetto atteso.
- `Test_Session_Scenarios_S32` aggiunge 20 sessioni (~1 minuto di suite in piu' [I], come S31).
- Firma del lettore `(observer, target, mode)`: diversa da `detection_factor` `(observer, target)` per il modo del
  bersaglio a terra; dichiarata nella docstring.
- Le sonde S-2 e S-3 sono state eseguite con lo script di sonda, non con il codice che scrivera' l'esecutore: se
  la permanenza implementata differisse da quella di §2.4, i valori di S-3 citati in §4.A.7 non si
  riprodurrebbero (segnale utile, non motivo per cambiare i test).
- Script di sonda `probe_dwell.py`: difetto noto nel salvataggio di `stats.json` con la modalita' `uniform`
  (chiave `None`, §1.9); riguarda solo le sonde, non il repository ne' questo piano.

---

## Documenti da aggiornare dopo (non scritti qui)

- **Manuale DES** (`des-manual-writer`): cap. 4 §4.2 (legge di Pd con la permanenza, interruttore, invarianza
  dell'RNG) e §4.1 (catena); cap. 3 §3.5 (lo scheduler non cambia; la permanenza la calcola il risolutore); cap. 7
  §7.4 (fattori e permanenza) e §7.8 (metriche del pianificatore, `DetectionThreat.dwell_time_s`); cap. 8 nuovo
  §8.14 S32-DWELL; cap. 9 §9.1 (limiti di §5.2; voce "Attraversamento a corda limitata (D-5 opzione 2) non
  implementato" sostituita da "legge D-5 fatta dietro `D5_DWELL_TIME`; corda limitata nel pianificatore rimandata,
  DW-7"); atlante `11a_Atlante_Risolutore.md` (costante `D5_DWELL_TIME`, funzioni `dwell_factor` e
  `registry_dwell_time`, sequenza di `_detect_direction`).
  Nel cap. 9 anche il limite DW-9 (meccanismo generico, valori ai soli EWR, nessun tiratore con dwell) e la
  regola DW-2 con l'interpretazione [S] dell'AMES-Type-80.
- **`F4_Differenze_Scenari.md`**: sezione "D-5 — permanenza nel volume (2026-11-xx)": il cambio, 1009 identiche, 20
  nuove di S32-DWELL, esiti delle sonde S-1 (interruttore acceso, 1009 identiche) e S-2 (sensibilita': 10 s a ogni
  osservatore cambiano 2 esecuzioni di S21), valori di fonte e regola DW-2, limiti, DW-9.
- **`Piano_Implementazione_Missione.md`**: riga in §5 "D-5 (Pd con permanenza)" fuori dalla numerazione F, come
  D-4b/D-4c; stato dell'interruttore; DW-9 (valori ad altri sensori in attesa di fonte).
- **`Proposta_Volumi_Rilevamento_Intercettazione.md`** §9 D-5: riga di stato aggiornata il 2026-11-06 (Proposta
  definitiva); a lavoro fatto, l'esito.
- **`Rapporti/Sonde_Dwell_D5/LEGGIMI.md`** (sessione principale): descrive ancora S-2 come incompleta e S-3 come mai
  eseguita; da allineare a §1.9 ed eventualmente copiare li' i log di S-2 e S-3 (oggi solo in `.ai-run/`).
- **Memoria** (solo la sessione principale): voce sulla D-5 (decisioni DW-1..DW-9, interruttore, finding della
  corda, esiti S-2 e S-3).

## Estensioni future (fuori da questo piano)

- **Valori per altre classi di sensori (DW-9)**: quando la ricerca per classe di sensore
  (`Ricerca_Dwell_Sensori_2026_11_06.md`, in preparazione) sara' completa e approvata, l'estensione e' **solo un
  dato**, senza cambi di codice: aggiungere la chiave `dwell_time_s` [s] al dizionario del sensore (`radar`, `TVD`
  o `visual`) nei record interessati di `Vehicle_Data`, `Ship_Data` o `Aircraft_Data`, con commento F/D/S e fonte
  come in A.1, e un test del valore nel file di test del registro. Poi: suite (con l'interruttore spento la
  fotografia resta identica) e un confronto con l'interruttore **acceso** (sonda tipo S-1 con i nuovi valori), da
  rileggere esecuzione per esecuzione prima di decidere l'accensione. Test da adeguare in quel momento: quelli che
  usano un record come esempio "senza dwell" (`Test_Mobile.TestDetectionDwellTime.test_records_without_dwell_give_none`
  e `Test_Threat_AA_Factory` B.2-7 usano il 9K331-Tor; `Test_EWR_Data` test 2 i 5 EWR senza dato): falliranno se
  quel record riceve un valore, ed e' il segnale voluto.
- **Accensione di `D5_DWELL_TIME`** (DW-5): dopo la verifica dei blocchi A e B; con i soli dati EWR non cambia la
  fotografia (S-1).
- **Blocco C e orizzonte radar nel DES** (DW-7): attivita' separate, da pianificare.

## Scelte minori lasciate all'esecutore (da elencare nel rapporto)

- Nomi delle variabili locali, ordine dei metodi nuovi dentro la classe, testo dei messaggi d'errore e di log.
- Il modello con radar e TVD per il test A.6 `Test_Mobile` 3 e il modo di sostituire in memoria il dizionario.
- La sessione minima di `Test_Session_Simulator` per i 2 test dell'interruttore.
- I campi confrontati negli eventi di danno del test S32 2 (purche' ne confronti l'istante e l'asset).
- La struttura interna di `Test_Session_Scenarios_S32.py` (riuso di funzioni di S31 o copia locale di `build`).
- La data nei titoli `2026-11-xx` (docstring del risolutore, A.3 punto 8): quella del commit del blocco A.
