# Proposta: ricalibrazione della Pd sul bordo della portata (PB)

**Stato: BOZZA PER LE DECISIONI DELL'UTENTE (PB-1..PB-6 aperte, §3).** Scritta il 2026-11-19 da `des-planner` sul
ProArt, codice letto al commit `068d7b75`. Dopo le decisioni il piano di §4 e' un contratto completo per l'esecutore
(`des-developer` o `oc-developer`): nessuna scelta di design resta all'esecutore.

**Origine.** Osservazione dell'utente del 2026-11-19 su `S36-GRAZE-0/band_max` (ZSU-57-2, vista 6 km, A-10C `casD0`
con CPA 5979 m, `Pd = 0,507`): la Pd al bordo della portata, oggi **0,5**, gli sembra **alta**; valori attesi
**0,1-0,3**. La costante e' una **stima** dichiarata, senza fonte (§1.4).

**Convenzioni.** **[V]** = verificato leggendo il codice (`file:riga`) o eseguendolo; **[C]** = calcolo mostrato;
**[I]** = ipotesi o conoscenza generale non verificata nel repository; **[S]** = stima o scelta di progetto, mai dato
tarato. Percorsi di codice relativi a `Code/Dynamic_War_Manager/Source/`. Le decisioni dell'utente sono numerate
**PB-1, PB-2, ...** ("PB" = **P**d al **B**ordo). Le sonde di questo documento sono numerate **Q-1, Q-2, ...**.

**Sigle usate.**

| Sigla           | Significato                                                                                                      |
| --------------- | ---------------------------------------------------------------------------------------------------------------- |
| Pd              | probabilita' di rilevamento (*probability of detection*): probabilita' che un sensore "veda" il bersaglio        |
| R               | portata del sensore letta dal registro (`acquisition_range`), in metri nel motore                                |
| d, CPA          | distanza al massimo avvicinamento (*Closest Point of Approach*) fra osservatore e bersaglio                      |
| p               | la costante "Pd sul bordo": il valore della legge a d = R (oggi 0,5)                                             |
| RCS             | *Radar Cross Section*, superficie equivalente radar del bersaglio [m^2]: quanto "si vede" al radar               |
| D-5, g          | legge di permanenza: `g = min(1, permanenza / dwell)`, moltiplica la Pd (`D5_DWELL_TIME`, acceso dal 2026-11-18) |
| dwell           | periodo di rivisita del sensore (`dwell_time_s` nel registro), DW-9                                              |
| FP              | rilevamento per passaggio: un'estrazione per ogni passaggio del bersaglio nel volume proprio                     |
| fotografia      | `Test/baseline/scenario_baseline.json`: gli esiti registrati delle esecuzioni di scenario; oggi 1103 installate  |
| cattura da 1219 | `.ai-run/confronto_capture.json` (2026-11-18): le 1103 + le 116 nuove di S36, **non installata**                 |
| Koopman         | teoria della ricerca: probabilita' cumulata su piu' "sguardi" (scansioni); rinvio dichiarato nel manuale         |

**Nessun file di codice o di test e' modificato da questo documento.** Le sonde Q-1..Q-3 (§1.7) sono script di sola
lettura nella cartella temporanea della sessione: cambiano la costante **in memoria** e rieseguono l'intera cattura,
confrontandola con la cattura da 1219; nessuna fotografia e' toccata.

---

## 0. Sintesi

**Che cosa c'e' oggi.** Una sola costante, `PD_AT_ACQUISITION_RANGE = 0.5` (`Logic/Engagement_Resolver.py:556`),
fissa la Pd di **ogni** sensore (radar, TVD, vista) quando il bersaglio passa esattamente sul bordo della portata:

    Pd(d) = factor * (1 - (1 - p) * (d / R)^4)   per d <= R;   0 per d > R          (p = 0,5)

Il commento la dichiara stima ("la piu' prudente fra le convenzioni Pd 0,5 e 0,9, da ricalibrare"), ma **nessuna
fonte** di quella convenzione e' stata trovata (bibliografia della guida, sezione "non verificate").

**Che cosa cambia con una p piu' bassa.** Due effetti, entrambi dentro la stessa estrazione (nessuna estrazione in
piu' ne' spostata, §1.3): (1) **meno rilevamenti** per i passaggi lontani dall'osservatore (a d = 0,9 R la Pd scende
da 0,672 a 0,475 con p = 0,2); (2) **rilevamenti piu' tardi** anche quando avvengono: oggi meta' delle estrazioni
(quelle sotto 0,5) danno il rilevamento all'ingresso nella portata, con p = 0,2 solo un quinto. Il secondo effetto
tocca quasi ogni ingaggio: con p = 0,2 cambiano **636 delle 1103** esecuzioni fotografate e **tutte le 116 di S36**
(sonda Q-1, §1.7); con 0,3 e 0,1 cambiano 582 e 678 delle 1103.

**Raccomandazione (PB-1).** Ipotesi **(a)**, costante unica ricalibrata a **0,2 [S]** (PB-2), dietro un interruttore
nuovo `Engagement_Resolver.PD_EDGE_RECALIBRATION`, **spento di default** (fotografia invariata). Le ipotesi (b)
(costante per sensore) e (c) (sezione radar del bersaglio) moltiplicano numeri inventati senza un dato a cui
ancorarli; (c) richiede inoltre dati RCS che il repository non ha e un cambio dello scheduler; si rinviano, (c) insieme
alla legge cumulativa (Koopman) e all'orizzonte radar. (a) e' un sottoinsieme di (b): se in futuro arriva un dato per
sensore, la costante unica resta il valore di ripiego.

**Dimensione dell'intervento (opzione raccomandata).** Piccola nel codice: 2 costanti, 1 funzione d'accesso, 2
funzioni toccate (6 righe) in `Logic/Engagement_Resolver.py`, docstring; 12 test nuovi, 7 test esistenti riscritti
per leggere la legge in vigore invece del numero 0,5 (nessun cambio di esito a interruttore spento) e alcuni
docstring. All'accensione (blocco 3, solo su decisione dell'utente): una riga di default, un test invertito, 3 file di
test ritoccati (PB-6). Grande nell'effetto: la lettura delle esecuzioni cambiate e la fotografia nuova sono il lavoro
vero, e li decide l'utente (blocchi 2-3).

---

## 1. Problema e comportamento attuale

### 1.1 La legge e la costante [V]

- `PD_AT_ACQUISITION_RANGE = 0.5` (`Logic/Engagement_Resolver.py:553-556`), commento: "STIMA DICHIARATA: delle due
  convenzioni con cui si dichiara la portata di un radar (Pd 0.5 o 0.9 a quella distanza) si adotta la piu' prudente.
  Da ricalibrare." `PD_RANGE_EXPONENT = 4` (`:558-561`): la forma R^4 viene dall'equazione radar, la curva vera
  (Swerling) e' una sigmoide; questa e' una semplificazione monotona.
- `detection_probability(distance, sensor_range, factor=1.0)` (`:1225-1252`): la legge sopra; `factor` in [0, 1] e'
  la degradazione del chiamante (meteo, notte, nebbia di guerra, permanenza D-5).
- `detection_radius(draw, sensor_range, factor=1.0)` (`:1255-1284`): l'inversa. Un'estrazione `draw` rileva a
  distanza R se `draw < factor * p` (`:1279-1280`), altrimenti al raggio
  `R * ((1 - draw/factor) / (1 - p))^(1/4)` (`:1282-1284`); None se `draw >= factor`.
- `weather_detection_factor` (`:1375-1422`) produce il `factor` meteo/notte (0,7 notte, 0,8 maltempo, stime): **non
  dipende da p** e non cambia con questa Proposta; il suo limite "fattore unico per ogni sensore" (`:1387-1392`) e' lo
  stesso problema di fondo dell'ipotesi (b): il risolutore non sa quale sensore ha prodotto la portata.

### 1.2 Tutti gli usi della Pd [V]

| Chiamante | Riga | Che cosa fa con p |
|---|---|---|
| `_EngagementRun._detect_direction` (estrazione unica o un solo passaggio) | `Logic/Engagement_Resolver.py:2364-2371` | `draw` estratto **prima**, poi `probability = detection_probability(...)`, `detected = draw < probability`, raggio con `detection_radius` -> istante del rilevamento |
| `_EngagementRun._detect_passes` (FP, >= 2 passaggi) | `:2585-2593` | stesso schema per ogni passaggio; il primo estrae dallo stream dell'ingaggio, gli altri da `pass_rng` |
| D-5 (`dwell_factor`) | `:2360-2362`, `:2579-2583` | moltiplica il `factor`: `Pd = g * Pd(d)`; con p diversa cambia `Pd(d)`, non `g` |
| Metrica del pianificatore `Path.compute_detection_metrics` | `Logic/Air_Route_Manager.py:1129-1207` | chiama `detection_probability(min_distance, sensor_range)` (e con D-5 e dwell, `detection_probability(d_min, R, dwell_factor(...))`): **segue la costante del modulo** |
| Consumatori di `max_detection_probability` / `detection_metrics` | `Logic/Air_Route_Manager.py:1207-1239` | **solo** dizionario di metriche sul percorso e sulla rotta; nessun altro modulo li legge (ricerca `detection_metrics|max_detection_probability|warning_time_s` fuori da `Air_Route_Manager.py`: zero usi di produzione) [V] |
| `Session_Simulator.engage` | `Logic/Session_Simulator.py:2792-2794` | passa solo `dwell_time_for`; la costante e' letta dentro il risolutore |
| Test che usano la legge | v. §4.4 | `Test_Engagement_Resolver.py:131-186`, `:240`, `:1030`; `Test_Air_Route_Manager.py:1955`, `:1965`, `:2043-2082`; `Test_Threat_AA_Factory.py:607-628`; `Test_Session_Scenarios.py:1394`; `Test_Session_Scenarios_S36.py:116-126`, `:823` |

Nessun altro punto del repository legge `PD_AT_ACQUISITION_RANGE` (ricerca su tutto `Source/`: solo
`Engagement_Resolver.py` e i test sopra) [V]. Nessuna dipendenza dall'adapter DCS.

### 1.3 Ordine delle estrazioni: invariato per costruzione [V]

