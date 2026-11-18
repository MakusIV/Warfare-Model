# Proposta: scenari di permanenza breve con i dwell reali dei registri (serie S36, richiesta "S34" dell'utente del 2026-11-18)

Autore: `des-planner` (Opus), 2026-11-18. Base: `683b4c38` (branch `analysis/dce-dcs-persistence`), `D5_DWELL_TIME = True`
(`Logic/Engagement_Resolver.py:596`, commit `ef8f657e`). Fotografia: 1103 esecuzioni. Suite: `Ran 4925`.

Legenda delle etichette: **[V]** verificato sul codice o con una sonda di sola lettura su questo commit; **[C]** calcolo
(formula e numeri dichiarati); **[S]** stima. I percorsi `Logic/...`, `Test/...`, `Asset/...` sono relativi a
`Code/Dynamic_War_Manager/Source/`.

> **Nome del file e nome della serie.** Il file conserva il nome chiesto (`Proposta_Scenari_S34_...`), ma la serie si chiama
> **S36**: `S34` e `S35` sono gia' occupati da unita' della fotografia con altro significato (`S34-BAND` = fascia di quota VA,
> `Test/Test_Session_Scenarios_S34.py`; `S35-ADTGT` = bersagli intercettabili BI) [V: `Test/Scenario_Baseline.py:423-430`].
> Il nome `S34-BAND` della bozza coincide addirittura con un'unita' esistente. Decisione S36-1.

---

## 0. Sintesi

**Che cosa si aggiunge.** Un modulo di test nuovo, `Test/Test_Session_Scenarios_S36.py`, con **cinque unita' in coda a
`Scenario_Baseline.UNITS`** (nomi stabili, 4 semi ciascuna, **116 esecuzioni NEW**), in cui i bersagli restano nel volume
dell'osservatore MENO del periodo di rivisita **letto dal registro** (`dwell_time_s` della DW-9): passaggio radente (leva A),
taglio alla fine della sessione (leva B), osservatore mobile (leva C, AWACS), unione FP-10 di due passaggi brevi, estremi
della banda di incertezza. Piu' **7 test unitari** fuori dalla fotografia (sensore vincente su un record reale a due
sensori; metriche di rilevamento del pianificatore con i dwell reali). Nessuna riga del motore cambia, nessun interruttore
nuovo, nessun dato dei registri toccato.

**Il punto critico scoperto con le sonde: la fotografia non vede la D-5 con i dwell reali.** La fotografia registra salve,
danni, munizioni, carburante, posture, esiti di forza; **non registra le `Detection`** [V: `Test/Scenario_Baseline.py:536-635`].
Con i dwell reali una permanenza `< dwell` **non produce mai una salva**: il tempo di reazione di ogni tiratore e' maggiore
del suo dwell (unica eccezione la Shilka, 5,1 s contro 7,3 s) e, sul bordo del volume, il bersaglio e' comunque fuori dalla
portata dell'arma (§1.4) [V]. Quindi, senza cambiare lo strumento, le 116 esecuzioni nuove sarebbero **identiche fra
interruttore acceso e spento** nella fotografia (sonde P-3/P-4/P-8: riassunti identici) e la "serie dentro la fotografia"
proteggerebbe solo il fatto che "non succede niente". **Raccomandazione (decisione S36-2): registrare le `Detection` nel
riassunto, SOLO per le unita' S36** (voce nuova `detections`, opzionale per unita'): le 1103 esecuzioni esistenti restano
identiche byte per byte per costruzione, e la fotografia diventa un guardiano reale della legge con i dati reali.

**Fattibilita' delle leve (tutte verificate con sonde) [V].**

