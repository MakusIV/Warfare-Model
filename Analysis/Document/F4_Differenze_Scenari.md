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

## F6 passo A: carburante per tratto e vincolo del movimento (F6-A, deviazione 14)

**Base del confronto**: `Test/baseline/scenario_baseline.json` (522 esecuzioni), ricontrollata
IDENTICA al codice di partenza (`03d77640` + Piano non committato) prima delle modifiche, 2026-10-12.
**Dopo**: `Session_Simulator.F6_FUEL_PER_LEG = True` e `F6_FUEL_CONSTRAINT = True`. Sulla STORIA
(contatti, colpi, danni, esiti, posture, ETA) **nessuna delle 522 esecuzioni cambia**; 126 cambiano
nel carburante: 88 solo nella FORMA degli eventi (uno per tratto), 32 nel consumo delle attese, 6 per
un arrotondamento all'ultima cifra. 88 esecuzioni nuove (scenario S24). Fotografia del repository NON
rigenerata: cattura finale fuori dal repository (610 esecuzioni).

### Il cambio

Decisioni dell'utente (2026-10-12, vincolanti):
1. **Un `FuelEvent` per tratto** (`Fuel_Model.build_leg_fuel_event`), di movimento o fermo; campi
   nuovi con default (forma precedente compatibile): `t_start`, `duration`, `duration_covered`,
   `stationary`. Tratto di movimento: in distanza come prima. **Tratto fermo** (attese e orbite della
   F5-C): consumo NEL TEMPO pari al movimento alla velocita' di CROCIERA dell'asset
   (`Fuel_Model.cruise_speed` = `speed['nominal']` del registro): `durata x crociera` metri equivalenti,
   al regime di crociera (`HOLD_REGIME`) anche se l'asset ha combattuto. Nessuna costante nuova.
   IPOTESI DICHIARATA: il loiter reale consuma meno della crociera (sovrastima pessimistica per gli
   aerei); stesso criterio per terra e mare (un'unita' in sosta a motore acceso consuma come in marcia:
   sovrastima, nessun dato di consumo da fermo nei registri). Un asset senza velocita' di crociera nota
   non consuma nelle soste. Carburante di partenza e rifornimenti NON toccati (rifornimento: F8).
2. **Vincolo del movimento e dei contatti**: il carburante dipende solo dai tratti e dal carburante di
   partenza, quindi `Fuel_Model.fuel_exhaustion` calcola A MONTE (al regime di crociera) istante e
   punto dell'esaurimento (interpolato nel tratto); `Session_Simulator` tronca i tratti di presenza a
   quel punto PRIMA dello scheduler e li passa come `legs` (meccanismo della F5-A) a scheduler e
   risolutore: oltre il punto l'asset non si muove e non ha contatti.
3. **Esito dell'esaurimento** (`Session_Simulator.FuelEnd`):
   * terra/mare: FERMI nel punto fino a fine sessione, presenti e bersagli (come la presenza fuori rotta
     della F5-B), postura `Defense`, NON distrutti;
   * aereo a secco in volo con una base aerea DEL PROPRIO LATO (`Mission_Adapter.air_base_points`)
     entro quota x `Fuel_Model.GLIDE_RATIO`: planata in linea retta sulla base piu' vicina alla
     velocita' di crociera, poi A TERRA sulla base (programma `grounded` dall'atterraggio, bersaglio di
     superficie passivo, postura `parking_cold`);
   * aereo a secco in volo senza base raggiungibile: PERSO all'esaurimento; salute a 0 con
     `Asset.apply_damage` (stato `Destroyed` come in combattimento) SENZA `DamageEvent` nell'esito (non
     e' un colpo); postura `off_scene` (la postura `destroyed` resta rimandata alla F6-B);
   * aereo ancora a terra all'esaurimento, o a quota <= 0 (serbatoio vuoto al decollo): resta fermo a
     terra nel punto (non perso).
4. **Esiti**: nuovo `AssetEndReason.FUEL_EXHAUSTED` (BINGO resta riservato al bingo in volo della
   F6-B); l'invariante di `AssetMissionOutcome` ammette `state` DESTROYED con FUEL_EXHAUSTED (aereo
   perso). Per asset: perso = DESTROYED/FUEL_EXHAUSTED all'istante dell'esaurimento (una distruzione in
   combattimento precedente prevale); fermo o atterrato = OPERATIONAL/DAMAGED, FUEL_EXHAUSTED; i punti
   dopo l'esaurimento non sono raggiunti (ETA effettiva None). Missione: DESTROYED se tutti distrutti
   (anche per carburante) > COMPLETED se qualcuno completa la rotta > **ABORTED (motivo FUEL)** se un
   asset non distrutto e' fermo/atterrato per carburante > FAILED.
5. **Interruttori**: `F6_FUEL_PER_LEG` (evento per tratto e consumo delle soste) e `F6_FUEL_CONSTRAINT`
   (troncamento ed esiti), separati per attribuire le differenze; spenti entrambi la sessione e'
   identica a prima (verificato sulle 522).
6. `Contact_Scheduler._asset_legs`: una lista di tratti VUOTA data dal chiamante significa "l'asset non
   esiste nella sessione" (aereo perso alla partenza), senza ricaduta sulla rotta o sulla posizione.