In entrambe le funzioni di rilevamento l'estrazione avviene **prima** e **sempre**, indipendentemente dalla Pd
(`draw = self._draw()` a `:2364`; `draw = self._draw() if index == 0 else self._draw(self.pass_rng)` a `:2585`); la Pd
decide solo l'esito e il raggio. Quindi cambiare p **non aggiunge, toglie ne' sposta estrazioni di rilevamento**.
Cambiano invece, **come conseguenza** degli esiti, le estrazioni a valle (salve, danni, intercettazioni): un
rilevamento perso o ritardato cambia i candidati al tiro e quindi le estrazioni successive dello stesso stream. E' lo
stesso meccanismo di ogni cambio di Pd (meteo, D-5) e non e' una regola nuova sull'RNG.

### 1.4 Il dato non c'e': che cosa significa p [V per i documenti, I per l'interpretazione]

- **Nessuna fonte** della convenzione "portata dichiarata a Pd 0,5 o 0,9": `Manuale_Motore_DES/Guida_Concettuale_
  DES_Bibliografia.md`, nota di §5 (righe 341-349) e tabella "non verificate" (riga 567: "Nessuna fonte specifica
  trovata"). Il manuale (capitolo 9 §9.1, `10_Limiti_Estensioni_Divergenze.md:406`) la registra come stima da
  ricalibrare, giudicata alta dall'utente.
- **Non si sa a che cosa corrisponda la portata R dei registri** (portata "nominale" a una Pd data per un bersaglio
  di riferimento, o portata "massima"): i record non lo dicono (es. Buk `acquisition_range` 85 km,
  `Asset/Vehicle_Data.py`, record `9K37-Buk`) [V]. Le due letture portano a p diverse [I]:
  - se R e' la **portata massima**, al bordo la Pd deve tendere a 0 (p piccola);
  - se R e' la **portata nominale** (Pd p per un bersaglio di riferimento), il sensore vedrebbe anche oltre R con Pd
    minore; ma il DES **taglia a R** (Pd = 0 oltre, `:1247-1248`; le finestre dello scheduler sono costruite su R).
- **Il taglio a R crea un salto**: la legge con p arriva a zero solo a `R * (1/(1-p))^(1/4)` [C]: 1,189 R con p = 0,5;
  1,057 R con p = 0,2; 1,027 R con p = 0,1. Con p = 0,5 la Pd salta da 0,5 a 0 sul bordo; con p piu' bassa il salto si
  riduce. **Una p bassa e' piu' coerente con il taglio a R che il motore gia' fa** (argomento di forma, non un dato).
- **Interazione con la D-5** [V per la legge, I per la lettura]: per i sensori con dwell la Pd e' `g * Pd(d)`; un
  passaggio radente dura poco e ha `g < 1`. Si puo' leggere `g` come "probabilita' che una scansione cada nella
  permanenza" e `Pd(d)` come "Pd di una scansione a distanza d": con questa lettura p e' la Pd **per scansione** al
  bordo e la convenzione 0,5 sarebbe sostenibile per i radar. Ma per i sensori **senza dwell** (aerei non AWACS,
  sensori dichiarati di test, `g = 1` sempre) la stessa p vale come Pd **dell'intero passaggio** radente: qui 0,5 e'
  alta. Il caso dell'utente (`casD0`) ha `g = 1` (permanenza 6,4 s > dwell 6 s): p entra pura. Una costante unica non
  distingue i due significati (§5, rischio R-3).

### 1.5 Tabella della legge per i valori candidati [C]

Pd senza degradazione (`factor = 1`) in funzione di d/R; ultime colonne: distanza alla quale la legge si annulla, Pd
media su CPA uniformi in [0, R] (`1 - (1-p)/5`), raggio medio di rilevamento per un bersaglio che passa sopra
l'osservatore (`0,8 + 0,2 p`, estrazione uniforme).

| p | 0,5 R | 0,7 R | 0,8 R | 0,9 R | 0,95 R | R | zero della legge | Pd media | raggio medio |
|---|---|---|---|---|---|---|---|---|---|
| **0,5 (oggi)** | 0,969 | 0,880 | 0,795 | 0,672 | 0,593 | 0,500 | 1,189 R | 0,900 | 0,900 R |
| 0,3 | 0,956 | 0,832 | 0,713 | 0,541 | 0,430 | 0,300 | 1,093 R | 0,860 | 0,860 R |
| **0,2 (raccomandata)** | 0,950 | 0,808 | 0,672 | 0,475 | 0,348 | 0,200 | 1,057 R | 0,840 | 0,840 R |
| 0,1 | 0,944 | 0,784 | 0,631 | 0,410 | 0,267 | 0,100 | 1,027 R | 0,820 | 0,820 R |
| 0 (limite) | 0,938 | 0,760 | 0,590 | 0,344 | 0,185 | 0 | R | 0,800 | 0,800 R |

Letture: vicino all'osservatore (d <= 0,5 R) la Pd quasi non cambia; il calo si concentra nell'ultimo 30 % della
portata. In media sui CPA il calo dei rilevamenti e' modesto (0,90 -> 0,84 con p = 0,2), ma **il raggio di
rilevamento si accorcia** in media del 6,7 % (0,90 R -> 0,84 R): contro un Buk (R = 85 km) e un bersaglio a 250 m/s,
~20 s di preavviso in meno in media [C].

### 1.6 Che cosa c'e' nei registri per le ipotesi (b) e (c) [V]

- **Sensori con portata aria nei registri** (conteggio in memoria): veicoli 24 radar, 4 TVD, 2 vista; navi 22 radar;
  aerei 33 radar, 14 TVD (piu' le portate terra/mare). Chiavi presenti nei dizionari sensore oltre a `model`,
  `capabilities`, `reliability`: `dwell_time_s`, `search_model`, `antenna_height`, `acquisition_profile`, `type`
  (aerei). **Nessuna chiave di Pd, nessuna RCS di riferimento.**
- **RCS dei bersagli: nessun campo in nessun registro** (ricerca `rcs|radar_cross|cross_section`: zero in `Asset/`,
  gia' rilevato da `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` §1.5 e `Proposta_Dati_Bersagli_Intercettabili.md`
  riga 132: "nessuna fonte, per nessuna delle 52 voci, pubblica un valore numerico").
- **Quale sensore produce la portata**: `Mobile.detection_range(mode)` restituisce il massimo fra radar, TVD e vista
  (`Asset/Mobile.py:1592-1674`) senza dire quale; `Mobile.detection_dwell_time(mode)` gia' ricalcola il sensore
  vincente (`:1692-1736`) e ne legge il dato: e' il modello per un lettore per sensore (ipotesi b).
- **Molti scenari usano sensori dichiarati di test** (`Test/Scenario_Fixtures.py:270-302`, `declare_sensor`): la
  portata e' un numero sull'istanza, il tipo di sensore non esiste. Per loro (b) e (c) ricadrebbero comunque sulla
  costante unica.
- **Aggancio gia' presente per un fattore dipendente dal bersaglio**: `resolve_engagement(detection_factor=...)`
  (S3, `Test_Session_Scenarios.py:274-391`, usa uno `STEALTH_FACTOR = 0.15` dichiarato di scenario). E' la forma
  "povera" di (c): un fattore moltiplicativo, non una portata efficace.

### 1.7 Sonde eseguite per questa Proposta (Q-1..Q-4, sola lettura)

Eseguite il 2026-11-19 sul ProArt, interprete `.direnv/python-3.12/bin/python3`, codice al commit `068d7b75`.
Script temporanei nella cartella della sessione (non nel repository); la versione per il blocco 2 e' in Appendice A.

- **Q-0 (controllo dello strumento).** Con la costante lasciata a 0,5, unita' `S1`: 16 esecuzioni, **0 cambiate**
  rispetto alla cattura da 1219.
- **Q-1, Q-2, Q-3: cattura completa con `PD_AT_ACQUISITION_RANGE` sostituita in memoria** (0,2 / 0,3 / 0,1), una
  spia attorno a `resolve_engagement` che non estrae nulla, confronto esecuzione per esecuzione con
  `.ai-run/confronto_capture.json` (1219 esecuzioni, 0 errori di unita' in ogni passata, 0 nuove, 0 mancanti). La
  cattura di riferimento e' del 2026-11-18; dopo di essa il codice del motore e' cambiato solo nei docstring
  (`34c4cefd`, `8fa92710`, `03555c81`) [V: `git log --stat`].

| p | Cambiate (di cui delle 1103 / di S36) | Identiche | Esito di forza cambiato | Salve totali (oggi 28453) | Distruzioni (oggi 2142) | Intercettazioni (oggi 477) | Ingaggi (oggi 1456) |
|---|---|---|---|---|---|---|---|
| 0,3 (Q-2) | **698** (582 / 116) | 521 | 61 | 25184 (-11,5 %) | 2103 (-1,8 %) | 483 | 1460 |
| **0,2 (Q-1)** | **752** (636 / 116) | 467 | 84 | 24457 (-14,0 %) | 2105 (-1,7 %) | 431 | 1468 |
| 0,1 (Q-3) | **794** (678 / 116) | 425 | 98 | 23504 (-17,4 %) | 2082 (-2,8 %) | 426 | 1475 |

  Letture [V dalle sonde]:
  - **Gli insiemi sono annidati**: ogni esecuzione cambiata con 0,3 lo e' anche con 0,2, e ogni cambiata con 0,2 lo e'
    con 0,1. La scelta del valore cambia soprattutto *quante* esecuzioni si muovono; le famiglie toccate sono quasi le stesse
    (eccezioni sotto: `S22-AIR`, `S31-VISUAL`).
  - **Le 116 di S36 cambiano tutte con qualunque valore**: registrano la `Detection` con la sua `probability`, che
    cambia per ogni distanza > 0 (§1.5). Per le 1103, con 0,2 ne cambiano 636 (58 %).
  - **Famiglie mai toccate** (identiche con tutti e tre i valori): `ORC-fuel`, `ORC-nocontact`, `S24-GLIDE`,
    `S25-DUR`, `S25-POST`, `S25-WIN`, `S28-ROE`, `S28-ZONE`, `S29-AREA`, `S30-ABSENT`, `S30-CAMPAIGN`; `S31-VISUAL` e'
    identica con 0,3 e 0,2, cambia con 0,1; `S22-AIR` e' identica con 0,3 (3 su 40 cambiate con 0,2). La ragione per
    famiglia non e' indagata (presumibilmente nessun rilevamento nell'ultimo tratto della portata o esiti insensibili
    all'istante del rilevamento: **non verificato**).
  - **Famiglie cambiate per intero con 0,2** (25): `ORC-base`, `ORC-interval`, `ORC-seed`, `ORC-twofronts`, `S2`,
    `S3`, `S6`, `S7`, `S8`, `S11`-`S18`, `S20`, `S23-TOT`, `S27-DOUBLE` e le cinque `S36-*`. **In parte**: `S1` 14/16,
    `S4` 15/16, `S5` 87/96, `S9` 15/18, `S9R` 21/24, `S10` 10/30, `S19` 1/4, `S19AD` 6/24, `S21` 14/16, `S21R` 3/6,
    `S22-AIR` 3/40, `S22-E1` 11/16, `S22-E3` 10/16, `S23-CAP` 8/32, `S23-HOLD` 21/24, `S24-E5` 22/32, `S24-ORBIT`
    12/24, `S25-DMG` 21/24, `S25-TGT` 23/24, `S26-BINGO` 49/96, `S28-CLASS` 2/24, `S32-DWELL` 8/20, `S33-PASSES` 6/10,
    `S34-BAND` 9/32, `S35-ADTGT` 6/32, `VAL-agn` 2/4, `VAL-det` 2/3.
  - **Il calo delle salve e' concentrato**: con 0,2 `S24-E5` -2716 e `S23-HOLD` -960 su -3996 totali; le distruzioni
    calano poco (-37 su 2142). Lettura [I], non verificata per esecuzione: un rilevamento piu' tardi accorcia il
    tempo di fuoco (meno salve), mentre il bersaglio viene comunque colpito.
  - **Rilevamenti persi a parita' di estrazione** (effetto di primo ordine, contato dalla spia sulle `Detection`
    dentro la portata; a cascata gli ingaggi successivi cambiano): 652 su 34544 (1,9 %) con 0,3; **1016 su 34631
    (2,9 %) con 0,2**; 1337 su 34759 (3,8 %) con 0,1. **Nessun rilevamento guadagnato** (la Pd scende per ogni d > 0).
    Il 91 % dei persi e' nell'ultimo 30 % della portata (d/R >= 0,7: 928 su 1016 con 0,2), come vuole la forma della
    legge (§1.5).
  - **Il caso dell'utente**: `S36-GRAZE-0`, ZSU-57-2 -> `casD0` (CPA 5979,32 m su 6000 m, `g = 1`): Pd 0,506859 ->
    **0,210975** con 0,2; estrazione 0,7126: non rilevato in entrambi i casi. Nessun rilevamento di S36-GRAZE viene
    perso **per la D-5** con 0,2 o 0,3 (i passaggi radenti non sono rilevati gia' a variante `off`): v. PB-6.
- **Q-4: suite completa con la costante sostituita in memoria** (`unittest discover` come `verifica.sh`, nello stesso
  processo dopo la sostituzione).
  - **p = 0,2**: `Ran 4961`, **14 falliti**, 0 errori, 7 saltati. 5 falliti per un numero scritto con p = 0,5 (§4.4
    T2: `test_fourth_power_law`, `test_low_draw_detects_at_the_range_edge`, `test_each_pass_uses_its_own_cpa`,
    `test_dwell_exposure_is_per_pass`, `Test_Air_Route_Manager...test_detection_metrics_hand_computed`); 9 di scenario
    (PB-6). Le tre suite sono girate in parallelo con le catture Q-2/Q-3 (processi separati, nessun file condiviso): un
    fallimento di tempo sarebbe stato possibile, nessuno dei fallimenti lo e' (sono tutti di valore).
  - **p = 0,3**: `Ran 4961`, **12 falliti**: 4 di numero scritto (come sopra meno `test_low_draw_detects_at_the_range_edge`,
    che usa l'estrazione 0,3 = p e quindi da' ancora il raggio pieno) e 8 di scenario (quelli di 0,2 meno S23-HOLD).
  - **p = 0,1**: `Ran 4961`, **11 falliti e 1 errore**: 6 di numero scritto (i 5 di 0,2 piu'
    `TestDetectionPerPass.test_the_second_pass_is_a_new_occasion`, che si aspetta il lancio a 300 s, cioe' il raggio
    pieno, valido solo se l'estrazione 0,1 e' sotto `0,9 p`: vero per p > 0,111) e 6 di scenario diversi:
    `Test_Session_Scenarios.TestS7LogisticInterdiction` (2, di cui 1 errore `ValueError`), S23-HOLD, S36-GRAZE
    (premessa), `TestS36WindowCut.test_detection_is_never_earlier` (premessa `> 0`),
    `TestPresenceAndPostures.test_postures_of_every_asset_in_the_outcome`; `TestEndToEnd` passa.
  - **L'elenco dei test di scenario non e' monotono nel valore** (`TestEndToEnd` fallisce con 0,3 e 0,2, passa con
    0,1; S7 solo con 0,1): dipende dal sorteggio di un seme fisso, non da una soglia. Per questo PB-6 si decide dopo
    PB-2, sull'elenco del valore scelto.

**Durata**: una cattura completa ~10 min (piu' lenta in parallelo); la suite ~10 min.

---

## 2. Alternative e raccomandazione

### 2.1 (a) Costante unica ricalibrata

Si sostituisce 0,5 con un solo valore piu' basso, uguale per ogni sensore, dietro un interruttore.

- **Pro.** Una riga di dato; nessun dato nuovo da inventare per sensore; la stima e' **una** e si dichiara in un
  punto; la metrica del pianificatore la segue da sola (chiama la stessa funzione, §1.2); nessuna nuova firma, nessun
  lettore, nessun cambio di `Session_Simulator`; reversibile con l'interruttore; compatibile con un futuro (b) (resta
  il ripiego).
- **Contro.** Non distingue l'occhio dal radar ne' la lettura "per scansione" (sensori con dwell) da quella "per
  passaggio" (sensori senza dwell) (§1.4); il valore e' comunque una stima; acceso, cambia 582-678 delle 1103
  esecuzioni fotografate a seconda del valore, e tutte le 116 di S36 (§1.7).
- **Valore** (PB-2): 0,1 / 0,2 / 0,3. Raccomandato **0,2 [S]**: centro dell'intervallo indicato dall'utente; la
  legge si annulla a 1,057 R, quindi il salto al taglio di R e' piccolo (§1.4); la Pd media sui CPA scende di 0,06
  (§1.5). 0,1 e' ancora piu' coerente col taglio ma rende quasi impossibili i rilevamenti radenti anche per i radar
  con dwell (`g * 0,1`); 0,3 e' il cambio minimo dentro l'intervallo dell'utente. Nessuno dei tre e' un dato.

### 2.2 (b) Costante per sensore

Due varianti:

- **(b1) per tipo di sensore**: tre costanti nel risolutore, `{'radar': x, 'TVD': y, 'visual': z}` [S], scelte dal
  sensore vincente dell'osservatore; ripiego sulla costante unica per i sensori dichiarati di test.
- **(b2) per modello**: chiave opzionale `pd_at_acquisition_range` nel dizionario del sensore del registro (accanto a
  `dwell_time_s`), letta come il dwell; ripiego su (b1) o sulla costante unica se manca.

Dove vivrebbe il dato (b2): nei tre registri (`Asset/Vehicle_Data.py`, `Ship_Data.py`, `Aircraft_Data.py`), con
commento per record "STIMA [S] -- motivo" e un registro `Analysis/Document/Registro_Pd_Bordo_Stimati.md` (come
`Registro_Dwell_Stimati.md`). Come si legge: un lettore `registry_pd_edge(observer, target, mode)` sul modello di
`registry_dwell_time` (`Logic/Engagement_Resolver.py:1312-1326`), un parametro `pd_edge_for` di `resolve_engagement`
passato da `Session_Simulator` solo con un interruttore `PD_EDGE_PER_SENSOR` acceso, e un campo nuovo in
`DetectionThreat` per il pianificatore.

- **Pro.** Distingue la vista (dove 0,5 e' certamente alta: il caso dell'utente) dal radar con dwell (dove la lettura
  "per scansione" rende 0,5 difendibile, §1.4); l'infrastruttura "il risolutore sa quale sensore vede" servirebbe
  anche a togliere il limite del fattore notte unico (`:1387-1392`).
- **Contro.** **Nessun dato per sensore**: ogni valore sarebbe una stima, quindi 3 (b1) o fino a ~100 (b2) numeri
  inventati invece di uno; per (b2) nessuna fonte pubblica dice a quale Pd e' data la portata di un sensore
  (bibliografia, §1.4); molti scenari usano sensori dichiarati (ripiego sulla costante unica: (b) li lascia come (a));
  lavoro medio (lettore, parametro del risolutore, `Session_Simulator`, pianificatore, fixture, ~25 test); stesso
  limite di `range_type` gia' dichiarato per il dwell (il lettore legge il vincitore di acquisizione,
  `10_Limiti_Estensioni_Divergenze.md`, "Tre limiti residui").

### 2.3 (c) Dipendenza dalla sezione radar (RCS) del bersaglio

La fisica [I, equazione radar]: a parita' di sensore la portata scala come `RCS^(1/4)`:
`R_eff = R_ref * (sigma / sigma_ref)^(1/4)`. Nella legge attuale equivale a scalare `(d/R)^4` per `sigma_ref / sigma`,
cioe' l'RCS cambia la **portata efficace**, non la Pd al bordo.

- **Che cosa servirebbe.** (1) Una RCS per ogni modello bersaglio (65 aerei, 23 navi, i missili per R-INT; per
  aspetto, almeno frontale), **assente** nei registri e, per i missili, senza fonti pubbliche numeriche (§1.6); (2) la
  **RCS di riferimento** a cui e' data la portata di ogni sensore (`sigma_ref`), **sconosciuta** per tutti; (3) per
  `sigma > sigma_ref` una portata efficace **maggiore** di R, quindi finestre dello scheduler piu' larghe
  (`Contact_Scheduler.mutual_detection_ranges`) e pianificatore da riallineare: un cambio di strato 1, non solo del
  risolutore; per `sigma < sigma_ref` basterebbe il risolutore (Pd = 0 oltre `R_eff`); (4) per TVD e vista l'RCS non
  vale (servono dimensione visiva o firma IR).
- **Pro.** E' la dipendenza fisica giusta (lo stealth, i missili piccoli); la forma `RCS^(1/4)` ha base fisica.
- **Contro.** Dati da inventare in quantita' (una RCS per modello bersaglio, una `sigma_ref` per sensore); costo grande (scheduler, risolutore,
  pianificatore, registri); non risponde alla domanda dell'utente (p resta comunque da fissare per `sigma = sigma_ref`).
- **Legame con il rinvio Koopman** (`10_Limiti_Estensioni_Divergenze.md`, "Rinvio dichiarato: dwell dipendente da
  distanza, modo e carico"; `05_Strato2_Risolutore_Ingaggio.md`, §4.36): la legge cumulativa (Pd per scansione
  composta lungo la traiettoria, `Pc = 1 - prod(1 - Pd_i)`, Mallett-Brennan 1963 in bibliografia 5.7) **cambierebbe il
  significato di p** (diventerebbe Pd per scansione) e andrebbe tarata insieme alla dipendenza da RCS e all'orizzonte
  radar. Fare (c) prima della legge cumulativa significherebbe tarare due volte.
- **Forma povera gia' disponibile**: un `detection_factor` per classe di bersaglio (come `STEALTH_FACTOR` di S3)
  senza toccare scheduler e legge. Anche questa richiede valori inventati; non e' proposta qui.

### 2.4 (d) Nessuna modifica del motore

Lasciare 0,5 e dichiararlo meglio (manuale, guida).

- **Pro.** Costo nullo, fotografia invariata.
- **Contro.** Non risponde al giudizio dell'utente; il salto al taglio di R resta (0,5 -> 0).

### 2.5 Confronto e raccomandazione

| | (a) unica | (b1) per tipo | (b2) per modello | (c) RCS | (d) nulla |
|---|---|---|---|---|---|
| Numeri stimati nuovi | 1 | 3 | fino a ~100 | una `sigma_ref` per sensore (~100) + RCS di ~90 modelli bersaglio | 0 |
| File di produzione toccati | 1 | 3 (`Engagement_Resolver`, `Mobile`, `Session_Simulator`) + `Air_Route_Manager` | come (b1) + 3 registri | come (b2) + `Contact_Scheduler` | 0 |
| Test nuovi (stima) | 12 | ~25 | ~35 + test di completezza | > 50 | 0 |
| Interruttore | `PD_EDGE_RECALIBRATION` | `PD_EDGE_PER_SENSOR` | `PD_EDGE_PER_SENSOR` | nuovo, con scheduler | - |
| Esecuzioni cambiate, acceso | 636 delle 1103 + 116 di S36 con 0,2 (§1.7) | come (a) per i sensori dichiarati, meno o piu' per gli altri a seconda dei valori | come (b1) | non stimabile senza dati | 0 |
| Risponde al caso `casD0` (vista) | si' | si' | si' | no (vista fuori RCS) | no |

**Raccomandazione: (a) con p = 0,2 [S], interruttore spento di default; (b) e (c) rinviate.** Motivi: (1) l'utente
chiede un valore piu' basso e (a) lo da' con una sola stima dichiarata; (2) (b) e (c) non hanno dati: moltiplicherebbero
le stime senza migliorare la taratura; (3) (a) non chiude la strada a (b): la costante unica diventa il ripiego; (4)
(c) va fatta con la legge cumulativa e l'orizzonte radar, che cambiano il significato di p. Se l'utente vuole
distinguere subito la vista dal radar, (b1) e' l'estensione minima (§4.8).

---

## 3. Decisioni aperte per l'utente (una per volta)

### PB-1 — Quale ipotesi

**Domanda.** Come rendere la Pd al bordo meno alta?
**Alternative.** (a) costante unica piu' bassa per tutti i sensori; (b1) tre costanti, una per tipo di sensore
(radar, TVD, vista); (b2) un valore per modello di sensore nei registri; (c) dipendenza dalla RCS del bersaglio; (d)
nessuna modifica, solo documentazione.
**Esempio.** Con (a) e p = 0,2 la ZSU-57-2 di `casD0` (vista, CPA 5979,32 m su 6000 m, `g = 1`) passa da Pd 0,507 a
0,211 [C: `1 - 0,8 * (5979,32/6000)^4`; V: sonda Q-1, 0,210975]; con (b1) e, per esempio (valori illustrativi, non
proposti), vista = 0,2 e radar = 0,5 la stessa ZSU avrebbe 0,211 ma un Buk al bordo resterebbe 0,5 (prima di `g`).
**Raccomandazione.** (a) (§2.5).

### PB-2 — Valore della costante (se PB-1 = a)

**Domanda.** Quale Pd sul bordo, dentro l'intervallo 0,1-0,3 indicato dall'utente?
**Alternative.** 0,1 / 0,2 / 0,3 (§1.5 per la curva; §1.7 per l'effetto sulle esecuzioni).
**Esempio.** A 0,9 R: 0,410 / 0,475 / 0,541 (oggi 0,672). Esecuzioni delle 1103 che cambiano all'accensione: 678 /
636 / 582 (sonde Q-3, Q-1, Q-2); test di scenario da trattare (PB-6): 6 / 9 / 8 (Q-4).
**Raccomandazione.** 0,2 [S] (§2.1). Il valore va scritto nel codice come STIMA, con il motivo.

### PB-3 — La metrica del pianificatore segue l'interruttore?

**Domanda.** `Path.max_detection_probability` (`Logic/Air_Route_Manager.py:1162`, `:1199`) chiama la stessa legge del
DES. Deve seguire la costante nuova quando l'interruttore e' acceso?
**Alternative.** (S) si', automaticamente (nessuna riga in `Air_Route_Manager`: legge la stessa funzione); (N) no, il
pianificatore resta a 0,5 (servirebbe passargli esplicitamente il valore vecchio: una riga e un'eccezione alla regola
"stessa legge del DES" scritta nel suo docstring, `:1108-1110`).
**Esempio.** Tratto a d = 10, R = 20: 0,96875 oggi, 0,95 con p = 0,2.
**Raccomandazione.** (S): la metrica dichiara di replicare il DES; nessun consumatore la usa per decidere (§1.2),
quindi non cambia nessuna rotta.

### PB-4 — Come leggere le esecuzioni cambiate

**Domanda.** All'accensione cambiano 752 esecuzioni su 1219 con p = 0,2 (§1.7): elencarle una per una come in
`Rapporti/S36_Esecuzioni_Nuove.md` (360 righe per 116 esecuzioni) non e' leggibile. Che rapporto produrre?
**Alternative.** (R1) rapporto riassuntivo `Rapporti/PB_Esecuzioni_Cambiate.md`: conteggi per famiglia di scenari
(cambiate/totali), elenco delle esecuzioni con **esito di forza** cambiato, somme di salve e distruzioni prima/dopo
per famiglia, statistica dei rilevamenti persi a parita' di estrazione, e per le sole unita' S36 (che registrano le
`Detection`) la tabella riga per riga prima/dopo (Pd, rilevato, istante), confrontabile con `S36_Esecuzioni_Nuove.md`;
(R2) il riassunto completo per esecuzione di `Scenario_Baseline --compare --summary` (migliaia di righe); (R3) R1 piu'
un campione di 20 esecuzioni scelte dall'utente in forma completa.
**Raccomandazione.** (R1); (R3) se dopo R1 l'utente vuole vedere casi specifici.

### PB-5 — Ordine fra la fotografia S36 e l'accensione

**Domanda.** La fotografia da 1219 (S36) non e' ancora installata. Quando si accende PB?
**Alternative.** (i) prima l'utente installa la fotografia da 1219, poi si esegue il blocco 1 (confronto atteso 1219
IDENTICHE), poi, se decide, l'accensione con una seconda fotografia nuova; (ii) blocco 1 subito (confronto atteso 1103
IDENTICHE + 116 NEW), accensione e unica fotografia nuova dopo; (iii) accensione insieme alla prima fotografia.
**Raccomandazione.** (i): ogni fotografia nuova ha **una** causa leggibile (S36, poi PB); (ii) va bene se l'utente non
vuole aspettare, ma allora il confronto dell'accensione mescola NEW (S36) e CHANGED (PB) e il rapporto R1 deve separarli.
(iii) sconsigliata.

