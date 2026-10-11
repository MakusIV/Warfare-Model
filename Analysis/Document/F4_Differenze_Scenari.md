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

---

## F4b: la missione e' l'unita' d'ingaggio

**Base del confronto**: fotografia di F4a (`951b0ee2`, 292 esecuzioni).
**Dopo**: motore con la missione come forza d'ingaggio (vista `Logic/Mission_Adapter.MissionForce`)
e `mission_id` negli id d'ingaggio, quindi nell'RNG. Gli scenari NON cambiano, tranne il numero di
repliche di S3 e S5 (v. "Test di scenario") e il nuovo S20.

### Il cambio

- **Forza d'ingaggio = missione** (D3.e). `Session_Simulator` raggruppa le finestre di contatto per
  missione (`_engagement_forces`) e passa al risolutore una `MissionForce` per missione: asset della
  missione (gli oggetti reali del blocco), lato del blocco, id e nome = `mission_id`,
  `salvo_interceptors()` ristretto ai propri asset, blocco in `owner_block`. Lo scheduler riceve
  ancora i blocchi: le finestre sono per coppia di asset, quindi sono le STESSE di prima.
- **Disingaggio, soglia di rottura e `committed` per missione** (D3.d, D3.e): ogni missione ha la
  propria tempra, la propria percezione del nemico, il proprio rapporto di forze (solo i suoi
  asset) e rompe il contatto da sola. Decisione dell'utente (2026-10-08): missioni dello stesso
  blocco ingaggiano e disingaggiano separatamente, nessuna Operazione le lega.
  `SessionOrder.committed` resta chiavato per blocco e vale per intersezione su ogni missione.
- **RNG**: `event_id` = `['engagement', id ordinati delle forze]` con gli id delle MISSIONI (e
  `['temper', ...]` per la tempra): uno stream per ingaggio fra missioni. Lo slot `mission_id` di
  `Session_Rng` resta None (un ingaggio e' fra piu' forze, nessuna ne possiede lo stream).
- **Esito**: un `ForceOutcome` per missione (`force_id` = `mission_id`, nuovo campo `block_id`).
  L'esito del blocco NON e' aggregato: e' l'insieme degli esiti delle sue missioni
  (`SessionOutcome.outcomes_of_block`). La fotografia tiene `force_outcomes` per blocco (stessa
  forma con una missione per blocco) e `--summary` mostra, per i blocchi con piu' missioni, l'esito
  di ciascuna (`<mission_id>.mission_outcome`).