Decisioni non coperte, scelte le piu' semplici (DA CONFERMARE):
- precedenza dello stato di missione: COMPLETED prevale su ABORTED per carburante (se un asset completa
  la rotta e un altro resta a secco la missione e' COMPLETED); un asset fermo a terra/mare per carburante
  rende la missione ABORTED come l'aereo atterrato in planata;
- le soste di un aereo A TERRA (parcheggio prima del decollo, sosta dopo l'atterraggio) non consumano;
- planata: aereo "in volo" come gli altri durante la planata (puo' essere ingaggiato e, se armato,
  sparare: la "fine di attivita'" e' della F6-B); punto d'atterraggio = l'asset di base piu' vicino a
  quota 0; durata = distanza 3D / crociera;
- `Scenario_Baseline`: l'unita' `ORC-fuel` esegue ora `test_without_the_constraint_exhaustion_is_only_reported`
  (stessa sessione del vecchio `test_exhaustion_is_reported_not_simulated`, vincolo spento): IDENTICA.

### Costanti stimate

- `Fuel_Model.GLIDE_RATIO = 10.0`: STIMA DI PROGETTO, non un dato tarato (nessun dato di planata o di
  efficienza in `Aircraft_Data`); ordine di grandezza indicato dall'utente per un caccia a motore spento,
  unico per tutti gli aerei.
- Nessun'altra costante: consumo delle soste = crociera del registro (ipotesi, non costante).
- Scenario S24: costanti DI TEST dichiarate (carburante 0,002 dell'E5, 50 km di carburante dell'F-16C,
  carburante della CAP per meta' orbita, sensori, velocita', tiri a precisione 0), soglia
  `MIN_FIRING_FRACTION` = 0,5 dichiarata di test.

### Come si attribuiscono le differenze

Tre catture fuori dal repository con gli interruttori impostati (script nello scratchpad) e la finale:

| Cattura | Contro | Esito |
|---|---|---|
| codice di partenza | base | IDENTICA (522) |
| A: `F6_FUEL_PER_LEG` e `F6_FUEL_CONSTRAINT` spenti | base | IDENTICA sulle 522, 88 nuove (S24) |
| B: solo `F6_FUEL_PER_LEG` | base | 126 cambiate; con `--ignore fuel_events` 38 |
| C (finale, entrambi attivi) | B | IDENTICA sulle 522: il vincolo non cambia nessuna esecuzione esistente; nelle 88 di S24 cambiano le 48 varianti con l'esaurimento (E5 'far'/'near', GLIDE 'glide'/'no_base'/'enemy_base', ORBIT 'dry') |
| C | base, `--ignore fuel_events` | 38 cambiate, SOLO in `assets.*.fuel` (nessun contatto, colpo, danno, esito, postura o ETA) |

`--ignore fuel_events` (nuovo in `Scenario_Baseline`) esclude la voce `fuel` e i conteggi
`counts.fuel_events`/`counts.fuel_exhausted`; il carburante finale per asset resta nel confronto.

### Esecuzioni cambiate (126 su 522, nessuna nella storia)

| Causa | Esecuzioni | Entita' |
|---|---|---|
| FORMA: un evento per tratto (rotte di piu' tratti) | 88: S22-AIR 40, S23-CAP 'no_wait'/'waits_off' 16, S23-HOLD 'no_hold'/'waits_off' 16, S23-TOT 'derived'/'waits_off' 16 | 192 asset passano da 1 a 2 eventi (112 restano a 1); somma di distanze e consumi per asset invariata (scarto massimo 1e-6, rumore di arrotondamento) |
| SOSTANZA: le attese consumano alla crociera | 32: S23-CAP 'during'/'after' 16 (orbita di 1500 s dei MiG-29S: -0,294 del pieno), S23-HOLD 'hold' 8 (sosta di 600 s dell'M1A2: -0,0215), S23-TOT 'own_tot' 8 (attese in volo al punto di partenza: strike 180 s -0,0306, sweep 300 s -0,0471) | solo il carburante finale; nessun asset si esaurisce |
| ARROTONDAMENTO: somma dei consumi per tratto | 6: S19AD 'strela_standoff' (4 A-10C) | carburante finale 0,954688 -> 0,954687 (ultima cifra di `ROUND_DIGITS`) |
| VINCOLO del movimento / planata | 0 delle 522 | nessun asset delle fotografie esistenti esaurisce il carburante |

Nessun cambio inatteso: la sola sorpresa apparente (S19AD) e' l'arrotondamento a 6 decimali della somma
di due consumi per tratto rispetto al consumo unico.

### Scenario nuovo S24 (`Test_Session_Scenarios_S24.py`, 88 esecuzioni, 13 test)

**S24-E5** (8 seed, 4 varianti): M1A2 con `fuel` = 0,002 (autonomia del registro 426 km: 852 m) su 7
km a 10 m/s, esaurimento a 85,2 s; 3 BMP-2 con sensore 'ground' dichiarato 4,2 km e tiro a precisione 0.
'far' (rotta verso i BMP, fermo a 6,65 km): nessun colpo in 8/8; 'far_off' (vincolo spento, l'E5 di
prima): Red spara in 8/8, primo colpo fra 361,0 e 362,9 s (oltre il punto di esaurimento, come i 370 s
dell'analisi); 'near' (fermo a ~3,9 km dal BMP piu' vicino): Red spara in 8/8 anche dopo 664 s (uscita
dal sensore senza vincolo), ultimi colpi a ~3597-3600 s; 'near_off': ultimi colpi fra 637 e 660 s.
Esito: carro non distrutto, FUEL_EXHAUSTED a 85,2 s, missione ABORTED/FUEL, postura `Defense`, un
FuelEvent esaurito su 852 m; con il vincolo spento rotta completata (COMPLETED) e FuelEvent esaurito.

**S24-GLIDE** (8 seed, 4 varianti): F-16C con carburante per 50 km a 5000 m, esaurimento a 200 s in
(-50 km, 0); raggio di planata 50 km. 'glide' (base Blue a 20 km): planata fino a ~277,3 s, a terra
sulla base fino a fine sessione; lo strike Red (lanci a precisione 0 contro gli aerei a terra) lancia
in 8/8 repliche, sempre dopo l'atterraggio; esito OPERATIONAL/FUEL_EXHAUSTED, missione ABORTED/FUEL.
'no_base' (base a 60 km) ed 'enemy_base' (base Red a 20 km): perso a 200 s, DESTROYED/FUEL_EXHAUSTED,
salute 0, nessun DamageEvent, missione DESTROYED, nessun lancio Red. 'off': rotta completata a secco
(evento esaurito a 50 km di 200), nessun lancio.

**S24-ORBIT** (8 seed, 3 varianti): MiG-29S 'CAP' (sensore 'air' dichiarato 30 km) in orbita in O per
1500 s da 300 s; bombardieri che non sparano per O a 1400 s. 'full': tre FuelEvent per tratto
(avvicinamento, orbita ferma da 1500 s alla crociera, rientro), la CAP spara in 8/8; 'dry' (carburante
per avvicinamento e meta' orbita): due FuelEvent, orbita esaurita dopo 750 s, MiG perso in O a 1050 s
(6000 m, nessuna base), nessun lancio in 8/8; 'per_leg_off' (`F6_FUEL_PER_LEG` spento): l'orbita non
consuma, un solo evento, nessun esaurimento, la CAP spara in 8/8.

### Test

- `Test_Fuel_Model`: `TestLegFuelEvent`, `TestFuelExhaustion`, `TestGlide` (nuove, 13 test).
- `Test_Session_Simulator.TestFuelExhaustion` riscritta (5 test: vincolo spento come prima, aereo perso,
  planata sulla base, aereo a terra con serbatoio vuoto, veicolo fermo); `TestWaitsAndEtas`: la sosta
  consuma per tratto (sostituisce il test del limite) + interruttore `F6_FUEL_PER_LEG` spento.
- `Test_Mission_Types`: FUEL_EXHAUSTED con e senza distruzione. `Test_Contact_Scheduler`: tratti dati
  vuoti = asset assente.
- `Test_Session_Scenarios_S23`: `test_the_orbit_does_not_consume_fuel` diventa
  `test_the_orbit_consumes_fuel_in_time`.
- `Test_Session_Scenarios_S24` (nuovo, 13 test).

### Limiti noti

- Il vincolo e' calcolato a monte alla CROCIERA, la contabilita' al regime della sessione ('max' per chi
  ha combattuto, solo per gli aerei: veicoli e navi hanno un'unica autonomia): un aereo che combatte puo'
  risultare esaurito nella contabilita' prima del punto di troncamento senza che il movimento sia
  ricalcolato (nessun ri-scheduling dopo gli ingaggi). Il consumo cambia per effetto di un ingaggio solo
  per questo regime.
- Idoneita' della base per tipo di aereo (pista, elicotteri, portaerei) non modellata; terreno non
  modellato (quota = altezza sulla base); base = posizione di un asset non aereo di un blocco
  `is_Air_Base` del lato.
- Durante la planata l'aereo e' un aereo in volo come gli altri (puo' essere ingaggiato e sparare).
- Consumo delle soste = crociera anche per il loiter (sovrastima) e per terra/mare (sovrastima).
- Un asset distrutto a meta' rotta consuma comunque i tratti (troncati) interi.
- Bingo in volo con rientro, criteri di fine attivita' e stato di missione completo: F6-B.

### Verifica

Suite 4166 test OK (7 skipped; +33 rispetto a 4133: 13 S24, 13 `Test_Fuel_Model`, 5 `Test_Session_Simulator`,
1 `Test_Mission_Types`, 1 `Test_Contact_Scheduler`; il test instabile preesistente
`Test_Tactical_Evaluation...testCalcFightResult` e' passato). Fotografia: prima delle modifiche
`--compare` IDENTICA su 522; dopo, v. le tabelle sopra (cattura finale 610 esecuzioni, fuori dal
repository).

## F6 passo B1: fine di attivita', stato di missione, postura `destroyed` (F6-B1, D2.a/D2.d)

**Base del confronto**: `Test/baseline/scenario_baseline.json` (610 esecuzioni), ricontrollata IDENTICA
al codice di partenza (`00b6b531`) prima delle modifiche, 2026-10-12. Poiche' la fotografia NON registra
lo stato di missione ne' i motivi di fine per asset, gli esiti di missione sono stati verificati con una
CATTURA ESTESA fuori dal repository (script nello scratchpad: fotografia standard + voce
`mission_outcomes` con stato, motivo ed esito per asset), eseguita sul codice di partenza (esportazione di
`HEAD`, non un worktree) e sul codice finale.
**Dopo**: `Session_Simulator.F6_END_CRITERIA = True` e `F6_DESTROYED_POSTURE = True`. Sulla STORIA
(contatti, colpi, danni, esiti di forza, carburante, ETA) e sugli ESITI DI MISSIONE **nessuna delle 610
esecuzioni cambia**; 429 cambiano nella sola voce `postures` (1431 asset distrutti passano a
`destroyed`). 112 esecuzioni nuove (scenario S25). Fotografia del repository NON rigenerata: cattura
finale fuori dal repository (722 esecuzioni).

### Il cambio

1. **Fine di attivita' nel risolutore senza cambio di rotta (D2.a)**. `Engagement_Resolver` riceve
   `activity_criteria` (`{asset_id: ActivityCriteria}`): dall'istante in cui un criterio scatta l'asset
   non lancia piu' salve offensive (nessuno scheduling oltre la fine, lancio gia' programmato annullato
   per generazione come la prelazione L3), le salve partite arrivano (R4), l'asset prosegue PASSIVO sulla
   rotta pianificata, resta presente, bersaglio e intercettore. Le fini scattate sono in
   `EngagementResult.activity_ends`. Senza criteri ogni percorso e' quello di prima (nessuna estrazione
   aggiunta o tolta).
2. **Criteri letti** (tutti inattivi nei default di `EndCriteria`), costruiti dalla sessione
   (`Session_Simulator._activity_plans`):
   * `winchester`: le voci della scorta per arma nelle categorie elencate; categoria = chiave di primo
     livello del registro d'arma del dominio (`Fire_Control.weapon_category`, nuova: la stessa categoria
     `weapon_type` con cui la fire control dai registri sceglie le armi; nessun modello compare in due
     categorie dello stesso dominio). Scatta a scorta zero di TUTTE quelle voci nello stato ombra;
   * `damage_threshold`: salute persa / salute a inizio sessione >= soglia, asset non distrutto;
   * `target_destroyed`: bersaglio ASSET (l'asset) o GROUP (asset del blocco, oppure della missione, con
     quell'id); fine all'ultima distruzione (combattimento, gia' all'inizio, perdita per carburante),
     non prima della partenza;
   * `max_duration_s`: fine a partenza della missione + durata (fine nota a monte, `until`).
3. **Esito per asset**: la prima fine di attivita' dentro la sessione (a parita' d'istante: danno,
   winchester, bersaglio, durata) se precede l'arrivo all'ultimo punto e l'esaurimento del carburante;
   motivo WINCHESTER / DAMAGE / TARGET_DESTROYED / MAX_DURATION all'istante della fine.
4. **Stato di missione, regola unica (D2.d)**, che sostituisce la precedenza provvisoria della F6-A:
   DESTROYED (tutti persi) > COMPLETED (obiettivo raggiunto) > ABORTED con motivo (FUEL, AMMUNITION,
   DAMAGE) > FAILED.
5. **Postura `destroyed`** (`Mission_Adapter.DESTROYED_POSTURE`, interruttore separato): un asset
   distrutto a fine sessione (in combattimento o per carburante) ha postura `destroyed` in
   `SessionOutcome.postures`. `Mission_Adapter.session_postures` resta la postura di piano.
6. **Interruttori**: `F6_END_CRITERIA` (criteri e regola unica; spento: criteri non letti e precedenza
   della F6-A) e `F6_DESTROYED_POSTURE` (solo la postura), separati per attribuire le differenze.

Decisioni non coperte dal Piano, scelte le piu' semplici (DA CONFERMARE):
- **ABORTED solo se OGNI asset superstite** ha chiuso per carburante, munizioni o danno (prima, nella
  F6-A, bastava UN asset a secco); motivo = quello dell'asset che ha chiuso per ULTIMO (a parita'
  d'istante FUEL, poi AMMUNITION, poi DAMAGE). Un gregario winchester con il capo ancora in missione non
  fa abortire la missione;
- **obiettivo** = i bersagli distrutti se `target_destroyed` e' dichiarato e rappresentabile (allora la
  sola rotta completata e' FAILED), altrimenti l'ultimo punto raggiunto prima di distruzione e fine di
  attivita'; **la durata massima e' una fine regolare** (COMPLETED senza criterio di bersaglio): "tempo
  sulla stazione esaurito" di una CAP;
- un arrivo all'ultimo punto DOPO la fine di attivita' non completa la missione (l'asset vi arriva
  passivo); un asset che completa la rotta PRIMA resta ROUTE_COMPLETED anche se un criterio scatta dopo
  (es. un'unita' terrestre in `Defense` danneggiata dopo l'arrivo smette comunque di sparare);
- l'asset a fine attivita' **continua a intercettare** (difesa di salva, non ingaggio offensivo);
- `max_duration_s` contata dalla **partenza della missione** (non dall'arrivo sulla stazione);
- winchester: criterio INATTIVO (warning) per un asset senza scorta per arma (pool anonimo, nomi 'test:*'),
  senza armi delle categorie, o con un'arma delle categorie NON modellata (contata a unita': non si
  esaurisce mai); gia' a zero alla partenza: fine alla partenza;
- soglia di danno: `>=` soglia (frazione rispetto alla salute a inizio sessione, non a 100);
- bersaglio GROUP: l'id e' cercato prima fra i blocchi passati, poi fra le missioni, poi fra gli asset;
  id sconosciuto: criterio ignorato con un warning.

### Costanti stimate

- Nessuna costante nuova nel motore.
- Scenario S25: costanti DI TEST dichiarate (scorta imposta {AIM-9M: 2, M61A1: 500}, tiri senza effetto a
  precisione 0, colpo "che graffia" a precisione 1 e capacita' distruttiva 0, scorta Red di 5 unita',
  soglia di danno 0,05, durata 120 s, sensori 30 km / 10 km / 4,2 km, velocita' 250 m/s e 2 m/s);
  soglia `MIN_FIRING_FRACTION` = 0,5 dichiarata di test (stessa stima di S22-S24).

### Come si attribuiscono le differenze

| Cattura (estesa, con `mission_outcomes`) | Contro | Esito |
|---|---|---|
| codice di partenza, fotografia standard | base del repository | IDENTICA (610) |
| finale con `F6_DESTROYED_POSTURE` spento | partenza estesa | IDENTICA sulle 610 (posture ed esiti di missione compresi), 112 nuove (S25) |
| finale | partenza estesa, `--ignore postures` | IDENTICA sulle 610 (esiti di missione compresi), 112 nuove |
| finale | partenza estesa | 429 cambiate SOLO in `postures` |
| finale (forma standard) | base del repository, `--ignore postures` | IDENTICA sulle 610, 112 nuove |

Quindi: nessuna missione delle fixture dichiara un criterio di stato o una durata (i criteri sono
inattivi nei default), la regola unica dello stato di missione non cambia nessun esito esistente (nessuna
missione con un asset a secco e un altro superstite che non lo e'), e l'unica differenza e' la postura
degli asset distrutti.

### Esecuzioni cambiate (429 su 610, solo `postures`)

Ogni asset cambiato e' DISTRUTTO a fine sessione (verificato asset per asset sullo stato registrato,
nessuna eccezione) e ogni asset distrutto ha ora `destroyed`. Transizioni: `Defense` -> `destroyed` 774
(unita' di superficie e strutture), `off_scene` -> `destroyed` 595 (aerei a fine rotta, compresi i persi
per carburante di S24), `parking_cold` -> `destroyed` 62 (aerei a terra, S21/S21R/S22-AIR). Per unita'
(esecuzioni / asset): S1 15/31, S2 23/68, S3 40/240, S4 13/30, S5 35/96, S6 4/21, S7 6/27, S8 1/63, S9
12/21, S9R 20/28, S10 26/66, S11 6/24, S12 12/47, S13 6/30, S14 6/23, S15 12/55, S16 4/52, S17 15/109,
S18 8/41, S19 4/8, S19AD 24/107, S20 10/21, S21 13/43, S21R 6/43, S22-AIR 21/27, S22-E1 10/10, S22-E3
12/12, S23-CAP 8/13, S24-GLIDE 16/16, S24-ORBIT 22/26, VAL-det 1/2, VAL-agn 4/8, ORC-base 1/1, ORC-seed
2/4, ORC-interval 2/6, ORC-twofronts 9/12. Nessun cambio inatteso.

### Scenario nuovo S25 (`Test_Session_Scenarios_S25.py`, 112 esecuzioni, 12 test)

Ogni scenario ha due controlli: criterio non dichiarato ('undeclared') e criterio dichiarato con
`F6_END_CRITERIA` spento ('switch_off'), identici fra loro.

**S25-WIN** (8 seed): F-16C con scorta imposta {AIM-9M: 2, M61A1: 500} e fire control "prima l'AIM-9M,
poi il cannone" (tiri senza effetto), affiancato a 10 km da 3 MiG-29S (uno lancia salve senza effetto
contro di lui). 'winchester' (`winchester=('MISSILES_AAM',)`): in 8/8 due salve AIM-9M (1,5 s e 16,5 s),
poi nessuna, cannone intatto (500); WINCHESTER a 16,5 s, missione ABORTED/AMMUNITION, ETA dell'ultimo
punto presente (prosegue passivo); la scorta Red gli lancia contro 32 salve dopo la fine. Controlli: 12
salve (2 AIM-9M e 10 raffiche di cannone fino a 121,5 s, scorta del cannone esaurita), COMPLETED.

**S25-DUR** (8 seed): stessa geometria, tiro 'fighter' senza effetto, `max_duration_s` = 120: 8 lanci fra
1,5 e 106,5 s, nessuno dopo 120 s, MAX_DURATION a 120 s, COMPLETED. Controlli: 32 lanci fino a 466,5 s,
ROUTE_COMPLETED a 480 s.

**S25-POST** (8 seed): stessa geometria, tiro 'aam' letale, Red non spara: 2 MiG distrutti in 8/8;
'on': postura `destroyed` per i distrutti, `off_scene` per gli altri; 'posture_off' (`F6_DESTROYED_POSTURE`
spento): nessuna postura `destroyed`, stessi danni.

**S25-DMG** (8 seed): M1A2 lungo x = -3 km a 2 m/s per 1500 s (tiro senza effetto), 3 BMP-2 con colpo che
graffia (5 punti a salva, mai un KILL) e una salva di scorta ciascuno. 'damage' (`damage_threshold` =
0,05): un solo lancio del carro (31 s), DAMAGE alla prima risoluzione Red a 32,5 s, salute finale 85-90
(non distrutto), DAMAGED, missione ABORTED/DAMAGE. Controlli: 42 lanci fino a 441 s, COMPLETED a 1500 s.

**S25-TGT** (8 seed): 2 F-16C 'strike' (tiro di riferimento 'agm') a 3000 m su un deposito bersaglio
(Red-Depot, bersaglio GROUP) e due depositi di Red-Other a ~2 km, dottrina senza disingaggio. 'target'
(`target_destroyed=True`): deposito distrutto in 8/8 fra 133,4 e 149,2 s, 2-4 lanci tutti non posteriori
alla distruzione, Red-Other mai attaccato dopo (in un seed un colpo lanciato PRIMA arriva dopo, R4),
TARGET_DESTROYED all'istante della distruzione, COMPLETED, postura `destroyed` del deposito. Controlli:
4-7 lanci, 2-5 colpi su Red-Other dopo la distruzione, ROUTE_COMPLETED a 320 s.

Controllo con `F6_END_CRITERIA` e `F6_DESTROYED_POSTURE` spenti su tutto il file (sonda fuori dal
repository): 10 test su 12 falliscono (passano solo i 2 test dei soli controlli): lo scenario distingue
la F6-B1.

### Test

- `Test_Engagement_Resolver.TestActivityEnd` (nuova, 7 test): winchester, soglia di danno (anche il lancio
  gia' programmato annullato), bersaglio distrutto nella run e fuori dalla run (istante futuro), `until`,
  nessun criterio = identico, input non validi.
- `Test_Session_Simulator.TestEndCriteria` (nuova, 7 test): default senza piani, bersaglio distrutto ->
  COMPLETED (e interruttore spento), rotta completata senza bersaglio -> FAILED, durata massima,
  winchester -> ABORTED/AMMUNITION, voci del winchester per categoria, bersagli per forma. Adeguati
  `test_aircraft_without_a_reachable_base_is_lost` e `test_postures_of_every_asset_in_the_outcome`
  (postura `destroyed`, con l'interruttore spento quella di prima).
- `Test_Fire_Control.TestWeaponCategory` (nuova, 3 test).
- `Test_Session_Scenarios_S22.test_final_postures` e `Test_Session_Scenarios_S24` (aereo perso):
  postura `destroyed` per gli asset distrutti.
- `Test_Session_Scenarios_S25` (nuovo, 12 test); `Scenario_Baseline`: unita' S25-WIN, S25-DUR, S25-POST,
  S25-DMG, S25-TGT in coda.

### Limiti noti

- Bersagli POINT/AREA (e ZONE): `target_destroyed` non rappresentabile prima della F7 (bersagli
  espliciti), ignorato con un warning.
- Nel risolutore il bersaglio distrutto vede solo le distruzioni della propria run e degli ingaggi gia'
  risolti (ordine della coda di sessione): una distruzione in un ingaggio risolto DOPO, anche se anteriore
  nel tempo, non ferma i lanci; l'esito (motivo e stato) e' invece calcolato sull'intera sessione.
- `abort_on_threat` non letto (fuori dal piano della F6); `bingo` non letto (F6-B2, con il rientro);
  `last_waypoint` non letto (la rotta completata e' sempre una fine).
- Nessun cambio di rotta: la fine di attivita' non porta l'asset a casa (il rientro e' della F6-B2); un
  aereo in planata per carburante non chiude l'attivita'.
- Fine di attivita' all'istante del lancio che esaurisce le armi (winchester) o della risoluzione (danno,
  bersaglio): nessuna latenza di valutazione.
- `MISSION_ABORTED` (gregari che seguono la missione che abortisce, D3.d) e `THREAT` non sono prodotti.

### Verifica

Suite 4195 test OK (7 skipped; +29 rispetto a 4166: 12 S25, 7 `Test_Engagement_Resolver`, 7
`Test_Session_Simulator`, 3 `Test_Fire_Control`; adeguati senza cambiare il numero i test di postura di
`Test_Session_Simulator`, S22 (E1, E3, AIR) e S24; il test instabile preesistente
`Test_Tactical_Evaluation...testCalcFightResult` e' passato). Fotografia: prima delle modifiche
`--compare` IDENTICA su 610; dopo, v. le tabelle sopra (cattura finale 722 esecuzioni, fuori dal
repository).

## F6 passo B2: bingo a priori e bingo in volo con rientro (F6-B2, decisione 14)

**Base del confronto**: `Test/baseline/scenario_baseline.json` (722 esecuzioni), ricontrollata IDENTICA
al codice di partenza (`60b3b14e`) prima delle modifiche, 2026-10-13 (cattura fuori dal repository).
**Dopo**: `Session_Simulator.F6_BINGO = True`. Con le fixture S24-GLIDE che dichiarano `bingo=False` (v.
sotto) **nessuna delle 722 esecuzioni cambia**; 40 esecuzioni nuove (scenario S26). Con le fixture S24
NON adeguate (bingo di default) cambierebbero 24 esecuzioni di S24-GLIDE, elencate sotto per
l'accettazione dell'utente. Fotografia del repository NON rigenerata: cattura finale fuori dal repository
(762 esecuzioni).

### Il cambio

1. **Riserva e punto di bingo** (`Fuel_Model`): `BINGO_RESERVE` (riserva [frazione del carico pieno], stima
   sotto); `return_margin` = carburante attuale - fabbisogno dei tratti alla crociera (soste nel tempo come
   nella F6-A) - rientro in linea retta 3D dall'ultimo punto alla base idonea piu' vicina (a quota 0) -
   riserva; `bingo_point` = primo istante in cui il residuo basta appena per rientrare alla base piu' vicina
   con la riserva. La condizione `H(t) = residuo - riserva - distanza dalla base piu' vicina` (in metri di
   crociera) e' NON CRESCENTE lungo i tratti (la distanza da una base cambia al piu' di 1 m per metro
   percorso), quindi il bingo e' unico e si calcola in forma chiusa per tratto (`u = (A^2 - |w|^2) / (2 (A +
   w.e))` per base, massimo fra le basi). Esiste se e solo se il margine e' negativo.
2. **Bingo a priori, validatore di pianificazione** (`Mission_Adapter.check_mission_bingo`): per ogni asset
   di una missione AEREA con `EndCriteria.bingo` (default True) il margine sulla missione intera pianificata
   (`airborne_legs`: andata, attese, ritorno, senza taglio alla sessione; le soste a terra non consumano)
   deve essere >= 0, altrimenti `ValueError` con il motivo (quanto carburante manca, dove cadrebbe il bingo
   in volo). Nessuna base idonea del lato: rifiuto. Missioni di terra/mare o con `bingo` False: non
   controllate (None). Asset con carburante non modellato: non controllati.
3. **Bingo in volo con rientro** (`Session_Simulator`, interruttore `F6_BINGO`): per un aereo di missione
   aerea con `bingo` e almeno una base aerea del lato fra le forze passate, il bingo e' calcolato A MONTE sui
   tratti che consumano (ritagliati alla sessione), prima dell'esaurimento e dello scheduler: i tratti oltre il
   bingo non esistono; dal punto di bingo l'aereo vola in linea retta alla base piu' vicina (a quota 0, alla
   crociera, come la planata della F6-A), poi resta A TERRA sulla base (programma `grounded`, postura
   `parking_cold`); il rientro consuma (arriva con la riserva alla crociera). Dal bingo l'aereo non lancia piu'
   salve offensive (`ActivityCriteria.until` del risolutore, il meccanismo della durata massima della F6-B1),
   resta bersaglio e intercettore.
4. **Esiti**: `AbortReason.BINGO` (nuovo); per asset BINGO all'istante del bingo (OPERATIONAL/DAMAGED), punti
   successivi non raggiunti; missione con la regola unica della F6-B1, ABORTED(BINGO) (a parita' d'istante
   dopo FUEL). A secco anche sul rientro (carburante insufficiente per la base gia' al bingo, es. alla
   partenza): regole della F6-A sui tratti col rientro (planata su base raggiungibile -> ABORTED(FUEL),
   altrimenti DESTROYED/FUEL_EXHAUSTED), motivo dell'asset FUEL_EXHAUSTED (l'ultimo fatto).
5. Senza base idonea, con `bingo` False o con l'interruttore spento: nessun rientro, l'aereo vola fino
   all'esaurimento (F6-A). Terra e mare: nessun bingo (invariati, fermi nel punto di esaurimento).

Decisioni non coperte dal Piano, scelte le piu' semplici (DA CONFERMARE):
- **il validatore NON e' chiamato da `run_session`**: e' del pianificatore (il futuro C2, o il validatore di
  sessione della F8). Motivi: l'esecutore (sintetico o DCS, "RTB on bingo") esegue l'ordine e fa tornare
  l'aereo, non rifiuta; e, poiche' a priori e in volo usano lo stesso criterio alla crociera, un rifiuto
  dentro `run_session` renderebbe il bingo in volo irraggiungibile (e farebbe sollevare `run_session` sugli
  scenari di esaurimento S24). Equivalenza verificata in S26: la missione rifiutata a priori e' esattamente
  quella che in sessione torna al bingo, allo stesso istante;
- **base idonea** = qualunque base aerea del lato (`air_base_points`, come la planata della F6-A); idoneita'
  per tipo d'aereo (pista, portaerei, elicotteri) non modellata;
- **`EndCriteria.bingo` False** = nessun controllo a priori e nessun rientro in volo (la missione dichiara di
  non rientrare al bingo);
- **dal bingo l'aereo non lancia piu'** (fine di attivita' come la F6-B1: la decisione 14 non dice nulla sul
  tiro; il rientro e' una fine di attivita' dichiarata dalla dottrina "RTB on bingo");
- **rientro in linea retta 3D** dal punto di bingo alla base a quota 0 (stessa convenzione della planata):
  l'aereo scende lungo tutto il rientro, quindi se resta a secco sul rientro la quota (e il raggio di
  planata) e' minore di quella di crociera;
- il bingo e' valutato sui tratti RITAGLIATI ALLA SESSIONE (come l'esaurimento della F6-A): una missione che
  arriverebbe al bingo dopo la fine della sessione non torna in questa sessione; a priori invece si valuta la
  missione intera;
- **interruttore indipendente** da `F6_FUEL_CONSTRAINT`: con il vincolo spento il bingo resta attivo (e'
  una regola di condotta, non il vincolo del carburante);
- precedenza a parita' d'istante fra i motivi d'aborto: FUEL, BINGO, AMMUNITION, DAMAGE.

### Costanti stimate

- `Fuel_Model.BINGO_RESERVE = 0.10` del carico pieno: STIMA DI PROGETTO, non un dato tarato (nessuna riserva
  per tipo d'aereo nei registri); ordine di grandezza delle riserve finali di dottrina (10% del carburante,
  20-30 minuti in attesa), unica per tutti gli aerei.
- Scenario S26: costanti DI TEST dichiarate (carburante 0,3 e 0,15 del pieno, sensore 'air' del sito Red 40
  km, tiro a precisione 0, velocita' 250 m/s, quota 5000 m), soglia `MIN_FIRING_FRACTION` = 0,5 dichiarata di
  test (stessa stima di S22-S25).

### Come si attribuiscono le differenze

Catture fuori dal repository (script nello scratchpad che imposta `F6_BINGO` prima di
`Scenario_Baseline.main`; mai un worktree):

| Cattura | Contro | Esito |
|---|---|---|
| codice di partenza (`60b3b14e`) | base del repository | IDENTICA (722) |
| finale con `F6_BINGO` spento | base del repository | IDENTICA sulle 722, 40 nuove (S26) |
| finale con `F6_BINGO` attivo, S24-GLIDE con il bingo di default | codice di partenza | 24 cambiate (S24-GLIDE, tabella sotto), 40 nuove |
| finale (`F6_BINGO` attivo, S24-GLIDE `bingo=False`) | base del repository | IDENTICA sulle 722, 40 nuove |
| finale | finale con `F6_BINGO` spento | cambiano solo le 8 esecuzioni S26 'bingo' (il rientro) |

Quindi: nessuna fixture esistente oltre a S24-GLIDE ha un aereo di missione che arriva al bingo con una
base aerea del suo lato fra le forze passate (dove le basi ci sono, il carburante basta con la riserva).

### Esecuzioni che cambierebbero con il bingo di default (24 su 722, solo S24-GLIDE)

Cattura con `F6_BINGO` attivo e la missione di S24-GLIDE con il bingo di DEFAULT (`bingo=True`), contro il
codice di partenza: cambiano le 24 esecuzioni `S24-GLIDE/S24-GLIDE-{0..7}/{glide,no_base,off}`, nient'altro
(`enemy_base` no: il lato Blue non ha basi). Con 50 km di carburante (0,032 del pieno) l'F-16C e' sotto la
riserva (0,1) gia' alla partenza: bingo a t = 0 e rientro verso la base Blue.

| Variante (8 seed ciascuna) | Campi cambiati | Entita' |
|---|---|---|
| `glide` (base a 20 km dal punto di esaurimento) | `fuel`, `assets` (F-16C e strike Red), `postures`, `engagements`, `force_outcomes.Blue-Flight`, `ammunition_*`, `damage_events`, `counts.{rounds,salvos,damage_events}`, `fuel` dello strike | rientro verso la base a 54 km dalla partenza: a secco a 187,5 s sul rientro, a ~380 m di quota (il rientro scende verso la base: raggio di planata ~3,8 km, base a ~4,1 km): PERSO (salute 0, postura `parking_cold` -> `destroyed`), lo strike Red non trova piu' l'aereo a terra (64 -> 0 lanci senza effetto) |
| `no_base` (base Blue a 60 km da x = -50 km) | `fuel` (solo l'istante dell'evento) | rientro verso la base lontana: a secco a 187,5 s invece di 200 s (alla crociera di 266,7 m/s invece dei 250 m/s di rotta), perso come prima |
| `off` (`F6_FUEL_CONSTRAINT` spento) | `fuel`, `actual_etas`, `postures`, lanci/danni dello strike | col vincolo spento il bingo resta attivo (interruttori indipendenti): rientro a t = 0, l'aereo vola a secco fino alla base (54 km, 202,8 s) e resta a terra (`off_scene` -> `parking_cold`); ultimo punto non raggiunto (ETA 800 -> None); lo strike Red lo trova a terra (0 -> 64 lanci) |

Per tenere S24-GLIDE come scenario dell'esaurimento della F6-A, la sua missione dichiara ora
`EndCriteria(bingo=False)` (il rientro al bingo e' coperto da S26): con questa scelta la cattura finale e'
IDENTICA sulle 722. Se l'utente preferisce tenere il bingo di default anche in S24-GLIDE, le 24 esecuzioni
sopra vanno accettate e i test di S24-GLIDE riscritti.

### Scenario nuovo S26 (`Test_Session_Scenarios_S26.py`, 40 esecuzioni, 7 test)

**S26-BINGO** (8 seed, 5 varianti): F-16C 'Strike' (autonomia di crociera del registro col loadout 'Strike'
1570 km, crociera 266,7 m/s) in volo a 5000 m da (10 km, 0) a (310 km, 0) a 250 m/s; base Blue in (0, 0);
BMP-2 Red in (260 km, 0) con sensore 'air' dichiarato di 40 km e tiro senza effetto.
- 'bingo' (carburante 0,3): il validatore RIFIUTA ("0.1886 of a full load is missing ... bingo at
  t=607.8 s"); in sessione bingo a 607,8 s in (161,96 km, 0, 5000) (lo stesso istante annunciato dal
  validatore, e quello ricavato nel test per bisezione), rientro e atterraggio a 1215,5 s con 0,1 a bordo
  (la riserva), BINGO/OPERATIONAL, ABORTED(BINGO), ETA (0, None), postura `parking_cold`, due FuelEvent; Red
  non spara mai (0 colpi in 8/8);
- 'none' (pieno): validatore accetta (margine 0,511); rotta completata, Red spara in 8/8 (26-28 colpi, primo
  fra 872 e 889 s);
- 'switch_off' (0,3, `F6_BINGO` spento): rotta completata come prima, Red spara in 8/8 come in 'none'
  (carburante finale 0,037: il volo e' contato al regime di combattimento);
- 'no_base' (0,15, nessuna base Blue): validatore rifiuta ("no suitable air base"); nessun rientro,
  esaurimento a 942 s (235,5 km), perso (DESTROYED/FUEL_EXHAUSTED, postura `destroyed`); Red spara 5-6
  colpi prima dell'esaurimento;
- 'bingo_off' (0,15, base, `EndCriteria(bingo=False)`): validatore non controlla; identico a 'no_base'
  (base a ~245 km, oltre il raggio di planata).
Controllo con `F6_BINGO` spento su tutto il file (sonda fuori dal repository): 4 test su 7 falliscono
(passano il test del validatore, che non dipende dall'interruttore, e i due dei soli controlli): lo scenario
distingue la F6-B2.

### Test

- `Test_Fuel_Model.TestBingo` (nuova, 9 test): riserva dichiarata, margine, bingo in un tratto di movimento,
  in una sosta, alla partenza, base davanti, rientro 3D con la riserva, nessun controllo senza carburante,
  basi o tratti, base piu' vicina deterministica.
- `Test_Mission_Adapter.TestBingoValidator` (nuova, 7 test): accettata con il margine, rifiutata, riserva di
  default, nessuna base, non applicabile (terra, `bingo` False), carburante non modellato, orbita che consuma
  e sosta a terra che non consuma.
- `Test_Session_Simulator.TestBingo` (nuova, 6 test): rientro sulla base piu' vicina con la riserva,
  interruttore spento, nessun bingo senza base o con `bingo` False, carburante sufficiente, nessuna salva
  dopo il bingo (`until` al risolutore), a secco sul rientro (perso). `TestFuelExhaustion._dry_flight`
  dichiara `bingo=False` (test della F6-A).
- `Test_Session_Scenarios_S24`: la missione di S24-GLIDE dichiara `bingo=False` (scenario dell'esaurimento).
- `Test_Session_Scenarios_S26` (nuovo, 7 test); `Scenario_Baseline`: unita' S26-BINGO in coda.

### Limiti noti

- Bingo calcolato alla CROCIERA come l'esaurimento: un aereo che combatte consuma di piu' nella contabilita'
  (regime 'max') e puo' arrivare a secco prima della base senza ri-scheduling.
- Riserva unica per tutti gli aerei (stima); idoneita' della base per tipo d'aereo non modellata; rientro in
  linea retta senza quota di rientro, rotte di avvicinamento ne' terreno.
- Il validatore non e' chiamato da nessun codice di produzione (non esiste ancora un pianificatore); il
  validatore di sessione della F8 potra' chiamarlo.
- Il bingo e' valutato nella sola sessione (tratti ritagliati alla sessione).
- `MISSION_ABORTED` (gregari che seguono il capo che rientra, D3.d) non prodotto: ogni aereo ha il proprio
  bingo.

### Verifica

Suite 4224 test OK (7 skipped; +29 rispetto a 4195: 7 S26, 9 `Test_Fuel_Model`, 7 `Test_Mission_Adapter`, 6
`Test_Session_Simulator`; adeguati senza cambiare il numero `Test_Session_Simulator.TestFuelExhaustion` e S24
(`bingo=False`); il test instabile preesistente `Test_Tactical_Evaluation...testCalcFightResult` e' passato).
Fotografia: prima delle modifiche IDENTICA su 722; dopo, v. le tabelle sopra (cattura finale 762 esecuzioni,
fuori dal repository).

## F6 passo B2bis: bingo con rientro lungo la rotta a ritroso (decisioni dell'utente del 2026-10-15)

**Base del confronto**: `Test/baseline/scenario_baseline.json` installata (722 esecuzioni, SENZA S26: la
baseline B2 non e' stata installata). **Dopo**: `Session_Simulator.F6_BINGO_REVERSE_ROUTE = True`.
`--compare`, 2026-10-15 su osboxes: **770 esecuzioni confrontate, le 722 della base IDENTICHE**, 48 righe di
differenza tutte `NEW` (S26-BINGO: 8 seed x 6 varianti). Nessuno scenario aereo esistente arriva (o smette di
arrivare) al bingo con la nuova regola. Fotografia del repository NON rigenerata.

### Il cambio

1. **Rientro = rotta percorsa a ritroso** (`Fuel_Model.bingo_point` con una `ReturnRule`): dal punto di bingo
   l'aereo ripercorre al contrario i tratti di MOVIMENTO gia' volati (il DES non devia le rotte, quindi sono
   quelli pianificati), alle quote dei waypoint (la discesa e' sul tratto finale), senza le soste (WAIT,
   orbite), fino al DEPARTURE, dove atterra e resta a terra (`parking_cold`).
2. **Partenza in volo** (`start_mode` AIR): ritroso fino al punto di comparsa, poi tratto diretto (3D) alla
   base del lato piu' vicina a quel punto, a quota 0; senza base del lato nessun bingo (F6-A come prima).
3. **Missione ad anello** (`Mission_Adapter.is_loop_mission`): ritorno = min(ritroso, resto della rotta fino al
   LAND), soli tratti di movimento; l'aereo prende la via piu' breve (`BingoPoint.via` = `reverse` o
   `forward`; parita' -> ritroso).
4. **Fabbisogno di bingo = `BINGO_RETURN_FACTOR` (1,2) x il carburante del ritorno** alla crociera, al posto
   della riserva fissa 0,10. Bingo al primo istante con `E - 1,2 min(Lb, Lf) <= 0` (metri di crociera; v. il
   commento-formula della sezione BINGO di `Fuel_Model`): in un tratto di movimento H e' il massimo di due
   funzioni lineari, in forma chiusa; il margine (`return_margin`, `BingoPoint.margin`) e' ora il MINIMO di H
   lungo i tratti (sull'anello H non e' monotono), e il bingo esiste se e solo se e' negativo.
5. **Destinazione finale esclusa**: il LAND su un'altra base (divert) non conta.
6. **Calcolo sulla missione intera**: in sessione il bingo usa `Mission_Adapter.airborne_legs` (gli stessi
   tratti del validatore, anche oltre la fine della sessione, cosi' l'anello legge il resto della rotta fino
   al LAND); un bingo che cadrebbe dopo la fine della sessione non c'e' nella sessione. I tratti del rientro
   (`Session_Simulator._return_legs`, spezzata `BingoEnd.route` a velocita' costante di crociera) vanno a
   scheduler, risolutore e carburante.
7. **Validatore** (`check_mission_bingo`, parametro nuovo `reverse_route`, default True come l'interruttore):
   stessa regola (`bingo_return_rule`) e stessi tratti dell'esecutore; base del lato richiesta solo con la
   partenza in volo (chi parte da una base rientra sul suo DEPARTURE).
8. **Interruttore** `F6_BINGO_REVERSE_ROUTE`: spento = la F6-B2 esattamente com'era (rientro rettilineo con la
   riserva, tratti ritagliati alla sessione, codice invariato); il validatore con `reverse_route=False`.

Invariati: niente salve offensive dal bingo, bersaglio e intercettore, BINGO / ABORTED(BINGO), `bingo` False
= nessun controllo, a secco sul rientro le regole della F6-A.

Scelte dove le decisioni lasciavano margine:
- **"stessa base" dell'anello**: se i riferimenti di DEPARTURE e LAND sono entrambi asset di una base vera
  decide il blocco (stesso oggetto); altrimenti decide la distanza orizzontale fra i due punti, entro
  `AIR_BASE_AREA_RADIUS_M` (3000 m, stima gia' dichiarata della F5-B). Stesso modello di `lands_on_air_base`;
- **rotta oltre la fine della sessione**: si usa la rotta della missione fino al LAND (`airborne_legs`), sempre
  disponibile dalla missione: nessun limite residuo per l'anello;
- **partenza "da una base"** = `start_mode` diverso da AIR (la `Mission` impone allora il primo punto
  DEPARTURE); il punto d'atterraggio e' il primo punto della rotta DELL'ASSET (con l'offset di formazione);
- **`BingoPoint`**: campi nuovi `route` (punti del rientro dal bingo all'atterraggio), `via`, `return_length`;
  `base` = ultimo punto di `route`; nella regola F6-B2 `route` = (punto, base).

### Costanti stimate

- `Fuel_Model.BINGO_RETURN_FACTOR = 1.2`: DECISIONE DELL'UTENTE, STIMA, non un dato tarato; unico per tutti
  gli aerei.
- `Fuel_Model.BINGO_RESERVE = 0.10` resta (stima della F6-B2) solo per l'interruttore spento.
- S26: costanti DI TEST, carburante `BINGO_FUEL` 0,28 (era 0,3) e `DRY_FUEL` 0,15; 0,28 scelto perche' basta
  per i 300 km anche al regime di combattimento (autonomia 'max' 1140 km: 0,263) in 'switch_off', e mette il
  bingo a ~56 km dal sito Red (fuori dal sensore di 40 km).

### Scenario S26 rifatto (`Test_Session_Scenarios_S26.py`, 48 esecuzioni, 8 test)

F-16C 'Strike' (autonomia di crociera 1570 km, crociera 266,7 m/s) in volo a 5000 m da (10 km, 0) a
(310 km, 0) a 250 m/s; base Blue in (0, 0); tratto diretto dal punto di comparsa alla base ~11,2 km.
- 'bingo' (0,28): validatore rifiuta ("does not keep the bingo fuel ... bingo at t=774.9 s"); in sessione
  bingo a ~775 s in (203,7 km, 0, 5000) (stesso istante del validatore e della bisezione del test), ritroso
  fino a (10 km, 0, 5000), discesa sulla base, atterraggio a ~1543 s con ~0,026 a bordo (20% del ritorno di
  204,9 km); tre FuelEvent (andata e due tratti di rientro); Red non spara mai;
- 'reverse_off' (nuova, 0,28, `F6_BINGO_REVERSE_ROUTE` spento): la F6-B2, bingo rettilineo a ~545 s in
  (146,3 km, 0, 5000), atterraggio a ~1094 s con la riserva 0,1; validatore con `reverse_route=False` rifiuta
  per la riserva;
- 'none', 'switch_off', 'no_base', 'bingo_off': stesso significato di prima ('switch_off' = `F6_BINGO`
  spento: rotta completata, Red spara nella maggior parte delle repliche).

### Test

- `Test_Fuel_Model.TestReverseRouteBingo` (nuova, 11 test): fattore dichiarato e validazione di `ReturnRule`,
  ritroso con sosta esclusa e residuo = 1,2 x ritorno, margine = minimo, anello con ritroso piu' breve, anello
  con resto della rotta piu' breve (bingo in una sosta), anello sicuro con ~1,1 volte la rotta, partenza in
  volo con tratto diretto alla base piu' vicina al punto di comparsa, nessuna base, bingo alla partenza,
  nessun controllo senza carburante/tratti, regola F6-B2 invariata senza regola. `TestBingo` (F6-B2) invariata.
- `Test_Mission_Adapter.TestReverseRouteBingoValidator` (nuova, 7 test): riconoscimento dell'anello (distanza,
  stesso blocco, basi diverse, partenza in volo), regola della missione, partenza in volo con base e senza,
  partenza da base senza basi, anello sicuro a ~1,1 x e divert escluso, coincidenza validatore/`bingo_point`
  su una serie di carburanti, interruttore spento = F6-B2. `TestBingoValidator` passa `reverse_route=False`.
- `Test_Session_Simulator.TestBingo`: rientro a ritroso sulla base (valori nuovi), interruttore spento =
  F6-B2, test d'integrazione nuovo con DEPARTURE da pista, sosta non ripercorsa, LAND su altra base, punti
  ripercorsi W2, W1, W0, atterraggio sul DEPARTURE, istante uguale a quello del validatore (+2 test).
- `Test_Session_Scenarios_S26`: docstring e asserzioni al nuovo comportamento, variante 'reverse_off', test
  nuovo sul rientro rettilineo; `Scenario_Baseline`: 'reverse_off' in coda all'unita' S26-BINGO.

### Limiti noti

- Idoneita' della base per tipo d'aereo non modellata (qualunque base aerea amica, per la partenza in volo).
- Consumo deterministico alla crociera: un aereo che combatte consuma di piu' nella contabilita' (regime
  'max') e puo' arrivare a secco prima della base, senza ri-scheduling.
- Il ritroso ripassa sulle minacce incontrate all'andata; la discesa e' quella dei waypoint (nessun profilo
  di avvicinamento, terreno non modellato).
- Divert escluso per decisione: una missione di trasferimento verso un'altra base richiede carburante per
  circa 2,2 volte la rotta per non andare in bingo.
- Il validatore resta non chiamato dal codice di produzione (come nella F6-B2).

### Verifica

Suite completa: **4245 test OK (7 skipped)**, +21 rispetto a 4224 (11 `Test_Fuel_Model`, 7
`Test_Mission_Adapter`, 2 `Test_Session_Simulator`, 1 S26). Fotografia: 722 IDENTICHE, 48 nuove (S26).

## G2: soglia di bingo con la riserva di disimpegno e albero di decisione (decisioni dell'utente del 2026-10-15)

**Base del confronto**: `Test/baseline/scenario_baseline.json` installata (770 esecuzioni, con S26 della F6-B2bis).
**Dopo**: `Session_Simulator.F6_BINGO_DISENGAGE_RESERVE = True`. `--compare`, 2026-10-15 su osboxes: **794
esecuzioni**; delle 770 della base **762 IDENTICHE**, **8 cambiate** (tutte `S26-BINGO/S26-BINGO-k/bingo`,
k = 0..7), **24 nuove** (`reserve_off`, `transfer_continue`, `transfer_return` x 8 seed). Nessuno scenario
aereo esistente fuori da S26 e' sotto il nuovo minimo (rotta intera + riserva di disimpegno): nessuno cambia.
Il campo `crew_recovered` e' nell'esito per asset, che la fotografia non registra: nessuna esecuzione cambia
per il campo (neppure gli aerei FUEL_EXHAUSTED di S24-GLIDE, S26 'no_base'/'bingo_off'). Fotografia del
repository NON rigenerata. **Verifica 2026-10-16** (osboxes): `--compare` ripetuto, stessi numeri (794: 762
identiche, 8 cambiate, 24 nuove); le 8 'reserve_off' identiche alle vecchie 'bingo'. Approvato dall'utente, fotografia
installata (794 esecuzioni).

### Il cambio

1. **Soglia** (`Fuel_Model.bingo_threshold`): bingo se residuo < resto della rotta fino al LAND (attese comprese,
   alla crociera, `remaining_route_demand`) + `disengagement_reserve(asset)` (G1).
2. **Tipo di missione** (`Mission_Adapter.is_transfer_mission`): trasferimento = categoria TRANSPORT della mappa
   di Context; ogni altra missione aerea = combattimento.
3. **Albero** (`Fuel_Model.bingo_decision` -> `BingoDecision`, azioni `BINGO_CONTINUE`, `BINGO_DEPARTURE`,
   `BINGO_ALTERNATE`, `BINGO_NEAREST`, `BINGO_UNREACHABLE`, `BINGO_NO_BASE`): trasferimento continua / ritroso /
   base piu' vicina / F6-A; combattimento interrompe e prende la raggiungibile piu' breve fra base di partenza
   (via piu' breve della F6-B2bis, `_return_route` riusato) e basi entro `ALTERNATE_BASE_MAX_OFFSET` = 3000 m
   dalla rotta (lungo la rotta fino al punto piu' vicino, poi diretto in discesa); parita' -> partenza, poi (x, y);
   poi base piu' vicina in linea retta / F6-A. Raggiungibile = il solo percorso alla crociera.
4. **Funzione generale, applicazione alla partenza**: `bingo_decision` accetta un istante e un residuo qualunque
   (G4); `run_session` la chiama una volta all'inizio dei tratti della missione intera (`_decision_end`), con il
   carburante di partenza; il rientro deciso diventa un `BingoEnd` con la meccanica della F6-B2bis
   (`_return_end`, `_return_legs`, `_legs_after_bingo`, `until` del risolutore).
5. **Equipaggio**: `AssetMissionOutcome.crew_recovered` = True per l'aereo perso per esaurimento in volo (F6-A e
   G2), None altrimenti; ammesso solo con stato DESTROYED.
6. **Validatore**: `check_mission_bingo(..., disengage_reserve=True)` (default) rifiuta esattamente le missioni
   che in sessione vanno in bingo (anche il trasferimento che continua), con soglia, riserva, istante e decisione;
   basi non richieste. Con `disengage_reserve=False` la F6-B2bis/F6-B2 come prima.
7. **Interruttore**: spento, la F6-B2bis (o la F6-B2 con `F6_BINGO_REVERSE_ROUTE` spento) esattamente come prima
   (verificato: le 8 esecuzioni 'reserve_off' sono identiche, valore per valore, alle 'bingo' della base).

### Differenze della fotografia, esecuzione per esecuzione

- `S26-BINGO/S26-BINGO-k/bingo` (k = 0..7), ATTESA: carburante di test portato da 0,28 (`BINGO_FUEL`, ora
  sopra la soglia del G2 ~0,276) a 0,27 (`G2_FUEL`, sotto la soglia). Con il G2 l'F-16C e' in bingo alla
  partenza (t = 0), missione di combattimento partita in volo: diretto dal punto di comparsa alla base (0, 0) a
  quota 0, ~11,2 km, atterraggio a ~41,9 s; nessun ingaggio (prima: un ingaggio HELD/HELD senza colpi a segno),
  un solo FuelEvent (prima 3), carburante finale 0,2629 (prima 0,0261), `movement_end` 41,9 s (prima 1543,3).
- Nuove: 'reserve_off' (G2 spento, 0,28: identica alla vecchia 'bingo'), 'transfer_continue' ('Transport',
  0,27: continua, rotta completata, Red spara, 0,0068 a bordo al regime di combattimento), 'transfer_return'
  ('Transport', 0,15 < rotta: diretto alla base come 'bingo', 0,1429 a bordo).

### Scelte dove le decisioni lasciavano margine

- Istante del bingo in sessione = inizio del primo tratto che consuma (dopo la sosta a terra, se c'e').
- Basi della linea retta (passi 3 e 4) = basi del lato piu', partendo da una base, il DEPARTURE.
- Partenza in volo senza basi del lato: `BINGO_NO_BASE`, nessun rientro, regole della F6-A (come la F6-B2bis);
  il validatore rifiuta comunque (sotto la soglia).
- Il trasferimento a ritroso non considera il resto della rotta dell'anello (se il residuo non basta a
  concludere, il resto non e' raggiungibile).
- Punto della rotta piu' vicino a una base alternativa = minimo globale della distanza orizzontale dalla
  spezzata dei tratti di movimento; a parita' di distanza, il percorso piu' breve.
- Alla partenza in volo una base alternativa non vince mai sul diretto alla base piu' vicina al punto di comparsa
  (disuguaglianza triangolare): il test d'integrazione verifica l'atterraggio sulla base della rotta quando e'
  la piu' vicina; le alternative lungo la rotta sono verificate nei test unitari (G4 le rendera' operative).
- Rapporto con il G1: il G1 rifiuta con carburante <= minimo, il G2 con carburante < soglia (solo l'uguaglianza
  esatta differisce).

### Costanti stimate

- `Fuel_Model.ALTERNATE_BASE_MAX_OFFSET = 3000.0` m: decisione dell'utente, STIMA, non tarata.
- Invariate: `DISENGAGE_TIME` 300 s (G1), `BINGO_RETURN_FACTOR` 1,2 e `BINGO_RESERVE` 0,10 (solo a G2 spento).
- S26, costanti DI TEST verificate nel test (`test_declared_fuels`): `G2_FUEL` 0,27 (fra rotta al regime di
  combattimento 0,263 e soglia 0,276), `BINGO_FUEL` 0,28 (varianti a G2 spento), `DRY_FUEL` 0,15.

### Limiti noti

- Consumo deterministico: la soglia scatta solo alla partenza; il bingo dopo un ingaggio arriva con G3/G4.
- Idoneita' della base per tipo d'aereo non modellata; terreno non modellato (discesa rettilinea a quota 0).
- Un trasferimento che continua consumando la riserva, se combatte, consuma al regime 'max' nella contabilita'
  senza ri-scheduling (limite gia' noto della F6-A).
- Il validatore resta non chiamato dal codice di produzione.

### Test

- `Test_Fuel_Model.TestBingoDecision` (nuova, 20 test): soglia, posizioni e residui arbitrari, rami di entrambi
  gli alberi, alternative avanti/indietro, limite 3,0/3,1 km, parita', raggiungibilita' senza riserva, nessuna base.
- `Test_Mission_Adapter.TestReserveBingoValidator` (nuova, 5 test); `TestBingoValidator` e
  `TestReverseRouteBingoValidator` girano con `disengage_reserve=False`.
- `Test_Mission_Types`: `crew_recovered` (+1).
- `Test_Session_Simulator.TestReserveBingo` (nuova, 8 test); `TestBingo` gira con il G2 spento.
- `Test_Session_Scenarios_S26`: riscritto per il G2, 9 varianti, 10 test (+2: soglia dei carburanti di test, discesa immediata; il vecchio test del ritroso ora su `reserve_off`).

## G3: consumo di carburante in ingaggio (decisioni dell'utente del 2026-10-15/16)

**Base del confronto**: `Test/baseline/scenario_baseline.json` installata (794 esecuzioni, G2).
**Dopo**: `Session_Simulator.G3_ENGAGEMENT_FUEL = True`. `--compare`, 2026-10-16 su osboxes: **802 esecuzioni**;
delle 794 della base **372 IDENTICHE**, **422 cambiate**, **8 nuove** (`S26-BINGO/S26-BINGO-k/engagement_fuel_off`,
k = 0..7). Verificato su tutte le 422 con un confronto chiave per chiave fuori dal repository: le differenze sono
SOLO nella voce `fuel`, nei conteggi `counts.fuel_events`/`counts.fuel_exhausted` e nel carburante finale
`assets.*.fuel`; nessuna differenza in ingaggi, salve, danni, munizioni, posture, ETA (i tratti, i contatti e gli
ingaggi sono calcolati a monte alla crociera e il G3 non li tocca). `counts.fuel_exhausted` cambia in 8 esecuzioni
sole (S26 'transfer_continue', sotto). Fotografia del repository NON rigenerata. **Verifica 2026-10-17** (ProArt
P16): `--compare` ripetuto, stessi numeri (802: 372 identiche, 422 cambiate solo nelle voci carburante, 8 nuove); le 8
'engagement_fuel_off' identiche alle vecchie 'none'. Approvato dall'utente, fotografia installata (802 esecuzioni).

### Il cambio

1. **Consumo per ingaggio** (`Fuel_Model.engagement_fuel[_with_source]`): il carburante di `DISENGAGE_TIME` (300 s)
   alla massima spinta militare, cioe' la riserva di disimpegno del G1 (delega a `disengagement_reserve_with_source`:
   stessa fonte `emergency.consume` in kg/h / capacita' del loadout, stesso ripiego sul regime 'max'). E' l'UNICO
   punto di calcolo: la regola futura per gli aerei con emergenza piu' breve di 5 minuti (WW2: "emergency per
   min(300 s, `speed_data['emergency']['time']`), poi 'combat'") e' documentata nel docstring ma NON implementata
   (campo `time` del registro non affidabile, unita' ignota).
2. **Evento** (`Fuel_Model.build_engagement_fuel_event`): `FuelEvent` ISTANTANEO, `time` = `t_start` = istante
   dell'ingaggio, distanza e durata nulle, `regime` = `Fuel_Model.ENGAGEMENT_REGIME` ('engagement', etichetta, non una
   chiave di `Mobile.FUEL_REGIMES`), limitato al disponibile; nessun evento a serbatoio vuoto.
3. **Chi e quando** (`Session_Simulator._engagement_instants`): partecipa chi ha combattuto secondo la definizione
   della F6-A (`_engaged_assets`: tiratore, bersaglio di una salva anche mancata o intercettata, intercettore);
   istante = il primo fra i lanci delle salve sue o dirette a lui (`Salvo.t_launch`) e le sue intercettazioni. Solo
   aerei di MISSIONE (dominio 'air') IN VOLO a quell'istante (`grounded`): un aereo colpito sul parcheggio non
   consuma. Un consumo per esito d'ingaggio (oggi ogni forza e' in una sola componente per sessione: al piu' uno per
   aereo e per sessione).
4. **Movimento**: gli aerei consumano SEMPRE alla crociera (prima: tutto al regime 'max' se avevano combattuto).
   Terra e mare invariati (regola 'max' della F6-A, quantita' identica alla crociera; nessun consumo d'ingaggio).
5. **Ordine**: il consumo d'ingaggio e' messo fra gli eventi per tratto in ordine di tempo, PRIMA del tratto in cui
   cade (nessun tratto spezzato); se l'evento MOVEMENT dell'aereo e' gia' passato, applicato subito.
6. **Esaurimento in ingaggio**: contatore a zero, nessun evento dopo; l'aereo NON e' fermato ne' perso (nessun
   ri-scheduling: G4), esito per asset, planata/perdita della F6-A e `crew_recovered` invariati.
7. **Interruttore**: spento, la F6-A esattamente come prima (verificato: le 8 esecuzioni 'engagement_fuel_off' hanno
   gli eventi e il carburante delle vecchie 'none', 0,736842 con un evento 'max' da 0,2632).

### Differenze della fotografia, esecuzione per esecuzione (per gruppi)

Il saldo per aereo che ha combattuto e' `D/A_max - D/A_nom - R` (D = movimento, A = autonomie del loadout,
R = consumo d'ingaggio): il G3 consuma PIU' della vecchia sovrastima sulle rotte brevi, MENO sulle lunghe. Per
l'F-16C 'Strike' (A_nom 1570 km, A_max 1140 km, R ~0,085) il pareggio e' a ~350 km di movimento; quasi tutti gli
scenari hanno rotte di 40-300 km, quindi quasi tutti gli aerei finiscono con MENO carburante.

- **Meno carburante (rotte brevi)**, 422 esecuzioni meno quelle sotto: ORC-base/interval/seed/twofronts (aerei di
  test, R = 0,12 di ripiego 'max': -0,08 / -0,05), S1 'with_cas', S2, S3 (436 aerei, -0,049), S4, S6, S7, S9, S9R,
  S11-S16, S18, S19, S19AD, S21, S21R, S23-CAP 'during', S23-TOT, S24-GLIDE 'glide', S24-ORBIT 'full'/'per_leg_off',
  VAL-agn/VAL-det: ogni aereo che ha combattuto ha un evento 'engagement' (R fra 0,050 e 0,104 secondo il modello e
  il loadout) e i tratti 'nominal' al posto di 'max'; differenza del carburante finale fra -0,013 e -0,167 (S11:
  due sessioni, la seconda parte dal residuo della prima). Gli aerei che non hanno combattuto non cambiano.
- **Piu' carburante**: S5 (103 aerei, +0,045: rotta di 950 km, oltre il pareggio, 'max' 0,609 contro crociera 0,475 +
  R 0,089); S22-AIR 'parked' (16 MiG, i soli 'piu'' di S22-AIR): bersagli di salve SUL PARCHEGGIO, prima contati
  "hanno combattuto" e consumati tutto il volo successivo a 'max', ora a terra all'istante dell'ingaggio, nessun
  consumo d'ingaggio, volo alla crociera. Gli altri 48 aerei di S22-AIR ('base_area', 'landed', 'parked': gli
  strike Blue) hanno meno carburante come sopra.
- **S26-BINGO** (40 cambiate): 'none' 0,7368 -> 0,7237 (evento 'engagement' 0,0852 al primo lancio del marcatore Red,
  872-889 s, poi il tratto alla crociera 0,1911); 'switch_off' 0,0168 -> 0,0037; 'transfer_continue' 0,0068 -> **0,0**:
  il trasferimento sotto la soglia del G2 che continua consumando la riserva e' ingaggiato e il consumo d'ingaggio
  esaurisce il contatore poco prima della fine della rotta (evento del tratto `exhausted`, 0,1848 di 0,1911), ma la
  rotta e' completata lo stesso (limite G4, sotto); 'no_base'/'bingo_off' finale 0 come prima, cambia la forma
  degli eventi (evento 'engagement' a ~872 s, tratto esaurito a 942 s: l'esaurimento A MONTE resta a 942 s, 235,5 km).
  Identiche 'bingo', 'reserve_off', 'reverse_off', 'transfer_return' (rientro dalla partenza, nessun ingaggio).
- **Identiche**: tutte le unita' senza aerei in combattimento con carburante modellato (ORC-fuel, ORC-nocontact, S8,
  S10, S17, S20, S22-E1, S22-E3, S23-HOLD, S24-E5, S25-*) e le varianti senza ingaggio aereo (S1 'without_cas',
  S22-AIR 'airborne'/'no_base', S23-CAP 'after'/'no_wait'/'waits_off', S24-GLIDE 'enemy_base'/'no_base'/'off',
  S24-ORBIT 'dry': la CAP si esaurisce a 1050 s, prima dell'ingaggio).
- **Nuove**: 'engagement_fuel_off' x 8 seed (G3 spento, pieno: identica alla vecchia 'none').

### Scelte dove le decisioni lasciavano margine

- "Partecipa" = la definizione esistente di "ha combattuto" della F6-A (tiratore, bersaglio di una salva,
  intercettore); il solo rilevamento non conta.
- Istante = il primo lancio di una salva sua o diretta a lui, o la prima intercettazione (non l'inizio della
  componente d'ingaggio, che e' l'inizio della finestra di contatto e puo' precedere di molto il combattimento).
- Solo aerei di missione IN VOLO (un aereo colpito a terra non manovra); terra e mare esclusi (nessun dato di consumo
  per regime nei registri; la loro regola 'max' resta, con quantita' identica alla crociera).
- Ordine nella contabilita' senza spezzare il tratto: il consumo d'ingaggio precede l'evento del tratto in cui cade.
  Approssimazione: il consumo e' limitato dal residuo all'INIZIO del tratto, non da quello all'istante (es. S26
  'no_base': all'istante 872 s il residuo reale e' ~0,011, il consumo prende 0,085 e il tratto risulta esaurito);
  il carburante finale non cambia (sempre limitato al disponibile).
- Esaurimento in ingaggio: SOLUZIONE MINIMA, coerente con il limite gia' dichiarato dalla F6-A per il regime 'max':
  solo il contatore va a zero, nessun ri-scheduling, nessun cambio di esito. Alternativa scartata (decisione di
  progetto, rimandata al G4): applicare planata/perdita della F6-A all'istante dell'ingaggio, che richiede di
  troncare tratti e contatti gia' calcolati.
- Evento istantaneo con durata 0 (non 300 s): "nell'istante dell'ingaggio" del brief; i 5 minuti di manovra non
  spostano l'aereo nel DES.

### Costanti stimate

- Nessuna costante nuova. Il consumo per ingaggio usa `DISENGAGE_TIME` = 300 s (stima dell'utente, G1) e il dato
  `emergency.consume` del registro (kg/h dedotti, circa spinta militare, stima non tarata, strada A del G1) o il
  ripiego 'max' del loadout.
- S26: nessuna costante di test nuova; la variante 'engagement_fuel_off' usa il pieno come 'none'.

### Limiti noti

- **Nessun ri-scheduling (G4)**: dopo un ingaggio l'aereo prosegue la rotta pianificata anche se e' sotto la soglia
  di bingo o ha il contatore a zero (S26 'transfer_continue'); l'esaurimento e la perdita della F6-A restano
  calcolati a monte alla crociera e non si anticipano per il consumo d'ingaggio.
- Un solo consumo per aereo per sessione, perche' ogni forza e' in una sola componente d'ingaggio per sessione: piu'
  scontri distinti nel tempo nella stessa componente contano come un ingaggio.
- Regola WW2 (emergenza piu' breve di 5 minuti, poi 'combat') non implementata; quando lo sara' va deciso se la
  riserva del G1 la segue.
- Consumo istantaneo, limitato dal residuo all'inizio del tratto che contiene l'ingaggio (sopra).
- Terra e mare senza consumo d'ingaggio.

### Test

- `Test_Fuel_Model.TestEngagementFuel` (nuova, 6 test propri + i 7 ereditati da `TestDisengagementReserve`):
  uguaglianza con la riserva (aereo reale, ripiego, non modellato), evento istantaneo non applicato, aereo reale,
  limite al disponibile, nessun evento, argomenti fuori dominio.
- `Test_Session_Simulator.TestEngagementFuel` (nuova, 8 test): un consumo prima del tratto e movimento alla
  crociera, interruttore spento = F6-A, nessun ingaggio nessun consumo, aereo parcheggiato colpito senza consumo,
  esaurimento in ingaggio (solo contatore), senza eventi per tratto, `_engagement_instants`. `TestEndToEnd`: i test
  sul carburante aggiornati al G3 (+1 test sul consumo all'istante del primo lancio; il test del regime 'max' gira
  con il G3 spento).
- `Test_Session_Scenarios_S26`: variante 'engagement_fuel_off', nuovo `test_engagement_fuel`,
  `test_without_bingo_the_route_is_completed` aggiornato ('transfer_continue' a zero se Red spara). Variante
  registrata nella tabella `UNITS` di `Scenario_Baseline.py` (in coda).
- `Test_Session_Scenarios_S24.TestS24OrbitExhaustion.test_fuel_events_are_per_leg` e
  `Test_Session_Scenarios_S10_S18.TestS11SessionBoundary.test_fuel_in_second_session_starts_from_carried_fuel`:
  adattati all'evento d'ingaggio (tratti filtrati, contatore concatenato; primo evento per asset).

## G4a: episodi d'ingaggio (decisioni dell'utente del 2026-10-17)

**Base del confronto**: `Test/baseline/scenario_baseline.json` installata (802 esecuzioni, G3).
**Dopo**: `Session_Simulator.G4_EPISODES = True`, `EPISODE_GAP` = 300 s. `--compare`, 2026-10-17 su ProArt P16:
**814 esecuzioni**; delle 802 della base **762 IDENTICHE**, **40 cambiate** (S5: 36 = 12 seed x 'press_on', 'default',
'resistant'; S6: 4 seed), **12 nuove** (`S5/S5-k/episodes_off`, k = 0..11). Sono esattamente le esecuzioni previste
dalla sonda della proposta (componenti con 2 episodi a 300 s): nessun'altra esecuzione cambia, quindi lo spostamento
della contabilita' del carburante in un passo finale e il nuovo campo `reference_health` non hanno effetti nelle
sessioni di un solo episodio per componente. Verificato fuori dal repository: le 12 'episodes_off' sono IDENTICHE
(confronto dell'intera voce) alle vecchie 'default'. Fotografia del repository NON rigenerata.

### Il cambio

1. **Episodio** (`_episodes`): finestre legate se le loro coppie di forze condividono una forza (o due forze dello
   stesso dominio di coordinamento) E gli intervalli si sovrappongono o distano al piu' `EPISODE_GAP` = 300 s
   (`Fuel_Model.DISENGAGE_TIME`). Union-find sulle finestre, una scansione per chiave (forza o dominio) come fusione di
   intervalli; ordine: inizio, `event_id`, prima finestra.
2. **Coda**: un `resolve_engagement` per episodio, in ordine di tempo, sulle sole sue finestre e forze; esito applicato
   subito.
3. **Forza occupata**: fino al `t_end` dell'esito; finestre successive delle sue forze ritagliate
   (`Contact_Scheduler.trim_contact_window`: CPA e reciproco ricalcolati) o scartate, episodi rimasti ricostruiti.
   Negli scenari della fotografia non scatta mai (nessuna salva in volo per piu' di 300 s oltre le finestre).
4. **RNG**: `event_id` di prima, `counter` = ordinale degli episodi con lo stesso insieme di forze, anche per la tempra.
5. **Forza DISENGAGED** passiva negli episodi successivi (`until` = istante del disingaggio); idem per le fini di
   attivita' della F6-B1 gia' scattate.
6. **Soglia di danno**: `ActivityCriteria.reference_health` = salute d'inizio sessione.
7. **G3**: un consumo d'ingaggio per episodio (codice invariato: uno per esito).
8. **Carburante**: passo finale dopo tutti gli episodi, stessa coda ripercorsa (stessi `FuelEvent`, stesso ordine).
9. `assemble_session_outcome(..., chained=True)`: nessun warning "health_before/after non concatenati" (lo sono).

### Differenze della fotografia, esecuzione per esecuzione

- **S5** (36 cambiate). Prima: una run con i quattro rossi; una formazione che rompeva il contatto con L1 era "andata
  via" per tutta la sessione (forza rotta nella run) e L2 non sparava. Ora due episodi per replica, L1
  ([556, 1648] s) e L2 + L3 + bersaglio (da ~2206 s); la formazione disingaggiata a L1 prosegue la rotta PASSIVA (il
  DES non la ri-instrada) e L2 la ingaggia di nuovo, con tempra nuova ed erosione contata sui superstiti. Stream RNG
  di entrambi gli episodi diversi da prima (insiemi di forze diversi da quello della componente). Su 12 seed:

  | variante | Blue distrutti prima -> G4a | repliche in cui L2 spara | L3 spara | salve Blue (bersaglio raggiunto) |
  |---|---|---|---|---|
  | press_on | 45 -> 41 | 12 -> 12 | 1 -> 2 | 2 -> 7 (S5-7; ora anche S5-9) |
  | default | 17 -> 28 | 1 -> 12 | 0 -> 0 | 0 -> 0 |
  | resistant | 30 -> 33 | 7 -> 12 | 1 -> 0 | 2 -> 0 |

  Con la dottrina di default la formazione si ferma al primo strato in 11 repliche su 12 sia prima sia dopo, ma ora
  subisce comunque il secondo strato (11 distrutti in piu'): e' l'effetto della decisione 5 (passiva, resta
  bersaglio) senza ri-instradamento. Esiti di forza: due per replica (`force_outcomes` 'disengaged/disengaged',
  'held/destroyed', ...). Carburante: chi partecipa a entrambi gli episodi ha due consumi d'ingaggio.
- **S6** (4 cambiate). Prima una run con le quattro forze; ora episodio 1 = Blue-AirWing contro Red-Coast +
  Red-Flotilla (dal ~100 s, la fusione terra-mare resta nello stesso episodio), episodio 2 = Blue-CSG contro
  Red-Flotilla (~3600-6500 s, il gruppo navale arriva molto dopo). Stream diversi (primo tiro 107,5-150,8 s ->
  107,5-107,8 s), esiti diversi per seed (es. S6-0 Blue-AirWing held -> destroyed, S6-1 destroyed -> held, la flottiglia
  'held/disengaged' in 3 seed su 4); gli invarianti del test (finestre miste, entrambe le minacce sparano, navi che
  intercettano, ala colpita da terra e da mare) valgono ancora.
- **Identiche**: tutte le altre 762, comprese S5-like a un episodio (ORC-twofronts M-raid: finestre a 100 s
  l'una dall'altra, un episodio), S20 e ogni scenario con Operazioni o missioni dello stesso blocco (finestre
  sovrapposte).
- **Nuove**: 'episodes_off' x 12 seed (S5, G4a spento, dottrina di default) = vecchia 'default'.

### Scelte dove le decisioni lasciavano margine

1. Legame per dominio: la chiave di legame di una finestra e' il dominio di coordinamento di ciascuna delle due forze
   (la forza stessa senza dominio): condividere una forza e' il caso particolare. Una forza che e' sola nel suo dominio
   si comporta esattamente come "condividono una forza".
2. Forza occupata "dal primo istante del suo episodio" letto come inizio dell'EPISODIO (non della prima finestra della
   forza nell'episodio): poiche' gli episodi sono estratti in ordine di inizio, ogni finestra non ancora risolta
   comincia dopo, e basta ritagliare quelle che cominciano prima del `t_end`. Garantisce la causalita' per forza
   (episodi di una forza mai sovrapposti nel tempo, risolti in ordine); costo: una forza entrata tardi in un episodio
   lungo e' occupata dall'inizio dell'episodio (un suo contatto altrove in quell'intervallo e' spostato alla fine).
3. Ritaglio della finestra: CPA e primo intervallo reciproco ricalcolati sui tratti ritagliati con la regola di
   `contact_windows`; portate e `first_detector` invariati. Funzione nello scheduler (`trim_contact_window`), che
   possiede la geometria delle finestre.
4. Ricostruzione degli episodi solo se un ritaglio ha cambiato qualcosa (equivalente a ricostruire sempre, perche' gli
   episodi sono componenti disgiunte); controllo limitato alle coppie delle forze dell'episodio appena risolto.
5. `counter` contato su ogni episodio estratto, anche se `resolve_engagement` restituisce None.
6. Passivita' dopo il disingaggio estesa a TUTTI gli asset della forza disingaggiata, anche quelli che nel suo
   episodio non erano in contatto (la decisione e' per forza; esempio nel test `TestEngagementEpisodes`: la forza
   rossa che rompe il contatto con il primo veicolo distrutto non spara piu' con il secondo, 150 km piu' avanti).
   `until` = `ForceOutcome.time` (istante del cambio di esito), `t_end` dell'esito se manca.
7. Estesa anche alle fini di attivita' della F6-B1 (danno, winchester, bersaglio distrutto) scattate in un episodio
   precedente: senza, nella run successiva l'asset tornerebbe a sparare fino al primo controllo dei criteri (il
   risolutore non ne ha memoria). Stesso meccanismo `until`, applicato solo agli asset delle forze dell'episodio (cosi'
   un episodio senza criteri resta "senza criteri" per il risolutore).
8. Salute di riferimento: nuovo campo opzionale `ActivityCriteria.reference_health` (None = comportamento precedente),
   passato solo per gli asset con `damage_threshold` e solo con il G4a acceso.
9. Erosione e shock della soglia di rottura per episodio (sugli asset impegnati all'inizio dell'episodio): coerente con
   "ingaggio diverso, tempra nuova"; e' la ragione per cui in S5 la formazione 'press_on'/'resistant' "held" a L1 con
   2 perdite su 4 rompe a L2 con 1 perdita su 2.
10. Contabilita' del carburante finale: SEMPRE (anche con il G4a spento), perche' e' verificata equivalente
    (risolutore e carburante non si leggono a vicenda) e la fotografia lo conferma (762 identiche, 'episodes_off' =
    vecchia 'default').
11. `assemble_session_outcome` riceve `chained=True` da `run_session` sempre (l'esecutore applica ogni esito prima del
    successivo da sempre): cambia solo un warning di log, mai emesso prima del G4a.
12. `Scenario_Fixtures.force_outcome`: con piu' esiti della stessa forza (piu' episodi) solleva ValueError come per le
    piu' missioni di un blocco (prima restituiva in silenzio il primo esito per un `mission_id`); S5 legge gli esiti
    per episodio.

### Costanti stimate

- `EPISODE_GAP` = `Fuel_Model.DISENGAGE_TIME` = 300 s: valore deciso dall'utente, legato alla stima G1 dei 5 minuti di
  disimpegno (non tarato).
- Nessuna costante di test nuova (scenario di test `TestEngagementEpisodes`: geometria scelta per avere finestre a
  700 s l'una dall'altra; salve di 1000 s di volo per la forza occupata).

### Limiti noti

- L'episodio e' risolto in blocco con i tratti calcolati a monte: nessuna decisione sul carburante dopo l'episodio
  (G4b), l'aereo sotto la soglia di bingo dopo un ingaggio prosegue la rotta; il contatore a zero (S26
  'transfer_continue') resta come al G3.
- Il DES non ri-instrada la forza disingaggiata: prosegue passiva sulla rotta e puo' essere ingaggiata dagli strati
  successivi (S5), effetto voluto dalla decisione 5 ma che rende la "rottura" meno protettiva di prima.
- Forza occupata per forza intera e dall'inizio dell'episodio (scelta 2), non per asset.
- Episodi separati da piu' di 300 s anche se fisicamente lo stesso scontro prolungato con una pausa: lo dichiara la
  regola.

### Test

- `Test_Session_Simulator.TestEpisodes` (9 test): intervallo di fusione (300 s, 0 s, limite incluso), forza condivisa e
  catena, dominio di coordinamento solo entro l'intervallo, intervallo infinito = componente connessa, un episodio =
  stesse finestre nello stesso ordine della componente, ordine per tempo ed `event_id` indipendente dall'ordine del
  dizionario, intervallo negativo, `_trim_busy` (ritaglio, scarto, idempotenza).
- `Test_Session_Simulator.TestEngagementEpisodes` (11 test): due episodi in ordine con le sole loro finestre,
  interruttore spento = una componente, `counter` 0/1 per ingaggio e tempra (tempre diverse), identita' delle sessioni
  a un episodio con l'interruttore spento (scenario base e due fronti), determinismo, due consumi d'ingaggio G3 in due
  episodi, salute concatenata fra episodi, salute di riferimento della soglia di danno, forza disingaggiata passiva,
  fine di attivita' riportata all'episodio successivo, forza occupata (finestra scartata).
- `Test_Engagement_Resolver.TestActivityEnd.test_reference_health_of_the_damage_threshold`,
  `Test_Contact_Scheduler.TestContactWindows.test_trim_recomputes_cpa_and_mutual_on_the_rest`.
- `Test_Session_Scenarios`: S5 riscritto per gli episodi (invarianti per episodio, verdetto sulla prima rottura,
  nuova variante 'episodes_off', nuovo `test_two_episodes_one_per_layer_group`), S6 aggiornato (due episodi). Variante
  registrata nella tabella `UNITS` di `Scenario_Baseline.py` (in coda).
- Suite completa: 4344 test OK (7 skipped), 23 nuovi.

## G4b: ri-pianificazione dopo l'episodio d'ingaggio (decisioni dell'utente del 2026-10-17)

**Base del confronto**: (1) `Test/baseline/scenario_baseline.json` installata (802 esecuzioni, G3); (2) la cattura del
G4a (814 esecuzioni, fuori dal repository), per separare gli effetti del G4b da quelli del G4a. **Dopo**:
`Session_Simulator.G4_EPISODES = True`, `G4_REPLAN = True`. `--compare`, 2026-10-17 su ProArt P16: **866 esecuzioni**.
- Contro la fotografia (802): **746 IDENTICHE**, **56 cambiate**, **64 nuove**. Delle 56 cambiate, 40 sono quelle del
  G4a (S5 'press_on'/'default'/'resistant' x 12, S6 x 4: identiche alla cattura G4a) e **16 sono del G4b** (S24-ORBIT
  'per_leg_off' x 8, S26 'transfer_continue' x 8). Delle 64 nuove, 12 sono del G4a (S5 'episodes_off') e 52 del G4b
  (S5 'with_base', 'with_base_resistant', 'replan_off' x 12; S26 'post_engagement_bingo', 'replan_off' x 8).
- Contro la cattura G4a (814): **798 IDENTICHE**, **16 cambiate** (le 16 del G4b sopra), **52 nuove**.
Ogni esecuzione cambiata ha un aereo ri-pianificato per carburante (nessuna per disingaggio fra le esecuzioni di prima:
nessuna ha una base del lato della forza disingaggiata, v. S5). Fotografia del repository NON rigenerata.

### Il cambio

1. **Candidati**, alla fine di ogni episodio (`t_r` = `t_end` dell'esito): aerei di MISSIONE che vi hanno consumato
   (G3, la stessa regola della contabilita') o la cui FORZA vi e' DISINGAGGIATA; in volo, non distrutti, non gia' a
   secco, con il carburante modellato; in ordine di id.
2. **Residuo analitico** a `t_d` (`Fuel_Model.fuel_at`): carburante d'inizio sessione - tratti che consumano fino a
   `t_d` alla crociera (in corso in proporzione) - consumi d'ingaggio fino a `t_d`. Stessa aritmetica della
   contabilita' (test `TestFuelAt.test_end_value_is_the_accounting` e, in sessione, residuo e carburante finale
   ricalcolati a mano in `TestReplanAfterEpisode`).
3. **A secco** (residuo zero): regole della F6-A dal punto a `t_d` (`_exhaustion_end`, estratta da `_fuel_end`).
4. **Bingo**: `Mission_Adapter.mission_bingo_decision(..., time=t_d, fuel=residuo)` sulla missione intera, albero del
   G2 (le basi alternative entro 3 km contano davvero); `BingoEnd` da `t_d` con la meccanica del G2.
5. **Rientro forzato dopo il disingaggio** (decisione dell'utente): `Fuel_Model.bingo_decision(..., forced=True)`,
   nessun controllo di soglia, regola di COMBATTIMENTO qualunque sia il tipo di missione; motivo nuovo
   `AssetEndReason.DISENGAGED`, missione `AbortReason.DISENGAGED`.
6. **Esaurimento sui nuovi tratti**: `Fuel_Model.fuel_exhaustion(..., fuel=residuo)` (nuovo parametro) da `t_d`.
7. **Ri-scheduling**: tratti di presenza e movimento e programma a terra sostituiti; `schedule_contacts` rieseguito
   sulle sole coppie con un aereo ri-pianificato (nuovo parametro `only_assets`); finestre nuove ritagliate a `t_r` e
   alle forze occupate; finestre non risolte di quegli aerei scartate; episodi rimasti ricostruiti. Episodi risolti
   invariati.
8. Interruttore `G4_REPLAN`, letto solo con `G4_EPISODES`; spento = G4a.

### Differenze della fotografia, esecuzione per esecuzione (solo G4b; per il G4a v. la sezione "G4a")

- **S26 'transfer_continue'** (8 cambiate; voce: `Blue-Flight.destroyed` 0 -> 1). Trasferimento a 0,27 (sotto la soglia
  alla partenza ma con carburante per la rotta: CONTINUA). In ogni seed Red-Site spara e l'F-16C consuma la riserva
  (~0,085): il residuo non basta piu' per la rotta (analiticamente a secco a ~1162 s). L'episodio con Red-Site dura
  fino all'ultimo impatto (~1211 s), OLTRE la fine della rotta (1200 s): la decisione e' alla fine dei tratti
  dell'aereo (scelta 2 sotto), residuo zero, regole della F6-A dal punto finale (310 km dalla base, planata 50 km da
  5000 m): perso, DESTROYED/FUEL_EXHAUSTED con l'equipaggio recuperato, missione DESTROYED. Prima: rotta completata con
  il contatore a 0,0. Carburante finale, eventi di carburante e istante di fine movimento invariati (0,0, 1200 s).
- **S24-ORBIT 'per_leg_off'** (8 cambiate; voci: `Red-CAP.destroyed` 0 -> 1, `Red-CAP.movement_end` 2400,0 ->
  2026,1). MiG-29S con il carburante 'dry' (dimensionato per mezza orbita) e `F6_FUEL_PER_LEG` spento (l'orbita non
  consuma): in ogni seed la CAP ingaggia i bombardieri (~1282 s, consumo d'ingaggio 0,104) e il residuo non basta piu'
  per il rientro. Nessuna base Red: nessun rientro possibile (NO_BASE), ma l'esaurimento e' ricalcolato dal residuo:
  a secco sul rientro a 2026,1 s, perso (nessuna base in planata). Prima: rientro completato con il contatore a zero.
- **S5** (nessuna delle 48 esecuzioni di prima cambia): la formazione parte in volo e Blue NON ha basi aeree, quindi
  il rientro forzato dopo il disingaggio non ha dove andare (`BINGO_NO_BASE`, passiva sulla rotta come al G4a); il
  consumo d'ingaggio degli F-15E (pieno) non porta mai sotto la soglia. Le nuove varianti con la base Blue (10 km
  dietro il punto di comparsa) mostrano il G4b. Su 12 seed:

  | variante | Blue distrutti | repliche in cui L2 spara | L3 spara | salve Blue | esito di missione |
  |---|---|---|---|---|---|
  | default (G4a, senza base) | 28 | 12 | 0 | 0 | COMPLETED 12 |
  | replan_off (base, G4b spento) | 28 | 12 | 0 | 0 | COMPLETED 12 (salve e danni = 'default') |
  | with_base (base, G4b) | 20 | 1 (S5-9) | 0 | 0 | ABORTED(DISENGAGED) 12 |
  | resistant (G4a, senza base) | 33 | 12 | 0 | 0 | COMPLETED 10, DESTROYED 2 |
  | with_base_resistant (base, G4b) | 31 | 9 | 0 | 0 | ABORTED(DISENGAGED) 8, COMPLETED 1, DESTROYED 3 |
  | episodes_off (G4a spento) | 17 | 1 | 0 | 0 | COMPLETED 12 |

  Con la dottrina di default e la base, la formazione disingaggiata a L1 (11 repliche) RIENTRA dalla fine
  dell'episodio lungo la rotta a ritroso fino al punto di comparsa e poi sulla base: L2 non spara mai; sul ritroso
  ripassa su L1 (nuovo episodio, passiva) e in alcune repliche perde un altro aereo (20 distrutti contro i 17 della
  vecchia run unica, 'episodes_off', e i 28 del G4a senza rientro). In S5-9 la rottura e' a L2: rientra e ripassa su L2
  e L1. Con la formazione resistente: 3 disingaggi a L1, 6 a L2 (in S5-11 la formazione rientrata e' distrutta da L2
  sul ritroso), 3 formazioni DESTROYED a L2 senza disingaggio (nessun rientro, come al G4a; in S5-3 il superstite
  prosegue e completa).
- **S26 'post_engagement_bingo'** (8 nuove): F-16C a 0,28 (sopra la soglia alla partenza), secondo sito Red-Near a
  (100 km, 0) e base Blue alternativa a (180 km, 2 km) (sensore 'ground' dell'F-16C dichiarato di 20 km perche' i due
  siti siano due episodi). Dopo l'episodio con Red-Near (fine ~523-533 s): residuo ~0,110 < resto della rotta ~0,106 +
  riserva ~0,085: BINGO, regola di combattimento, base alternativa (~42 km lungo la rotta e discesa) contro il ritroso
  (~145 km); atterraggio ~690 s, carburante finale 0,0831 in ogni seed, Red-Site non spara mai. ABORTED(BINGO).
- **S26 'replan_off'** (8 nuove): lo stesso scenario con il G4b spento: prosegue, entrambi i siti sparano, due consumi
  d'ingaggio, rotta completata a carburante 0,0 (il limite del G3).
- **Identiche**: tutte le altre (798 contro il G4a), compresi S26 'none' (pieno: sopra la soglia dopo il consumo),
  'switch_off' (`F6_BINGO` spento: residuo 0,0037 positivo, nessun esaurimento), 'no_base'/'bingo_off' (gia' a secco
  a monte a 942 s, dentro l'episodio), e ogni scenario senza aerei che consumano in ingaggio o senza basi del lato di una
  forza aerea disingaggiata.

### Scelte dove le decisioni lasciavano margine (da approvare)

1. **Rientro forzato**: parametro `forced` di `Fuel_Model.bingo_decision` (e di `Mission_Adapter.mission_bingo_decision`)
   invece di una funzione nuova: salta il controllo di soglia e il passo "continua"; tutto il resto dell'albero
   (candidate, raggiungibilita', passi 3 e 4, NO_BASE) e' lo stesso codice. La sessione lo chiama con `transfer`
   False (regola di combattimento anche per un trasferimento). Riserva non modellata: il rientro forzato e' deciso lo
   stesso (riserva 0 nella decisione: serve solo alla soglia).
2. **Istante della decisione** `t_d` = `t_r`, oppure la fine dei tratti di movimento dell'aereo se la sua rotta finisce
   DENTRO l'episodio (S26 'transfer_continue': episodio fino a ~1211 s, rotta fino a 1200 s). In quel caso conta solo
   l'esaurimento (A.2), non c'e' rotta da cui rientrare. Senza questa estensione "in volo a `t_r`" escluderebbe l'aereo
   e 'transfer_continue' resterebbe "rotta completata a 0,0", contro l'atteso.
3. **Punto dell'esaurimento in ingaggio** = posizione a `t_d`, non l'istante analitico dell'esaurimento (anteriore): la
   storia dell'episodio, risolto in blocco con l'aereo in volo fino a `t_d`, resta fissata.
4. **Bingo e disingaggio insieme**: prima il consumo (residuo), poi il bingo (se l'aereo ha consumato e dichiara
   `EndCriteria.bingo`); se il bingo non fa rientrare (sopra la soglia, o un trasferimento che continua) e la forza e'
   disingaggiata, rientro forzato. Se fanno rientrare entrambi vince il bingo (motivo BINGO). Il rientro forzato NON
   dipende da `EndCriteria.bingo` (e' un altro criterio), ma richiede `F6_BINGO` e `F6_BINGO_DISENGAGE_RESERVE` accesi
   (usa l'albero del G2).
5. **Precedenza dei motivi d'aborto** a parita' d'istante: FUEL > BINGO > DISENGAGED > AMMUNITION > DAMAGE (prima i
   fatti di carburante, poi la decisione tattica).
6. **Chi rientra per il disingaggio**: tutti gli aerei della MISSIONE disingaggiata in volo a `t_d` (decisione per
   forza, come la passivita' del G4a); per il carburante ogni aereo decide per se' (la formazione si puo' dividere). Una
   forza con esito DESTROYED (anche con superstiti) non rientra (S5 'with_base_resistant' S5-3).
7. **Esaurimento ricalcolato anche senza rientro**: un aereo che ha consumato e non rientra (sopra la soglia, NO_BASE,
   bingo non dichiarato, `F6_BINGO` spento) ha comunque l'esaurimento ricalcolato dal residuo (S24-ORBIT 'per_leg_off');
   un aereo disingaggiato che NON ha consumato e non rientra non e' toccato (esaurimento a monte ancora valido).
8. **Coda gia' risolta**: il tratto di una finestra nuova gia' coperto da una finestra RISOLTA della stessa coppia di
   asset con la geometria di prima (prima dell'istante da cui i tratti cambiano) e' tolto. Senza, in S24-ORBIT
   'per_leg_off' il solo anticipo dell'esaurimento sul rientro (tratti invariati fino a 2026 s) faceva rieseguire come
   NUOVO episodio la coda della finestra con i bombardieri gia' risolta (stessi tratti, seconda estrazione: un secondo
   consumo d'ingaggio e la perdita a ~1383 s). Con un rientro (tratti cambiati da `t_d` = `t_r`) la coda E' rieseguita:
   la geometria e' un'altra.
9. **Scheduler rieseguito solo sulle coppie con un aereo ri-pianificato** (`only_assets`, sottoinsieme esatto delle
   finestre senza filtro, testato): stessa potatura e stesso ordine, senza ricalcolare le altre coppie. Lo scheduler
   vede lo stato degli asset a `t_r`: un asset distrutto nei primi episodi non ha finestre nuove.
10. **S5**: lo scenario di sempre (senza basi Blue) e' lasciato com'e' (non cambia: NO_BASE); il rientro si vede in tre
    varianti nuove con una base Blue, in coda. Alternativa scartata: aggiungere la base a tutte le varianti (avrebbe
    cambiato nella fotografia anche le esecuzioni in cui il G4b non agisce, con una causa diversa dal G4b). Gli
    invarianti "dentro ciascun episodio" di S5 leggono ora gli eventi del SOLO episodio (esiti per episodio registrati
    con un `resolve_engagement` che li annota): dal G4b uno strato gia' attraversato puo' sparare di nuovo sul ritroso,
    in un episodio successivo.
11. **S26**: 'transfer_continue' tenuto (cambia); due varianti nuove 'post_engagement_bingo' / 'replan_off' con un
    secondo sito e una base alternativa, e il sensore 'ground' dell'F-16C dichiarato di 20 km (col radar del registro,
    ~95 km, i due siti sarebbero un solo episodio).

### Costanti stimate

- Nessuna costante del modello nuova. Costanti di SCENARIO dichiarate (non tarate): S5 `BASE_POSITION` = (-310 km, 0);
  S26 `NEAR_SITE_POSITION` = (100 km, 0), `ALTERNATE_BASE_POSITION` = (180 km, 2 km), `NEAR_JET_GROUND_SENSOR` = 20 km.
  Restano le stime gia' dichiarate: `DISENGAGE_TIME` 300 s, `ALTERNATE_BASE_MAX_OFFSET` 3000 m, `GLIDE_RATIO` 10.

### Limiti noti

- Decisione alla FINE dell'episodio, non a meta' (episodio risolto in blocco con i tratti di prima).
- Forza occupata: un aereo ri-pianificato incontra una forza impegnata in un episodio gia' risolto solo dopo la sua fine.
- Il rientro a ritroso ripercorre le minacce dell'andata (S5: L1 di nuovo sul ritroso).
- Episodi "vuoti" per le finestre di aerei gia' distrutti (lo scheduler non le tronca alla distruzione: comportamento
  del G4a, visibile in S5 come esiti di forza 'held' senza eventi).
- Danno oltre la soglia (F6-B1): l'aereo resta passivo sulla rotta, nessun rientro per danno. Aerei di una forza
  disingaggiata ancora a terra a `t_r` non sono ri-pianificati. Terra e mare invariati.
- Col G3 spento (regime 'max' per chi ha combattuto) il residuo resta calcolato alla crociera: la contabilita' puo'
  divergere (limite della F6-A).

### Test

- `Test_Session_Simulator.TestReplanAfterEpisode` (10 test): interruttore acceso e letto solo con il G4a; bingo dopo
  l'episodio (residuo analitico ricalcolato a mano, rientro, r2 piu' avanti mai incontrato, contatti ricalcolati da
  `t_r`: nuovo episodio passivo su r1 sul ritroso); G4b spento = contatore a zero; sopra la soglia nulla cambia
  (esito identico al G4b spento); esaurimento in ingaggio senza base (perso) e con una base in planata (a terra,
  ABORTED(FUEL)); disingaggio con carburante pieno = rientro forzato (anche 'Transport'); disingaggio senza basi =
  passivo sulla rotta; terra invariata; determinismo. `TestEngagementFuel.test_exhaustion_by_the_charge_empties_the_counter_only`
  ora con il G4b spento.
- `Test_Fuel_Model`: `TestFuelAt` (3), `TestExhaustionFromAResidual` (1), `TestForcedReturn` (3).
- `Test_Contact_Scheduler.TestScheduleContacts.test_only_assets_is_the_filtered_subset`.
- `Test_Session_Scenarios` S5: tre varianti nuove e tre test (`test_without_a_base_the_replan_changes_nothing`,
  `test_with_a_base_the_disengaged_formation_returns`, `test_with_a_base_the_resistant_formation_returns_where_it_breaks`),
  invarianti per episodio sugli esiti registrati. `Test_Session_Scenarios_S26`: `transfer_continue` riscritto, due
  varianti e due test nuovi. `Test_Session_Scenarios_S24`: 'per_leg_off' aggiornato. Varianti registrate in coda nella
  tabella `UNITS` di `Scenario_Baseline.py`.
- Suite completa: 4368 test (7 skipped), 24 nuovi.

### G4b: uscita di scena senza basi (decisione dell'utente del 2026-10-17)

**Regola**: un aereo di missione COMPARSO IN VOLO (`start_mode` AIR, nessuna base di partenza) senza alcuna base aerea
del suo lato che nella RI-PIANIFICAZIONE G4b deve rientrare (rientro forzato per disingaggio, o bingo dopo l'episodio)
non resta piu' passivo sulla rotta (`BINGO_NO_BASE`): ripercorre la rotta a ritroso fino al punto di comparsa (la
meccanica del ritroso F6-B2bis/G2, alle quote dei waypoint, senza le soste) e li' ESCE DI SCENA: nessuna presenza dopo
(come l'aereo che finisce la rotta senza atterrare su una base vera, F5-B), mai a terra, postura `off_scene` a fine
sessione se uscito, non distrutto; nessuna salva offensiva dal rientro. Esito per asset e missione: il motivo del
rientro (DISENGAGED o BINGO, ABORTED(...)) all'istante della decisione. Il ritroso consuma alla crociera; residuo
insufficiente: regole della F6-A sul ritroso (senza basi: perso, DESTROYED/FUEL_EXHAUSTED, equipaggio recuperato).

**Codice**: nuova azione `Fuel_Model.BINGO_EXIT` di `bingo_decision(..., exit_scene=True)`, data AL POSTO di
`BINGO_NO_BASE` (stesso punto dell'albero: nessuna candidata, nessuna base in linea retta) e solo con partenza in volo
(`rule.departure` False: partendo da una base il DEPARTURE c'e' sempre); rotta = `_return_route` a ritroso senza il
tratto diretto finale, `base` = punto di comparsa, `reachable` come le altre. `BingoDecision.exits`; parametro
passato da `Mission_Adapter.mission_bingo_decision(exit_scene=)`. In sessione `BingoEnd.exits`: `_legs_after_bingo`
senza sosta, `_grounded_after_bingo` senza intervallo a terra, `_postures_after_bingo` `off_scene` se uscito entro la
fine della sessione. La ri-pianificazione passa `exit_scene=G4_OFF_SCENE_EXIT` alle due chiamate (bingo dopo
l'episodio, rientro forzato). Sotto-interruttore `Session_Simulator.G4_OFF_SCENE_EXIT` (attivo, letto solo con
`G4_REPLAN`).

**Confronto** (2026-10-17, ProArt P16, 878 esecuzioni: le 866 della cattura G4b + 12 della variante nuova S5
'exit_off'):
- Contro la cattura G4b (866): **728 IDENTICHE**, **138 cambiate**, **12 nuove** ('exit_off').
- Contro la fotografia del repository (802): **637 IDENTICHE**, **165 cambiate** (le 56 gia' cambiate dal G4a/G4b +
  109 dall'uscita di scena), **76 nuove** (64 del G4a/G4b + 12 'exit_off'). Fotografia NON rigenerata. **Verifica 2026-10-17** (ProArt P16): suite 4375 OK (7 skipped), `--compare` ripetuto, stessi numeri, cattura identica a quella dell'agente (determinismo). G4a, G4b e uscita di scena approvati dall'utente insieme, fotografia installata (878 esecuzioni). Alla partenza (G2) restano le regole della F6-A (decisione dell'utente del 2026-10-17).
- **Causalita' verificata in due modi**: (1) cattura con `G4_OFF_SCENE_EXIT` spento = cattura G4b esattamente (866
  identiche, solo le 12 'exit_off' nuove), e 'exit_off' coincide esecuzione per esecuzione con la 'default' della
  cattura G4b; (2) cattura strumentata (`bingo_decision` avvolta): 425 decisioni `BINGO_EXIT` in 109 sessioni, e OGNI
  esecuzione cambiata appartiene a una sessione con un'uscita di scena, tranne S11 '*-dcs' (3), seconda sessione che
  riparte dagli asset mutati dalla prima sessione '*-synthetic', che ne ha una; nessuna sessione con un'uscita resta
  invariata. Ripetuta, la cattura e' IDENTICA (determinismo).
- **Chi esce** (aerei comparsi in volo senza basi del lato; 417 rientri forzati per disingaggio, 8 bingo dopo
  l'episodio):

  | scenario (esecuzioni cambiate) | forze che escono di scena |
  |---|---|
  | S3 'control' 18, 'stealth' 20 | Blue-Stealth, Red-Mass (caccia contro caccia: chi rompe torna indietro e spesso l'altro lo reincontra) |
  | S5 'default' 12, 'resistant' 9 | Blue-Deep (v. sotto) |
  | S2 'baseline' 8 | Blue-Strike |
  | S21 'control' 8, 'parked' 8; S21R 2 | Blue-Strike; Blue-CAS |
  | S24-ORBIT 'per_leg_off' 8 | Red-CAP in BINGO dopo l'ingaggio, ritroso irraggiungibile: a secco a ~1540-1610 s verso il punto di comparsa (prima: a secco sul rientro a 2026 s), perso in entrambi i casi |
  | S24-ORBIT 'full' 5 | Blue-Bomber disingaggiati: ripassano nell'orbita, secondo episodio con la CAP |
  | S11 6 (3 'synthetic' + 3 'dcs' a valle) | Blue-CAS |
  | S13 6, S14 6, S4 'with_sam' 6, S9 'detection_factor=0.0' 6 | Blue-Strike, Blue-Bombers, Blue-CAS, Blue-CAS |
  | S7 3, S18 'network' 1 | Red-Escort e scorta Blue; Red-CAP e Blue-Package |
  | S23-CAP 'during' 2 | Blue-Bomber |
  | ORC-twofronts 'first' 3, ORC-seed 1 (sessioni dei test d'orchestrazione) | aerei di test in volo senza basi |

  Effetti tipici: sul ritroso la formazione ripassa sulle minacce dell'andata (nuovo episodio, passiva) o reincontra la
  forza aerea avversaria; gli strati/bersagli oltre il punto della rottura non sono piu' raggiunti; postura `off_scene`
  invece del tipo di missione a fine sessione.
- **S5 per variante** (12 seed; "chi spara" = strato che ha distrutto gli aerei Blue; la formazione non lancia mai):

  | variante | Blue distrutti | L2 spara | L3 spara | distrutti da L1 / L2 / L3 | esito di missione | posture superstiti |
  |---|---|---|---|---|---|---|
  | default (G4b + uscita, senza base) | 20 | 1 (S5-9) | 0 | 20 / 0 / 0 | ABORTED(DISENGAGED) 12 | off_scene 28 |
  | resistant (G4b + uscita, senza base) | 31 | 9 | 0 | 19 / 12 / 0 | ABORTED(DISENGAGED) 8, COMPLETED 1, DESTROYED 3 | off_scene 17 |
  | exit_off (uscita spenta = 'default' del G4b) | 28 | 12 | 0 | 17 / 11 / 0 | COMPLETED 12 | off_scene 20 (fine rotta) |
  | with_base | 20 | 1 | 0 | 20 / 0 / 0 | ABORTED(DISENGAGED) 12 | parking_cold 28 |
  | with_base_resistant | 31 | 9 | 0 | 19 / 12 / 0 | ABORTED(DISENGAGED) 8, COMPLETED 1, DESTROYED 3 | parking_cold 16, off_scene 1 |
  | replan_off (base, G4b spento) | 28 | 12 | 0 | 17 / 11 / 0 | COMPLETED 12 | off_scene 20 |
  | press_on (non disingaggia: invariata) | 41 | 12 | 2 | 19 / 20 / 2 | DESTROYED 7, COMPLETED 5 | off_scene 7 |
  | episodes_off (G4a spento: invariata) | 17 | 1 | 0 | 17 / 0 / 0 | COMPLETED 12 | off_scene 31 |

  Senza base la storia degli ingaggi e' QUELLA delle varianti con la base (stesse salve, danni ed episodi: la base e'
  10 km dietro il punto di comparsa, fuori da ogni minaccia); cambiano solo il tratto finale (uscita al punto di
  comparsa invece dei 10 km fino alla base), il carburante finale e la postura (`off_scene` invece di `parking_cold`).
  In 'resistant' le 3 repliche invariate sono le formazioni DESTROYED a L2 senza disingaggio (nessun rientro).

**Scelte** (margine lasciato dalla decisione):
1. Logica come azione nuova dell'albero (`BINGO_EXIT`) e non come caso speciale della sessione su `BINGO_NO_BASE`: la
   rotta del ritroso e la raggiungibilita' sono calcolate dove si calcolano tutte le altre (`_return_route`, la stessa
   del ritroso F6-B2bis), la sessione riceve un rientro come gli altri con il solo flag `exits`.
2. Ambito conservativo: SOLO la ri-pianificazione G4b; `_decision_end` (G2 alla partenza) e il validatore
   `check_mission_bingo` non passano `exit_scene` (invariati).
3. Sotto-interruttore `G4_OFF_SCENE_EXIT` per isolare l'effetto (spento = il G4b di prima, verificato sulla cattura).
4. Postura: `off_scene` solo se l'uscita avviene entro la fine della sessione; ancora in volo sul ritroso a fine
   sessione: il tipo di missione (come un rientro verso una base non ancora raggiunta).
5. Test non di G4b che usavano incidentalmente forze aeree in volo senza basi disingaggiate (`Test_Session_Simulator`:
   `test_destroyed_mission`, `test_coordination_domains_are_passed_to_every_engagement`,
   `test_a_disengaged_force_is_passive_in_the_later_episodes`, `test_one_episode_sessions_are_identical_to_the_switch_off`)
   girano con l'uscita spenta (decoratore, commento): provano altro (regola DESTROYED/COMPLETED, domini, passivita'
   del G4a, requisito del G4a).
6. Scenari: invarianti aggiornati, non la composizione. `Scenario_Fixtures.losses_of` somma le perdite sugli episodi
   della stessa forza d'ingaggio (gli impegnati di un episodio sono gli operativi al suo inizio: nessun doppio conteggio;
   piu' missioni di un blocco restano un ValueError); S13/S14/S21 leggono gli esiti per episodio
   (`outcome.outcomes_of`); S7/S18 accettano episodi successivi fra le sole forze aeree dopo un disingaggio; S24 'full'
   al piu' due consumi d'ingaggio della CAP, 'per_leg_off' esaurimento sul ritroso verso il punto di comparsa; S5 nuova
   variante 'exit_off' in coda (`UNITS` di `Scenario_Baseline.py`), `test_without_a_base_the_replan_changes_nothing`
   sostituito da `test_without_a_base_the_disengaged_formation_exits`, "due episodi" verificato su 'exit_off' e
   'replan_off'.

**Costanti stimate**: nessuna nuova.

**Limiti**: uscita sempre al punto di comparsa, anche se il resto della rotta in avanti fosse piu' corto o fuori dalle
minacce; il ritroso ripercorre le minacce dell'andata (S2, S3, S5, S24: secondi episodi); solo dopo un episodio (non
alla partenza); la scelta fra "uscire" e "atterrare" non considera basi di altri lati o neutrali.

**Test**: `Test_Fuel_Model.TestExitScene` (3); `Test_Session_Simulator.TestReplanAfterEpisode`: uscita dopo il
disingaggio (ABORTED(DISENGAGED), ritroso alla crociera fino al punto di comparsa, nessuna sosta, `off_scene`, nessun
contatto dopo l'uscita, carburante), uscita al bingo dopo l'episodio (ABORTED(BINGO)), residuo insufficiente (perso a
meta' ritroso; G2 alla partenza invariato), interruttore spento (passivo sulla rotta, il test di prima), nessun effetto
con una base o con il G4b spento (5 test, il test "passivo senza base" sostituito).
Suite completa: 4375 test OK (7 skipped), 7 nuovi rispetto ai 4368 del G4b.

## G5: scenari del modello finale e chiusura del piano G1-G5 (2026-10-18)

**Base del confronto**: `Test/baseline/scenario_baseline.json` installata (878 esecuzioni, G4a + G4b + uscita di
scena). **Dopo**: nessun cambio del motore; S26 riorganizzato, nuovo S27-DOUBLE in coda alla tabella `UNITS` di
`Scenario_Baseline.py`. `--compare`, 2026-10-18 su ProArt P16: **918 esecuzioni**.
- Contro la fotografia (878): **878 IDENTICHE** (S26 compreso: 96 su 96), **0 cambiate**, **40 nuove** (S27-DOUBLE,
  5 varianti x 8 seed). **Verifica 2026-10-18** (ProArt P16, sessione principale): suite 4385 OK (7 skipped),
  `--compare` ripetuto con lo stesso esito, cattura identica a quella dell'agente. **Approvato dall'utente
  2026-10-18**: fotografia 918 installata.

### Il cambio

1. **S26 riscritto sul modello finale** (`Test_Session_Scenarios_S26.py`): docstring centrato sul bingo di G1-G4
   (riserva, soglia e albero, consumo d'ingaggio, episodi e ri-pianificazione); varianti divise in modello finale
   (`TestS26Bingo.FINAL_MODEL`: 'none', 'bingo', 'transfer_return', 'transfer_continue', 'no_base', 'bingo_off',
   'post_engagement_bingo') e controprova degli interruttori (`TestS26Bingo.SWITCH_CHECKS`: 'switch_off' ->
   `F6_BINGO`, 'reverse_off' -> `F6_BINGO_REVERSE_ROUTE` col G2 spento (la F6-B2), 'reserve_off' ->
   `F6_BINGO_DISENGAGE_RESERVE` (la F6-B2bis), 'engagement_fuel_off' -> `G3_ENGAGEMENT_FUEL` (la F6-A), 'replan_off' ->
   `G4_REPLAN`). I test misti di prima (che verificavano insieme regole finali e storiche) sono separati: un test per
   regola storica con validatore, istante del bingo, tratti ed esito (`test_reverse_off_is_the_straight_return_of_f6_b2`,
   `test_reserve_off_retraces_the_route_as_in_f6_b2bis`, `test_engagement_fuel_off_is_the_max_regime_of_f6_a`,
   `test_switch_off_flies_the_whole_route`); nuovo `test_variants_split_into_final_model_and_switch_checks`. Helper,
   costanti, `VARIANTS` (valori e ordine), `_scenario`, `_run` e `setUpClass` INVARIATI: le chiavi e le esecuzioni
   della fotografia non cambiano (verificato: 96 identiche). Asserzioni di prima tutte conservate.
2. **S27-DOUBLE** (`Test_Session_Scenarios_S27.py`, `TestS27DoubleEngagement`), descritto sotto.

### S27-DOUBLE: doppio ingaggio dello stesso aereo

Blue-Flight: un F-16C Block 52d 'Strike' (dati del registro: autonomia di crociera 1570 km col loadout, 'max' 1140 km,
consumo d'ingaggio = riserva di disimpegno 0,0852 del pieno), ruolo 'unarmed', in volo a 5000 m da (10 km, 0) a
(510 km, 0) a 250 m/s (2000 s; rotta 0,318 alla crociera, 0,439 al regime 'max'), sensore 'ground' DICHIARATO 20 km.
Red-First (BMP-2 in (100 km, 0)) e Red-Second (BMP-2 in (300 km, 0)), sensore 'air' DICHIARATO 40 km, tiro marcatore
senza effetto (precisione 0, come S26). Blue-Base in (0, 0); Blue-Alternate in (400 km, 2 km), entro 3 km dalla rotta e
60 km oltre la fine della finestra di Red-Second. Finestre ~[160, 520] s e ~[1000, 1320] s: due episodi.

Esito per variante (8 seed; in tutti e 8 sparano entrambi i siti):

| variante | interruttore spento | consumi d'ingaggio | decisioni dopo l'episodio | esito | carburante finale | postura |
|---|---|---|---|---|---|---|
| double | - | 2 | ~524-532 s: nessun bingo (residuo ~0,361); ~1323-1327 s: `BINGO_ALTERNATE` (residuo ~0,149) | ABORTED(BINGO) a fine 2o episodio | 0,1077 | parking_cold (Blue-Alternate) |
| transfer ('Transport') | - | 2 | 1o: nessun bingo; 2o: `BINGO_CONTINUE` | COMPLETED | 0,0411 | off_scene (fine rotta) |
| replan_off | `G4_REPLAN` | 2 | nessuna | COMPLETED | 0,0411 | off_scene |
| episodes_off | `G4_EPISODES` | 1 (componente connessa: un ingaggio) | nessuna | COMPLETED | 0,1263 | off_scene |
| engagement_fuel_off | `G3_ENGAGEMENT_FUEL` | 0 (movimento al regime 'max') | nessuna | COMPLETED | 0,0914 | off_scene |

Cosa mostra: (1) due consumi d'ingaggio dello stesso aereo nella stessa sessione, ciascuno all'istante del primo lancio
del suo sito (il limite "un consumo per sessione" del G3 e' risolto dal G4a; 'episodes_off' e' la controprova);
(2) ri-pianificazione dopo CIASCUN episodio con il residuo analitico (letta da uno spia su
`Mission_Adapter.mission_bingo_decision`, le chiamate con `time`): dopo il primo il residuo e' sopra resto della rotta +
riserva, dopo il secondo e' sotto; (3) bingo con la regola di combattimento: la base alternativa in avanti (~60 km +
discesa) batte il ritroso (~340 km, che ripasserebbe sopra entrambi i siti); (4) trasferimento: sotto la soglia ma con
carburante per la rotta, continua consumando la riserva; (5) gli interruttori G3/G4 non cambiano chi spara.

### Scelte

1. Gli "ingaggi" sono di siti terrestri con tiro marcatore, non di intercettori aerei: storia deterministica (nessun
   danno, nessun disingaggio, che farebbe scattare il rientro forzato al posto del bingo), stesso schema di S26; il
   consumo d'ingaggio del G3 non distingue la natura dell'avversario.
2. Asserzioni condizionate a quali siti sparano nella replica (il rilevamento e' un'estrazione per finestra) piu' una
   frazione aggregata dichiarata; nessuna asserzione tarata sul risultato.
3. Decisioni della ri-pianificazione osservate con uno spia nel test (nessuna voce nuova nell'esito ne' nella
   fotografia).
4. Nessuna variante "senza base alternativa": il ritroso ripasserebbe su Red-Second (terzo episodio) e mescolerebbe
   due effetti; il rientro a ritroso dopo l'episodio e' gia' coperto da S5 e S24-ORBIT.

### Costanti stimate

- Nessuna costante del modello nuova. Costanti di SCENARIO S27 dichiarate di test (non tarate): posizioni dei siti
  (100 km, 300 km), della base alternativa (400 km, 2 km), sensori dichiarati (40 km 'air' dei siti, 20 km 'ground'
  dell'F-16C), velocita' 250 m/s, quota 5000 m, `DOUBLE_FUEL` = 0,53 (verificato in `test_declared_fuels`: rotta + 2
  riserve ~0,489 <= 0,53 < rotta + 3 riserve ~0,574, e > rotta al regime 'max'; geometria con finestre separate da piu'
  di `EPISODE_GAP`), `MIN_FIRING_FRACTION` = 0,5 (stessa stima di S22-S26).

### Limiti noti

- Quelli del modello di bingo elencati al §5, deviazione 22, del Piano (registro `emergency` non tarato, regola WW2 non
  implementata, validatori fuori da `run_session`, nessuna salva offensiva dopo il bingo, F6-B3 S24-GLIDE aperto).
- S27 non copre il doppio ingaggio con intercettori aerei veri (danno e disingaggio in mezzo).

### Test

- `Test_Session_Scenarios_S26`: 16 test (erano 14), stesse esecuzioni.
- `Test_Session_Scenarios_S27`: 8 test (`test_declared_fuels`, `test_both_sites_fire_in_most_replicas`,
  `test_two_episodes_two_engagement_charges`, `test_replanned_after_each_episode`,
  `test_bingo_after_the_second_episode_lands_on_the_alternate_base`, `test_transfer_continues_after_the_second_episode`,
  `test_switches_off`, `test_switches_do_not_change_who_fires`).
- Suite completa: 4385 test OK (7 skipped), 10 nuovi rispetto ai 4375 del G4b (S26 +2, S27 +8).