### PB-6 — Test di scenario che falliscono con l'interruttore acceso (si applica solo al blocco 3)

**Domanda.** La sonda Q-4 (§1.7) esegue la suite completa con la costante sostituita in memoria. Oltre ai 5 test con
un numero scritto a mano (riscritti nel blocco 1, §4.4 T2), con p = 0,2 falliscono **9 test di scenario**, che non
provano la legge di Pd ma ne dipendono:
- `Test_Session_Simulator.TestEndToEnd` (6: `test_one_engagement_per_front`, `test_fronts_are_resolved_in_time_order`,
  `test_fuel_distance_time_and_application`, `test_fuel_events_only_for_moving_assets`,
  `test_g3_movement_at_cruise_plus_one_engagement_charge`, `test_regime_is_combat_only_for_assets_that_fought`) e
  `TestPresenceAndPostures.test_postures_of_every_asset_in_the_outcome` (1): scenario di orchestrazione a due fronti
  con sensori dichiarati di 5 km (`Test_Session_Simulator.py:76`, `SENSOR_RANGE`): con p = 0,2 cambia l'esito
  degli ingaggi del fronte nord (i messaggi d'errore citano `M-north`/`Blue-North`, `bn1`, `bn2`; causa esatta non
  indagata). `TestEndToEnd` e' anche l'unita' `ORC-base` della fotografia (`Scenario_Baseline.py:340`);