- **Asset senza missione** (la postura e' della F4c): comportamento di prima. Un blocco senza
  missioni entra nel risolutore com'e' (stesso id, stessa classe); asset non assegnati di un blocco
  con missioni formerebbero la vista residua con l'id del blocco (nessuno scenario ne ha).
- **Verifica del rischio del piano** (attributi della forza letti dal risolutore oltre a `assets`,
  `side`, `id`/`name`): `salvo_interceptors()` (ristretto nella vista) e la CLASSE della forza
  (`_can_disengage`: `Military` si', `Block` non militare no). Adattatore: la vista dichiara
  `can_disengage` calcolato sul blocco, e il risolutore onora un `can_disengage` booleano
  dichiarato. `morale_for`/`enemy_estimate_for` ricevono la vista (nessun chiamante di produzione).
  Rilevamento, nebbia di guerra, RWR, carburante, danno e munizioni leggono gli asset: invariati.

### Come si attribuiscono le differenze

Due catture di controllo, oltre a quella del codice di F4b:
1. **RNG riportato agli id di blocco** per i blocchi con UNA sola forza d'ingaggio (`event_id` e
   ordine delle forze calcolati con l'id del blocco al posto del `mission_id`), poi normalizzata
   (`force_id` di missione -> blocco, `block_id` tolto): **270 esecuzioni su 292 coincidono con F4a
   byte per byte**. Per tutte le esecuzioni con una missione per blocco la F4b cambia quindi SOLO
   gli stream casuali: stesso motore, altri numeri estratti.
2. **RNG riportato agli id di blocco per TUTTE le missioni** (anche nei blocchi con piu' missioni):
   le 22 esecuzioni restanti differiscono anche cosi'. Sono le differenze di comportamento.

### Esecuzioni invariate (33)

S10 (30: blocchi fermi senza missioni, stream invariato), S8 (blocchi fermi), ORC-fuel,
ORC-nocontact (nessun ingaggio).

### Esecuzioni cambiate per il solo stream RNG (237, una missione per blocco)

Stesso motore, estrazioni diverse: cambiano perdite, colpi, istanti, e in 51 esecuzioni anche
un'etichetta d'esito di forza. Non c'e' un effetto sistematico da spiegare (verifica 1 sopra): e'
la variabilita' del modello stocastico, che i test di scenario verificano per tendenza su piu'
seed. Per scenario (cambiate / con un esito di forza diverso / con distruzioni diverse):

| Scenario | Cambiate | Esito diverso | Distruzioni diverse |
|---|---|---|---|
| S1 | 16 | 2 | 12 |
| S2 | 24 | 9 | 19 |
| S3 | 20 | 10 | 18 |
| S4 | 16 | 6 | 12 |
| S5 | 12 | 4 | 9 |
| S6 | 4 | 3 | 4 |
| S9 / S9R | 18 / 24 | 0 / 0 | 16 / 12 |
| S11 | 6 | 0 | 5 |
| S12 | 12 | 1 | 10 |
| S13 / S14 | 6 / 6 | 0 / 0 | 4 / 6 |
| S15 / S16 | 12 / 4 | 0 / 1 | 7 / 4 |
| S17 | 15 | 3 | 13 |
| S18 `far` (Blue-East, Blue-West: una missione ciascuno) | 2 | 0 | 2 |
| S19AD (overflight, tor_rear, tor_forward: una missione) | 18 | 0 | 7 |
| VAL-det / VAL-agn | 3 / 4 | 0 / 0 | 2 / 4 |
| ORC-base / seed / interval / twofronts | 1 / 2 / 2 / 10 | 0 / 2 / 1 / 9 | 0 |

Esempi: `S1/S1-6/without_cas` primo colpo da 185.1 a 162.2 s, Red-Line una distruzione in meno;
`ORC-twofronts/S-det/*` Raider da DISENGAGED a HELD e Red-A, Red-B da HELD a DESTROYED;
`S2/S2-1-sead` Red-SAM da DISENGAGED a DESTROYED.

**S5 e la frequenza degli esiti rari.** Gli stream di F4a erano fortunati: con gli id di blocco
nell'RNG la formazione "ad oltranza" arriva al terzo strato in 4 dei seed S5-0..5 ma solo in 2 dei
seed S5-6..23 (6 su 24); con gli stream della F4b in 1 su 24 (S5-7), e con la dottrina di default 23
formazioni su 24 si fermano al primo strato. Stesso motore (verifica 1), campione piccolo.

### Esecuzioni cambiate anche nel comportamento (22, piu' missioni per blocco)

In tutte: il blocco ha un `ForceOutcome` per missione invece di uno. Il resto, per scenario
(confronto con l'RNG riportato al blocco, verifica 2, poi con gli stream della F4b):

- **S7** (6; Blue-Interdiction = Strike F-16C + Escort F-15C) e **S18 `network`** (6;
  Blue-Package = Strike + Escort): con gli stessi numeri casuali NESSUNA grandezza aggregata cambia
  (esiti, perdite, colpi, distruzioni): il blocco si divide in due forze, ciascuna HELD. Con gli
  stream della F4b cambiano perdite ed esiti come per lo stream (es. S7-0 Red-Escort da DISENGAGED a
  DESTROYED) e si vede il disingaggio indipendente: in `S7/S7-3` la scorta rompe il contatto a 200.6
  s (1 perdita) mentre lo strike resta HELD, in `S7/S7-4` la scorta e' distrutta (2 perdite) e lo
  strike resta HELD, in `S18/S18-5/network` lo strike disingaggia a 270.4 s (1 perdita) e la scorta
  resta HELD (prima l'intero Blue-Package era HELD).
- **S19** (4; Blue-Transit = CAS 2 A-10C, Escort 2 F-16C, Strike 1 B-52H): una missione di un solo
  aereo e' DESTROYED alla prima perdita. Con gli stessi numeri casuali `S19-2/run` passa da
  Blue-Transit HELD a CAS HELD, Escort HELD (1 perdita), Strike DESTROYED a 262.0 s: la perdita del
  B-52, che per il blocco di 5 aerei non bastava a rompere, distrugge la sua missione. Nelle altre
  tre il blocco era gia' DESTROYED e lo sono tutte e tre le missioni. Con gli stream della F4b Blue
  perde meno aerei (S19-0 da 4 a 2, S19-1 da 5 a 2): effetto dello stream (con l'RNG del blocco le
  perdite sono quelle di F4a).
- **S19AD `strela_standoff`** (6; Blue-CAS = 4 A-10C in 4 missioni per la geometria): **effetto di
  comportamento robusto, uguale con entrambi gli RNG**. Maverick lanciati da 8-10 (4-5 salve) a 16 (8 salve), Red-Line da
  DESTROYED (4 perdite) a HELD (3 perdite: lo Strela-10 sopravvive). Causa: la ripartizione del fuoco
  e la dottrina di tiro (saturazione del bersaglio, `_engaged_shooters`, `_coverage`) sono PER
  FORZA. In F4a i 4 A-10 erano una forza: lanciavano 2 Maverick ciascuno su bersagli diversi e
  l'ultimo aspettava (cas3 a 169.8 s sullo Strela). In F4b ogni aereo e' una missione e non vede le
  salve delle altre: tutti lanciano a 162.7 s e di nuovo a 164.2 s, si concentrano sugli stessi
  bersagli (in S19-0 ifv0 e' colpito da cas0, cas2 e cas3) e lo Strela resta in piedi.

### Nuove esecuzioni (36)

- **S20** (12, `Test_Session_Scenarios_S20.py`): composizione di S1 senza CAS; Blue-Armor in due
  missioni d'attacco sulla stessa rotta ('Blue-Armor:Tanks' 3 M1A2, 'Blue-Armor:IFV' 2 M2) e, per
  confronto, in una ('Blue-Armor:Attack'), 6 seed. E' lo scenario del criterio "Fatto quando":
  nella variante divisa le due missioni finiscono diversamente in 5 seed su 6 (es. S20-0:
  Tanks DISENGAGED a 231.9 s, IFV continua a sparare fino a 318.7 s e disingaggia a 319.0 s; S20-5:
  Tanks DISENGAGED a 294.4 s, IFV HELD e Red-Line rompe a 319.3 s), e in 4 seed gli asset di una
  missione sparano dopo il disingaggio dell'altra; con una missione, dopo la rottura nessun asset
  del blocco spara piu'.
- **S3** seed S3-10..19 (20) e **S5** seed S5-6, S5-7 (4): repliche aggiunte (v. sotto).

### Test di scenario

Asserzioni sugli id di forza (S1, S4, S6, S7, S11, S12, S15, S16, S17, S18, test dell'orchestratore e
di validazione): dalla F4b l'id di forza e' il `mission_id`. Le verifiche di struttura ("quali
blocchi combattono nello stesso ingaggio") leggono ora i blocchi (`Scenario_Fixtures.engagement_blocks`,
dal `block_id` degli esiti), con gli stessi valori attesi di prima; S7 verifica in piu' le due forze
d'ingaggio dello stesso blocco nello stesso ingaggio. In `Test_Session_Simulator` le attese sugli id
sono le missioni (`M-north`, `M-south`, `M-raid`, `M-stable`), e lo stream documentato si
riproduce a mano con la vista della missione. In `Test_Session_Validation` i `mission_id` sono id di
dominio ammessi nell'esito.

Repliche: le due verifiche statistiche al limite (S3, S5) sono state riprogettate il 2026-10-11
(v. «Riprogettazione dei test S3/S5» in fondo al documento); il campione di questo passo (S3 a 20
seed, S5 a 8) e' superato.

### Fotografia di riferimento

Rigenerata dopo questo confronto (`--capture` nel percorso standard) sul codice di F4b: 328
esecuzioni (292 + 36 nuove); due catture consecutive identiche (determinismo).

### Limiti noti introdotti

- ~~Nessuna ripartizione del fuoco fra missioni dello stesso blocco o lato~~ e ~~nessuna
  condivisione dell'informazione fra missioni~~: risolti con il dominio di coordinamento
  (decisioni dell'utente 6 e 7 del 2026-10-11, v. la sezione seguente).
- Una missione di un solo asset e' DESTROYED alla prima perdita (S19 Strike).

---

## Dominio di coordinamento: fuoco e rilevamenti condivisi fra missioni (decisioni 6 e 7)

**Base del confronto**: fotografia di F4b (`a4d8acf0`, 328 esecuzioni; ricontrollata IDENTICA al
codice di partenza `ed14aadf` prima delle modifiche).
**Dopo**: motore con il dominio di coordinamento. Gli scenari NON cambiano.

### Il cambio

- **Dominio di coordinamento** (`Logic/Mission_Adapter.coordination_domains`): due forze
  d'ingaggio dello stesso lato sono nello stesso dominio se hanno lo stesso blocco OPPURE
  appartengono alla stessa Operazione (`SessionOrder.operations` / `Mission.operation_id`), con
  unione transitiva (union-find). La vista residua e un blocco senza missioni hanno l'id del blocco
  e quindi stanno nel dominio delle missioni del blocco. Chiave = id di forza minore del dominio
  (senza legami: l'id della forza, comportamento di prima). Un'Operazione con missioni di lati
  diversi lega solo le missioni dello stesso lato (un dominio per lato, warning); il risolutore
  verifica comunque che un dominio non stia a cavallo di due lati (ValueError).
- **Decisione 6, fuoco** (`Engagement_Resolver`, parametro `coordination_of` di
  `resolve_engagement`, default None = la forza e' il proprio dominio): `_engaged_shooters`,
  `_force_shots_on` e quindi `_coverage`, `_blocked` e `_wait` contano le salve, in volo o
  schedulate, di tutte le forze del dominio. Invariati il tetto "due missili, poi guarda" (per
  tiratore e bersaglio), la soglia P_des (dottrina del lato) e le estrazioni RNG. Anche i
  lanciatori prioritari (L2/L3, `launchers_against`) sono registrati contro il dominio: un aereo
  che attacca una missione e' prioritario (ed esente dalla saturazione) per i tiratori delle altre
  missioni del dominio che lo hanno fra i PROPRI candidati, com'era per il blocco prima della F4b.
- **Decisione 7, percezione (opzione B)**: `seen_by`, `identified_by` e le classi RWR sono chiavati
  per dominio; un rilevamento vale per tutte le forze del dominio dall'istante del rilevamento.
  Rapporto percepito, fuoco senza risposta e peso R-CLS li leggono dal dominio, la forza propria
  resta quella della missione. **Nessun cueing**: i candidati di tiro restano per osservatore.
- Condivisione **istantanea**, senza latenza ne' perdite del canale: approssimazione dichiarata nei
  docstring.
- **Componenti** (`Session_Simulator._connected_components`): le forze di uno stesso dominio
  sono messe nella stessa run anche senza nemici in comune (la condivisione vale dentro una run),
  come lo era il blocco prima della F4b; la componente unita ha l'`event_id` delle forze riunite.

### Come si attribuiscono le differenze

Tre catture di controllo su copie del codice con un interruttore ciascuna (solo misura, non nel
repository), ristrette agli scenari con piu' missioni per blocco (S7, S18, S19, S19AD, S20):
1. percezione per forza (decisione 7 spenta): restano solo le differenze di S19AD, identiche
   byte per byte a quelle del codice completo -> S19AD e' la decisione 6, S20 la decisione 7;
2. componenti non unite per dominio: stesse differenze del codice completo -> nessun effetto
   negli scenari (nessuno ha missioni di un dominio su fronti disgiunti);
3. lanciatori L2 per forza: stesse differenze -> nessun effetto negli scenari.

### Esecuzioni cambiate (8 su 328)

| Scenario | Cambiate | Causa | Effetto |
|---|---|---|---|
| S19AD `strela_standoff` | 6 su 6 | decisione 6 (fuoco) | Maverick lanciati da 16 a 8-10, Red-Line da HELD (3 perdite) a DESTROYED (4 perdite: lo Strela-10 e' distrutto) |
| S20 `split` | 2 su 6 (S20-1, S20-3) | decisione 7 (percezione) | solo grandezze fini della missione 'Blue-Armor:IFV': rapporto percepito e soglia di rottura all'ultima valutazione |

- **S19AD standoff** (Blue-CAS = 4 A-10C in 4 missioni dello stesso blocco): torna nell'ordine
  di F4a, come atteso dalla decisione 6. Per seed (Maverick, perdite Red-Line): S19-0 10/4,
  S19-1 10/4, S19-2 8/4, S19-3 8/4, S19-4 8/4, S19-5 8/4 (F4b: 16/3 ovunque). Le salve degli altri
  aerei contano nella saturazione e nella ripartizione, quindi gli A-10C non sommano piu' le salve
  sugli stessi bersagli (meccanismo descritto nella F4b). Nuovo test
  `test_standoff_missions_share_the_fire` (6 seed): 8-10 Maverick, Red-Line DESTROYED, Strela
  distrutto.
- **S20 split** (Blue-Armor:Tanks + Blue-Armor:IFV, stesso blocco): in S20-1 l'IFV, che non aveva
  rilevato nessuno all'istante della sua ultima valutazione, percepisce i nemici rilevati dai carri:
  rapporto da indefinito a 0.67, soglia registrata da 0.249 a 0.201; in S20-3 da indefinito a 0.33,
  soglia da 0.145 a 0.084. Gli esiti non cambiano (S20-1: IFV HELD senza perdite; S20-3: l'IFV
  disingaggia comunque a 271.9 s con 1 perdita su 2, erosione 0.5 sopra entrambe le soglie).

### Esecuzioni invariate (320), con le attese della deviazione 7

Il piano si attendeva che la percezione condivisa riducesse le differenze di disingaggio di S7,
S18 e S19 rispetto a F4a. **Non succede: S7, S18 e S19 sono invariati.** Misura (sonda sulle
valutazioni della soglia di rottura, insieme dei nemici percepiti entro t dal dominio contro quello
della sola missione): in S7 (17 valutazioni) e S19 (19) ogni missione aveva gia' rilevato da se' gli
stessi nemici a ogni valutazione; in S18 2 valutazioni su 14 (scorta di Blue-Package) percepiscono
in piu' due infrastrutture (ponte e scambio di Red-Rail), che non cambiano ne' il rapporto
percepito ne' la soglia registrati (fotografia identica). Le differenze di S7/S18/S19 rispetto a F4a restano quindi quelle dello stream RNG e del
disingaggio per missione documentate nella F4b. Neanche la ripartizione del fuoco le tocca: in quegli
scenari le missioni dello stesso blocco non sparano agli stessi bersagli (fotografia identica).

S3 e S5 sono invariati: i test da riprogettare (deviazione 8) non sono toccati da questo passo.

### Test

- `Test_Engagement_Resolver`: `TestCoordinationDomainFire` (saturazione dall'altra forza, attesa
  dell'impatto altrui, ripartizione round-robin sul dominio, tetto per tiratore, mappa identita' =
  nessuna mappa, nessuna estrazione in piu', lanciatori registrati sul dominio, lati, tipi) e
  `TestCoordinationDomainPerception` (fuoco con risposta e rapporto percepito da un rilevamento
  della missione gemella, stesse estrazioni, nessun cueing).
- `Test_Mission_Adapter.TestCoordinationDomains`: stesso blocco, stessa Operazione (anche solo
  elencata dall'ordine), transitivita' (A-blocco1, B-blocco1+Op, C-blocco2+Op -> un dominio),
  vista residua, lati separati, determinismo, accettazione da parte del risolutore.
- `Test_Session_Simulator`: componenti unite per dominio, mappa passata a ogni ingaggio,
  Operazione fra blocchi diversi -> una run.
- `Test_Session_Scenarios_S19_Air_Defence.test_standoff_missions_share_the_fire`.

### Fotografia di riferimento

Rigenerata dopo questo confronto (`--capture` nel percorso standard): 328 esecuzioni; due catture
consecutive identiche (determinismo).

### Limiti noti

- **Nessun cueing del tiro**: un tiratore spara solo ai bersagli che ha rilevato lui; EWR->SAM,
  AWACS->caccia, scorta->strike restano una funzionalita' futura (Fase 0 C2).
- Condivisione istantanea, senza latenza ne' perdite del canale.
- Una missione di un solo asset e' DESTROYED alla prima perdita (S19 Strike).
- Difesa di salva per missione: superato dalla F4b++ (sezione seguente).

---

## F4b++: intercettori di dominio (deviazione 8c)

**Base del confronto**: fotografia di F4b+ (`098671d7`, 328 esecuzioni; ricontrollata IDENTICA al
codice di partenza `5c1c297a` prima delle modifiche).
**Dopo**: motore con la difesa di salva per dominio. **Fotografia IDENTICA (328 su 328)**: nessuno
scenario esercita il caso, la fotografia non e' stata rigenerata.

### Il cambio

- Una salva diretta a un asset della forza X e' intercettata dagli intercettori
  (`salvo_interceptors`) di QUALUNQUE forza del dominio di coordinamento di X
  (`_EngagementRun.domain_interceptors`), non piu' solo da quelli di X. Prima della F4b, con la
  forza = blocco, la scorta di un gruppo navale difendeva i trasporti dello stesso blocco; con
  scorta e trasporti in missioni distinte non piu': ora di nuovo si'.
- Invariati, per intercettore: geometria L1 (`_may_intercept`), tempi R-INT (`_in_time`, sul
  rilevamento del singolo intercettore: la percezione condivisa della decisione 7 non anticipa la
  traccia), canali per evento-salva, scorta di intercettori (R3, `consume_interceptions`).
- Ordine: quello globale della regola F (rank, poi id) sugli intercettori del dominio, indipendente
  dall'ordine di passaggio delle forze.
- Canali: due forze dello stesso dominio risolte nello STESSO istante sono servite dagli stessi
  canali (`instant_interceptions`: si sottraggono quelli gia' spesi per le altre forze del dominio
  in quell'istante; la scorta e' gia' scalata dal loro consumo). Le risoluzioni di una stessa forza
  restano a canali pieni, come prima.
- `SalvoResolution.capacity` e' la somma delle disponibilita' degli intercettori del dominio;
  l'`InterceptionEvent` porta l'intercettore (anche di un'altra forza) e la forza DIFESA
  (`force_id`); `apply_engagement_result` cerca gli asset fra tutte le forze passate, invariato.
- Senza `coordination_of` ogni dominio ha una sola forza: stessi intercettori, stesso ordine,
  nessuna sottrazione di canali, comportamento identico (test e fotografia).
- Nessun cueing, nessuna costante nuova.

### Perche' la fotografia non cambia

Il cambio agisce solo se un dominio ha piu' forze e una di esse e' colpita da colpi intercettabili
mentre un'ALTRA ha intercettori che soddisfano L1 e R-INT. Le forze divise in missioni sono quelle
di S7, S18, S19, S19AD e S20; la fotografia identica dice che in nessuna loro esecuzione questo
accade (verificato sul risultato, non analizzato scenario per scenario); i blocchi con intercettori
di S6 e S16 sono una sola forza. Prova fatta (solo misura, non nel repository) su una variante di S16 con le
corvette in una missione propria e il resto del porto nella vista residua: la capacita' delle
risoluzioni sulla vista residua sale da 0 ai canali delle corvette (il dominio funziona), ma le
corvette non intercettano per la regola R-INT (non hanno il tempo di reagire ai colpi diretti
alle strutture); con R-INT spenta intercettano. Per questo non e' stato aggiunto un test di
scenario: il caso e' coperto con stub nel risolutore.

### Test

- `Test_Engagement_Resolver.TestCoordinationDomainSalvoDefence`: la scorta (missione 'm1')
  intercetta la salva diretta al trasporto ('m2') con il dominio condiviso e non senza mappa
  (regressione); mappa identita' = nessuna mappa; scorta di un dominio diverso; lancio dentro il V_I
  della scorta (L1) e scorta senza tempo di reagire (R-INT) non intercettano; scorta per arma
  scalata alla scorta e applicata da `apply_engagement_result`; canali non contati due volte con
  due trasporti del dominio colpiti nello stesso istante (verificato anche per mutazione: senza il
  contabile per istante le intercettazioni salgono da 3 a 6); ordine deterministico con tre
  permutazioni delle forze.

### Limiti noti

- La condivisione dei canali e' per ISTANTE di risoluzione (entro `TIME_EPS`): due forze del
  dominio colpite a istanti diversi ma ravvicinati (meno di `salvo_window`) ricevono i canali pieni
  ciascuna, come una forza sola che subisce due eventi-salva distinti.
- Nessuno scenario esercita il caso (v. sopra).

## Riprogettazione dei test S3/S5 (deviazione 9, 2026-10-11)

Solo test e docstring (`Test_Session_Scenarios.py`; in `Scenario_Baseline.py` solo il nome della
nuova variante S5): il motore non e' toccato. Motivazione: dalla F4b i due test passavano solo
aumentando le repliche, perche' misuravano una metrica sbagliata (S3) o un evento raro (S5).

**S3** (stealth contro massa, 4 contro 8 F-15C, 20 repliche). Su 40 seed: senza stealth perdite
assolute Blue 3,90 / Red 3,68 (z = -1,4), frazione persa 97,5 % / 46 % (Blue peggio in 40 seed su
40); con stealth Blue 1,85 / Red 3,80, frazione 46 % / 47,5 %, differenza assoluta Red - Blue a
coppie +1,95 (sd 1,22, z = 10), rapporto di scambio 2,05-2,4 contro 0,94-1,0. Nuove verifiche:
(1) senza stealth la frazione persa da Blue supera quella di Red (aggregato e differenza a coppie
per seed >= 3 errori standard; sui 20 seed di test z = 16,4); (2) con stealth Red perde piu' aerei
assoluti di Blue (differenza media a coppie >= 3 errori standard; sui 20 seed media 2,3, z = 12,8);
(3) il rapporto di scambio migliora con stealth e Blue perde meno aerei (invariato). Helper
`_paired_z` nella classe; soglia `MIN_Z` = 3 dichiarata, non tarata. Con stealth il vantaggio e' nel
rapporto di scambio, non nella frazione persa.

**S5** (3 strati, 4 F-15E). Su 24 seed: default 23 su 24 si fermano al primo strato (prosegue S5-7);
PRESS_ON arriva al terzo strato 1 volta su 24. Nuova struttura (SEEDS da 8 a 12):
- default: maggioranza (stopped > went_on + held; sui 12 seed 11 contro 1) + invarianti per replica
  (strati in ordine geometrico, nessun lancio rosso dopo la rottura, fermata al primo strato =>
  nemmeno il terzo ha sparato);
- nuova variante «formazione resistente»: dottrina Blue di default con `RESISTANT_EROSION` = 0,65
  (costante di scenario, stima, non calibrata). Frequenza di «prosegue oltre il primo strato»: 0,5 ->
  4/24; 0,6 -> 7/24; 0,75 -> 18/24 (24 seed); 0,65 -> 23/40 (57,5 %); 0,7 -> 28/40 (70 %). Con 12 seed
  la probabilita' di non vedere un esito e' 0,12 %. Sui 12 seed di test: 7 proseguono, 5 si fermano.
  Asserzione «entrambi gli esiti compaiono» + le stesse invarianti;
- PRESS_ON: via `assertIn(3, fired)`; resta «almeno due strati in ogni replica» e l'ordine geometrico.
  Varianti per numero di aerei misurate su 24 seed (terzo strato): 4 -> 1/24, 5 -> 19/24, 6 -> 24/24,
  8 -> 24/24: nessuna fra il 30 % e il 70 %, quindi nessuna asserzione sul terzo strato (1/24 e' solo
  informazione nel docstring).

**Fotografia.** Prima: 328 esecuzioni IDENTICHE. Dopo: nessuna esecuzione esistente cambiata, 20
nuove (S5-8..11 default e PRESS_ON, S5-0..11 resistant); 348 esecuzioni; due catture consecutive
identiche byte per byte.
