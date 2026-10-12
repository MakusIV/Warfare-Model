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

---

## F4c: postura continua degli asset senza missione (D1.c, decisioni dell'utente 2026-10-11)

**Base del confronto**: fotografia della riprogettazione S3/S5 (`3d7b1fe5`, 348 esecuzioni;
ricontrollata IDENTICA al codice di partenza prima delle modifiche).
**Dopo**: motore con la postura continua. **346 esecuzioni identiche, 2 cambiate** (sotto),
nessuna nuova esecuzione cambiata da altro. Decisione dell'utente (2026-10-11): cambio ACCETTATO,
fotografia rigenerata (370 esecuzioni = 348 + 22 nuove; due catture identiche byte per byte).

### Il cambio

Decisioni dell'utente:
1. **aereo senza missione = a terra**: bersaglio di SUPERFICIE passivo, colpibile da bombe, razzi,
   cannoni e missili aria-suolo, mai ingaggiato da SAM/AAA/caccia come minaccia aerea, non spara mai;
2. **unita' terrestri e navali senza missione**: postura `Defense` dichiarata, tiro invariato.

Dove vive "a terra": un INSIEME di id (`grounded`) calcolato dalla sessione, mai uno stato
dell'`Aircraft` (nessuna mutazione degli asset).
- `Mission_Adapter.continuous_posture` (aereo -> `PARKED_POSTURE` = `StartMode.PARKING_COLD`;
  nave -> `Sea_Task.DEFENSE`; il resto -> `Ground_Action.DEFENSE`); la vista residua porta
  `postures` e `grounded`; `grounded_assets(forces)` raccoglie gli aerei della vista residua e dei
  blocchi senza missioni (passati tali e quali). Gli aerei di una missione non sono a terra (F5).
- `Session_Simulator.run_session` passa l'insieme a `schedule_contacts(grounded=...)` e a ogni
  `resolve_engagement(grounded=...)`. Insieme vuoto = comportamento di prima, percorso per percorso.
- **Rilevamento** (`Contact_Scheduler.mutual_detection_ranges`): un aereo a terra come bersaglio e'
  interrogato nel modo 'ground' (`GROUNDED_DETECTION_MODE`), come osservatore non ha portata
  (sensori spenti). Il risolutore ripete la regola per le finestre costruite dal chiamante (nessuna
  estrazione come osservatore) e spegne l'RWR del parcheggiato.
- **Fire control**: estensione facoltativa del protocollo, keyword `target_grounded=True` passata
  SOLO per un bersaglio a terra e solo se la fire control la dichiara (`**kwargs` compreso,
  `Engagement_Resolver.accepts_target_grounded`, introspezione della firma); altrimenti la chiamata
  di sempre con un warning per run. `Fire_Control.make_registry_fire_control` e la fixture di
  scenario la dichiarano. Nei registri l'aereo a terra usa la classificazione ESISTENTE di un aereo
  parcheggiato (`Context.Parked_Asset_Type`, `get_target_classification` -> 'Soft'; tabella
  `PARKED_TYPE_BY_AIR_TYPE`, nessuna costante numerica nuova): SAM e AAM esclusi dal filtro di
  superficie, bombe/razzi/cannoni/ASM con la riga 'Soft', gittata delle bombe dalla quota reale.
  Nella fixture il ruolo 'parked' e' un bersaglio di superficie della tabella di riferimento.
- **Tiro**: un aereo a terra non e' mai tiratore ne' intercettore. Chi lo attacca e' un lanciatore
  aria-superficie per L2/L3 (la difesa della base lo prioritizza).