- `Test_Session_Scenarios_S23.TestS23GroundHold.test_the_halted_tank_is_engaged_during_the_hold`: soglia di scenario
  `MIN_FIRING_FRACTION = 0.5` (`Test_Session_Scenarios_S23.py:168`), osservato 3 su 8 = 0,375 (unita' `S23-HOLD`);
- `Test_Session_Scenarios_S36.TestS36Graze.test_same_draws_and_no_extra_detection`: la premessa "non vacua"
  (`lost > 0`, almeno un rilevamento perso per la D-5 in `band_max`) non vale piu': con p = 0,2 e 0,3 nessun
  rilevamento di S36-GRAZE si perde per la D-5, perche' a variante `off` quei passaggi radenti non sono gia' piu'
  rilevati (sonde Q-1, Q-2).

**Alternative.** (A) fissare l'interruttore **spento dentro la classe** di test (`patch.object(ER_MODULE,
'PD_EDGE_RECALIBRATION', False)` in `setUp`/`setUpClass`, con il commento "premessa tarata con p = 0,5, PB-6"): il
test resta com'e' e le esecuzioni della fotografia di quell'unita' restano quelle di oggi (non seguono il default);
(B) riscrivere premessa o geometria per la p nuova (richiede un mini-piano per test: es. S23 con la sosta piu'
vicina all'osservatore, S36 con la premessa "almeno una Pd ridotta a parita' di estrazione" invece di "almeno un
rilevamento perso"); (C) abbassare le soglie ai valori osservati (sconsigliata: adatta il test all'esito).
**Raccomandazione.** (A) per `Test_Session_Simulator` (sono test di orchestrazione: fronti, carburante, posture, non
di rilevamento; l'interruttore si fissa nella classe base comune del file, quindi anche le unita' `ORC-*` della
fotografia restano a p = 0,5) e per `S23-HOLD` (prova la sosta, non la Pd); (B) per S36-GRAZE, perche' e' il caso che ha motivato
la Proposta e deve mostrare la p nuova: la premessa diventa "in `band_max` almeno una `Detection` ha
`probability < reference.probability`" (vera per costruzione con `g < 1`, quindi la premessa resta non vacua sulla
**legge**, non piu' sul sorteggio), e il controllo "nessun rilevamento in piu'" resta invariato. L'elenco definitivo
viene dal rapporto del blocco 2 (con l'interruttore vero): se differisce da questo, la decisione si riprende.
**L'elenco dipende dal valore di PB-2** (Q-4, §1.7): con 0,3 esce S23-HOLD (8 test); con 0,1 escono i 6 di
`TestEndToEnd` ed entrano i 2 di `TestS7LogisticInterdiction` (unita' `S7`) e
`TestS36WindowCut.test_detection_is_never_earlier` (premessa `> 0`, come S36-GRAZE). Per analogia la raccomandazione
diventa: (A) per i test di orchestrazione e di scenario che non provano il rilevamento (S7: interdizione logistica),
(B) per le premesse di S36 (stessa riscrittura "almeno una Pd ridotta"). Il piano di §4.3 e' scritto per 0,2.

---

## 4. Piano di intervento (opzione raccomandata: PB-1 = a, PB-2 = 0,2, PB-3 = S, PB-4 = R1, PB-5 = i, PB-6 = A+B)

Se l'utente sceglie un altro valore in PB-2, si sostituisce **solo** il numero 0,2 nel blocco 1 e nei test che lo
citano (nessuna costante dei test e' scritta a mano: leggono `ER.PD_AT_ACQUISITION_RANGE_RECALIBRATED`, §4.4). Se
sceglie (b1), v. §4.8. Blocchi piccoli, verifica parziale per blocco; suite e confronto completi **solo a fine task**,
con `tools/ai/verifica.sh`, **mai in parallelo**.

### 4.1 Blocco 1 — Interruttore, costante, funzione d'accesso (esecutore; interruttore SPENTO)

**File: `Logic/Engagement_Resolver.py`.**

1. **Costanti**, subito dopo `PD_AT_ACQUISITION_RANGE` (`:556`), prima di `PD_RANGE_EXPONENT`:

   ```python
   # Ricalibrazione della Pd sul bordo della portata (Proposta_Pd_Bordo_Portata.md, PB), interruttore dedicato:
   #   * `PD_EDGE_RECALIBRATION` (SPENTO): acceso, la legge di Pd (`detection_probability`, `detection_radius`, e
   #     quindi la metrica del pianificatore `Air_Route_Manager.Path.compute_detection_metrics`) usa
   #     PD_AT_ACQUISITION_RANGE_RECALIBRATED al posto di PD_AT_ACQUISITION_RANGE; spento, la legge di prima. Letto a
   #     ogni chiamata (`pd_at_acquisition_range`). Nessuna estrazione in piu' ne' in ordine diverso in nessuno dei due
   #     stati: l'estrazione precede la Pd; cambiano esito e raggio del rilevamento, e a valle le estrazioni di tiro.
   PD_EDGE_RECALIBRATION = False

   # Pd sul bordo della portata ricalibrata. STIMA DICHIARATA (decisione PB-2 dell'utente, <data>), nessuna fonte:
   # l'utente giudica 0.5 alta (attesi 0.1-0.3); 0.2 e' il centro dell'intervallo. Con il taglio a R del motore la
   # legge si annullerebbe a R * (1/(1 - 0.2))^(1/4) = 1.057 R (con 0.5: 1.189 R): salto al bordo piu' piccolo. Vale
   # per ogni sensore (radar, TVD, vista): una costante per sensore e la dipendenza dalla RCS sono rinviate
   # (Proposta §2.2-§2.3).
   PD_AT_ACQUISITION_RANGE_RECALIBRATED = 0.2
   ```
   Il commento di `PD_AT_ACQUISITION_RANGE` (`:553-555`) diventa: "Pd sul bordo della portata di acquisizione (legge
   di prima, in vigore con PD_EDGE_RECALIBRATION spento). STIMA DICHIARATA: convenzione 'la piu' prudente fra Pd 0.5 e
   0.9' senza fonte verificata (Guida_Concettuale_DES_Bibliografia.md, 'non verificate'). Valore ricalibrato:
   PD_AT_ACQUISITION_RANGE_RECALIBRATED." Il valore 0.5 **non cambia**.

2. **Funzione d'accesso**, subito prima di `detection_probability` (`:1225`):

   ```python
   def pd_at_acquisition_range() -> float:
       """Pd sul bordo della portata in vigore: PD_AT_ACQUISITION_RANGE_RECALIBRATED con PD_EDGE_RECALIBRATION acceso,
       altrimenti PD_AT_ACQUISITION_RANGE (globali letti a ogni chiamata, cosi' i test li sostituiscono).

       Raises:
           ValueError: il valore in vigore non e' in [0, 1) (con 1 `detection_radius` dividerebbe per zero).
       """
       value = PD_AT_ACQUISITION_RANGE_RECALIBRATED if PD_EDGE_RECALIBRATION else PD_AT_ACQUISITION_RANGE

       if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0.0 <= value < 1.0:
           raise ValueError(f"Pd at the acquisition range must be in [0, 1), got {value!r}")

       return float(value)
   ```

3. **`detection_probability`** (`:1225-1252`): una variabile locale `edge = pd_at_acquisition_range()` letta **dopo**
   i controlli degli argomenti e prima del ritorno; la formula diventa `factor * (1.0 - (1.0 - edge) * ratio)`. Il
   docstring scrive `p = pd_at_acquisition_range()` al posto di `PD_AT_ACQUISITION_RANGE` e cita l'interruttore.
   Ordine dei controlli invariato (prima distanza, portata, fattore; poi `distance > sensor_range` -> 0.0): con
   `distance > sensor_range` la funzione d'accesso **non** e' chiamata (nessun effetto, ma l'ordine resta quello di
   prima).

4. **`detection_radius`** (`:1255-1284`): `edge = pd_at_acquisition_range()` letta dopo `factor = _check_factor(...)`;
   `if draw < factor * edge: return float(sensor_range)`; `ratio = (1.0 - draw / factor) / (1.0 - edge)`. Docstring
   come sopra.

5. **Docstring** di `weather_detection_factor` (`:1384`): "accanto a PD_AT_ACQUISITION_RANGE" -> "accanto alla Pd sul
   bordo (`pd_at_acquisition_range`)". Docstring del modulo, punto 1 della catena (`:14-21`): aggiungere in coda
   "La Pd sul bordo della portata e' `pd_at_acquisition_range()` (interruttore `PD_EDGE_RECALIBRATION`, PB)."

**Nient'altro cambia**: `Session_Simulator`, `Air_Route_Manager`, `Contact_Scheduler`, i registri, `Detection` e
`Scenario_Baseline` restano come sono (la metrica del pianificatore segue da sola, PB-3 = S). Nessun nuovo campo nella
voce `detections` di S36 (cambierebbe `DETECTION_FIELDS` e quindi le 116 esecuzioni).

**Test del blocco 1** (§4.4, gruppi T1 e T2). **Verifica parziale del blocco 1** (dalla root del repo, `<python>` =
interprete stampato da `verifica.sh`):

```
<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Engagement_Resolver
<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Air_Route_Manager
<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Threat_AA_Factory
<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S36
<python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare .ai-run/confronto_capture.json --only '^(S1|S5|S36-GRAZE|S36-BAND)/' --quiet
```
Atteso: tutti OK; il confronto parziale `IDENTICAL` (interruttore spento). Se `.ai-run/confronto_capture.json` non
c'e' sulla macchina, usare la fotografia installata con `--only '^(S1|S5)/'`.

### 4.2 Blocco 2 — Sonda con l'interruttore acceso e rapporto di lettura (sessione principale, sola lettura)

Dopo il merge del blocco 1, **la sessione principale** (non l'esecutore: serve la cattura di riferimento e la
decisione PB-4) esegue lo script dell'Appendice A, salvato in `Analysis/Document/Rapporti/Sonde_Pd_Bordo/probe_pd_edge.py`
(come `Rapporti/Sonde_Dwell_D5/`), con l'interruttore **vero** acceso in memoria:

```
PYTHONPATH=. <python> Analysis/Document/Rapporti/Sonde_Pd_Bordo/probe_pd_edge.py on <dir_uscita>
```
e scrive `Analysis/Document/Rapporti/PB_Esecuzioni_Cambiate.md` (formato R1, PB-4): (1) conteggi per famiglia;
(2) esecuzioni con `force_outcomes` cambiati; (3) salve e distruzioni prima/dopo per famiglia; (4) rilevamenti persi
e guadagnati a parita' di estrazione (contatori della spia); (5) tabella prima/dopo delle `Detection` delle cinque unita'
S36; (6) i test che falliscono con l'interruttore acceso: suite completa con l'interruttore acceso in memoria
(script dell'Appendice B, ~10 min, dopo la cattura e mai in parallelo con essa). **Attenzione**: la cattura non lo
dice, perche' per le unita' senza metodi espliciti `Scenario_Baseline` esegue solo `setUpClass`, non i test
(`Scenario_Baseline.py`, `_run_unit`); le righe `WARNING test failed` coprono solo le unita' con metodi espliciti.
L'elenco `changed_list` del `report.json` e' **l'esito atteso** del confronto del blocco 3: va conservato nella
cartella della sonda. Durata: una cattura completa (~9-12 min sul ProArt; mai in parallelo con suite o confronto).

### 4.3 Blocco 3 — Accensione (SOLO dopo la decisione esplicita dell'utente, letto il rapporto del blocco 2)

1. `PD_EDGE_RECALIBRATION = True` (`Logic/Engagement_Resolver.py`), commento: "ACCESO dalla decisione dell'utente del
   <data>; prima spento" (forma di `D5_DWELL_TIME`, `:593-601`).
2. Il test del default (T1-1, §4.4) si rinomina `test_switch_is_on_by_default` e diventa:
   `assertIs(ER.PD_EDGE_RECALIBRATION, True)`; `assertEqual(ER.pd_at_acquisition_range(),
   ER.PD_AT_ACQUISITION_RANGE_RECALIBRATED)`; `assertEqual(ER.PD_AT_ACQUISITION_RANGE, 0.5)` (la legge di prima resta
   disponibile spegnendo l'interruttore).
3. I test di scenario che falliscono con l'interruttore acceso (PB-6; elenco di Q-4 in §1.7, confermato dal punto 6
   del rapporto del blocco 2) si trattano come deciso in PB-6, **senza** cambiare la legge. Con la raccomandazione:
   - `Test_Session_Simulator.py`, `_Base.setUp` (`:161-164`, classe base comune di tutti i test di orchestrazione del
     file, `TestEndToEnd` e `TestPresenceAndPostures` compresi): aggiungere a `self._patches`, prima del ciclo che li
     avvia, `patch.object(ER, 'PD_EDGE_RECALIBRATION', False)` (`ER` e' gia' importato, `:62`), con il commento
     "Premessa tarata con p = 0,5: test di orchestrazione, non di rilevamento (Proposta_Pd_Bordo_Portata.md, PB-6)".
     `tearDown` lo ferma con gli altri. Effetto sulla fotografia: le unita' `ORC-*` (`Scenario_Baseline.py:340-354`)
     restano con p = 0,5;
   - `Test_Session_Scenarios_S23.py`, `TestS23GroundHold.setUpClass` (`:403-409`): importare
     `from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER` e `import sys`, definire
     `ER_MODULE = sys.modules[ER.__name__]` (come `Test_Session_Scenarios_S36.py:56`) e avvolgere il ciclo sui seed con
     `with patch.object(ER_MODULE, 'PD_EDGE_RECALIBRATION', False):`, stesso commento. Effetto: `S23-HOLD` resta con
     p = 0,5;
   - `Test_Session_Scenarios_S36.py`, `test_same_draws_and_no_extra_detection` (`:242-261`): la variabile `lost` e
     l'asserzione finale si sostituiscono con `reduced` = numero di casi `band_max` con `detection.probability <
     reference.probability` e `self.assertGreater(reduced, 0)`; commento "premessa non vacua sulla legge (PB-6): con
     p = 0,2 nessun rilevamento radente e' perso per la D-5 perche' non e' rilevato gia' a `off`". Il resto del test
     non cambia.
   Se il rapporto del blocco 2 elenca test diversi, l'esecutore **si ferma** e la sessione principale riprende PB-6.
4. Verifiche: suite completa e confronto completo con `verifica.sh` (§4.6, stato "acceso").

La fotografia nuova la installa **solo l'utente**.

### 4.4 Test da scrivere o aggiornare

Classi base: nessuna classe base nuova; le classi di test ereditano da `unittest.TestCase` come le vicine. Le costanti
dei test **non** sono scritte a mano: si leggono da `ER` (lezione DW-9: le copie a mano divergono dal codice).

**T1 — nuova classe `TestPdEdgeRecalibration(unittest.TestCase)` in `Test/Test_Engagement_Resolver.py`**, subito dopo
`TestDetectionRadius` (`:162-186`). Ogni test che accende l'interruttore usa
`with patch.object(ER, 'PD_EDGE_RECALIBRATION', True):` (`patch` e' gia' importato, `:30`); **ogni test che confronta
i due stati imposta anche lo stato spento esplicitamente** (`patch.object(..., False)`), mai per default: cosi' T1
(tranne il n. 1), T3 e T4 restano validi senza modifiche dopo l'accensione del blocco 3.

| # | Nome | Asserzioni |
|---|---|---|
| 1 | `test_switch_is_off_by_default` | `assertIs(ER.PD_EDGE_RECALIBRATION, False)`; `assertEqual(ER.pd_at_acquisition_range(), ER.PD_AT_ACQUISITION_RANGE)`; `assertEqual(ER.PD_AT_ACQUISITION_RANGE, 0.5)` |
| 2 | `test_recalibrated_value_is_a_lower_estimate` | `0.0 <= ER.PD_AT_ACQUISITION_RANGE_RECALIBRATED < ER.PD_AT_ACQUISITION_RANGE` |
| 3 | `test_switch_on_uses_the_recalibrated_edge` | acceso: `pd_at_acquisition_range() == PD_AT_ACQUISITION_RANGE_RECALIBRATED`; `detection_probability(1000.0, 1000.0)` == stesso valore (`assertAlmostEqual`); `detection_probability(0.0, 1000.0) == 1.0`; `detection_probability(500.0, 1000.0)` == `1.0 - (1.0 - v) * 0.5 ** 4` con `v = ER.PD_AT_ACQUISITION_RANGE_RECALIBRATED`; `detection_probability(1000.1, 1000.0) == 0.0` |
| 4 | `test_switch_on_lowers_pd_inside_the_range` | per `d` in `range(50, 1001, 50)`: Pd accesa `<` Pd spenta; per `d = 0`: uguali (1.0) |
| 5 | `test_switch_on_radius_is_the_inverse` | acceso, per `draw` in `(v + (1 - v) * k for k in (0.1, 0.4, 0.7, 0.95))`: `detection_probability(detection_radius(draw, 1000.0), 1000.0) ≈ draw` (places=9) |
| 6 | `test_switch_on_low_draw_detects_at_the_edge` | acceso: `detection_radius(0.5 * v, 1000.0) == 1000.0`; e un'estrazione fra `v` e 0.5 (es. `(v + 0.5) / 2`): spento il raggio e' 1000.0, acceso e' `< 1000.0` |
| 7 | `test_switch_on_with_factor` | acceso, `factor=0.5`: `detection_probability(1000.0, 1000.0, factor=0.5) ≈ 0.5 * v`; `detection_radius(0.5 * v * 0.5, 1000.0, factor=0.5) == 1000.0` |
| 8 | `test_invalid_edge_raises` | acceso con `patch.object(ER, 'PD_AT_ACQUISITION_RANGE_RECALIBRATED', 1.0)`: `ValueError` da `pd_at_acquisition_range()` e da `detection_probability(10.0, 1000.0)`; con `-0.1`: `ValueError`; con `True`: `ValueError` |
| 9 | `test_resolver_same_draws_lower_pd` | forze e asset come `test_draw_above_pd_means_no_detection_and_no_fire` (`:190-200`); `resolve_engagement` con una finestra `_window('b1', 'r1', distance=900.0, range_a=1000.0, range_b=None)`, `_ScriptedRng([d])` con `d = (pd_on + pd_off) / 2`, dove `pd_off` e `pd_on` sono `ER.detection_probability(900.0, 1000.0)` calcolata a interruttore spento e acceso (valori di oggi: 0,672 e 0,475 con v = 0,2; non scriverli a mano), `fire_control = lambda s, t: None`: spento `detected` True, acceso `detected` False; in entrambi un solo `Detection` con `draw == d`, `rng.calls` uguali; `probability` pari a `pd_off` / `pd_on` (places=12) |
| 10 | `test_resolver_with_legs_detection_is_later` | geometria di `test_with_legs_detection_time_is_exact` (`:226-241`), estrazione `0.9` per entrambi gli stati: istante atteso `(10000.0 - r) / 100.0` con `r = 8000.0 * ((1 - 0.9) / (1 - pd_at_acquisition_range())) ** 0.25` letto **dentro** ciascuno stato; istante acceso > istante spento |

**T2 — test esistenti riscritti per leggere la costante in vigore** (passano identici a interruttore spento, restano
validi acceso; nessun cambio di significato):

| File:riga | Oggi | Dopo |
|---|---|---|
| `Test_Engagement_Resolver.py:131` (docstring di `TestDetectionProbability`) | "PD_AT_ACQUISITION_RANGE al bordo" | "pd_at_acquisition_range() al bordo" |
| `Test_Engagement_Resolver.py:137` | `ER.PD_AT_ACQUISITION_RANGE` | `ER.pd_at_acquisition_range()` |
| `Test_Engagement_Resolver.py:142-144` | docstring "1 - 0.5 * 0.5^4 = 0.96875"; `1.0 - 0.5 * 0.5 ** 4` | docstring "1 - (1 - p) * 0.5^4 (0.96875 con p = 0.5)"; `1.0 - (1.0 - ER.pd_at_acquisition_range()) * 0.5 ** 4` |
| `Test_Engagement_Resolver.py:178-179` | `detection_radius(0.3, 1000.0) == 1000.0` | `detection_radius(0.5 * ER.pd_at_acquisition_range(), 1000.0) == 1000.0` |
| `Test_Engagement_Resolver.py:192` (docstring di `test_draw_above_pd_means_no_detection_and_no_fire`) | "Pd = 0.5" | "Pd = pd_at_acquisition_range() (0.5 di default)"; l'estrazione 0.9 resta (non rileva in nessuno dei due stati) |
| `Test_Engagement_Resolver.py:4125` (`TestDetectionPerPass.test_each_pass_uses_its_own_cpa`) | `0.9352` (= `1 - 0,5 * 0,6^4`) | `ER.detection_probability(3000.0, 5000.0)` |
| `Test_Engagement_Resolver.py:4142` (commento) | "0.1 < 0.9352 x 0.9" | "0.1 < Pd(3000, 5000) x 0.9 (0.9352 x 0.9 con p = 0.5)". **Solo se PB-2 = 0,1**: il test (`test_the_second_pass_is_a_new_occasion`, `:4134-4146`) si aspetta il lancio a 300 s, cioe' il raggio pieno, che richiede l'estrazione < `0.9 * p`; con p = 0,1 fallisce (Q-4): l'estrazione di `pass_rng` passa da `0.1` a `0.05` e il commento diventa "0.05 < 0.9 * p: raggio pieno" (con 0,2 e 0,3 nessun cambio) |
| `Test_Engagement_Resolver.py:4169` (`test_dwell_exposure_is_per_pass`) | `0.64 * 0.9352` | `0.64 * ER.detection_probability(3000.0, 5000.0)` |
| `Test_Engagement_Resolver.py:240` | `(1 - ER.PD_AT_ACQUISITION_RANGE)` | `(1 - ER.pd_at_acquisition_range())`; docstring `:227` "((1 - 0.9)/(1 - p))" |
| `Test_Air_Route_Manager.py:1945`, `:1955` | commento "Pd = 1 - 0,5*(10/20)^4 = 0,96875"; `1 - 0.5 * (10 / 20) ** 4` | commento con p ("0,96875 con p = 0,5"); `1 - (1 - ER.pd_at_acquisition_range()) * (10 / 20) ** 4`. `ER` e' gia' importato a livello di modulo a `:2006` (eseguito all'import, prima dei test): nessun import nuovo |

La tabella copre **tutti** i test che la sonda Q-4 (§1.7) trova falliti per un numero scritto con p = 0,5 (5:
`test_fourth_power_law`, `test_low_draw_detects_at_the_range_edge`, `test_each_pass_uses_its_own_cpa`,
`test_dwell_exposure_is_per_pass`, `test_detection_metrics_hand_computed`), i 2 che leggono `PD_AT_ACQUISITION_RANGE`
per nome (`:137`, `:240`: con la costante sostituita passano, con l'interruttore acceso fallirebbero) e i docstring e
commenti che citano 0,5. `Test_Engagement_Resolver.py:1030`, `Test_Threat_AA_Factory.py:607-628`, `Test_Session_Scenarios.py:1394`,
`Test_Session_Scenarios_S36.py:116-126` e `:823`, `Test_Air_Route_Manager.py:1965`, `:2043-2082` usano gia'
`ER.detection_probability` (o rapporti fra Pd): **non si toccano**. Il docstring di `Test_Session_Scenarios_S22.py:30`
("Pd ~0,59 a 4 km") resta: descrive l'esito a interruttore spento; al blocco 3 si aggiunge "(con p = 0,5)".

**T3 — metrica del pianificatore (`Test/Test_Air_Route_Manager.py`)**: nella classe `TestDetectionMetricsWithDwell`
(`:2010`), un test `test_pd_edge_switch_follows_the_des_law`: stesso `edge` di `test_switch_off_metrics_are_unchanged`
(`:2034-2045`) con `dwell_time_s=None`; con `patch.object(ER, 'PD_EDGE_RECALIBRATION', True)` attorno a
`compute_detection_metrics`: `max_detection_probability ≈ 1 - (1 - ER.PD_AT_ACQUISITION_RANGE_RECALIBRATED) *
(10/20)**4` (places=9) e `<` del valore calcolato sullo stesso `Path` con `patch.object(ER, 'PD_EDGE_RECALIBRATION',
False)` (stato spento esplicito).

**T4 — scenario (fuori dalla fotografia)**: nuova classe `TestPdEdgeOnGraze(F.LoggerSilencer, unittest.TestCase)` in
coda a `Test/Test_Session_Scenarios_S36.py`, **non** aggiunta a `UNITS` di `Scenario_Baseline` (come
`TestS36BaselineDetections`): per ogni seme di `GRAZE_SEEDS`, `run_variant(session_id, build_graze(None), True)`
eseguito due volte in `setUpClass`, la prima dentro `with patch.object(ER_MODULE, 'PD_EDGE_RECALIBRATION', False):`
(esecuzione `old`), la seconda dentro `... True:` (esecuzione `new`); `run_variant` gestisce gia' `D5_DWELL_TIME`
(qui acceso, dwell del registro). Un test `test_same_draws_lower_pd_and_no_new_detection` che, per ogni A-10C
(`GRAZE_FACTORS`) e seme, sulla `Detection` della ZSU (`detections_of(results, OBSERVER, f'Blue-CAS/{prefix}0')`, una
sola per esecuzione): stesso `draw`, stessa `distance_cpa`, stessa `exposure_s`; `new.probability ≈ g * (1 - (1 - v)
* (d / R)**4)` con `d = distance_cpa`, `R = sensor_range`, `g = ER.dwell_factor(exposure_s, dwell_time_s)`,
`v = ER.PD_AT_ACQUISITION_RANGE_RECALIBRATED` (places=12); `new.probability < old.probability`; `new.detected`
implica `old.detected`; se entrambi rilevati, `new.time >= old.time - 1e-9`. Le 8 sessioni costano ~2 s (S36-GRAZE intera, 16 sessioni, gira in 3,3 s nella sonda Q-1).

**Totale test nuovi: 10 (T1) + 1 (T3) + 1 (T4) = 12.** Suite attesa `Ran 4961 + 12 = 4973` **se** la base e' ancora
`Ran 4961` (2026-11-18): la base va **riletta** dall'ESITO di una suite sul commit di partenza, non presa da qui.

### 4.5 Vincoli per l'esecutore

- **RNG**: nessuna estrazione nuova, nessuno spostamento; la funzione d'accesso non estrae. Non toccare `_draw`,
  `_detect_direction`, `_detect_passes`.
- **Interruttore**: nome `PD_EDGE_RECALIBRATION`, default `False` nei blocchi 1-2; letto a ogni chiamata (mai copiato
  in una variabile di modulo o di classe all'import).
- **Costante**: `PD_AT_ACQUISITION_RANGE_RECALIBRATED = 0.2` (o il valore di PB-2), con il commento STIMA di §4.1.
- **Nomi stabili** in `Test/Scenario_Baseline.py`: nessuna unita' o variante nuova, nessuna modifica di `UNITS`,
  `DETECTION_UNITS`, `DETECTION_FIELDS`.
- **Core indifferente al simulatore**: nessun import dall'adapter DCS; nessuna dipendenza nuova.
- **Import** con il percorso completo; logger mockato come negli altri `Test_*.py` dove serve.
- **Fotografia**: mai installata dall'esecutore.

### 4.6 Esito atteso del confronto con la fotografia

| Stato | Contro la fotografia installata da 1103 | Contro una fotografia da 1219 (se l'utente l'installa prima, PB-5 = i) |
|---|---|---|
| Dopo il blocco 1 (interruttore spento) | **1103 IDENTICHE + 116 NEW** (S36), 0 CHANGED, 0 MISSING | **1219 IDENTICHE**, 0 CHANGED/NEW/MISSING |
| Dopo il blocco 3 (interruttore acceso, PB-6 come raccomandata) | CHANGED = `changed_list` della sonda del blocco 2 ristretto alle 1103, **meno** le esecuzioni delle unita' `ORC-*` e `S23-HOLD` (interruttore fissato spento nei loro test); NEW = 116 | CHANGED = esattamente `changed_list` della sonda del blocco 2 meno `ORC-*` e `S23-HOLD` |

Perche' a interruttore spento nulla cambia: `pd_at_acquisition_range()` restituisce `PD_AT_ACQUISITION_RANGE` = 0.5,
la formula e' algebricamente la stessa (stessa espressione in virgola mobile: `1.0 - (1.0 - 0.5) * ratio`), nessuna
estrazione nuova. Perche' acceso ne cambiano 752 su 1219 (con 0,2): §1.3 e §1.7 (esito e soprattutto istante di
rilevamento). Perche' le altre 467 restano identiche: non indagato per famiglia (§1.7).

### 4.7 Documenti da aggiornare (dopo il blocco 1; di nuovo dopo il blocco 3)

- `F4_Differenze_Scenari.md`: sezione "PB" (interruttore spento: nessuna differenza; acceso: rimando a
  `Rapporti/PB_Esecuzioni_Cambiate.md`).
- `Piano_Implementazione_Missione.md`: riga di stato PB.
- Manuale (`des-manual-writer`): `05_Strato2_Risolutore_Ingaggio.md` §4.2 (legge, funzione d'accesso,
  interruttore; righe `:178-185`); `10_Limiti_Estensioni_Divergenze.md` §9.1 "Pd sul bordo della portata" (`:406`),
  `:375` ("Pd sul bordo = 0,5 x fattore"), §9.6 e la tabella di stato (`:848`, voce 0ter); `11a_Atlante_Risolutore.md`
  `:639-643` (costanti del modulo); `Guida_Concettuale_DES_Scaletta.md` `:332`, `:384`, `:402`, `:799`.
- Memoria e stato: solo la sessione principale.

### 4.8 Se l'utente sceglie (b1) invece di (a): piano essenziale

1. `Asset/Mobile.py`: `detection_sensor(mode, range_type=DEFAULT_DETECTION_RANGE_TYPE) -> Optional[str]`, il
   sensore vincente (stessa scelta di `detection_dwell_time`, `:1715-1734`, che va rifattorizzata per usare questa
   funzione senza cambiare esito: test `Test_Mobile.TestDetectionDwellTime` invariati).
2. `Logic/Engagement_Resolver.py`: `PD_EDGE_PER_SENSOR = False`; `PD_AT_ACQUISITION_RANGE_BY_SENSOR = {'radar': x,
   'TVD': y, 'visual': z}` [S, valori da decidere: nuova decisione PB-2b]; lettore `registry_pd_edge(observer, target,
   mode)` (None se l'osservatore non ha `detection_sensor`, se il sensore e' None o se l'istanza dichiara la portata
   di test); parametro `pd_edge_for=None` di `resolve_engagement` (`:4322`, validato come `dwell_time_for`,
   `:4446-4447`) e di `_EngagementRun.__init__` (`:1956`, `:2025`); `_pd_edge_of(window, observer, target)` come
   `_dwell_of` (`:2503-2512`); parametro opzionale `pd_at_range: Optional[float] = None` di `detection_probability` e
   `detection_radius` (None = `pd_at_acquisition_range()`), passato in `_detect_direction` e `_detect_passes`.
3. `Logic/Session_Simulator.py:2792`: `if ER.PD_EDGE_PER_SENSOR: extra['pd_edge_for'] = ER.registry_pd_edge`.
4. `Logic/Air_Route_Manager.py`: `DetectionThreat` con il sensore gia' scelto (`build_detection_threat`, `:776-800`)
   passa `pd_at_range` a `detection_probability`.
5. `Test/Scenario_Fixtures.py`: `declare_sensor` fa restituire `None` a `detection_sensor` per i modi dichiarati.
6. Test: ~25 (lettore, parametro, ripiego, `Session_Simulator`, pianificatore, fixture, uno scenario sulla ZSU a vista
   contro un radar). Esito spento: come §4.6. Acceso: cambiano le esecuzioni con osservatori da registro, non quelle con
   soli sensori dichiarati (che restano a p = 0,5 se (a) e' spento): elenco solo da una sonda.

(b2) aggiunge a (b1) la chiave di registro, il registro delle stime e un test di completezza: non pianificata qui
(nessun dato per sensore da scrivere). (c) non e' pianificabile senza dati RCS e `sigma_ref` (§2.3): il primo passo
sarebbe una ricerca (`oc-researcher`) delle RCS pubblicate dei 65 aerei, con la regola "nessun valore senza fonte".

---

## 5. Rischi e limiti

- **R-1 — Piu' di meta' della fotografia cambia all'accensione** (752 su 1219 con 0,2, §1.7). La lettura e' per
  famiglie (PB-4), non riga per riga: un errore del motore che cambiasse qualche esecuzione in piu' sarebbe mascherato.
  Mitigazione: l'elenco `changed_list` della sonda del blocco 2 e' l'esito atteso esatto del blocco 3 (stesso codice,
  stesso interruttore, meno le unita' fissate da PB-6); ogni scarto e' un'anomalia. La fotografia nuova, se
  installata, non permette piu' di confrontare con le esecuzioni a p = 0,5 se non spegnendo l'interruttore.
- **R-2 — Il valore resta una stima.** Nessuna fonte per 0,5 ne' per 0,2; si sposta la stima, non la si tara.
- **R-3 — Una costante per due significati** (§1.4): per scansione (sensori con dwell, `g` a parte) e per passaggio
  (sensori senza dwell). Con p = 0,2 un radar con dwell su un passaggio radente breve ha `g * 0,2`: potrebbe essere
  basso. Da rivedere con (b1) o con la legge cumulativa.
- **R-4 — Test di scenario tarati con p = 0,5**: 9 falliscono con 0,2 (Q-4, PB-6). Fissare l'interruttore spento nei
  test di orchestrazione e in S23-HOLD (PB-6 (A)) lascia quelle unita' della fotografia a p = 0,5: dichiararlo in
  `F4_Differenze_Scenari.md`. Altri test tarati potrebbero dipendere da p senza fallire (soglie larghe): non rilevabili
  dalla sonda.
- **R-5 — La metrica del pianificatore cambia** (PB-3 = S) senza che la fotografia lo registri (non e' esercitata);
  nessun consumatore la usa per decidere oggi [V], ma un consumatore futuro la leggera' con la p nuova.
- **R-6 — Forma della legge invariata**: resta la semplificazione monotona R^4 con taglio a R; la curva sigmoide
  (Swerling) e la Pd cumulativa (Koopman, Mallett-Brennan) restano rinviate.
- **R-7 — Il taglio di sessione** (due estrazioni per un passaggio a cavallo di due sessioni, manuale §9.1) e il
  rilevamento che non passa fra sessioni **non cambiano** con questa Proposta.
- **R-8 — Ordine con la fotografia S36** (PB-5): se si accende prima di installare la fotografia da 1219, il
  confronto mescola NEW e CHANGED.

---

## Appendice A — Script della sonda del blocco 2 (da salvare in `Analysis/Document/Rapporti/Sonde_Pd_Bordo/`)

Lo script usa la funzione d'accesso e l'interruttore del blocco 1: si esegue **dopo** il merge del blocco 1. E' la versione per il blocco 2 della sonda Q-1..Q-3 di §1.7 (che sostituiva direttamente la costante, perche' l'interruttore non esiste ancora). Controllo minimo prima dell'uso: con `off` il riepilogo deve dare `changed: 0` contro la cattura da 1219.

```python
"""Sonda PB (sola lettura, Proposta_Pd_Bordo_Portata.md, blocco 2): interruttore PD_EDGE_RECALIBRATION impostato IN
MEMORIA, cattura completa, confronto con una cattura di riferimento. Nessun file del repository modificato.

uso (dalla root del repo): PYTHONPATH=. <python> probe_pd_edge.py <on|off> <out_dir> [cattura_di_riferimento] [regex]
  riferimento di default: .ai-run/confronto_capture.json (cattura da 1219, interruttore spento)
  uscita: <out_dir>/capture.json, <out_dir>/report.json (changed_list = esito atteso del blocco 3), stdout = riepilogo
  le righe 'WARNING test failed' su stderr sono i test delle unita' con metodi espliciti che falliscono
"""
import json
import logging
import os
import sys
from collections import Counter

