# F4: differenze degli scenari rispetto alla fotografia di riferimento

Documento delle differenze della fotografia degli scenari (`Test/baseline/scenario_baseline.json`)
introdotte dai passi della Fase 4 di `Piano_Implementazione_Missione.md`. Ogni sezione confronta la
fotografia PRIMA del passo con quella DOPO, e spiega la causa di ogni differenza.

Strumento: `Test/Scenario_Baseline.py --compare <prima.json> --against <dopo.json>` (differenze
puntuali) e, dal passo F4a, `--summary` (riepilogo leggibile per esecuzione: esito per forza, asset
distrutti, colpi, intercettazioni, carburante, fine del movimento, istante del primo colpo e del
primo danno).

---

## F4a: fusione per velocita'

**Base del confronto**: fotografia di `533cd1f5` (F3; identica al codice di F3 su 292 esecuzioni).
**Dopo**: stesso motore (forza = blocco, nessun cambio a resolver, scheduler, RNG), con la sola
fusione negli scenari dei blocchi divisi in F3 per sola differenza di velocita'.

### La regola

Decisione dell'utente (regola A): **una missione si muove insieme, alla velocita' del mezzo piu'
lento** (come un gruppo DCS). Chi vuole velocita' diverse fa missioni separate, eventualmente
coordinate da un'Operazione.

- **Negli scenari** (`Scenario_Fixtures.missions_for`): la velocita' non divide piu' le missioni;
  dominio e geometria si'. La rotta di riferimento di una missione ha, tratto per tratto, la
  velocita' minima fra quelle (nominali, dal registro) dei suoi asset. Gli offset di formazione sono
  quelli di F3: la geometria non cambia.
- **Nel modello** (`Logic/Mission_Adapter.check_mission_speed`, chiamata da
  `Session_Simulator._check_missions`): la velocita' pianificata di ogni tratto non puo' superare la
  velocita' MASSIMA (`speed['max']`) del mezzo piu' lento della missione; altrimenti `ValueError`.
  Un asset senza velocita' massima nota e' escluso con un warning (non blocca). Negli scenari tutti
  i modelli in missione hanno il dato: il controllo non scatta mai (le velocita' pianificate sono
  le nominali, sotto le massime).

### Casi toccati e casi lasciati

| Scenario | Blocco | F3 | F4a | Motivo |
|---|---|---|---|---|
| S1 (e VAL-det, VAL-agn: stessa composizione) | Blue-Armor (3 M1A2 + 2 M2) | 2 missioni (M2 56 km/h, M1A2 55 km/h) | **1 missione** a 55 km/h | divisione per sola velocita' |
| S9, S9R | Blue-Armor (composizione di S1) | 2 | **1** | idem |
| S12 | Blue-Armor (M1A2 + M2) | 2 | **1** | idem |
| S17 (Company..Division, k=1..6) | Blue-Armor (3k M1A2 + 2k M2) | 2 | **1** | idem |
| S11 | Blue-Mech (3 M1A2 + 3 M2) | 2 | **1** | idem |
| S7 | Blue-Package: Strike (F-16C) + Escort (F-15C) | 2 | 2 (invariato) | tipi di missione diversi; nessuna Operazione introdotta: il motore attuale non la usa |
| S18 | Blue-Package: Strike (F-16C) + Escort (F-15C) | 2 | 2 (invariato) | idem |
| S19 | Blue-Transit: CAS (A-10C) / Escort (F-16C) / Strike (B-52H) | 3 | 3 (invariato) | tipi di missione diversi, ognuna alla velocita' del proprio modello |
| S19AD standoff | Blue-CAS: 4 A-10C | 4 | 4 (invariato) | stessa velocita'; divisione per geometria (formazione rigida con virata), decisione della sessione principale |

Velocita' nominali dal registro: M1A2-Abrams 15.278 m/s (55 km/h), M2-Bradley 15.556 m/s (56 km/h).
Velocita' massime: M1A2 18.611 m/s, M2 18.333 m/s (il piu' lento in velocita' massima e' l'M2, in
nominale l'M1A2: la missione procede a 55 km/h, sotto entrambi i limiti).

### Effetto atteso