- **Peso di minaccia**: nullo da entrambe le parti nel rapporto percepito (`_perceived_ratio`):
  escluso dai nemici percepiti e dalla forza propria. La forza "aerea" si decide sugli asset non a
  terra (una base con difese e aerei parcheggiati e' di superficie).
- **Disingaggio**: forza di soli aerei a terra senza dottrina (HELD, poi DESTROYED, come un blocco
  non militare); forza mista: erosione e shock della dottrina contano solo chi puo' ritirarsi,
  senza combattenti operativi nessun disingaggio, l'annientamento conta tutti; se la forza
  disingaggia gli aerei a terra restano bersagli (`_gone`). `ForceOutcome` e `SalvoResolution`
  contano tutti gli asset.
- **Danno**: `Damage_Model` e' indipendente dalla classe dell'asset; un `Aircraft` colpito da armi
  di superficie e' danneggiato e distrutto come ogni altro asset (verificato in S21/S21R), nessun
  adeguamento.
- **Domini di coordinamento**: invariati (la vista residua resta nel dominio del suo blocco).

### Esecuzioni cambiate (2 su 348): DA DECIDERE

`VAL-agn/S7-agn-2` e `VAL-agn/S7-agn-3` (mini-campagna di agnosticismo, `Test_Session_Validation.
TestAgnosticEndToEnd`): la seconda e la terza sessione sono SENZA missioni, quindi i 2 A-10C di
Blue-CAS, che prima restavano fermi IN VOLO nella posizione iniziale (x = -60 km, 3000 m) e
sparavano, ora sono a terra (decisione 1) e non sparano piu':
- S7-agn-2: Blue-CAS da 2 colpi a 0, nessun danno (prima 2 eventi), Red-Line da DISENGAGED a HELD;
- S7-agn-3: Blue-CAS da 2 colpi a 0, nessun danno, Red-Line 2 asset distrutti invece di 3.
Sonda sulla fotografia (solo misura): sono le UNICHE esecuzioni con aerei fuori missione. E'
l'effetto voluto della decisione 1, ma il piano chiedeva una fotografia identica. L'utente ha scelto
il 2026-10-11 di ACCETTARE il cambio (l'alternativa era dare a Blue-CAS una missione nelle sessioni
2-3, che avrebbe snaturato il test «senza missioni, forze ferme»). I test di `Test_Session_Validation`
verificano la concatenazione dello stato, non gli esiti, e passano.

### Scenario nuovo S21 / S21R (`Test_Session_Scenarios_S21.py`)

**S21** (tabella a ruoli, 8 seed, varianti 'parked' e 'control'): Red-Airbase (Military
'Airbase' senza missioni, MISTA: 4 MiG-29S sul piazzale con loadout 'CAP', Strela-10, Shilka)
attaccata da Blue-Strike (4 F-16C 'Strike', missione Strike in sorvolo a 3000 m). Controllo: la
stessa base senza aerei.

| Seed | MiG-29S distrutti | colpi Blue | colpi difese | Blue persi | Red-Airbase | controllo: colpi Blue / Blue persi |
|---|---|---|---|---|---|---|
| S21-0 | 3/4 | 8 | 13 | 2 | HELD (4 persi su 6) | 0 / 2 |
| S21-1 | 2/4 | 8 | 9 | 2 | HELD (4/6) | 0 / 3 |
| S21-2 | 3/4 | 9 | 10 | 2 | HELD (4/6) | 0 / 2 |
| S21-3 | 3/4 | 6 | 2 | 1 | HELD (4/6) | 0 / 0 |
| S21-4 | 3/4 | 4 | 13 | 2 | HELD (4/6) | 0 / 2 |
| S21-5 | 3/4 | 7 | 3 | 0 | HELD (4/6) | 0 / 0 |
| S21-6 | 1/4 | 5 | 7 | 1 | HELD (4/6) | 0 / 0 |
| S21-7 | 3/4 | 6 | 3 | 2 | HELD (4/6) | 0 / 1 |

Totale 21/32 distrutti (0,66). In ogni seed: i MiG-29S non sparano, non intercettano, non
infliggono danno; sono colpiti solo dall'arma aria-suolo dello strike ('test:agm'); le difese
colpiscono solo gli F-16C; la base perde 4 asset su 6 ma resta HELD (prima della F4c l'erosione
4/6 l'avrebbe fatta disingaggiare e gli aerei sarebbero diventati irraggiungibili). Controllo: lo
strike non spara mai (nessun bersaglio di superficie che il ruolo 'strike' possa ingaggiare).

**S21R** (fire control dei registri, 6 seed): Red-Apron (4 MiG-29S, blocco di soli aerei a terra)
+ Red-AD (Strela-10 + Shilka), Blue-CAS 2 A-10C 'Maverick/Gun CAS'. MiG-29S distrutti 4, 4, 4, 4,
3, 4 (23/24); armi sui parcheggiati: AGM-65D e Mk-82AIR (riga 'Soft'), mai l'AIM-9M; Red-Apron
DESTROYED in 5 seed, HELD in 1 (mai DISENGAGED); Red-AD distrutto in tutti i seed (la fire control
dei registri non ha ruoli: gli A-10C attaccano anche le difese); Blue-CAS perde 0-2 aerei.

Asserzioni (robuste, invarianti per replica + una frazione aggregata): nessun colpo, intercettazione
o danno dai parcheggiati; frazione distrutta aggregata >= `MIN_DESTROYED_FRACTION` = 0,5 (soglia di
test dichiarata, non tarata, circa due deviazioni standard sotto la misura); bersagli delle difese
solo Blue; danni sui parcheggiati solo da 'test:agm' dello strike (S21) o da armi non AAM (S21R);
Red-Airbase/Red-Apron mai DISENGAGED; controllo S21 senza colpi Blue, variante 'parked' con colpi
Blue in ogni seed.

Fotografia: 22 esecuzioni nuove in coda (`S21/<seed>/parked|control`, `S21R/<seed>`), catturate nella
rigenerazione.

### Test

- `Test_Contact_Scheduler.TestGroundedAircraftRanges`: modo 'ground' per il bersaglio a terra,
  nessuna portata come osservatore, default invariato, `schedule_contacts(grounded=...)`.
- `Test_Engagement_Resolver.TestGroundedAircraft` (non spara ne' osserva, colpito solo da armi di
  superficie, il SAM non lo ingaggia, keyword solo per i bersagli a terra, fire control ignara con
  warning, `accepts_target_grounded`, una estrazione in meno per finestra, insieme vuoto = identico),
  `TestGroundedForceDisengagement` (soli parcheggiati: DESTROYED senza disingaggio; mista: dottrina
  sui soli combattenti, aerei ancora colpiti dopo il disingaggio; nessun combattente operativo:
  nessun disingaggio), `TestGroundedTargetIsASurfaceLauncherTarget` (L2/L3 con bersaglio a terra).
- `Test_Fire_Control.TestFireControlGroundedAircraft`: chiave 'Soft', tabella dei tipi
  parcheggiati, SAM e AAM esclusi, righe 'Soft' delle armi CAS, gittata della bomba dalla quota
  reale, fire control dei registri e della fixture dichiarano l'estensione.
- `Test_Mission_Adapter.TestContinuousPosture`: postura per classe, etichette = valori di Context,
  vista residua mista, vista di missione senza postura, `grounded_assets`, nessuna mutazione.
- `Test_Session_Simulator`: insieme passato a scheduler e risolutore, postura della vista residua
  mista, insieme vuoto senza aerei fuori missione.

### Limiti noti

- Un aereo senza missione e' a terra nella sua posizione registrata, anche se la quota e' di volo
  (caso VAL-agn): la posizione non persiste fra sessioni (D1.d, F8) e il motore non lo porta a terra.
- Gli aerei a terra non hanno sensori ne' RWR: non contribuiscono alla percezione della base.
- Una fire control che non dichiara `target_grounded` li classifica come gli altri aerei (warning).
- Nessuna protezione di shelter/hangar: un aereo parcheggiato e' 'Soft' come all'aperto.
- La postura `Defense` delle unita' di superficie e' solo dichiarata (nessun effetto: tiro e
  rilevamento invariati per decisione); non entra nel `ForceOutcome`.
- La potatura per blocco dello scheduler conta ancora velocita' e portata degli aerei a terra
  (conservativa: piu' coppie esaminate, nessun contatto perso).
- La presenza prima della partenza (aerei con missione ancora a terra) e' della F5: l'insieme
  `grounded` e' per l'intera sessione; la F5 dovra' renderlo dipendente dal tempo.


## F5 passo (a): `grounded` dipendente dal tempo (deviazioni 12-13)

**Base del confronto**: fotografia di F4c (`af2efbe6`, 370 esecuzioni).
**Dopo**: motore con `grounded` come funzione del tempo. **370 esecuzioni IDENTICHE**, nessuna
rigenerazione della fotografia (verificato 2026-10-12: `--compare` IDENTICAL; suite 4072 test OK,
7 skipped). Il passo cambia la FORMA dello stato, non i dati di sessione: in sessione resta
l'insieme costante della F4c (ogni id a terra su tutta la linea del tempo), quindi scheduler e
risolutore percorrono gli stessi rami di prima.

### Il cambio

- `Contact_Scheduler.GroundedSchedule`: per asset, gli intervalli semiaperti `[lo, hi)` in cui e' a
  terra (all'istante del decollo e' gia' in volo, a quello dell'atterraggio e' gia' a terra).
  Immutabile, intervalli ordinati e fusi. `GroundedSchedule.of(...)` accetta `None`, uno schedule,
  una mappa `{id: [(lo, hi)]}` o un iterabile di id (la forma F4c: ogni id su `ALWAYS` = (-inf,
  +inf)). Interrogazioni: `at(id, t)`, `always(id)`, `ever(id)`, `transitions(id)`.
- `schedule_contacts(grounded=...)` accetta le tre forme; le finestre di una coppia sono SPEZZATE
  agli istanti di decollo/atterraggio (`_pair_windows`), cosi' ogni finestra ha stato costante per
  entrambi gli asset. Senza transizioni (insieme semplice) e' la sola chiamata di prima.
  Nuovo argomento facoltativo `legs`: tratti gia' calcolati dal chiamante, con precedenza sulle
  rotte (`_asset_legs`).
- `Engagement_Resolver`: ogni regola della F4c legge lo stato all'istante in cui si applica
  (finestra: punto medio; tiro: istante di tiro; classificazione verso la fire control: istante del
  LANCIO, una salva partita contro un aereo che decolla arriva comunque con l'arma scelta al lancio;
  intercettazione: istante di risoluzione; peso di minaccia, dottrina, `_gone`: istante corrente).
  Solo gli aerei SEMPRE a terra (`always`) restano esclusi fin dalla costruzione dalla dottrina,
  dagli intercettori, dai tiratori e dalla decisione «forza aerea»: un aereo a terra per un tratto e'
  un aereo e un combattente.
- `SessionOutcome.postures` (`{asset_id: postura}`, immutabile, ordinato) e parametro `postures` di
  `assemble_session_outcome`: predisposti, `Session_Simulator` non li valorizza ancora (restano
  vuoti, quindi la fotografia non cambia).

### Predisposto in `Mission_Adapter`, NON ancora cablato in sessione

Funzioni con test propri che i passi successivi collegheranno: `grounded_schedule`,
`grounded_intervals`, `movement_legs` (presenza ferma prima della partenza e dopo la fine, attese),
`mission_holds` e le azioni WAIT (`_wait_actions`, `_wait_end`), `lands_on_air_base` /
`is_air_base_reference` (aereo a terra dopo la fine SOLO su una base vera), `final_posture`,
`session_postures`, `OFF_SCENE_POSTURE`. Cablaggio: F5-B (presenza, postura nell'esito, scenari
E1/E3/aerei) e F5-C (WAIT, ETA, TOT, CAP in orbita).

### Verifica

Test nuovi in `Test_Contact_Scheduler`, `Test_Engagement_Resolver`, `Test_Mission_Adapter` (+33
rispetto a 4039). Suite 4072 OK; fotografia IDENTICA su 370 esecuzioni.


## F5 passo (b): presenza fuori dalla rotta e postura nell'esito (F5-B, deviazioni 12-13)

**Base del confronto**: fotografia di F4c/F5-A (`Test/baseline/scenario_baseline.json`, 370
esecuzioni; ricontrollata IDENTICA al codice di partenza `c6051fc8` prima delle modifiche,
2026-10-12).
**Dopo**: motore con presenza e postura cablate in sessione. Sulla STORIA (contatti, colpi, danni,
esiti, carburante) **368 esecuzioni identiche, 2 cambiate** (S6-0, S6-2, sotto); in TUTTE le 370 il
riassunto ha una voce nuova, `postures` (postura di ogni asset a fine sessione). 72 esecuzioni
nuove (scenario S22). Cambio ACCETTATO dall'utente il 2026-10-12; fotografia del repository rigenerata a 442
esecuzioni (370 + 72 nuove; due catture indipendenti identiche byte per byte).

### Il cambio

Decisioni dell'utente (D1.a/b, deviazione 13):
1. **unita' terrestri e navali di missione**: presenti FERME nella posizione di partenza prima di
   partire e in quella finale dopo la fine, in postura `Defense`, quindi rilevabili e ingaggiabili
   in quei tratti (tiro di sempre);
2. **aerei che non partono in volo** (parcheggio, pista): A TERRA dall'inizio della sessione al
   decollo, bersagli di superficie passivi come gli aerei senza missione della F4c;
3. **aerei dopo la fine della rotta**: a terra SOLO se l'ultimo punto e' LAND su una base vera
   (`Mission_Adapter.lands_on_air_base`: riferimento del waypoint a un asset di un blocco
   `is_Air_Base()`, OPPURE punto nell'area di una base del lato della missione: entro
   `AIR_BASE_AREA_RADIUS_M` = 3000 m, STIMA di progetto, da un asset non aereo di un blocco
   `is_Air_Base()`, `air_base_points`); altrimenti escono di scena all'arrivo come prima (postura
   `off_scene`) finche' la F6 non porta il rientro;
4. **postura nell'esito** (`SessionOutcome.postures`) per OGNI asset delle forze passate, anche dei
   blocchi senza missioni (deviazione 12): postura continua della F4c per gli asset senza missione
   (`parking_cold` aereo, `Defense` terra/mare), postura di fine missione per gli altri (`Defense` a
   movimento finito o non ancora iniziato, tipo di missione in movimento, `parking_cold` aereo a
   terra, tipo di missione aereo in volo, `off_scene` aereo uscito di scena).

Cablaggio (`Session_Simulator.run_session`):
- `Mission_Adapter.grounded_schedule(forze, movimenti)` al posto dell'insieme costante: allo
  scheduler e a ogni `resolve_engagement` (sempre a terra gli aerei senza missione, a intervalli
  quelli di missione);
- `Mission_Adapter.movement_legs` (movimento + presenza ferma) allo scheduler (`legs`) e al
  risolutore (tratti degli asset); il carburante usa i soli tratti di MOVIMENTO
  (`presence=False`): la presenza ferma non consuma, `FuelEvent` invariati;
- `Mission_Adapter.session_postures` -> `assemble_session_outcome(postures=...)`.
- Interruttori separati in `Mission_Adapter` (il vecchio `F5_PRESENCE_AND_WAITS` diviso in due):
  `F5_PRESENCE = True` (presenza, F5-B) e `F5_WAITS = False` (WAIT/ETA bloccate/TOT, F5-C, come
  prima: nessuna attesa, partenza invariata). La postura e' riportata in ogni caso (e' un'uscita).
- `Scenario_Baseline`: il riassunto registra `postures` se l'esito la porta; nuova opzione
  `--ignore KEY` (es. `--ignore postures`) per confrontare la sola storia.

### Come si attribuiscono le differenze

Catture complete (434 esecuzioni ciascuna, script di misura fuori dal repository che sostituisce
`Mission_Adapter._presence` o l'interruttore), confrontate sulle 370 esecuzioni della base (le
prime quattro prima dell'aggiunta del criterio d'area; la cattura finale, con il criterio d'area e
la variante S22-AIR 'base_area', e' nell'ultima riga):

| Cattura | Contro | Storia (`--ignore postures`) | Postura |
|---|---|---|---|
| cablaggio F5-B con `F5_PRESENCE = False` | base | IDENTICA (370) | voce nuova in 370 |
| solo presenza AEREI (prima del decollo + dopo l'atterraggio), terra/mare spenta | `F5_PRESENCE = False` | IDENTICA (370) | identica |
| solo presenza TERRA/MARE, aerei spenti (S6) | cattura finale | IDENTICA (4 esecuzioni S6, posture comprese) | identica |
| tutto attivo, senza criterio d'area | base | 2 cambiate (S6-0, S6-2) | voce nuova in 370 |
| FINALE: tutto attivo, con criterio d'area (442 esecuzioni) | base | 2 cambiate (S6-0, S6-2), identica alla riga sopra su 402 esecuzioni (posture comprese) | voce nuova in 370 |

Quindi: (a) il cablaggio in se' (programma a terra, tratti dati allo scheduler, carburante sul solo
movimento) non cambia nulla; (b) la presenza degli aerei non tocca nessuna esecuzione esistente (tutte
le missioni aeree delle fixture partono in volo, `StartMode.AIR`, e l'ultimo LAND non riferisce una
base); (c) le due esecuzioni cambiate sono dovute alla presenza di unita' navali dopo la fine
della rotta; (d) la postura nell'esito e' la stessa con o senza presenza in tutte le 370 (nessun
movimento delle fixture e' tagliato dalla fine della sessione, quindi nessuna postura "in
movimento").

Distribuzione delle posture nelle 370 esecuzioni (4742 asset): `Defense` 3263, `off_scene` 1419,
`parking_cold` 60 (gli aerei senza missione della F4c: VAL-agn, S21, S21R).

### Esecuzioni cambiate nella storia (2 su 370): presenza navale dopo l'arrivo

`S6/S6-0` e `S6/S6-2` (`TestS6CarrierGroupVersusCoastalDefence`, sessione di 7200 s): il gruppo
navale Blue-CSG (missione `Shore_Bombardment` da x = -150 km a x = -60 km) arriva a t = 6043 s. Prima
della F5-B spariva all'arrivo; ora resta fermo nel punto finale (in `Defense`) e continua a lanciare
missili antinave contro la Red-Flotilla (a ~108 km), che li intercetta:
- S6-0: salve Blue-CSG 9 -> 29 (colpi 18 -> 58, l'ultimo a 7185 s), intercettazioni Red-Flotilla
  18 -> 58; nessun danno nuovo, esiti di forza invariati;
- S6-2: salve Blue-CSG 26 -> 41 (colpi 52 -> 82), intercettazioni Red-Flotilla 52 -> 80; una corvetta
  (`Red-Flotilla/fsg1`) distrutta a 6945 s da un missile del CG-65, Red-Flotilla HELD -> DISENGAGED
  (6945 s), eventi di danno 10 -> 11.
`S6-1` e `S6-3` invariate: la Red-Flotilla aveva gia' disingaggiato prima dell'arrivo (5806 s e
6045 s). E' l'effetto ATTESO della decisione 1 (una nave arrivata e' ancora li', con il tiro di
sempre). I test di S6 verificano la fusione delle finestre e i domini, non i conteggi, e passano.

Nessun cambio inatteso: nessuna esecuzione con unita' terrestri cambia, perche' nelle fixture le
missioni terrestri partono a t = 0 (nessun tratto prima) e quelle che arrivano prima della fine non
hanno piu' nemici a portata dopo l'arrivo (o il loro ingaggio era gia' concluso).

### Scenario nuovo S22 (`Test_Session_Scenarios_S22.py`, 72 esecuzioni)

**S22-E1** (esperimento E1 dell'analisi del 26/09, 8 seed): Red-Post 3 BMP-2 fermi in (0, 0) con
sensore 'ground' dichiarato di 4,2 km; Blue-Armor 1 M1A2 che non spara (ruolo 'unarmed').
'finished': missione da -12 km a -4 km a 10 m/s, arrivo a 800 s (contatto da 780 s: prima della
F5-B 20 s di finestra, meno del rilevamento + reazione, nessun colpo possibile); 'static': lo stesso
carro senza missione a -4 km (E2, riferimento). Misura: Red spara in 8/8 repliche in entrambe le
varianti; in 'finished' ogni colpo parte dopo l'arrivo (811-828 s) e il carro e' messo fuori
combattimento in 8/8; in 'static' i colpi partono a 31-41 s.

**S22-E3** (E3, 8 seed): il carro e' a -4 km e parte a 1000 s verso -12 km (esce dal sensore a
1020 s); 'not_departed': partenza oltre la fine della sessione. Red spara in 7/8 repliche in
entrambe le varianti, ogni colpo PRIMA della partenza (31-61 s); postura finale `Defense` (finita a
1800 s, o non partita).

**S22-AIR** (8 seed, 5 varianti): Red-Airbase (Military 'Airbase': 2 MiG-29S 'CAP' + deposito
`Structure` 'Oil_Tank', riferimento della base) e Blue-Strike (2 F-16C 'Strike', sorvolo a 3000 m,
fuoco solo sui bersagli 'parked'). 'parked': missione Red dal parcheggio con decollo a 900 s, strike a
t = 0: MiG colpiti in 8/8 repliche (16/16 danneggiati, 9/16 distrutti), solo da 'test:agm', colpi
tutti prima del decollo; 'airborne': strike a 1500 s, MiG gia' decollati e usciti di scena: nessun
colpo; 'landed': MiG in volo da est, LAND sul deposito della base a 240 s, strike a 1500 s: di nuovo a
terra e colpiti (16/16 danneggiati, colpi solo dopo l'atterraggio), postura `parking_cold`;
'no_base': stesso volo, LAND senza riferimento a 30 km dalla base (fuori area): escono di scena,
nessun colpo, postura `off_scene`; 'base_area': LAND senza riferimento a 1,9 km dal deposito (dentro
l'area): a terra e colpiti come 'landed', postura `parking_cold`.
I MiG non sparano ne' intercettano mai.

Controllo con `F5_PRESENCE = False` (sonda fuori dal repository): E1 'finished' e E3 'late' 0 colpi
su 8 seed, nessun danno ai MiG in 'parked' e 'landed': lo scenario distingue la F5-B.

Asserzioni: invarianti per replica (chi spara, a chi, quando rispetto ad arrivo/partenza/decollo/
atterraggio; postura nell'esito) e frazioni aggregate con soglie DICHIARATE (stime di test, non
tarate): `MIN_ENGAGED_FRACTION` = 0,5 (attesa a priori ~0,93: Pd ~0,59 per osservatore a 4 km con
3 osservatori), `MIN_HIT_FRACTION` = 0,5 (misura 1,0); 'finished' e 'static' ingaggiati in un numero
di repliche che differisce al piu' di 2 (margine dichiarato). Costanti dello scenario dichiarate di
test: portata 4,2 km, velocita' 10 m/s (carro) e 250 m/s (MiG), istanti 900 s e 1500 s.

### Test

- `Test_Session_Simulator.TestPresenceAndPostures` (nuova): tratti di presenza a scheduler e
  risolutore, aereo in volo assente fuori dalla rotta, programma a terra di un aereo dal parcheggio,
  carburante sul solo movimento, posture di tutti gli asset (anche di blocchi senza missioni), postura
  in movimento / prima del decollo, interruttore spento = tratti della sola rotta. Adeguati
  `test_aircraft_without_mission_are_grounded...` e `test_every_aircraft_in_a_mission...` (il
  risolutore riceve un `GroundedSchedule`, non piu' un frozenset) e
  `test_nothing_moves_nothing_meets` (l'esito porta le posture).
  Nuovo `test_landing_in_the_area_of_an_own_air_base` (area di una base del proprio lato: a terra
  dall'arrivo; base nemica: esce di scena).
- `Test_Mission_Adapter`: `_F5Active` attiva i due interruttori; nuova `TestF5BSwitches` (default:
  presenza attiva, attese spente; una WAIT dichiarata non produce attese; ETA bloccata sul punto di
  partenza non sposta la partenza); nuova `TestAirBaseArea` (`air_base_points`: asset non aerei
  delle basi vere, filtro di lato; LAND dentro/fuori `AIR_BASE_AREA_RADIUS_M`).
- `Test_Session_Scenarios_S22` (nuovo, 16 test).

### Limiti noti

- La postura nell'esito NON tiene conto della distruzione: un aereo distrutto sul parcheggio prima
  del decollo e' riportato `off_scene` (dove sarebbe secondo il piano); lo stato distrutto e' negli
  asset e nel `MissionOutcome`. Decisione dell'utente (2026-10-12): rimandata, da rivalutare con la F6 (fine missione).
- La presenza dopo la fine e' nella posizione finale della rotta, senza criteri di fine missione
  (F6): un asset senza carburante resta comunque "arrivato" (P4).
- Un aereo che parte dal parcheggio e' a terra nel PRIMO punto della rotta, alla sua quota: la rotta
  deve cominciare sulla base (quota del terreno), il motore non la porta a terra.
- Un aereo che atterra su una base vera e' a terra dall'istante d'arrivo all'ultimo punto (nessuna
  fase di rullaggio). L'area di una base e' un cerchio di `AIR_BASE_AREA_RADIUS_M` (stima) intorno
  a ciascun asset non aereo della base, non il perimetro reale (modulo mappe); conta solo il lato
  della missione (atterrare su una base nemica non e' un atterraggio), e una base senza asset non
  aerei ha area vuota (resta il criterio del riferimento).
- Attese WAIT, ETA bloccate e TOT restano spente (F5-C).

### Verifica

Suite 4101 test OK (7 skipped; +29 rispetto a 4072). Fotografia: prima delle modifiche `--compare`
IDENTICA su 370; dopo, `--compare <base> --ignore postures` = 2 esecuzioni cambiate (S6-0, S6-2) + 72
nuove (S22), senza `--ignore` le 370 differiscono tutte per la voce `postures`. Cambio accettato dall'utente il
2026-10-12 e `Test/baseline/scenario_baseline.json` rigenerato (442 esecuzioni).


## F5 passo (c)-(d): attese WAIT, ETA bloccate, TOT comune, ETA effettive (F5-C, deviazione 13)

**Base del confronto**: fotografia di F5-B (`Test/baseline/scenario_baseline.json`, 442 esecuzioni;
ricontrollata IDENTICA al codice di partenza `b63ba53a` prima delle modifiche, 2026-10-12).
**Dopo**: `Mission_Adapter.F5_WAITS = True` e TOT comune delle Operazioni cablato in sessione. Sulla
STORIA (contatti, colpi, danni, esiti, carburante, posture) **442 esecuzioni identiche, nessuna
cambiata**; in 401 il riassunto ha una voce nuova, `actual_etas` (ETA effettive delle missioni; le
altre 41 non hanno missioni). 80 esecuzioni nuove (scenario S23). Fotografia del repository NON
rigenerata (in attesa della decisione dell'utente): cattura finale fuori dal repository (522 esecuzioni).

### Il cambio

Decisioni del Piano (Fase 5, N2.b/N2.c):
1. **Azione WAIT** (`MissionAction`, modo 'hold' o 'orbit', durata o fino all'istante t, con la sua
   condizione d'avvio): un tratto FERMO nel punto della rotta (`AssetMovement.holds`,
   `Mission_Adapter._timeline`); i tratti successivi sono spostati della durata. Le attese
   sono le stesse per tutti gli asset della missione (regola A).
2. **Orbita = presenza ferma nel punto** per la durata: approssimazione DICHIARATA, nessun circuito
   geometrico (`MissionAction` non dichiara raggio ne' velocita' d'orbita: nessuna stima introdotta).
   Le finestre di contatto di una CAP in orbita coprono quindi tutta l'attesa.
3. **ETA bloccate e TOT**: con `start_time` la missione attende nel punto PRECEDENTE quello bloccato
   quanto basta per arrivarci all'istante (`mission_holds`); senza `start_time` la partenza e'
   derivata all'indietro (ETA o TOT meno percorrenza e attese di durata nota: anticipo, dalla F3 per
   il TOT); un'ETA bloccata sul punto di partenza piu' tarda di `start_time` ritarda la partenza. In
   ritardo: warning, l'ETA effettiva lo riporta (la velocita' non cambia).
4. **TOT comune di un'Operazione** (`Operation.tot`, prima non letto da nessuno):
   `Mission_Adapter.operation_tots(missioni, operazioni)` lo assegna alle missioni dell'Operazione che
   non dichiarano un `tot` proprio; agisce come il TOT della missione (attese prima del punto
   d'ancoraggio ATTACK/OBJECTIVE). Spento con `F5_WAITS = False`.
5. **Tratti**: le attese entrano in `movement_legs`, quindi nei tratti dati allo scheduler (`legs`) e
   al risolutore (stessi oggetti, come la presenza della F5-B).
6. **Carburante INVARIATO** (Piano: consumo nel tempo = F6): il consumo e' in distanza sui soli tratti
   di movimento e un tratto fermo ha lunghezza nulla, quindi attese e orbite NON consumano; il
   `FuelEvent` resta uno per asset, all'istante di fine movimento (spostato dalle attese).
7. **ETA effettive**: `MissionOutcome.actual_etas` esisteva gia' dalla F3 (immutabile, validato non
   decrescente) ed era gia' calcolato da `Mission_Adapter.waypoint_times` (attese comprese); la F5-C
   non cambia il campo ne' il calcolo, documenta che sono istanti d'ARRIVO ai punti dai tratti (prima
   di un'eventuale attesa nel punto). `Scenario_Baseline` registra la voce `actual_etas`
   (`{mission_id: [ETA | None]}`) solo se l'esito porta esiti di missione; `--ignore actual_etas`.

Decisioni non coperte dal Piano, scelte le piu' semplici (DA CONFERMARE):
- una missione con un `tot` proprio DIVERSO dal TOT comune della sua Operazione e' un ordine
  incoerente: `ValueError` (in `operation_tots`, quindi in `run_session`); uguale e' accettato;
- con `start_time` dichiarato il TOT comune NON sposta la partenza: si sincronizza con un'attesa
  (la missione aspetta in volo/a terra nel punto prima dell'ancoraggio); la partenza e' anticipata
  solo per le missioni senza `start_time`, dal proprio TOT o ETA bloccata (una missione ha sempre un
  proprio istante bloccato, quindi il TOT comune non deriva mai da solo una partenza);
- un TOT senza punto ATTACK/OBJECTIVE e con `start_time` e' ignorato con un warning (prima in
  silenzio).

### Come si attribuiscono le differenze

| Cattura | Contro | Esito |
|---|---|---|
| codice di partenza (prima delle modifiche) | base | IDENTICA (442) |
| FINALE, `--ignore actual_etas` | base | IDENTICA sulle 442, 80 nuove (S23) |
| FINALE senza `--ignore` | base | 401 esecuzioni differiscono SOLO per la voce nuova `actual_etas` (assente nella base); 41 identiche (nessuna missione) |
| FINALE | cattura con `F5_WAITS = False` (script fuori dal repository) | IDENTICA sulle 442 (anche `actual_etas`); nelle 80 di S23 differiscono solo le varianti che usano le attese: S23-CAP 'during' e 'after', S23-HOLD 'hold', S23-TOT 'operation' (32 esecuzioni) |

Quindi: nessuna esecuzione esistente usa WAIT, ETA bloccate o TOT (verificato anche sulle fixture:
nessuna dichiara azioni WAIT, `eta_locked`, `tot` o Operazioni con TOT), le attese non cambiano ne'
la storia ne' le ETA effettive delle 442, e l'unica differenza e' il campo nuovo nel riassunto.
Nessun cambio inatteso.

### Scenario nuovo S23 (`Test_Session_Scenarios_S23.py`, 80 esecuzioni, 17 test)

Ogni scenario ha una variante di controllo `waits_off` (`F5_WAITS` spento con un patch nel
`setUpClass`, registrata nella fotografia come le altre).

**S23-CAP** (8 seed, 4 varianti): Red-CAP 2 MiG-29S ('fighter', sensore 'air' dichiarato 30 km) da
x = -75 km al punto O = (0, 0) a 250 m/s (arrivo 300 s), WAIT 'orbit' 1500 s, rientro a ovest;
Blue-Bomber 2 F-16C che non sparano, da nord a sud per O. 'during' (passaggio a 1000 s): la CAP spara
in 8/8 repliche, 32 lanci tutti fra 877 e 927 s (dentro l'orbita), 13/16 bombardieri distrutti;
'after' (passaggio a 2200 s), 'no_wait' (stessa CAP senza WAIT) e 'waits_off': nessun lancio, nessun
danno. Sonda dello scheduler (fuori dalla sessione): un osservatore fermo sotto O ha con ogni MiG una
finestra che copre [300, 1800] s con l'orbita, non senza. Distanze di `FuelEvent` della CAP identiche
con e senza orbita (limite F6).

**S23-HOLD** (8 seed, 3 varianti): S22-E1 rifatto con una sosta: M1A2 da x = -12 km a W1 = (-4 km, 0)
(800 s), WAIT 'hold' 600 s, poi a sud fino a (-4 km, -12 km); 3 BMP-2 con sensore 'ground' 4,2 km e
tiro DICHIARATO senza effetto (precisione 0, il carro sopravvive e la ripartenza e' misurabile).
'hold': Red spara in 7/8 repliche, in tutte e 7 anche dopo 948 s (uscita dal sensore senza sosta),
colpi fra 811 e 1541 s (uscita con la sosta ~1548 s), ETA effettive (0, 800, 2600); 'no_hold' e
'waits_off': colpi fra 811 e 941 s, ETA (0, 800, 2000).

**S23-TOT** (8 seed, 3 varianti): Blue-Near (x = -60 km) e Blue-Far (x = -120 km), 2 F-16C ciascuno
con lanci dichiarati senza effetto e sensore 'ground' dichiarato 10 km, missione NAV -> ATTACK
(x = -15 km) -> LAND, nell'Operazione 'Op-Strike'; Red-Depot 3 depositi in (0, 0). 'operation'
(partenza 0, `Operation.tot` = 600 s): ATTACK raggiunto a 600 s da entrambe (la vicina attende 420 s,
la lontana 180 s al punto di partenza), distanza media fra i primi lanci 0,8 s; 'own_tot' (nessuna
partenza, `tot` = 600 per missione): partenze derivate 420 s e 180 s, stessi arrivi e stessi lanci;
'waits_off': ATTACK a 180 s e 420 s, distanza fra i primi lanci 240,8 s.

**ETA effettive** (tutti gli scenari): `actual_etas` dell'esito = istanti d'arrivo dai tratti
(`waypoint_times`, attese comprese) per ogni missione senza asset distrutti.

Soglie DICHIARATE di test (non tarate sul risultato): `MIN_FIRING_FRACTION` = 0,5 (CAP che spara;
carro ingaggiato durante la sosta, stessa stima di S22), `TOT_SPREAD_RATIO` = 0,5 (distanza media
fra i primi lanci con il TOT al massimo la meta' di quella senza attese). Costanti dello scenario
dichiarate di test: sensori 30 km (CAP), 10 km (strike), 20 km (sonda), 4,2 km (BMP); velocita' 250
m/s e 10 m/s; tiri a precisione 0.

Controllo con `F5_WAITS = False` su tutto il file (sonda fuori dal repository): 7 test su 17
falliscono (CAP che spara, finestre per tutta l'orbita, ETA dell'orbita, TOT comune, lanci
sincronizzati, carro ingaggiato nella sosta, ripartenza): lo scenario distingue la F5-C.

### Test

- `Test_Mission_Adapter`: `TestF5BSwitches` diventa `TestF5Switches` (default: presenza e attese
  attive; una WAIT produce l'attesa; con le attese spente il comportamento della F5-B; ETA bloccata
  sul punto di partenza ritarda `start_time`); nuova `TestOperationTot` (`operation_tots`, TOT
  proprio uguale/diverso, interruttore spento, TOT senza ancoraggio con warning).
- `Test_Session_Simulator.TestWaitsAndEtas` (nuova): sosta come tratto fermo a scheduler e
  risolutore, ETA effettive con la sosta, carburante invariato (distanza della sola rotta, evento a
  fine movimento), interruttore spento, TOT comune di un'Operazione in sessione, TOT incoerente.
- `Test_Session_Scenarios_S23` (nuovo, 17 test).

### Limiti noti

- Attese e orbite NON consumano carburante (consumo in distanza, F6: `Fuel_Model` per tratto).
- Orbita senza circuito: l'aereo e' fermo nel punto (errore di posizione pari al raggio del circuito
  reale, qualche km per un caccia); nessuna velocita' d'orbita, quindi nessun effetto della cinematica
  sul rilevamento o sul tiro durante l'attesa.
- In ritardo su un'ETA bloccata la missione non accelera (warning + ETA effettiva).
- Il TOT comune si applica con le attese: una missione con `start_time` troppo tardo non lo rispetta
  (warning), nessuna ripianificazione.
- Le ETA effettive sono gli istanti d'arrivo (non di partenza dopo l'attesa) e non tengono conto dei
  criteri di fine missione (F6).
- Osservazione non corretta (precedente alla F5-C, F5-B): se i tratti di un asset di missione cadono
  tutti fuori dalla sessione e non c'e' presenza (aereo in volo che parte dopo la fine), lo scheduler
  ricade sulla posizione registrata dell'asset (`_asset_legs`: tratti vuoti -> `static_legs`). Nessuno
  scenario lo esercita.

### Verifica

Suite 4131 test OK (7 skipped; +30 rispetto a 4101: 17 S23, 7 `Test_Session_Simulator`, 6
`Test_Mission_Adapter`). Fotografia: prima delle modifiche `--compare` IDENTICA su 442;
dopo, `--compare <base> --ignore actual_etas` = 80 nuove (S23) e nessuna cambiata; senza `--ignore`
le 401 esecuzioni con missioni differiscono solo per la voce `actual_etas`.

### Correzione: TOT per missione (2026-10-12)

**Decisione dell'utente (2026-10-12)**: il TOT (Time Over Target) e' SPECIFICO DI OGNI MISSIONE e NON e'
condiviso dalle missioni di un'Operazione. Esempio: un'Operazione di due missioni che partono insieme,
una Fighter Sweep su una zona che anticipa l'arrivo nella stessa zona dei bombardieri della seconda
missione: le due missioni hanno TOT DIVERSI. Il TOT comune descritto sopra (punto 4 de "Il cambio" e
la prima decisione "da confermare") non ha quindi senso ed e' stato RIMOSSO; le sezioni precedenti
restano come storia della F5-C.

Rimosso: il campo `Operation.tot` (con la sua validazione), `Mission_Adapter.operation_tots` e
`_effective_tot`, il parametro `tot` di `_locked_targets`/`mission_holds`/`mission_movements`, la
chiamata in `Session_Simulator.run_session`. La missione usa solo il proprio `Mission.tot`, come prima
della F5-C; il resto del meccanismo resta invariato (TOT ancorato al primo ATTACK/OBJECTIVE, partenza
derivata senza `start_time`, attesa prima del punto d'ancoraggio con `start_time`). Missioni
coordinate dichiarano ciascuna il proprio TOT (uguali o sfalsati).

**S23-TOT rifatto** (`TestS23TotPerMission`, il caso dell'utente): Blue-Sweep (2 F-16C 'CAP', missione
'Fighter_Sweep', ruolo 'unarmed', a x = -60 km) e Blue-Strike (2 F-16C 'Strike', lanci dichiarati
senza effetto e sensore 'ground' dichiarato 10 km, a x = -120 km), stessa Operazione senza TOT, stessa
rotta NAV -> ATTACK (x = -15 km) -> LAND a 250 m/s. TOT dello strike 600 s, dello sweep 600 -
`SWEEP_LEAD` = 480 s, con `SWEEP_LEAD` = 120 s STIMA DI TEST (non un dato dottrinale). Varianti:
'own_tot' (partenza 0 per entrambe: ATTACK a 480 s e 600 s, attese 300 s e 180 s al punto di
partenza), 'derived' (nessuna partenza: derivate 300 s e 180 s, stessi arrivi; nuova), 'waits_off'
('own_tot' con `F5_WAITS` spento: ATTACK a 180 s e 420 s). Eliminata la variante 'operation'.
Risultati su 8 seed: lo strike lancia in 8/8 repliche in ogni variante, primi lanci fra 627,5 e 627,9
s con i TOT ('own_tot', 'derived') e fra 447,5 e 447,9 s con le attese spente; lo sweep non lancia mai.
Test (5): ciascuna missione raggiunge il PROPRIO TOT; lo sweep precede lo strike esattamente di
`SWEEP_LEAD` (240 s con le attese spente); partenze; lo strike lancia solo dopo il proprio ATTACK;
ETA effettive = istanti dai tratti. Rimossa la soglia `TOT_SPREAD_RATIO` (non piu' usata).

**Test**: `Test_Mission_Types` (Operation senza `tot`: il campo non esiste, `tot=` e' un TypeError);
`Test_Mission_Adapter` `TestOperationTot` -> `TestTotPerMission` (due missioni della stessa
Operazione con TOT diversi raggiungono ciascuna il proprio, con partenza comune e derivata; una
missione senza TOT non ne eredita uno; TOT senza ancoraggio ignorato con warning);
`Test_Session_Simulator.TestWaitsAndEtas` (`_tot_run` con TOT 780/900 s per missione; via il test del
TOT incoerente con quello d'Operazione).

**Fotografia** (`--compare` contro `Test/baseline/scenario_baseline.json`, 522 esecuzioni): prima delle
modifiche IDENTICA; dopo, differenze SOLO in S23-TOT: 8 rimosse ('operation'), 16 cambiate ('own_tot'
e 'waits_off', scenario rifatto: forze, tipi di missione e TOT), 8 nuove ('derived'); le altre 498
identiche. Fotografia del repository NON rigenerata (cattura finale fuori dal repository, 522
esecuzioni).

Suite 4133 test OK (7 skipped; +2 rispetto a 4131: +1 `Test_Mission_Types`, +1 S23; in
`Test_Mission_Adapter` e `Test_Session_Simulator` lo stesso numero, test sostituiti).