logging.disable(logging.CRITICAL)

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB

SWITCH = {'on': True, 'off': False}[sys.argv[1]]
OUT = sys.argv[2]
REF = sys.argv[3] if len(sys.argv) > 3 else '.ai-run/confronto_capture.json'
ONLY = sys.argv[4] if len(sys.argv) > 4 else None
os.makedirs(OUT, exist_ok=True)

ER.PD_EDGE_RECALIBRATION = SWITCH
NEW_EDGE = ER.pd_at_acquisition_range()
OLD_EDGE = ER.PD_AT_ACQUISITION_RANGE

# Spia sulle Detection: esito con la soglia in vigore e quello che la STESSA estrazione avrebbe dato con la soglia di
# prima (effetto di primo ordine: a cascata cambiano anche gli ingaggi e le estrazioni successive).
_inner = ER.resolve_engagement
STATS = Counter()


def spy(*args, **kwargs):
    result = _inner(*args, **kwargs)
    if result is not None:
        for d in result.detections:
            STATS['draws'] += 1
            if d.sensor_range <= 0 or d.distance_cpa > d.sensor_range:
                STATS['out_of_range'] += 1
                continue
            r4 = (d.distance_cpa / d.sensor_range) ** ER.PD_RANGE_EXPONENT
            den = 1.0 - (1.0 - NEW_EDGE) * r4
            factor = d.probability / den if den > 0 else 0.0
            old_detected = d.draw < factor * (1.0 - (1.0 - OLD_EDGE) * r4)
            STATS['in_range'] += 1
            STATS['detected_now'] += int(d.detected)
            STATS['detected_with_old_edge_same_draw'] += int(old_detected)
            STATS['lost'] += int(old_detected and not d.detected)
            STATS['gained'] += int(d.detected and not old_detected)
            band = min(int(r4 ** 0.25 * 10), 9)
            STATS[f'band_{band}_in_range'] += 1
            STATS[f'band_{band}_lost'] += int(old_detected and not d.detected)
    return result