L'unica variazione fisica: **i Bradley procedono a 55 invece che 56 km/h** (-1.8 %). Sulla rotta di
S1 (10 301 m) arrivano 12.04 s piu' tardi (662.21 s -> 674.25 s); ogni tratto della loro presenza e'
spostato in proporzione al percorso fatto. I carri (gia' a 55 km/h) non cambiano. Lo scaglione resta
quello della formazione (i Bradley partono 300 m dietro i carri, `origin=(-8300, 150)`), ma non lo
recuperano piu': prima guadagnavano circa 16.7 m al minuto (0.278 m/s).

### Esecuzioni che cambiano (90 su 292)

**Solo il tempo di arrivo dei Bradley** (`fuel.<ifv>.time`, nessun altro valore): 81 esecuzioni.
- S1, tutte le repliche e varianti tranne `S1-6/without_cas`: 662.21 -> 674.25 s.
- S9 (tutte, tranne `S9-5/detection_factor=0.0`) e S9R (tutte): idem.
- S11 (a/b/c, dcs e synthetic): 4262.21 -> 4274.25 s (la sessione b parte a 3600 s).
- S12 `prolonged` (tutte tranne S12-2): idem a S1.
- S17 Company (k=1) e Battalion (k=2), Regiment (k=3), tutte le repliche: idem, su 2k Bradley.
- VAL-det (S7-det-alpha first/second, S7-det-beta first) e VAL-agn (S7-agn-1 single/campaign):
  idem (composizione di S1).

**Tempi d'ingaggio spostati, stessi esiti e stesse perdite**:
- `S9/S9-5/detection_factor=0.0`: la prima salva (artiglieria Red-Line/art0 sul Bradley
  Blue-Armor/ifv1) passa da 178.91 a 181.60 s (+2.7 s), il primo danno (ifv1 distrutto) da 208.91 a
  211.60 s, il disingaggio di Blue-Armor da 248.91 a 251.60 s; slittano solo le prime due salve
  (e i loro tre eventi di danno), il resto e' invariato. Causa: il primo bersaglio dell'artiglieria e' un Bradley, che entra
  nella sua portata piu' tardi.
- `S12/S12-2/prolonged`: un solo colpo tardivo (salva 16, del Bradley Blue-Armor/ifv0 che
  distrugge Red-Line/sam0) passa da 372.87 a 379.08 s (danno da 374.37 a 380.58 s), stessi esiti
  (Blue-Armor HELD, Blue-CAS e Red-Line DESTROYED, agli stessi istanti). Causa: il Bradley entra in
  portata 6.2 s piu' tardi.

**Esito di forza diverso nei numeri, non nella categoria**:
- `S1/S1-6/without_cas`: Blue-Armor DISENGAGED in entrambi, ma a 326.90 s invece di 310.16 s, con
  `lost` 3 invece di 4 (erosione 0.8 -> 0.6, frazione senza risposta 0 -> 0.33); eventi di
  distruzione 3 -> 2, il Bradley Blue-Armor/ifv1 sopravvive (salute 0 -> 100). Red-Line invariato
  (DISENGAGED a 309.16 s, 2 perdite). Sequenza: in F3 a 310.16 s il BMP Red-Line/ifv0 distruggeva
  Blue-Armor/ifv1 e a 322.15 s l'artiglieria Red-Line/art0 distruggeva Blue-Armor/ifv0 (un colpo
  mancato, uno a segno); in F4a il colpo su ifv1 non c'e' piu' (ifv1, 12 s piu' lento sulla rotta,
  verosimilmente non e' ancora ingaggiabile da ifv0 quando Red-Line disingaggia) e la salva d'artiglieria su ifv0
  arriva a 326.90 s. Una salva in meno di Red-Line/ifv0 (colpi totali 13 -> 12). Con una perdita in
  meno Blue-Armor raggiunge la soglia di rottura 16.7 s dopo.

**Ridistribuzione delle perdite fra gli asset, totali uguali o quasi** (S17 grandi, k=4 e k=6):
- `S17-0/Brigade_k=4`: una salva in piu' di Blue-Armor (colpi del lato 6 -> 7; mbt3 spara 1 colpo),
  59 eventi di danno invece di 58; asset distrutti per forza invariati (cambia QUALE: in Blue-Armor
  ifv0 distrutto invece di mbt3, in Red-Line ifv3 invece di ifv7); shock massimo di Red-Line 0.125
  -> 0.083. Esiti di forza invariati.
- `S17-1/Brigade_k=4`, `S17-2/Brigade_k=4`, `S17-{0,1,2}/Division_k=6`: stessi conteggi (salve,
  colpi, danni, distruzioni per forza) ed esiti di forza invariati; cambiano gli asset colpiti
  (es. in S17-0 Division: distrutti ifv0, ifv11, ifv5, mbt17 invece di ifv10, ifv2, ifv3, ifv9) e il
  regime di carburante dei singoli (`max` per chi e' impegnato in combattimento, `nominal` per gli
  altri) segue di conseguenza.
- Causa: con molti asset in linea, l'ordine in cui i Bradley entrano nelle portate nemiche (ora 300 m
  costanti dietro i carri, non piu' in recupero) cambia quale bersaglio e' il piu' vicino a ogni
  ciclo di tiro, quindi chi colpisce chi; l'estrazione RNG e' la stessa (flusso per forza), ma
  applicata a una sequenza di coppie diversa.

In nessuna esecuzione cambia un esito di forza (HELD/DISENGAGED/DESTROYED). Il riepilogo completo
si ottiene con:

    python3 -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline \
        --compare <fotografia F3> --against <fotografia F4a> --summary

### Esecuzioni invariate (202)

ORC-* (tutte: base, seed, nocontact, twofronts, interval, fuel), S2, S3, S4, S5, S6, S7, S8,
S10, S12 `c2_strike` (S12-0..5), S13, S14, S15, S16, S18, S19 (run, replay), S19AD (tutte e quattro
le varianti, tutte le repliche), VAL-agn `S7-agn-2/single` e `S7-agn-3/single`. Nessuna di queste ha
un blocco misto per velocita'; dove ci sono piu' missioni per blocco (S7, S18, S19, S19AD) la
divisione era per tipo di missione o per geometria ed e' rimasta.

### Test di scenario

Nessuna asserzione dei test di scenario cambia esito: le differenze sopra non toccano le proprieta'
qualitative verificate (S1: con CAS meno perdite di Blue-Armor; S9/S9R: monotonia rispetto al
rilevamento; S11: confine di sessione; S12; S17: andamento con la scala). Nessuna asserzione e'
stata modificata.

### Fotografia di riferimento

Rigenerata dopo questo confronto (`--capture` nel percorso standard) sul codice di F4a; due catture
consecutive identiche (determinismo).