| Leva | Esempio verificato | Permanenza misurata | g |
|---|---|---|---|
| A, passaggio radente | ZSU-57-2 (vista 6 km, 3,2 s), A-10C a 3000 m, 155,56 m/s, scostamenti 5194,66 / 5191,32 / 5188,93 / 5172,25 m | 1,6 / 2,88 / 3,52 / 6,4 s | 0,5 / 0,9 / 1 / 1 |
| B, taglio della finestra | stessa ZSU, 3 A-10C che entrano 1 / 3 / 10 s prima della fine (sessione di 120 s) | 1,0 / 3,0 / 10,0 s | 0,3125 / 0,9375 / 1 |
| C, osservatore mobile | E-3A (400 km, 10 s) a 208,3 m/s contro MiG-29S a 255,6 m/s in verso opposto | 5,0 s (velocita' relativa 463,9 m/s) | 0,5 |

La geometria di A e' "stretta" (il bersaglio sfiora la sfera a pochi metri dal bordo) ma **non fragile**: il calcolo e'
analitico (`range_intervals`, equazione di secondo grado) e le permanenze escono esatte alla sesta cifra [V]. Una sola
eccezione: `g = 1,0` esatto sta sul confine del `min` e va evitato (si usa 1,1; decisione S36-4).

**Effetto atteso sul confronto**: `UNCHANGED (1103)`, `NEW (116)`, 0 `CHANGED`, 0 `MISSING`. **Suite attesa**: `Ran 4961`
(4925 + 36). **Tempo aggiunto** [V, misurato con le sonde]: ~0,05-0,2 s per esecuzione, in tutto **< 30 s** sul confronto e
sulla suite (budget dichiarato: <= 120 esecuzioni nuove, <= +30 s, <= +1 MB di fotografia).

**Esecutore consigliato**: `des-developer` (Sonnet high), 6 blocchi piccoli; ~1000 righe, quasi tutte di test.

---

## 1. Problema e comportamento attuale

### 1.1 La richiesta

L'utente (2026-11-18) vuole scenari con bersagli che restano nel volume **meno** del `dwell_time_s`, con i **dwell reali** dei
registri, **dentro la fotografia** (unita' nuove in coda, come S32-DWELL; nessuna esecuzione esistente deve cambiare nome ne'
esito), con la disciplina di S32: comportamento qualitativo o strutturale (relazioni fra varianti), mai un numero calibrato.
Il motivo: le sonde S-4 e S-5 (`Analysis/Document/Rapporti/Sonde_Dwell_D5/LEGGIMI.md`) hanno dato 1103 identiche con la
legge accesa, ma delle 93 chiamate con `g < 1` della S-5, 77 hanno `g = 0` con Pd gia' 0 (bersaglio fuori portata) e 16 sono
di S32 con un dwell di prova da 600 s (`s5/stats.json`, `g_below_1`) [V]: **nessuna esecuzione fotografata mette alla prova
la legge con un dwell reale**.

### 1.2 Che cosa fa il codice [V]

- **Legge** (`Logic/Engagement_Resolver.py`): `detection_probability(d, R, f) = f (1 - 0,5 (d/R)^4)` per `d <= R`
  (`:1220`, `PD_AT_ACQUISITION_RANGE = 0.5` a `:553`); `dwell_factor(e, dwell) = min(1, e / dwell)` (`:1282`); il fattore entra
  in `f` (`_detect_direction`, `:2356-2357`; `_detect_passes`, `:2576-2578`). **Nessuna estrazione nuova**: le estrazioni
  sono quelle di prima, solo la soglia cambia (verificato anche nelle sonde: stesse `draw` a interruttore acceso e spento).
- **Raggio estratto e istante**: `detection_radius(draw, R, f)` (`:1250`) si riduce con `f`; quindi con `g < 1` un
  rilevamento che avviene comunque puo' avvenire **piu' tardi** (sonda P-4: 118,15 s contro 119,07 s) [V].
- **Permanenza di un passaggio**: `max(0, min(end, window.t_end) - start)` (`:2347`; `:2577` per piu' passaggi), dove
  `(start, end)` e' l'intervallo **unito** del bersaglio nella sfera propria (`_own_passes`, `:2509`; `_join_passes`,
  `:1324`). L'inizio non e' ritagliato all'inizio della finestra (DW-4), ma i tratti di presenza cominciano a `t0` e finiscono
  a `session_end` (`Logic/Session_Simulator.py:2393`, `MA.movement_legs(movement, t0, session_end)`): una sessione che
  finisce mentre il bersaglio e' dentro taglia la permanenza (leva B).
- **Unione FP-10**: due intervalli separati da un'uscita `<= dwell` diventano UN passaggio **dall'inizio del primo alla fine
  dell'ultimo** (`:1339-1345`, `joined[-1]` a `:1342`): la permanenza unita e' l'**arco totale, uscita compresa**, non la somma dei due passaggi
  (discordanza con la bozza, §1.7). Senza dwell (interruttore spento) nessuna unione.
- **Lettore del dwell**: `registry_dwell_time` (`:1307`) chiama `observer.detection_dwell_time(mode)` senza `range_type`, cioe'
  con `acquisition_range`: il sensore e' quello con la portata di acquisizione MAGGIORE (`Asset/Mobile.py:1692-1735`).
  `_dwell_of` (`:2498`) sceglie il modo dal bersaglio (`'air'` per un aereo in volo).
- **Accensione in sessione**: `Session_Simulator.engage` passa il lettore solo con `ER.D5_DWELL_TIME` vero
  (`Logic/Session_Simulator.py:2792-2794`) e chiama `ER.resolve_engagement` come attributo di modulo (`:2801`, unico punto di
  chiamata; import `:783`). E' il punto che i test sostituiscono con una spia (S32, S33).
- **Sfera 3D senza orizzonte**: `range_intervals` risolve `|Δr + Δv s|^2 = R^2` in 3D (`Logic/Contact_Scheduler.py:874`):
  a 3000 m di quota la sezione orizzontale della sfera della ZSU (6 km) ha raggio `sqrt(6000^2 - 3000^2) = 5196,15 m` [C].

### 1.3 Che cosa registra la fotografia [V]

`summarize_run` (`Test/Scenario_Baseline.py:536-635`) registra intervallo della sessione, forze, parametri, esiti di forza
(con `force_ratio`, `unanswered_fraction`), stato finale degli asset, munizioni, intercettazioni, carburante, eventi di
danno/munizioni/intercettazione, posture, ETA. **Le `Detection` (`Logic/Engagement_Resolver.py:772`) non ci sono**: il
docstring lo dichiara per la D-5 (`:176-184`, "i `Detection` non sono registrati"). Il registratore `_Recorder` (`:640`)
sostituisce `run_session` e vede solo il `SessionOutcome`; il `capture` (`:685`) crea un registratore per unita' (`:708`).
`--ignore <voce>` e' generico sulle voci di primo livello (`_without_keys`, `:794`). Nessun test unitario di
`Scenario_Baseline` esiste [V: `grep`].

Conseguenza (sonde P-3, P-4, P-8): con la legge accesa o spenta i **riassunti sono identici** in tutte le geometrie di
permanenza breve, anche quando i rilevamenti cambiano.

### 1.4 Perche' nessun tiratore spara su un passaggio piu' breve del suo dwell [V]

Un tiratore lancia solo se `t_ready = istante del rilevamento + profilo di reazione <= fine del passaggio` (FP-3 (a),
`Logic/Engagement_Resolver.py:2379-2383` e `:2597-2602`); con `g < 1` il passaggio dura meno del dwell, quindi serve
`reazione < dwell`. Valori letti dai registri e da `Context/Reaction_Profile.profile_for_asset` (sonda P-1):

| Osservatore | Portata aria (acquisizione) | dwell [s] | Reazione totale [s] | Puo' sparare con g < 1? |
|---|---|---|---|---|
| ZSU-57-2 (vista) | 6 km | 3,2 | 5,1 | no |
| M163-VADS (vista) | 6 km | 3,2 | 5,1 | no |
| 9K35-Strela-10 (TVD) | 10 km | 3,2 | 5,6 | no |
| Strela-1-9P31 (TVD) | 8 km | 3,2 | 5,6 | no |
| M6-Linebacker, MIM-72G (TVD) | 12 / 10 km | 3,2 | 13,1 | no |
| 9K331-Tor | 25 km | 3,0 | 6,5 (`Reaction_Profile.py:170`) | no |
| 9A33-Osa | 30 km | 1,82 | 26,0 | no |
| 2K22-Tunguska | 18 km | 1,82 | 6,1 | no |
| Flakpanzer-Gepard / MIM-115-Roland | 15 / 18 km | 1,0 | 5,1 / 14,1 | no |
| 2K12-Kub | 75 km | 3,5 | 26,1 | no |
| 9K37-Buk | 85 km | 9,0 | 27,1 | no |
| S-300PS | 150 km | 12,0 | 28,0 (`:178`) | no |
| **ZSU-23-4-Shilka** | 20 km | 7,3 | **5,1** | solo tra 5,1 e 7,3 s di permanenza |
| navi (es. FFG-46, SPS-49) | 350 km | 5,0 | 31,0 (ripiego) | no |

Anche per la Shilka un passaggio radente avviene a ~20 km, ben oltre la portata del cannone: l'unico caso in cui la legge con
i dwell reali tocca una salva e' artificiale (bersaglio gia' dentro l'inviluppo del cannone a `t0` e sessione piu' corta di
7,3 s). La sonda P-8 lo ha provato: 8 semi con un A-10C e 4 semi con quattro A-10C, sessione di 5,5 s (`g = 0,753`): la
Shilka spara sempre a 5,1 s e **i riassunti restano identici** fra acceso e spento (le estrazioni che cadrebbero fra `g·Pd` e
`Pd` riguardano bersagli a cui la Shilka non spara). Per questo la variante "SHORT" e' scartata (§2.3).

Lo stesso vale per la percezione condivisa (`seen_by`, `Logic/Engagement_Resolver.py:4141-4200`): nelle sonde non cambia ne'
`force_ratio` ne' `unanswered_fraction` [V: riassunti identici].

### 1.5 Sonde eseguite (sola lettura, interprete `.direnv/python-3.12/bin/python3`, `PYTHONPATH=.`)

Copie in `.ai-run/sonde_s36/` (cartella ignorata da git; alcuni script includono con `exec` quelli precedenti dal percorso
dello scratchpad della sessione: per rieseguirli sostituire il percorso con `.ai-run/sonde_s36/`).

| Sonda | Contenuto | Esito |
|---|---|---|
| P-1 `p1_registry.py` | portate, dwell, reazioni, velocita' di 19 veicoli, 11 aerei, 7 navi | tabella di §1.4; A-10C `speed['nominal'] = 155,5556 m/s` (max 195,83) |
| P-2 `p2c.py`, `p2d.py` | record con due sensori a portata aria e un dwell | **nessuno** (i record a due sensori sono tutti aerei senza dwell) |
| P-3 `p3_graze.py` | leva A, ZSU + 4 A-10C, acceso/spento | permanenze 1,6 / 2,88 / 3,2 / 6,4 s; `p_on = g·p_off`; stesse estrazioni; nessuna salva |
| P-4 `p4_cut.py` | leva B, sessione di 120 s | permanenze 1,0 / 3,0 / 10,0 s; riassunti identici; istante di rilevamento posticipato con `g < 1` |
| P-5, P-8 `p5_shilka.py`, `p8_short.py` | Shilka, sessione di 5,5-12 s | salve a 5,1 s; riassunti identici acceso/spento in tutti i semi provati |
| P-6, P-12 `p6_families.py`, `p12_band.py` | 6 famiglie a terra/mare + E-3A, valore raccomandato ed estremi della banda | permanenza = dwell/2 in tutte; Pd = 0,25 (g = 0,5); estremi come in §4.5; nessuna salva |
| P-7 `p7_passes.py` | due passaggi di 1 s con uscita di 1 s e di 5 s | acceso + uscita 1 s: **un** passaggio, permanenza 3,0 s, g = 0,9375; uscita 5 s: due passaggi da 1,0 s, g = 0,3125 ciascuno |
| P-10, P-13, P-14 | `Path.compute_detection_metrics` con minacce reali | §2.5 |
| P-11 `p11_graze_final.py` | GRAZE definitiva (g 0,5 / 0,9 / 1,1 / 2,0; varianti off/on/band_min/band_max), 4 semi | tutte le asserzioni di §4.3 vere; 16 esecuzioni in 3,1 s |
| P-15 `p15.py` | F-16C Block 52d con dwell di prova su radar e TVD | `detection_dwell_time('air') = 2,0` (TVD, 110 km), con `tracking_range` 6,0 (radar, 150 km); `registry_dwell_time` = 2,0 |
| P-16 `p16_final_names.py` | S36-CUT con i nomi definitivi (`obs`, `casA/B/C`, semi `S36-CUT-0..3`) | permanenze 1,0 / 3,0 / 10,0; `p_on/p_off` = 0,3125 / 0,9375 / 1; nessuna salva; rilevamento posticipato in `S36-CUT-0`, `casB0` (119,07 contro 118,15 s); 8 esecuzioni in 0,94 s |

Nota: P-3..P-15 usano nomi di asset provvisori (`ad0`, `cas0_0`...); le estrazioni dipendono dal `session_id` e dall'ordine
delle finestre, non dai valori geometrici: P-16 conferma con i nomi definitivi le proprieta' di S36-CUT e P-17
(`p17_graze_obs.py`, osservatore `Red-Line/obs0`) quelle di S36-GRAZE (stesse Pd ed estrazioni di P-11, asserzioni vere).
Le altre unita' non hanno asserzioni che dipendono dai semi.

### 1.6 Fattibilita' delle tre leve: numeri

Notazione: `R` portata 3D, `dz` differenza di quota, `v` velocita' relativa, `τ` permanenza voluta; la retta del bersaglio
ha scostamento laterale `h = sqrt(R^2 - dz^2 - (v τ / 2)^2)` dal centro (corda `L = v τ`) [C].

**Leva A (radente).** ZSU-57-2 a terra, A-10C a 3000 m (`dz = 3000`), `v = 155,5556 m/s`, `dwell = 3,2 s`: `v · dwell = 497,8 m`.
Con `g = 0,5 / 0,9 / 1,1 / 2,0` -> `τ = 1,6 / 2,88 / 3,52 / 6,4 s` -> `h = 5194,662 / 5191,322 / 5188,935 / 5172,255 m` [C, V].
Il bersaglio passa 1,5-24 m dentro il bordo orizzontale (5196,15 m). Nessuna fragilita' numerica: permanenze esatte a 1e-6
(P-11). Vale per ogni famiglia: corde da 233 m (Tor, g = 0,5) a 1,1 km (E-3A, velocita' relativa).
**Leva B (taglio).** Ingresso a `t = D - k`: origine `x = -(5196,152 + (D - k) v)`, `y = 0`. Con `D = 120 s`, `k = 1 / 3 / 10`:
`x = -23707,264 / -23396,152 / -22307,264 m` [C]; permanenze 1,0 / 3,0 / 10,0 s [V]. Non dipende dalla portata.
Avvertenza: la Pd usa la distanza minima **dentro la finestra** (qui quella a fine sessione, 5865,8 / 5600,7 / 4717,4 m [V]),
quindi la Pd cresce con `k` anche per la distanza: l'asserzione corretta e' sul rapporto `p_on / p_off = g`, non sulla
monotonia.
**Leva C (osservatore mobile).** Con un osservatore a terra o una nave la velocita' propria e' trascurabile (nave 12-14 m/s);
l'unico osservatore mobile con dwell e velocita' paragonabile al bersaglio e' l'AWACS. E-3A a 9000 m e 208,333 m/s verso +x,
MiG-29S a 3000 m e 255,556 m/s verso -x: `v = 463,889 m/s`, `dz = 6000 m`, `τ = 5 s` -> `h = 399953,316 m`, incontro a
`t = 200 s` con il MiG che parte da `x = 92777,778 m` [C]; permanenza 4,9999999996 s [V].

### 1.7 Discordanze fra la bozza e il codice

| # | Bozza | Codice / sonde | Conseguenza nel piano |
|---|---|---|---|
| 1 | serie "S34-..." (con un'unita' `S34-BAND`) | `S34-BAND` e `S35-ADTGT` esistono gia' [V] | serie **S36** (decisione S36-1) |
| 2 | A-10C ~190 m/s [da verificare] | `speed['nominal'] = 155,556 m/s`, max 195,83 [V]; in ingaggio il moto e' alla crociera (G3) | geometrie con 155,556 m/s, premessa nei test |
| 3 | "nessun rilevamento in piu'", "meno lanci o ingaggi ritardati" per i tiratori | nessun tiratore puo' lanciare su un passaggio < dwell (§1.4); nessun lancio in nessuna variante [V] | l'asserzione sui lanci diventa "nessuna salva" (premessa strutturale); la legge si verifica sulle `Detection` |
| 4 | dentro la fotografia | le `Detection` non sono registrate (§1.3) | voce `detections` per le sole unita' S36 (decisione S36-2) |
| 5 | g = 1,0 come variante | `min(1, e/dwell)` sul confine: rischio di `0,9999999` | g = **1,1** (decisione S36-4) |
| 6 | PASSES: "le permanenze si sommano" | l'unione da' l'**arco totale, uscita compresa** (`:1339-1345`; P-7: 1 + 1 + 1 = 3,0 s, non 2,0) | asserzione sull'arco |
| 7 | WINNER con M6 Linebacker o un altro record reale con TVD e radar | **nessun** record con due sensori a portata aria e un dwell (P-2); l'M6 ha solo il TVD | test unitario su un record reale a due sensori (F-16C Block 52d) con dwell **di prova** (decisione S36-5) |
| 8 | ROUTE: "verifica se la rotta scelta cambia" | la scelta usa `(detection_exposure_s, total_danger, total_length)` o `(total_danger, total_length)` (`Logic/Air_Route_Manager.py:1301-1311`): **la Pd non entra mai** [V]; il pianificatore non e' nella fotografia [V] | test unitari fuori dalla fotografia; un test fissa che la chiave di scelta non dipende dall'interruttore (decisione S36-6) |
| 9 | ROUTE: Tor 3 s e Buk 9 s in un attraversamento | nel cilindro del pianificatore, se il raggio e' la portata piena, un attraversamento con `Pd > 0` ha corda `>= 2·quota` (fuori dalla sfera 3D `Pd = 0`, `:1110-1114`); con Tor a 3000 m e corda di 1,5 s Pd = 0 sia acceso sia spento [V] | Tor a 150 m e Buk a 500 m; caso principale S-300PS a 100 m (cilindro limitato dall'orizzonte, 50434,8 m) |
| 10 | leva B "o la rotta finisce dentro il volume" | dopo la fine della rotta l'asset resta presente fermo fino a fine sessione (`Logic/Session_Simulator.py:2380-2393`): la permanenza cresce | solo il taglio alla fine della sessione |
| 11 | BAND con "patch del registro solo in test" | `F.declare_dwell` scavalca sull'istanza, senza stato globale (`Test/Scenario_Fixtures.py:306`); un patch del registro nel processo unico di `Scenario_Baseline` rischia di trapelare | BAND con `declare_dwell` dei valori della banda |
| 12 | riferimenti `:1282`, `:2467`, `:2498`, `Air_Route_Manager.py:1098-1212`, `:1132` | esatti [V] | — |

---

## 2. Alternative e raccomandazione

### 2.1 Dove si vede la legge nella fotografia

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| R1 nessun cambio allo strumento | le unita' S36 entrano in `UNITS` come S32 | nessuna riga fuori dai test | le 116 esecuzioni registrano solo "nessuna salva": acceso e spento identici; un cambio ai dwell del registro o alla legge **non** cambierebbe la fotografia |
| **R2 voce `detections` per le sole unita' S36** (raccomandata) | `Scenario_Baseline` registra, per le unita' elencate in `DETECTION_UNITS`, le `Detection` di ogni `EngagementResult` (14 campi in ordine fisso) | la fotografia vede permanenza, dwell, Pd, estrazione, istante: un cambio della legge, dei dwell del registro o della geometria del volume salta fuori come `CHANGED`; 1103 esistenti identiche per costruzione (il loro registratore non cambia); `--ignore detections` gia' funziona | ~60 righe nello strumento; la fotografia cresce di poco (~0,7 MB) |
| R3 fuori dalla fotografia | solo test | nessun file di strumento | contro la richiesta dell'utente |

**Raccomandazione: R2.** E' l'unico modo di avere "dentro la fotografia" qualcosa che dipende dai dwell reali. Non e' una
regola del motore (strumento di test): nessun interruttore. Registrare le `Detection` per TUTTE le unita' cambierebbe le 1103
(voce nuova) e richiederebbe una fotografia nuova: escluso.

### 2.2 Composizione della serie (bozza -> proposta)

| Bozza | Proposta | Nella fotografia | Esecuzioni | Motivo del cambio |
|---|---|---|---|---|
| 1 S34-GRAZE | **S36-GRAZE**: ZSU-57-2 + 4 A-10C con g 0,5 / 0,9 / 1,1 / 2,0; varianti `off`, `on`, `band_min`, `band_max` | si' | 16 | g = 1,1 al posto di 1,0; estremi della banda della vista qui (assorbe la parte "vista" di BAND) |
| 2 S34-CUT | **S36-CUT**: ZSU-57-2 + 3 A-10C che entrano 1 / 3 / 10 s prima della fine; `off`, `on` | si' | 8 | asserzione sul rapporto `g`, non sulla monotonia (§1.6) |
| 3 S34-FAMILIES | **S36-FAMILIES**: Strela-10, Tor, Buk, S-300PS, P-37, FFG-46 (SPS-49), E-3A (leva C); una variante per famiglia, g = 0,5 | si' | 28 | "meno lanci" -> "nessuna salva" (§1.4); niente varianti spente (la Pd spenta si ricalcola dai campi della `Detection`) |
| 4 S34-BAND | **S36-BAND**: le 6 famiglie con banda, estremi `min` e `max` (12 varianti) | si' | 48 | `declare_dwell` invece del patch del registro |
| 5 S34-PASSES | **S36-PASSES**: un A-10C, due passaggi da 1 s con uscita di 1 s (unione) o 5 s (nessuna unione); `join_off/on`, `split_off/on` | si' | 16 | permanenza unita = arco con l'uscita |
| 6 S34-WINNER | test unitari in `Test/Test_Dwell_Data.py` (F-16C Block 52d, dwell di prova) | no | — | nessun record reale adatto (§1.7 #7) |
| 7 S34-ROUTE | test unitari in `Test/Test_Threat_AA_Factory.py` | no | — | il pianificatore non e' nella fotografia (§1.7 #8) |
| — | SHORT (Shilka, sessione < 7,3 s) | **scartata** | — | §2.3 |

Totale: **116 esecuzioni NEW**, 5 unita'.

### 2.3 Variante con salva (Shilka in sessione corta): scartata

Pro: sarebbe l'unico caso con un evento di tiro legato al dwell reale. Contro: geometria artificiale (aereo che compare a
1,5 km dalla Shilka in una sessione di 5,5 s), effetto che dipende dai semi e **non osservato** in 12 semi provati (P-8).
Con R2 non serve: la fotografia vede gia' le `Detection`. Se l'utente la volesse comunque: nuova decisione.

### 2.4 Sensore vincente (WINNER)

| Opzione | Pro | Contro |
|---|---|---|
| W0 niente (copre gia' `Test_Mobile.TestDetectionDwellTime.test_dwell_follows_the_sensor_of_detection_range`, `Test/Test_Mobile.py:1441`, con uno stub) | zero lavoro | nessun record reale, limite `range_type` non documentato da un test |
| **W1 due test unitari su F-16C Block 52d** (raccomandata): radar aria 70 km (inseguimento 150), TVD aria 110 km (inseguimento 90) [V]; dwell DI PROVA 6,0 s sul radar e 2,0 s sul TVD con `patch.dict` (ripristinato) | record reale; fissa il limite noto: con `tracking_range` vince il radar (6,0) ma `registry_dwell_time` legge sempre il vincitore di acquisizione (2,0) | i dwell sono di prova (gli aerei non hanno dwell, DW-9 decisione 1) |
| W2 nella fotografia con un aereo osservatore | — | dwell di prova dentro la fotografia, contro lo spirito della richiesta (dwell reali) |

### 2.5 Metriche del pianificatore (ROUTE)

Fatti [V, P-13]: la chiave di scelta del percorso non legge `max_detection_probability` (`:1301-1311`): **la rotta scelta non
puo' cambiare con la D-5**. La metrica cambia solo se l'attraversamento dura meno del dwell **e** ha `Pd > 0`, il che con il
cilindro a portata piena richiede quota bassa (corda minima `2 · quota`); con il cilindro limitato dall'orizzonte radar
(bassa quota contro un radar a lunga portata) basta un passaggio radente qualunque.

| Minaccia (asset reale, `build_detection_threat`) | Quota [m] | Raggio cilindro [m] | τ [s] | Pd spenta | Pd accesa |
|---|---|---|---|---|---|
| S-300PS | 100 | 50434,8 (orizzonte) | 6,0 | 0,99361 | 0,49681 (g = 0,5) |
| S-300PS | 100 | 50434,8 | 24,0 | 0,99363 | 0,99363 |
| 9K331-Tor | 150 | 25000 | 2,5 | 0,50002 | 0,41669 (g = 0,833) |
| 9K37-Buk | 500 | 85000 | 7,5 | 0,50001 | 0,41668 (g = 0,833) |
| 9K331-Tor | 3000 | 25000 | 1,5 | 0,0 | 0,0 (fuori dalla sfera 3D) |

**Raccomandazione**: 5 test unitari in `Test_Threat_AA_Factory.py` (ha gia' `_AssetStub` con i lettori reali, `:68`), fuori
dalla fotografia; il pianificatore entrera' in una fotografia solo con un'unita' dedicata, da proporre a parte.

---

## 3. Decisioni aperte per l'utente (una per volta)

**S36-1 — Nome della serie.**
Domanda: le unita' nuove si chiamano `S36-...`? Esempio: la bozza chiama `S34-BAND` la prova degli estremi della banda; ma
`S34-BAND` e' gia' l'unita' VA della fascia di quota (32 esecuzioni nella fotografia). Due unita' con lo stesso nome farebbero
fallire la cattura (`duplicate scenario key`). Opzioni: (a) **S36** con file `Test_Session_Scenarios_S36.py`; (b) un altro
numero. **Raccomandazione: (a).** Il nome di questa Proposta resta quello chiesto.

**S36-2 — Registrare le `Detection` nella fotografia, solo per le unita' S36.**
Domanda: si aggiunge allo strumento la voce `detections` per le unita' S36? Esempio: in S36-GRAZE il primo A-10C passa 1,6 s
nel volume della ZSU; spento Pd = 0,5004, acceso Pd = 0,2502. Senza la voce la fotografia registra per entrambe "nessuna
salva, nessun danno" e le due esecuzioni sono identiche: se domani qualcuno cambiasse il 3,2 s della ZSU nel registro, il
confronto direbbe "identiche". Con la voce, quel cambio diventa `CHANGED` su S36. Opzioni: R1, **R2**, R3 (§2.1).
**Raccomandazione: R2.**

**S36-3 — Quali unita' nella fotografia, e quanti semi.**
Domanda: si tengono le cinque unita' (GRAZE, CUT, PASSES, FAMILIES, BAND) con 4 semi ciascuna (116 esecuzioni)? Esempio:
BAND da sola vale 48 esecuzioni (12 estremi x 4 semi); le Pd dipendono solo dalla geometria e dal dwell, i semi decidono solo
"rilevato si'/no". Opzioni: (a) **cinque unita', 4 semi** (116); (b) FAMILIES e BAND con 2 semi (80); (c) senza BAND (68).
**Raccomandazione: (a)**: il costo e' trascurabile (< 30 s), e 4 semi come S32/S34/S35 danno rilevamenti si' e no in ogni
famiglia. SHORT resta esclusa (§2.3).

**S36-4 — g = 1,1 invece di 1,0 nella geometria radente.**
Domanda: la terza corda di GRAZE si fissa a g = 1,1 (permanenza 3,52 s) invece che esattamente sul confine (3,20 s)?
Esempio: con 3,20 s la permanenza calcolata puo' valere 3,1999999999 e allora g = 0,99999999997: la Pd differisce dalla legge
di prima all'undicesima cifra e l'asserzione "g = 1 riproduce esattamente la legge di prima" diventa casuale. Con 1,1 e 2,0
la riduzione esatta e' provata due volte. **Raccomandazione: 1,1.**

**S36-5 — Sensore vincente.**
Domanda: si scrive WINNER come due test unitari su F-16C Block 52d con dwell di prova (W1)? Esempio: radar 70 km e TVD
110 km in acquisizione; con dwell di prova 6 s (radar) e 2 s (TVD) il lettore restituisce 2 s; con `tracking_range` vincerebbe
il radar (150 km) ma il motore legge sempre 2 s: e' il limite noto, che il test fissa. Opzioni: W0, **W1**, W2 (§2.4).
**Raccomandazione: W1.**

**S36-6 — Metriche del pianificatore.**
Domanda: ROUTE come 5 test unitari fuori dalla fotografia, con un test che fissa "la rotta scelta non dipende dalla D-5"?
Esempio: S-300PS a 100 m, attraversamento di 6 s al bordo del cilindro limitato dall'orizzonte: Pd 0,994 spenta, 0,497 accesa,
ma la chiave `(detection_exposure_s, total_danger, total_length)` e' la stessa. Opzioni: (a) **test unitari** (raccomandata);
(b) anche un'unita' di fotografia del pianificatore (Proposta separata). **Raccomandazione: (a)**; se si vuole che la D-5
pesi nella scelta della rotta, e' una regola nuova del pianificatore (interruttore, Proposta separata).

**S36-7 — Esecutore.**
Opzioni: (a) **`des-developer` (Sonnet high)**; (b) `oc-developer` (DeepSeek V4 Pro high) a blocchi. Il lavoro e' quasi tutto
test con numeri gia' calcolati; serve precisione sui nomi stabili e sulla spia del resolver. **Raccomandazione: (a)**, come
indicato nel compito; (b) e' adatto se si vuole risparmiare (blocchi gia' piccoli).

---

## 4. Piano di intervento (per le opzioni raccomandate: S36, R2, 5 unita' x 4 semi, g = 1,1, W1, ROUTE unitari)

### 4.1 Vincoli comuni

- **Nessun file del motore** cambia (`Logic/`, `Asset/`, `Context/`, `Command/`), nessun registro di dati, nessun valore,
  nessun interruttore, nessuna fotografia installata. Si toccano solo: `Test/Scenario_Baseline.py`,
  `Test/Scenario_Fixtures.py` (solo docstring), `Test/Test_Session_Scenarios_S32.py` e `_S33.py` (solo docstring), il nuovo
  `Test/Test_Session_Scenarios_S36.py`, `Test/Test_Dwell_Data.py`, `Test/Test_Threat_AA_Factory.py`, e i documenti di §4.11.
- **Determinismo**: nessun `random`; le sessioni usano solo l'RNG di sessione (`F.run` -> `run_session`). Le spie chiamano
  l'originale e non estraggono nulla. L'ordine delle estrazioni non cambia (nessuna riga del motore cambia).
- **Interruttore**: ogni variante sostituisce `D5_DWELL_TIME` con `patch.object(ER_MODULE, 'D5_DWELL_TIME', switch)` attorno a
  costruzione ed esecuzione (come S32, `Test/Test_Session_Scenarios_S32.py:96`), con `ER_MODULE = sys.modules[ER.__name__]`.
  Il default resta `True` e non si tocca.
- **Logger**: le classi di scenario ereditano `(F.LoggerSilencer, unittest.TestCase)` (`Test/Scenario_Fixtures.py:216`);
  aiuti come funzioni di modulo; nessuna classe base condivisa che erediti da `unittest.TestCase`.
- **Import** sempre con il percorso completo `Code.Dynamic_War_Manager.Source...`.
- **Costanti**: tutte le geometrie (scostamenti, durate, origini) sono **geometria di test**, non dati; i dwell, le portate e le
  velocita' sono **copie dei registri** controllate da un test di premessa; gli estremi delle bande sono **valori di prova**
  presi dalla banda di incertezza dichiarata (Proposta_Dwell_Estensione_DW9.md §2.1-§2.4; `probe_dw9.py`, `VALUES`), non dati.
  Scriverlo nel docstring e nei commenti.
- **Nomi stabili**: in ogni `setUpClass` ciclo esterno sui semi, interno sulle varianti nell'ordine del dizionario
  `VARIANT_SPEC` (stesso `session_id` per tutte le varianti di un seme); seme `f'S36-<UNITA'>-{i}'`, `i = 0..3`. Le righe di
  `UNITS` usano `_by_occurrence(...)` con le varianti nello stesso ordine. Chiavi risultanti:
  `S36-GRAZE/S36-GRAZE-0/off`, ecc.

### 4.2 Blocco 1 — `Test/Scenario_Baseline.py`: voce `detections` per le unita' dichiarate

Modifiche (nessun cambio per le altre unita'):

1. Accanto a `_SS_MODULE` (`:241`): `_ER_MODULE = 'Code.Dynamic_War_Manager.Source.Logic.Engagement_Resolver'`.
2. Dopo `UNITS` (dopo il commento di `:436-440`):
   ```python
   # Unita' per cui il riassunto registra anche le `Detection` del risolutore (voce `detections`, S36: permanenza breve con i
   # dwell reali). Le altre unita' non la registrano: le loro esecuzioni restano identiche byte per byte.
   DETECTION_UNITS = frozenset({'S36-GRAZE', 'S36-CUT', 'S36-PASSES', 'S36-FAMILIES', 'S36-BAND'})
   # Campi di una `Engagement_Resolver.Detection`, nell'ordine in cui la voce `detections` li registra.
   DETECTION_FIELDS = ('observer_id', 'target_id', 'sensor_range', 'distance_cpa', 'probability', 'draw', 'detected',
                       'time', 'exposure_s', 'dwell_time_s', 'pass_index', 'pass_count', 'pass_start', 'pass_end')
   ```
3. Funzione nuova prima di `summarize_run`:
   ```python
   def detection_rows(results) -> List[List]:
       """Le `Detection` di una sessione: una riga (campi `DETECTION_FIELDS`) per rilevamento, nell'ordine dei risultati
       d'ingaggio e, dentro un risultato, nell'ordine del risolutore."""
       return [[getattr(detection, name) for name in DETECTION_FIELDS]
               for result in results for detection in result.detections]
   ```
4. `summarize_run(order, forces_a, forces_b, kwargs, outcome, detections=None)` (`:536`): se `detections is not None`,
   `summary['detections'] = detections` subito prima di `return norm(summary)` (`:635`); con `None` nessuna voce (forma di
   prima). Aggiornare il docstring.
5. `_Recorder.__init__(self, original, with_detections=False)`; in `__call__`, se `with_detections`:
   ```python
   er = importlib.import_module(_ER_MODULE)
   inner, results = er.resolve_engagement, []
   def spy(*args, **kwargs):
       result = inner(*args, **kwargs)
       if result is not None:
           results.append(result)
       return result
   with patch.object(er, 'resolve_engagement', spy):
       outcome = self.original(order, forces_a, forces_b, fire_control, **kwargs)
   ```
   e `summarize_run(..., detections=detection_rows(results))`; altrimenti il codice di prima, invariato. `inner` va letto
   **al momento della chiamata** (i test di S36 sostituiscono a loro volta `ER.resolve_engagement` con una spia attorno a
   `F.run`: la spia del registratore la avvolge e la catena chiama sempre l'originale).
6. `capture` (`:708`): `recorder = _Recorder(SS.run_session, with_detections=label in DETECTION_UNITS)`.
7. Docstring del modulo: nuova sezione dopo "Rilevamento per passaggio dopo la FP" (`:199-206`), testo:
   "## Permanenza breve con i dwell reali (S36)" — la serie S36 (`Proposta_Scenari_S34_Permanenza_Breve.md`) non cambia le
   esecuzioni esistenti; aggiunge in coda 5 unita' (S36-GRAZE 4 varianti, S36-CUT 2, S36-PASSES 4, S36-FAMILIES 7,
   S36-BAND 12; 4 semi): 116 esecuzioni nuove. Solo per le unita' di `DETECTION_UNITS` il riassunto ha la voce
   `detections` (righe `DETECTION_FIELDS` delle `Detection` del risolutore, catturate con una spia attorno a
   `Engagement_Resolver.resolve_engagement`); `--ignore detections` la esclude. Correggere anche la frase di `:177-178`
   ("i `Detection` non sono registrati") aggiungendo "(salvo le unita' S36, v. sotto)".

Verifica del blocco: `<python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare
Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json --only 'S32-DWELL|S33-PASSES'` -> 30 esecuzioni
IDENTICAL (le unita' S36 non esistono ancora; `DETECTION_UNITS` contiene etichette non ancora in `UNITS`, innocuo). Se
l'agente non ha il permesso di lanciarlo, lo fa la sessione principale.

### 4.3 Blocco 2 — modulo `Test/Test_Session_Scenarios_S36.py`, aiuti comuni e S36-GRAZE

**Docstring del modulo** (come S32): scopo (permanenza < dwell con i dwell del registro), disciplina (relazioni fra varianti),
tabella delle 5 unita', il fatto che nessuna salva e' possibile (§1.4, con i numeri), la voce `detections`, i valori di prova
della banda, rimando a questa Proposta.

**Import**: `math`, `sys`, `unittest`, `unittest.mock.patch`; `MissionRules` da `Command.Mission_Types`;
`Engagement_Resolver as ER`; `make_registry_fire_control` da `Logic.Fire_Control`; `Scenario_Fixtures as F`; `BOTH_HOLD` da
`Test.Test_Session_Scenarios_S10_S18`; `Scenario_Baseline as SB` (solo nel blocco 4).

**Costanti comuni** (commento: copia del registro [V, premessa nei test] oppure geometria di test):
```python
ER_MODULE = sys.modules[ER.__name__]
SEEDS_PER_SCENARIO = 4
DURATION = 600.0                          # durata delle sessioni [s], geometria di test
A10 = 'A-10C Thunderbolt II'
A10_LOADOUT = 'Maverick/Gun CAS'
A10_SPEED = 155.55555555555554            # speed['nominal'] del registro [m/s] (copia, test di premessa)
TARGET_Z = 3_000.0                        # quota degli A-10C [m], geometria di test
OBSERVER = 'Red-Line/obs0'                # osservatore a terra o in mare (prefisso 'obs')
ZSU = 'ZSU-57-2'
ZSU_RANGE = 6_000.0                       # portata aria (vista) del registro [m] (copia)
ZSU_DWELL = 3.2                           # dwell_time_s della vista del registro [s] (copia; STIMA [S] DW9-6)
HORIZONTAL_RADIUS = math.sqrt(ZSU_RANGE ** 2 - TARGET_Z ** 2)   # 5196,152 m a 3000 m di quota [C]
HOLD = MissionRules(roe='weapon_hold')    # gli A-10C non sparano: si isola il rilevamento
```

**Aiuti** (funzioni di modulo):
- `lateral_offset(sensor_range, height_difference, relative_speed, exposure_s) -> float`: `sqrt(R^2 - dz^2 - (v·τ/2)^2)`;
  docstring con la formula.
- `run_variant(session_id, build, switch) -> (outcome, results)`: come `Test_Session_Scenarios_S32.run_variant`
  (`:84-111`): dentro `patch.object(ER_MODULE, 'D5_DWELL_TIME', switch)` chiama `build()` che restituisce
  `(forces_a, forces_b, missions, duration)`, poi con `patch.object(ER, 'resolve_engagement', side_effect=spy)` esegue
  `F.run(session_id, forces_a, forces_b, make_registry_fire_control(), duration=duration, missions=missions,
  thresholds=BOTH_HOLD)`; `results` = risultati non None.
- `detections_of(results, observer_id, target_id=None) -> list`: le `Detection` dell'osservatore (e del bersaglio se dato).
- `expected_probability(detection) -> float`: `ER.detection_probability(detection.distance_cpa, detection.sensor_range,
  ER.dwell_factor(detection.exposure_s, detection.dwell_time_s))` (vale solo con `exposure_s` non None);
  `previous_probability(detection)` = `ER.detection_probability(distance_cpa, sensor_range)` se `distance_cpa <=
  sensor_range`, altrimenti 0.

**S36-GRAZE** (`TestS36Graze(F.LoggerSilencer, unittest.TestCase)`, leva A).
```python
GRAZE_SEEDS = [f'S36-GRAZE-{i}' for i in range(SEEDS_PER_SCENARIO)]
GRAZE_FACTORS = (('casA', 0.5), ('casB', 0.9), ('casC', 1.1), ('casD', 2.0))   # g con il dwell del registro
GRAZE_EXPOSURE = {p: g * ZSU_DWELL for p, g in GRAZE_FACTORS}                  # 1,6 / 2,88 / 3,52 / 6,4 s [C]
GRAZE_OFFSET = {p: lateral_offset(ZSU_RANGE, TARGET_Z, A10_SPEED, e) for p, e in GRAZE_EXPOSURE.items()}
#   = 5194,662 / 5191,322 / 5188,935 / 5172,255 m [C, V]
GRAZE_VARIANTS = {'off': (False, None), 'on': (True, None), 'band_min': (True, 1.75), 'band_max': (True, 6.0)}
#   (interruttore, dwell dichiarato sulla ZSU | None = registro); 1,75 e 6,0 = estremi della banda della vista, VALORI DI PROVA
```
Costruzione: Red `F.build_force('Red-Line', 'Red', [F.Unit('vehicle', ZSU, 1, origin=(0.0, 0.0), prefix='obs')])`; se il
dwell dichiarato non e' None, `F.declare_dwell(red.assets[OBSERVER], {'air': valore})`; Blue `F.build_force('Blue-CAS',
'Blue', [F.Unit('aircraft', A10, 1, origin=(-40_000.0, GRAZE_OFFSET[p], TARGET_Z), prefix=p, loadout=A10_LOADOUT) for p, _ in
GRAZE_FACTORS], mil_category=F.AIR_UNIT)` (id `Blue-CAS/casA0` ... `casD0`); missioni `F.missions_for(blue, [(40_000.0,
GRAZE_OFFSET['casA'])], mission_type='CAS', target=F.group_target('Red-Line'), rules=HOLD)` (ogni A-10C va a `(40 km,
proprio scostamento)`; `missions_for` ne fa 4 missioni, nessun problema [V]); forze `[blue]`, `[red]`, durata `DURATION`.
`VARIANTS = tuple(GRAZE_VARIANTS)`; riga di `UNITS`:
`('S36-GRAZE', 'Test_Session_Scenarios_S36', 'TestS36Graze', None, _by_occurrence('off', 'on', 'band_min', 'band_max'))`,
**in coda dopo `S33-PASSES`** (`:433-434`), con il commento
`# ── S36 (permanenza breve con i dwell reali, Proposta_Scenari_S34_Permanenza_Breve.md) — in coda, nomi stabili ──`.

Test (9; `p` = prefisso, `d` = `Detection` della ZSU sull'A-10C `p`, uno per sessione):
1. `test_premise_registry_values`: su asset costruiti con `F.make_vehicle`/`F.make_aircraft`: ZSU `detection_range('air')
   == ZSU_RANGE`, `detection_dwell_time('air') == ZSU_DWELL`; A-10C `speed['nominal'] == A10_SPEED` (assertAlmostEqual,
   places=9).
2. `test_premise_no_salvo`: nessun `ammunition_events` in nessuna variante e seme (passaggio piu' breve della reazione della
   ZSU, 5,1 s; A-10C in `weapon_hold`).
3. `test_exposure_is_the_chord_time`: in `on`, `band_min`, `band_max`: ogni `d` ha `pass_index is None`, `exposure_s` ≈
   `GRAZE_EXPOSURE[p]` (places=6), `dwell_time_s` = 3,2 / 1,75 / 6,0.
4. `test_probability_is_scaled_by_the_dwell_factor`: in `on`/`band_*`: `d.probability` ≈ `expected_probability(d)`
   (places=12) e ≈ `min(1, exposure/dwell) * d_off.probability` (places=12), con `d_off` della stessa sessione e dello stesso
   A-10C in `off`.
5. `test_same_draws_and_no_extra_detection`: per ogni seme, A-10C e variante accesa: `d.draw == d_off.draw` e `d.detected`
   implica `d_off.detected`; `d.distance_cpa == d_off.distance_cpa`. Premessa non vacua: sui 4 semi esiste almeno un
   A-10C rilevato in `off` e non in `band_max` (P-11, seme 0: `casB0`, estrazione 0,4328, Pd 0,5014 contro 0,2407).
6. `test_factor_one_reproduces_the_previous_law`: in `on`, per `casC` e `casD` (g >= 1): `probability == d_off.probability`,
   `detected == d_off.detected`, `time == d_off.time` (uguaglianza esatta); in `band_max` per `casD` (6,4 >= 6,0) idem.
7. `test_band_orders_the_probability`: per seme e A-10C: `p(band_min) >= p(on) >= p(band_max)`; rilevati in `band_max` ⊆ in
   `on` ⊆ in `band_min`.
8. `test_switch_off_leaves_no_dwell_fields`: in `off` ogni `Detection` ha `exposure_s is None` e `dwell_time_s is None`;
   in tutte le varianti le `Detection` degli A-10C (osservatori) hanno `dwell_time_s is None` (gli aerei non dichiarano dwell).
9. `test_variant_switch_is_scoped`: come `Test_Session_Scenarios_S33.test_variant_switches_are_scoped` (`:302-320`): con
   `F.run` sostituito da una sonda che registra `(ER_MODULE.D5_DWELL_TIME, asset ZSU.detection_dwell_time('air'))` e solleva,
   per ogni variante: registrato `(switch, dwell atteso)` e `ER.D5_DWELL_TIME` invariato dopo.

Esito atteso numerico [V, P-11, seme `S36-GRAZE-0`]: `on` Pd 0,25022 / 0,45125 / 0,50208 / 0,50686; `off` 0,50043 /
0,50139 / 0,50208 / 0,50686 (non da asserire: solo per controllo dell'esecutore).

Verifica del blocco: `<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S36` (9 test OK);
`Scenario_Baseline --compare <fotografia> --only 'S36'` -> `NEW (16)`, nessun errore; ogni esecuzione NEW ha la voce
`detections`.

### 4.4 Blocco 3 — S36-CUT e S36-PASSES

**S36-CUT** (`TestS36WindowCut`, leva B).
```python
CUT_SEEDS = [f'S36-CUT-{i}' for i in range(SEEDS_PER_SCENARIO)]
CUT_DURATION = 120.0                                        # durata della sessione [s], geometria di test
CUT_LEFT = (('casA', 1.0), ('casB', 3.0), ('casC', 10.0))   # secondi di sessione rimasti all'ingresso nella sfera
CUT_ORIGIN_X = {p: -(HORIZONTAL_RADIUS + (CUT_DURATION - k) * A10_SPEED) for p, k in CUT_LEFT}
#   = -23707,264 / -23396,152 / -22307,264 m [C]
CUT_VARIANTS = {'off': False, 'on': True}
```
Red: la ZSU come in GRAZE (registro, nessun dwell dichiarato). Blue: tre A-10C `F.Unit('aircraft', A10, 1,
origin=(CUT_ORIGIN_X[p], 0.0, TARGET_Z), prefix=p, loadout=A10_LOADOUT)`; missioni `F.missions_for(blue,
[(CUT_ORIGIN_X['casA'] + 80_000.0, 0.0)], mission_type='CAS', target=F.group_target('Red-Line'), rules=HOLD)`; durata
`CUT_DURATION`. Riga di `UNITS`: `('S36-CUT', ..., 'TestS36WindowCut', None, _by_occurrence('off', 'on'))`.
Test (5):
1. `test_exposure_is_the_time_left_in_the_session`: in `on`, `d.exposure_s` ≈ `k` (places=6), `dwell_time_s == ZSU_DWELL`.
2. `test_probability_is_scaled_by_the_dwell_factor`: `p_on` ≈ `min(1, k/3,2) * p_off` (places=12) e ≈
   `expected_probability(d)`; per `casA` e `casB` `p_on < p_off` (stretto); per `casC` uguali.
3. `test_same_draws_and_no_extra_detection`: come GRAZE n. 5.
4. `test_detection_is_never_earlier`: se rilevato in entrambe, `time_on >= time_off` (raggio estratto minore con `g < 1`,
   `detection_radius`); premessa non vacua: esiste almeno un caso con `time_on > time_off` sui 4 semi (P-4: seme 0, `casB`).
   Se la premessa non vale con i semi finali, l'esecutore si ferma e riferisce (non cambia i semi).
5. `test_premise_no_salvo`.

**S36-PASSES** (`TestS36PassJoin`, unione FP-10 con il dwell reale).
```python
PASS_SEEDS = [f'S36-PASSES-{i}' for i in range(SEEDS_PER_SCENARIO)]
PASS_S = 1.0                                               # durata di ciascun passaggio [s], geometria di test
PASS_HALF_CHORD = A10_SPEED * PASS_S / 2                   # 77,778 m
PASS_OFFSET = math.sqrt(HORIZONTAL_RADIUS ** 2 - PASS_HALF_CHORD ** 2)   # 5195,570 m [C]
PASS_GAP = {'join': 1.0, 'split': 5.0}                      # uscita fra i due passaggi [s]: <= e > dwell 3,2 s
PASS_VARIANTS = {'join_off': ('join', False), 'join_on': ('join', True),
                 'split_off': ('split', False), 'split_on': ('split', True)}
```
Un solo A-10C `Blue-CAS/cas0` da `(-20_000.0, PASS_OFFSET, TARGET_Z)`; punti `[(PASS_HALF_CHORD + A10_SPEED * gap / 2,
PASS_OFFSET), (-20_000.0, PASS_OFFSET)]` (andata oltre la corda, inversione fuori dalla sfera, ritorno sulla stessa retta,
come il `REENTRY` di S33 `:54`); svolta a `x = 155,556 m` (join) o `466,667 m` (split) [C]; durata `DURATION`. Riga:
`('S36-PASSES', ..., 'TestS36PassJoin', None, _by_occurrence('join_off', 'join_on', 'split_off', 'split_on'))`.
Test (5):
1. `test_premise_two_one_second_passes`: in `join_off` e `split_off` esattamente 2 `Detection` della ZSU con `pass_index` 0 e
   1, `pass_count == 2`, `pass_end - pass_start` ≈ 1,0 (places=6) ciascuno, e uscita `pass_start[1] - pass_end[0]` ≈ 1,0
   (join) / 5,0 (split) (places=6) [V: passaggi a 128,071-129,071 e 130,071-131,071 s].
2. `test_join_on_merges_the_passes_over_the_exit`: in `join_on` UNA `Detection`, `pass_index is None`, `exposure_s` ≈
   `2 * PASS_S + PASS_GAP['join']` = 3,0 (places=6: l'arco con l'uscita, NON la somma 2,0), `dwell_time_s == ZSU_DWELL`,
   `probability` ≈ `expected_probability(d)` (g = 0,9375).
3. `test_split_on_scales_each_pass`: in `split_on` 2 `Detection` (pass 0 e 1), `exposure_s` ≈ 1,0 ciascuna, probabilita' ≈
   `expected_probability` (g = 0,3125).
4. `test_draw_streams_are_shared`: per seme, la `draw` del primo rilevamento e' la stessa nelle 4 varianti (stream
   dell'ingaggio); la `draw` del secondo passaggio e' la stessa in `join_off`, `split_off`, `split_on` (stream `pass_rng`).
5. `test_merge_removes_the_second_draw`: `join_on` ha 1 estrazione della ZSU, `join_off` 2; nessuna salva in nessuna variante.

Verifica del blocco: modulo S36 (19 test OK); `--only 'S36'` -> `NEW (40)`.

### 4.5 Blocco 4 — S36-FAMILIES, S36-BAND, test dello strumento

**Tabella delle famiglie** (copie del registro [V, P-1, P-6], tranne la geometria):
```python
# nome: (tipo, modello, portata aria di acquisizione [m], dwell del registro [s], mil_category)
GROUND_FAMILIES = {
    'strela10': ('vehicle', '9K35-Strela-10', 10_000.0, 3.2, F.GROUND_UNIT),   # TVD, STIMA [S] DW9-6
    'tor':      ('vehicle', '9K331-Tor', 25_000.0, 3.0, F.GROUND_UNIT),        # FONTE
    'buk':      ('vehicle', '9K37-Buk', 85_000.0, 9.0, F.GROUND_UNIT),         # FONTE NON VERIFICATA [S]
    's300':     ('vehicle', 'S-300PS', 150_000.0, 12.0, F.GROUND_UNIT),        # STIMA PER CONFRONTO [S]
    'p37':      ('vehicle', 'P-37-Mech', 280_000.0, 14.1, F.GROUND_UNIT),      # FONTE, valore centrale
    'ffg46':    ('ship', 'FFG-46', 350_000.0, 5.0, F.NAVAL_UNIT),              # SPS-49, FONTE
}
E3A = 'E-3A Sentry'; E3A_RANGE = 400_000.0; E3A_DWELL = 10.0; E3A_Z = 9_000.0; E3A_SPEED = 208.33333333333331
MIG = 'MiG-29S'; MIG_SPEED = 255.55555555555554          # velocita' nominali del registro [m/s] (copie)
FAMILY_EXPOSURE_RATIO = 0.5                              # permanenza = meta' del dwell (g = 0,5), geometria di test
```
Geometria a terra/mare: Red `F.build_force('Red-Line', 'Red', [F.Unit(tipo, modello, 1, origin=(0.0, 0.0), prefix='obs')],
mil_category=...)`; Blue un A-10C `Blue-CAS/cas0` da `(-20_000.0, h, TARGET_Z)` a `[(20_000.0, h)]`, CAS, `HOLD`, con `h =
lateral_offset(R, TARGET_Z, A10_SPEED, dwell * 0.5)` (= 9538,580 / 24819,073 / 84946,321 / 149969,271 / 279983,391 /
349987,089 m [C]); forze `[blue]`, `[red]`; durata `DURATION`.
Geometria AWACS (leva C): Blue `F.build_force('Blue-AEW', 'Blue', [F.Unit('aircraft', E3A, 1, origin=(0.0, 0.0, E3A_Z),
prefix='obs')], mil_category=F.AIR_UNIT)` con `F.missions_for(blue, [(E3A_SPEED * 600.0, 0.0)], mission_type='AWACS',
target=F.zone_target((E3A_SPEED * 300.0, 0.0, E3A_Z), 50_000.0))` (un aereo senza missione e' a terra e non osserva);
Red `F.build_force('Red-Air', 'Red', [F.Unit('aircraft', MIG, 1, origin=(x0, h, TARGET_Z), prefix='tgt')],
mil_category=F.AIR_UNIT)` con `x0 = (E3A_SPEED + MIG_SPEED) * 200.0` (= 92777,778 m) e missione `F.missions_for(red,
[(x0 - MIG_SPEED * 600.0, h)], mission_type='Fighter_Sweep', target=F.group_target('Blue-AEW'), rules=HOLD)`;
`h = lateral_offset(E3A_RANGE, E3A_Z - TARGET_Z, E3A_SPEED + MIG_SPEED, E3A_DWELL * 0.5)` (= 399953,316 m); forze `[blue]`,
`[red]`; osservatore `Blue-AEW/obs0`, bersaglio `Red-Air/tgt0`. [V, P-12: nessuna salva, permanenza 4,9999999996 s].

**S36-FAMILIES** (`TestS36Families`): `FAMILY_VARIANTS = ('strela10', 'tor', 'buk', 's300', 'p37', 'ffg46', 'e3a')`, tutte con
interruttore acceso e dwell del registro. Riga: `('S36-FAMILIES', ..., 'TestS36Families', None, _by_occurrence('strela10',
'tor', 'buk', 's300', 'p37', 'ffg46', 'e3a'))`.
Test (5):
1. `test_premise_registry_values`: per ogni famiglia `detection_range('air') == R`, `detection_dwell_time('air') == dwell`
   sull'asset reale; velocita' nominali di A-10C, E-3A, MiG-29S.
2. `test_exposure_is_half_the_dwell`: la `Detection` dell'osservatore ha `exposure_s` ≈ `dwell / 2` (places=6),
   `dwell_time_s == dwell`, `sensor_range == R`.
3. `test_probability_is_half_the_previous_law`: `probability` ≈ `expected_probability(d)` (places=12) e ≈
   `0.5 * previous_probability(d)` (places=12); `previous_probability(d) > 0` (premessa: il bersaglio entra nella sfera).
4. `test_no_salvo_on_a_pass_shorter_than_the_dwell`: nessun `ammunition_events` (docstring con la tabella reazione/dwell di
   §1.4 per Strela-10, Tor, Buk, S-300PS).
5. `test_targets_read_no_dwell`: le `Detection` degli aerei bersaglio (A-10C, MiG-29S) hanno `dwell_time_s is None`.

**S36-BAND** (`TestS36Band`): stessa geometria delle 6 famiglie a terra/mare (permanenza = dwell del registro / 2), interruttore
acceso, `F.declare_dwell(observer, {'air': valore})` con:
```python
# Estremi della banda di incertezza [s] dichiarata con il valore del registro (Proposta_Dwell_Estensione_DW9.md §2.1-§2.4;
# Rapporti/Sonde_Dwell_D5/probe_dw9.py, VALUES): VALORI DI PROVA, non dati.
BAND = {'strela10': (1.75, 6.0), 'tor': (1.0, 3.0), 'buk': (4.3, 20.0), 's300': (5.0, 12.0),
        'p37': (10.0, 20.0), 'ffg46': (5.0, 10.0)}
BAND_VARIANTS = ('strela10_min', 'strela10_max', 'tor_min', 'tor_max', 'buk_min', 'buk_max',
                 's300_min', 's300_max', 'p37_min', 'p37_max', 'ffg46_min', 'ffg46_max')
```
Riga: `('S36-BAND', ..., 'TestS36Band', None, _by_occurrence(*BAND_VARIANTS))` (scrivere i 12 nomi per esteso nella riga,
come le altre). g attesi [C, V P-12]: strela10 0,914 / 0,267; tor 1 / 0,5; buk 1 / 0,225; s300 1 / 0,5; p37 0,705 / 0,3525;
ffg46 0,5 / 0,25. (`tor_max`, `s300_max` e `ffg46_min` coincidono con il valore del registro: tenuti per regolarita'.)
Test (3):
1. `test_declared_dwell_is_read`: `dwell_time_s` = valore dichiarato, `exposure_s` ≈ dwell del registro / 2 (places=6).
2. `test_probability_is_monotone_in_the_dwell`: `probability` ≈ `expected_probability(d)` (places=12); per famiglia e seme
   `p(min) >= p_registro >= p(max)`, con `p_registro = ER.detection_probability(d.distance_cpa, d.sensor_range,
   ER.dwell_factor(d.exposure_s, dwell_del_registro))` calcolata sulla stessa `Detection`.
3. `test_detected_with_max_is_subset_of_min`: stessa `draw` fra `_min` e `_max` dello stesso seme; rilevato in `_max` implica
   rilevato in `_min`.

**Test dello strumento** (`TestS36BaselineDetections(unittest.TestCase)`, NON in `UNITS`; `capture` silenzia da se' i logger):
1. `test_detection_units_are_the_s36_tail`: `SB.DETECTION_UNITS == {'S36-GRAZE', 'S36-CUT', 'S36-PASSES', 'S36-FAMILIES',
   'S36-BAND'}` e le ultime 5 etichette di `SB.UNITS` sono, nell'ordine, `S36-GRAZE`, `S36-CUT`, `S36-PASSES`,
   `S36-FAMILIES`, `S36-BAND` (nessuna unita' precedente registra le `Detection`).
2. `test_capture_records_the_detections_voice`: `snapshot = SB.capture(only='^S36-CUT$', verbose=False)`: `errors` vuoto,
   8 esecuzioni; ognuna ha la voce `detections`, ogni riga ha `len(SB.DETECTION_FIELDS)` campi; nelle chiavi `/on` le righe
   con osservatore `Red-Line/obs0` hanno `dwell_time_s` (indice 9) = 3,2, nelle `/off` None.

Verifica del blocco: modulo S36 (29 test OK); `--only 'S36'` -> `NEW (116)`.

### 4.6 Blocco 5 — test unitari fuori dalla fotografia (WINNER, ROUTE)

**`Test/Test_Dwell_Data.py`**, classe nuova `TestDwellOfTwoSensorRecord(unittest.TestCase)` (usa `_DwellReader`, `:110`;
import nuovo `from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER`; logger di Mobile silenziato con
`patch(_MOBILE_LOGGER, MagicMock())` in `setUp`/`tearDown`). Costanti: `TWO_SENSOR_MODEL = 'F-16C Block 52d'`,
`TEST_RADAR_DWELL_S = 6.0`, `TEST_TVD_DWELL_S = 2.0` (**valori di prova**: gli aerei non dichiarano dwell, DW-9 decisione 1;
`test_non_awacs_aircraft_declare_no_dwell` resta vero perche' il patch e' ripristinato). Patch:
`patch.dict(Aircraft_Data._registry[TWO_SENSOR_MODEL].radar, {'dwell_time_s': 6.0})` e lo stesso sul `TVD` con 2,0.
1. `test_dwell_follows_the_acquisition_winner_of_a_real_record`: premesse sul record (aria: radar 70 km, TVD 110 km in
   acquisizione; terra: 55 e 95); `detection_dwell_time('air') == 2.0`, `detection_dwell_time('ground') == 2.0`,
   `sensor_dwell_time('radar') == 6.0`; dopo il `with`, nessuna chiave `dwell_time_s` nei due dizionari.
2. `test_registry_reader_ignores_the_tracking_winner`: premesse (inseguimento aria: radar 150, TVD 90);
   `detection_dwell_time('air', range_type='tracking_range') == 6.0` ma `ER.registry_dwell_time(reader, None, 'air') ==
   2.0`. Docstring: LIMITE NOTO (`registry_dwell_time` non passa `range_type`, `Logic/Engagement_Resolver.py:1307`): una
   sessione con `range_type='tracking_range'` userebbe la portata del radar e il dwell del TVD; il test fissa il
   comportamento attuale e va cambiato insieme al limite.

**`Test/Test_Threat_AA_Factory.py`**, classe nuova `TestDetectionMetricsWithRegistryDwell(unittest.TestCase)`, dopo
`TestBuildDetectionThreat` (`:393`). Import in piu' da `Logic.Air_Route_Manager`: `Path`, `PathCollection`, `ThreatMode`,
`Edge`, `Waypoint` (classi interne del pianificatore) e `from Code.Dynamic_War_Manager.Source.Logic import
Engagement_Resolver as ER`; `ER.detection_probability`. `setUp`: `_silence_data_warnings()`. Aiuti:
- `_threat(model, altitude)`: `build_detection_threat(_AssetStub(model=model, category=Vehicle_Data._registry[model].category,
  position=Point3D(0, 0, 0), id=model), altitude)`.
- `_crossing(threat, altitude, speed, exposure_s)`: scostamento `h = sqrt(r^2 - (speed·τ/2)^2)` con `r =
  float(threat.cylinder.radius)`; un `Edge('e', 0, Waypoint('a', Point3D(-c - 5000, h, altitude), None), Waypoint('b',
  Point3D(c + 5000, h, altitude), None), speed)` con `c = speed·τ/2`; `Path([edge])`.
- `_metrics(path, threat, speed, switch)`: `with patch.object(ER, 'D5_DWELL_TIME', switch): path.compute_detection_metrics(
  [threat], speed)` (il pianificatore legge l'interruttore a ogni chiamata, `Logic/Air_Route_Manager.py:1132`).
Velocita' `SPEED = 155.55555555555554` (A-10C nominale, copia). Test (5), valori di §2.5 [V, P-13]:
1. `test_horizon_limited_short_crossing_halves_the_pd`: S-300PS a 100 m; premessa `r < threat.acquisition_range` e
   `threat.dwell_time_s == 12.0`; τ = 6 s: `crossing_exposure_s` ≈ 6,0 (places=6); acceso ≈ `detection_probability(d_min,
   150000, 0.5)` (places=9, `d_min = float(tract['min_distance'])`) e ≈ meta' dello spento (places=9).
2. `test_crossing_longer_than_the_dwell_is_unchanged`: S-300PS a 100 m, τ = 24 s: acceso == spento (places=12).
3. `test_low_altitude_short_crossings_of_tor_and_buk`: Tor a 150 m con τ = 2,5 s e Buk a 500 m con τ = 7,5 s: spento > 0,
   acceso ≈ `detection_probability(d_min, R, τ/dwell)` (places=9) e < spento.
4. `test_full_range_cylinder_edge_has_zero_pd_either_way`: Tor a 3000 m, τ = 1,5 s: `detection_exposure_s` ≈ 1,5 e
   `max_detection_probability == 0.0` acceso e spento (divergenza nota cilindro/sfera, `:1110-1114`).
5. `test_best_path_key_ignores_the_switch`: per il percorso del test 1, `PathCollection.best_path_key(mode)(path)` uguale
   acceso e spento per `mode` in `(None, ThreatMode.AVOID_DETECTION)`: la scelta della rotta non dipende dalla D-5.

Verifica del blocco: `Test_Dwell_Data` (12 test, +2) e `Test_Threat_AA_Factory` (+5) OK.

### 4.7 Blocco 6 — testi, verifiche complete, documenti, rapporto

1. `Test/Scenario_Fixtures.py:307-308`, docstring di `declare_dwell`: sostituire "serve agli scenari che devono mostrare la
   legge su un tiratore (nessun tiratore del registro ha dati di scansione)" con: "serve agli scenari che provano la legge con
   un periodo DIVERSO da quello del registro (valori di prova come i 30/600 s di S32, la stima di 2 s di S33, gli estremi della
   banda di incertezza di S36). Dalla DW-9 i registri dichiarano `dwell_time_s` per SAM/AAA, TVD e vista, EWR, navi e AWACS
   (`Analysis/Document/Registro_Dwell_Stimati.md`)".
2. `Test/Test_Session_Scenarios_S32.py:27-28`: "30 s e 600 s sono periodi di rivisita DICHIARATI DI TEST sulla ZSU-57-2, non
   dati: il visivo non ha dati di scansione; il P-18 usa il dato di fonte del registro (6 s)." -> "30 s e 600 s sono periodi di
   rivisita DICHIARATI DI TEST sulla ZSU-57-2 (`declare_dwell`), non dati. Dalla DW-9 il registro dichiara per la vista della
   ZSU-57-2 3,2 s [S] (banda 1,75-6,0 s): lo leggono le varianti `ewr_on` (permanenza oltre 60 s, g = 1) e, con i dwell reali
   e permanenze brevi, gli scenari S36; il P-18 usa il dato di fonte del registro (6 s)." Nella tabella (`:25`) la riga
   `ewr_on`, colonna del dwell: "- (registro: 3,2 s [S], g = 1; P-18: dato di fonte 6 s)".
3. `Test/Test_Session_Scenarios_S33.py:20-22`: aggiungere dopo "non un dato." la frase: "E' precedente alla DW-9 (registro:
   3,2 s [S], banda 1,75-6,0 s) e resta dichiarata per non cambiare la fotografia di S33; con 3,2 s le conclusioni non
   cambierebbero (passaggi di 50-67 s: g = 1; uscite di 100-130 s: nessuna unione) [C]." Nessun valore cambia.
4. Suite e confronto completi, **mai in parallelo**: `bash tools/ai/verifica.sh suite start` / `wait` fino a `ESITO`, poi
   `bash tools/ai/verifica.sh confronto start` / `wait`. Riportare i numeri letti dall'`ESITO` e da `.ai-run/confronto.log`
   (`grep -E '^(CHANGED|NEW)'`).
5. Documenti di §4.11 (salvo il manuale) e rapporto `Analysis/Document/Rapporti/Rapporto_S36_<agente>.md` secondo
   `Rapporti/TEMPLATE.md`. **Non installare la fotografia.**

### 4.8 Esito atteso del confronto con la fotografia (`Test/baseline/scenario_baseline.json`, 1103 esecuzioni)

- **Identiche: tutte le 1103** (nessuna riga del motore cambia; il registratore delle unita' esistenti e' quello di prima,
  `with_detections=False`; le righe nuove di `UNITS` sono in coda).
- **Cambiate: 0. MISSING: 0.**
- **Nuove: 116**, tutte con la voce `detections`: `S36-GRAZE` 16 (`off`, `on`, `band_min`, `band_max` x `S36-GRAZE-0..3`),
  `S36-CUT` 8, `S36-PASSES` 16, `S36-FAMILIES` 28, `S36-BAND` 48. Riepilogo atteso: `UNCHANGED (1103)`, `NEW (116)`,
  `compared 1219 runs: 116 difference lines` (le righe di differenza sono le NEW, come per S32 in `F4_Differenze_Scenari.md`
  `:2700`).
- Con `--ignore detections` le 116 restano NEW (la voce si toglie su entrambi i lati, l'esecuzione resta nuova).
- La fotografia nuova (1219) la installa **solo l'utente**, dopo aver letto le 116.

### 4.9 Test nuovi (conteggio)

| File | Classe | Test |
|---|---|---|
| `Test_Session_Scenarios_S36.py` (nuovo) | `TestS36Graze` | 9 |
| | `TestS36WindowCut` | 5 |
| | `TestS36PassJoin` | 5 |
| | `TestS36Families` | 5 |
| | `TestS36Band` | 3 |
| | `TestS36BaselineDetections` | 2 |
| `Test_Dwell_Data.py` | `TestDwellOfTwoSensorRecord` | 2 |
| `Test_Threat_AA_Factory.py` | `TestDetectionMetricsWithRegistryDwell` | 5 |
| **Totale** | | **36** |

Suite attesa: **`Ran 4961`**, `OK (skipped=7)` (base 4925 dichiarata dal commit `a99bb3d4` e verificata in
`.ai-run/suite.log` su questa macchina: `Ran 4925 ... OK (skipped=7)`). Nessun test esistente cambia numero; quelli di S32 e
S33 cambiano solo nel docstring.

### 4.10 Budget di tempo [V, sonde]

Una sessione S36 costa 0,01-0,05 s di motore e ~0,2 s con la costruzione delle forze (P-11: 16 esecuzioni di GRAZE in 3,1 s;
P-12: 18 esecuzioni a famiglia in 0,7 s). Stima per 116 esecuzioni: **10-25 s** in piu' sul confronto (oggi 508 s sul
ProArt, `.ai-run/confronto.log`) e circa altrettanto sulla suite (le `setUpClass` S36 piu' la cattura di S36-CUT nel test
dello strumento); fotografia +0,5-1 MB su 13,5 MB. Budget: **<= 120 esecuzioni, <= +30 s, <= +1 MB**; se l'esecutore misura
di piu' si ferma e riferisce.

### 4.11 Documenti da aggiornare

- `Analysis/Document/F4_Differenze_Scenari.md` (esecutore, blocco 6): sezione nuova "## S36 — permanenza breve con i dwell
  reali (data)": il cambio (voce `detections` per le sole unita' S36), differenze della fotografia (1103 identiche + 116 NEW),
  tabella delle 5 unita' con varianti e semi, costanti (geometria di test; estremi della banda = valori di prova), limiti
  (§5).
- `Analysis/Document/Piano_Implementazione_Missione.md` (esecutore, blocco 6): riga nuova nella tabella dei lavori fuori
  numerazione (vicino a BI e FP, `:311-312`): "S36 (permanenza breve con i dwell reali)", stato, commit, rimando a questa
  Proposta e a F4.
- Manuale DES (dopo il merge, `des-manual-writer`, NON l'esecutore): `09_Validazione.md` §8.4 e §8.14 (unita' S36, voce
  `detections` dello strumento, §8.7), riga `:144` (stessa frase superata su `declare_dwell`); `05_Strato2_Risolutore_Ingaggio.md`
  §4.36 (il "limite della fotografia" del 2026-11-18 e' coperto da S36; unione FP-10 = arco con l'uscita);
  `10_Limiti_Estensioni_Divergenze.md` (limiti di §5: `range_type`, taglio di sessione, pianificatore).
- `Analysis/Document/Rapporti/Sonde_Dwell_D5/LEGGIMI.md`: nessuna modifica (le sonde S36 sono in `.ai-run/sonde_s36/`; la
  sessione principale decide se versionarle).

### 4.12 Esecutore e dimensione

`des-developer` (Sonnet high), un blocco per volta con la verifica parziale indicata; suite e confronto completi solo nel
blocco 6. Dimensione: modulo S36 ~700-800 righe; `Scenario_Baseline.py` ~60 righe (codice e docstring); `Test_Dwell_Data.py`
~45; `Test_Threat_AA_Factory.py` ~110; docstring ~20; documenti ~60. Se un numero del piano non torna (permanenza, Pd,
conteggio di esecuzioni o di test, tempo), l'esecutore si ferma e riferisce: non ritocca la geometria.

---

## 5. Rischi e limiti

1. **La legge con i dwell reali non tocca il tiro** (§1.4): S36 la prova sulle `Detection`, non su salve o danni. La
   fotografia la vede solo grazie alla voce `detections` (R2); con R1 le 116 esecuzioni non distinguerebbero acceso e spento.
2. **Copertura parziale**: la voce `detections` vale solo per S36; le altre 1103 esecuzioni non registrano rilevamenti (un
   cambio della legge che non tocca il tiro resta invisibile li'). Restano fuori dalla fotografia con dwell reale: Shilka,
   Gepard, Osa, Tunguska, Roland, Kub, M163, Strela-1, Chaparral, M6, gli altri EWR, le altre navi, E-2D e A-50 (coperti solo
   dai test di dati `Test_Dwell_Data`).
3. **Geometrie radenti a pochi metri dal bordo**: esatte in doppia precisione, ma qualunque cambio del volume di rilevamento
   (es. VA-6, `_own_intervals` `Logic/Engagement_Resolver.py:2481-2496`; un orizzonte radar nel DES) cambiera' le S36: e'
   voluto (guardiano), ma andra' riletto dall'utente. Con l'orizzonte nel DES le geometrie a 280-400 km (P-37, FFG-46,
   E-3A) non sarebbero piu' raggiungibili cosi'.
4. **Taglio di sessione (leva B)**: la Pd dipende dalla durata scelta per la sessione: un bersaglio che entra 1 s prima della
   fine ha g = 0,31. In una campagna a sessioni concatenate un passaggio a cavallo di due sessioni avrebbe due estrazioni, ognuna
   con la sua permanenza tagliata: **proprieta' del modello da valutare** (non verificata qui su sessioni concatenate; nessuna
   proposta di cambio in questo piano).
5. **Limite `range_type`** (WINNER): `registry_dwell_time` legge sempre il dwell del vincitore di acquisizione; oggi nessun
   record con due sensori ha dwell, quindi senza effetto pratico; il test lo fissa.
6. **Pianificatore**: la D-5 cambia `max_detection_probability` ma non la scelta della rotta (la chiave non la legge); nel
   cilindro a portata piena un attraversamento breve con Pd > 0 richiede quota bassa (corda >= 2 · quota). Il pianificatore non
   e' nella fotografia.
7. **Valori stimati**: i dwell della vista e del TVD (3,2 s), di Buk e S-300PS sono stime [S] (Registro_Dwell_Stimati.md); le
   S36 li copiano e ne verificano l'uso, non la taratura. Se il registro cambia, falliscono i test di premessa e cambiano le
   esecuzioni S36: entrambe le cose sono volute.
8. **Semi**: le asserzioni sono strutturali e non dipendono dai semi, salvo la premessa non vacua di S36-CUT n. 4 (verificata
   con i nomi definitivi dalla sonda P-16: `S36-CUT-0`, `casB0`).
9. **A-10C in `weapon_hold`**: isola il rilevamento; il comportamento CAS reale non e' messo alla prova da S36.