ER.resolve_engagement = spy
current = SB.capture(ONLY, verbose=True)
SB.dump(current, os.path.join(OUT, 'capture.json'))
reference = SB.load(REF)['runs']

changed, unchanged, new = [], [], []
keys_changed, family_changed, family_total, outcome_changed = Counter(), Counter(), Counter(), []
delta = {}
for key, run in sorted(current['runs'].items()):
    family = key.split('/')[0]
    family_total[family] += 1
    if key not in reference:
        new.append(key)
        continue
    ref = reference[key]
    if ref == run:
        unchanged.append(key)
        continue
    changed.append(key)
    family_changed[family] += 1
    keys_changed.update(top for top in set(ref) | set(run) if ref.get(top) != run.get(top))
    if ref['force_outcomes'] != run['force_outcomes']:
        outcome_changed.append(key)
    row = delta.setdefault(family, Counter())
    for count in ('salvos', 'destroyed_events', 'interceptions', 'engagements'):
        row[count + '_before'] += ref['counts'].get(count, 0)
        row[count + '_after'] += run['counts'].get(count, 0)

missing = [] if ONLY else sorted(k for k in reference if k not in current['runs'])
s36_rows = []
for key in sorted(k for k in changed if k.split('/')[0] in SB.DETECTION_UNITS):
    for before, after in zip(reference[key].get('detections', []), current['runs'][key].get('detections', [])):
        # campi DETECTION_FIELDS: 0 osservatore, 1 bersaglio, 2 portata, 3 CPA, 4 Pd, 5 estrazione, 6 rilevato, 7 istante
        s36_rows.append([key, before[0], before[1], before[2], before[3], before[4], after[4], before[5],
                         before[6], after[6], before[7], after[7]])

report = {'switch': SWITCH, 'edge_now': NEW_EDGE, 'edge_before': OLD_EDGE, 'reference': REF,
          'runs': len(current['runs']), 'errors': current['errors'], 'changed': len(changed),
          'unchanged': len(unchanged), 'new': new, 'missing': missing, 'keys_changed': dict(keys_changed),
          'family': {f: [family_changed.get(f, 0), family_total[f]] for f in sorted(family_total)},
          'family_counts': {f: dict(c) for f, c in sorted(delta.items())}, 'outcome_changed': outcome_changed,
          'detections': dict(STATS), 's36_rows': s36_rows, 'changed_list': changed, 'unchanged_list': unchanged}
with open(os.path.join(OUT, 'report.json'), 'w', encoding='utf-8') as handle:
    json.dump(report, handle, indent=1, sort_keys=True)
print(json.dumps({k: v for k, v in report.items() if k not in ('changed_list', 'unchanged_list', 's36_rows')},
                 indent=1, sort_keys=True))
```

## Appendice B — Suite completa con l'interruttore acceso in memoria (blocco 2, punto 6)

Da salvare in `Analysis/Document/Rapporti/Sonde_Pd_Bordo/suite_pd_edge.py` ed eseguire dalla root del repo dopo il
merge del blocco 1 (`PYTHONPATH=. <python> .../suite_pd_edge.py on > <file>`). E' la versione per il blocco 2 della
sonda Q-4 (che sostituiva la costante). Atteso con `on`: fallisce `test_switch_is_off_by_default` (T1-1, per
costruzione) e i test di scenario di PB-6; con `off`: nessun fallimento.

```python
"""Sonda PB (sola lettura): suite completa con PD_EDGE_RECALIBRATION impostato IN MEMORIA; elenca i test falliti.
uso (dalla root del repo): PYTHONPATH=. <python> suite_pd_edge.py <on|off>"""
import os
import sys
import unittest

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER

ER.PD_EDGE_RECALIBRATION = {'on': True, 'off': False}[sys.argv[1]]
suite = unittest.defaultTestLoader.discover('Code/Dynamic_War_Manager/Source/Test', pattern='Test_*.py')

with open(os.devnull, 'w') as sink:
    result = unittest.TextTestRunner(verbosity=0, stream=sink).run(suite)

print(f'Ran {result.testsRun}, failures {len(result.failures)}, errors {len(result.errors)}, '
      f'skipped {len(result.skipped)}')
for test, trace in result.failures + result.errors:
    print('FAIL', test.id(), '|', trace.strip().splitlines()[-1][:300])
```
