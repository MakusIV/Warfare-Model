# Proposta: finestra di rilascio delle bombe (campo `release`)

**Stato**: PROPOSTA, in attesa di approvazione dell'utente (2026-09-26). Nessun registro modificato.
Riguarda le 32 voci `Bombs` / `Cluster bombs` / `Guided bombs` di `AIR_WEAPONS['BOMBS']`
(`Asset/Aircraft_Weapon_Data.py`, dalla riga 3622). Razzi e pod-cannone sotto la stessa chiave sono
esclusi. Contesto d'uso: `Proposta_Munizioni_Compatibili_e_Rotte_Attacco.md` §2.2, §2.4, §2.5.

**Solo una parte dei valori è un dato documentato.** Ogni voce indica la fonte o il ragionamento e
un livello di confidenza. Le stime vanno marcate come tali anche nei commenti del codice.

Legenda confidenza:
- **A (alta)**: valore esplicito in una fonte tecnica o ufficiale, per quella arma;
- **M (media)**: valore esplicito ma da fonte secondaria, oppure dedotto da un dato documentato
  della stessa famiglia;
- **B (bassa)**: stima per analogia o dalla fisica, senza un dato diretto.

Legenda fonti: in fondo al documento, §5 ([F1]…[F23]).

## 0. Principi e convenzioni

### 0.1 Semantica dei campi (proposta di interpretazione)

| Campo | Significato proposto |
|---|---|
| `modes` | profili di rilascio ammessi **dall'arma** (non dall'aereo): `level`, `dive`, `loft` |
| `min_altitude` | m AGL. Minimo **dell'arma**: schegge proprie, tempo d'armamento della spoletta, tempo d'apertura del contenitore. Per le armi a lunga distanza di sgancio (GBU-24, BK-90) il vincolo delle schegge sparisce, perché l'aereo è lontano al momento dell'impatto |
| `max_altitude` | m. Massimo **operativo** dell'arma: da fonte se c'è, altrimenti il limite oltre cui l'arma perde senso (dispersione, guida) |
| `min_speed`, `max_speed` | km/h. Limiti **dell'arma** (spoletta, freno, stabilità balistica). Nel pianificatore vanno intersecati con l'inviluppo `attack` del loadout (§2.4 della proposta B), quindi un `max_speed` alto (es. 2300 km/h delle RBK) non produce effetti assurdi |
| `dive_angle` | gradi `(min, max)`, solo se `dive` è ammesso |
| `drag` | `'low'` caduta libera (anche le bombe russe M-54 dalla forma tozza); `'high'` frenata (paracadute, ballute, alette) **oppure** contenitore che si apre subito dopo lo sgancio, per cui quasi tutta la caduta è quella delle submunizioni |
| `glide_ratio` | rapporto distanza/quota di una bomba che plana davvero. `None` se l'arma non plana in modo significativo |

### 0.2 Regola di stima della quota minima per schegge (bombe non frenate)

Per le bombe HE non frenate prive di dato diretto si usa **un solo punto di ancoraggio documentato**,
la FAB-500 M-62 (201 kg di esplosivo, minimo ufficiale **570 m**, [F1][F2]), e si scala con la
**radice cubica della carica**, che è la legge di scala classica delle distanze d'effetto
dell'esplosione (distanza scalata di Hopkinson-Cranz, Z = R / W^(1/3)):

`min_altitude ≈ 570 × (carica_kg / 201)^(1/3)`

| Carica (kg, dal registro) | Fattore | Minimo stimato | Arrotondato |
|---|---|---|---|
| 20 (FAB-50) | 0,46 | 264 m | **270** |
| 39-40 (FAB-100, M/71) | 0,58 | 331 m | **330** |
| 76 (BetAB-500, carica reale) | 0,72 | 411 m | **400** |
| 90-94 (Mk-82, FAB-250) | 0,77 | 440 m | **450** |
| 201-202 (Mk-83, SAMP-400, FAB-500) | 1,00 | 570 m | **570** |
| 240 (BLU-109, carica reale della GBU-27) | 1,06 | 605 m | **600** |
| 429 (Mk-84) | 1,29 | 735 m | **750** |
| 667 (FAB-1500) | 1,49 | 851 m | **850** |

È una **stima [B→M]**: l'ancoraggio è un dato vero, la legge di scala è fisica standard, ma il
coefficiente reale dipende da spoletta, ritardo, velocità e manovra d'uscita. Controllo incrociato
qualitativo: nella pratica NATO l'ordine di grandezza del volume di schegge è 2000 ft (~600 m) per le
Mk-82/83 e 3000 ft (~900 m) per la Mk-84 (dato di letteratura di addestramento, non verificato su
un manuale: **B**). La scala è coerente con quell'ordine di grandezza.

### 0.3 Inviluppo di velocità delle bombe NATO Mk-80

Da [F3] (Mk-82 AIR, stessa famiglia): *"can be delivered at speeds from 200 to 700 knots"*,
*"low drag deliveries should be limited to 600 knots maximum due to ballistic instability"*. Si adotta
per tutte le Mk-80 a bassa resistenza **370-1110 km/h** (200-600 kt), **M**.

### 0.4 Verifica richiesta: "le bombe a grappolo hanno una quota minima più alta"

**Non è vero in generale**, e non è stato assunto. Il dato reale dipende dal tipo:
- rispetto a una bomba HE **non frenata** di pari peso il minimo è **più basso** o simile, perché le
  submunizioni hanno schegge piccole: RBK-500 da 300 m [F4] contro FAB-500 da 570 m [F1];
- rispetto a una bomba **frenata** il minimo è **più alto**: le submunizioni devono armarsi e
  disperdersi (Mk-20 Rockeye ~150 m, contro ~60 m della Mk-82 AIR);
- fanno eccezione le armi **progettate** per la bassissima quota: BLG-66 Belouga (paracadute, 60 m),
  KMGU-2 (contenitore che resta sull'aereo, 30 m [F5]), BK-90 (planante, 50 m).

Le bombe a grappolo hanno invece quasi sempre una quota **massima** bassa (3-5 km), perché da quote
alte la rosa si allarga e le spolette a tempo perdono senso. È il dato più rilevante per il
pianificatore.

### 0.5 Verifica richiesta: "le Paveway non planano"

- **Paveway II** (GBU-10/12/16): alette posteriori ripiegabili per la manovra, guida "bang-bang" che
  dissipa energia. Gittata massima dichiarata ~15 km da alta quota [F6][F7]. Il lancio nel vuoto da
  7600 m a 900 km/h dà già ~10 km: l'allungamento dovuto alla portanza è modesto (+30-50 % al
  massimo, e solo in condizioni ideali). **Proposta: `glide_ratio: None`** e trattarle come
  balistiche. È un'approssimazione conservativa (sottostima un po' la gittata massima), **M**.
- **Paveway III** (GBU-24): ali grandi, autopilota proporzionale, progettata per volare livellata
  dopo lo sgancio. *"more than 18 km (10 nm)"* da bassa quota, ~30 km da 10 000 m [F8][F9]. Plana
  davvero: `glide_ratio` ≈ 3 (30 km / 10 km), **M**.
- **GBU-27**: testa e autopilota Paveway III, ma alette di tipo Paveway II per la stiva dell'F-117.
  Planata ridotta rispetto alla GBU-24: `None`, **B**.
- **KAB-500L / Kr**: alette canard e impennaggi, senza ali di planata. ru.wikipedia parla di
  "proprietà di planata" e indica una distanza minima di lancio di 2-9 km [F10]: compatibile con una
  traiettoria balistica corretta. `None`, **M**.

---

## 1. Bombe generiche NATO (Mk-80) e derivate

### Mk-84 (2000 lb LDGP, 429 kg di carica)
- `modes`: level, dive, loft. Tutte e tre sono consegne standard delle Mk-80 (inclusa la toss/LABS).
- `min_altitude` **750** m. Regola §0.2, **B/M**.
- `max_altitude` **12 000** m. Allineato al massimo documentato della FAB-500 M-62 [F1]. Le Mk-80
  sono state sganciate in quota da B-52 e B-1, **M**.
- velocità **370-1110** km/h (§0.3), **M**.
- `dive_angle` **(0, 60)**. Angoli d'addestramento standard 10/20/30/45/60°, **M**.
- `drag` low, `glide_ratio` None, **A**.

### Mk-83 (1000 lb LDGP, 202 kg)
Come la Mk-84 salvo `min_altitude` **570** m (stessa carica della FAB-500 M-62, quindi ancoraggio
diretto, **M**).

### Mk-82 (500 lb LDGP, 92 kg)
Come la Mk-84 salvo `min_altitude` **450** m (§0.2, **B/M**).

### Mk-82AIR (Mk-82 con coda frenante BSU-49 a ballute, 92 kg)
- `modes`: level, dive. È un'arma pensata per il volo livellato basso ad alta velocità [F11].
- `min_altitude` **60** m. Nella pratica d'impiego frenato si parla di circa 150-200 ft AGL. Il
  dato preciso dipende da spoletta e velocità e non è stato trovato in una fonte primaria: **M/B**.
- `max_altitude` **1500** m in modalità frenata. Sopra questa quota il ballute non serve, e l'arma
  viene sganciata in modalità "bassa resistenza": è di fatto una Mk-82. **B**, vedi decisione D2.
- `min_speed` **520** km/h: *"FMU-139 / MK-82 AIR MIN 280 KCAS"* [F3]. Con la spoletta FMU-54 il
  minimo è 330 KCAS ≈ 610 km/h. **A** per la famiglia.
- `max_speed` **1300** km/h (700 kt) [F3], **A**.
- `dive_angle` **(0, 30)**. Consegne frenate solo livellate o in picchiata leggera, **B**.
- `drag` **high**, `glide_ratio` None, **A**.

### SAMP-400LD (SAMP tipo 21, 400 kg, 202 kg, versione a bassa resistenza)
Nessun dato specifico trovato. Analoga alla Mk-83 (il commento nel registro lo dice): valori
identici, `min_altitude` 570. **B** per analogia.

### SAMP-250HD (SAMP tipo 25, 250 kg, 92 kg, versione ad alta resistenza)
"HD" = *high drag*: la versione frenata esiste anche in DCS (Mirage 2000C) accanto alla LD.
Nessun dato specifico trovato ([F12] conferma la famiglia SAMP tipo 25, non l'inviluppo). Analoga
alla Mk-82AIR: level e dive, 60-1500 m, 520-1100 km/h, dive (0, 30), drag high. **B**.
Nota: il commento nel registro "(Mk-82)" vale per la carica, non per il profilo di rilascio.

### M/71 (Sprängbomb m/71, 120 kg, 40 kg di carica, AJS 37 Viggen)
Esiste in due configurazioni: bassa resistenza e alta resistenza, con paracadute [F13]. Sul Viggen
l'impiego tipico è radente, con la versione frenata. Il registro ha **una sola voce**: la proposta la
tratta come **frenata** (decisione D2).
- level e dive, `min_altitude` **50** m, `max_altitude` 1500 m, velocità **500-1100** km/h,
  dive (0, 30), drag **high**. **B**: nessun dato numerico trovato, analogia con la Mk-82AIR.
- Se si preferisse la versione LD: 330-12 000 m (§0.2), level/dive/loft, drag low.

---

## 2. Bombe guidate

### GBU-12 (Paveway II su Mk-82) / GBU-16 (su Mk-83) / GBU-10 (su Mk-84)
- `modes`: level, dive, loft. Paveway II: impiego tipico da media quota, possibile anche il loft
  [F6][F7], **M**.
- `min_altitude`: quello della bomba base, **450 / 570 / 750** m. La guida non riduce il volume
  delle schegge. **B/M** (§0.2).
- `max_altitude` **10 000** m. Impiego tipico 15-25 000 ft. Sopra i ~30 000 ft la gittata non
  cresce più, perché la guida bang-bang consuma l'energia. **B**.
- velocità **370-1110** km/h come la bomba base, **M**.
- `dive_angle` (0, 45), **B**.
- `drag` low, `glide_ratio` **None** (§0.5), **M**.

### GBU-24 (Paveway III, LLLGB)
- `modes`: level, dive, loft. La consegna principale è **livellata a bassa quota**, poi loft e
  picchiata, con *"a larger delivery envelope for the dive, glide and loft modes"* [F8], **A**.
- `min_altitude` **60** m. Progettata per lo sgancio a bassa quota a >18 km di distanza [F8][F9]:
  l'aereo è lontano all'impatto, quindi il vincolo delle schegge non si applica. Il valore esatto è
  una stima, **M**.
- `max_altitude` **12 000** m (~30 km da 10 000 m [F9]), **M**.
- velocità **550-1110** km/h. Il minimo è stimato: serve energia per la planata. **B**.
- `dive_angle` (0, 45), **B**.
- `drag` low, `glide_ratio` **3.0**, **M**. Stima dalla gittata da 10 km. Include anche l'energia
  cinetica iniziale, quindi è un rapporto "effettivo", non un L/D aerodinamico.

### GBU-27 (Paveway III su BLU-109, F-117 / F-111F)
- `modes`: level, dive. Impiego a media quota da F-117, **M**.
- `min_altitude` **600** m, dalla carica reale del BLU-109 (~240 kg, §0.2), **B**. Vedi anomalia A1
  sulla carica nel registro.
- `max_altitude` 10 000 m, velocità 370-1110 km/h, dive (0, 45), **B**.
- `drag` low, `glide_ratio` **None** (§0.5), **B**.

### KAB-500L (FAB-500 con guida laser semiattiva)
- `modes`: level, dive, **M**. Il loft non è documentato ed è escluso.
- quota **500-5000** m, velocità **500-1150** km/h. Il dato si trova su en.wikipedia
  (voce KAB-500L/S-E, [F14]). Nelle schede Rosoboronexport circola anche 550-1100 km/h, per
  memoria e non verificato in questa sessione. **M/A**.
- `dive_angle` (0, 50). Stima: le KAB russe sono descritte come sganciabili in picchiata, ma
  l'angolo massimo non è stato trovato. **B**.
- `drag` low, `glide_ratio` None (§0.5), **M**.
- Nota: 500 m < 570 m della FAB-500 non guidata. È plausibile, perché lo sgancio guidato avviene a
  distanza.

### KAB-500Kr (FAB-500 con guida TV "fire and forget")
Come la KAB-500L: 500-5000 m, 500-1150 km/h, level e dive (0, 50), drag low, glide None. Solo
la versione esportazione **Kr-E** ha un tetto aumentato a 10 km [F10]. **M** per analogia di
famiglia: stessa scheda, stesso vettore.

---

## 3. Bombe generiche sovietiche/russe (FAB, BetAB)

### FAB-500M62 (201 kg) — ancoraggio
- quota **570-12 000** m, velocità **500-1180** km/h [F1][F2], **A**. Una seconda fonte dà
  500-1900 km/h: si è scelto il valore più basso, cioè conservativo.
- `modes`: level, dive, loft. La serie M-62 è per il trasporto esterno sui cacciabombardieri
  [F1]. Picchiata e cabrata sono le consegne standard dei Su-17/MiG-27. **M**.
- `dive_angle` (0, 60), **B** per analogia NATO.
- `drag` low, `glide_ratio` None.

### FAB-250M54 (94 kg)
- Serie M-54: corpo tozzo, nata per la stiva dei bombardieri [F1]. È comunque caduta libera, quindi
  `drag` low (coefficiente balistico peggiore, vedi limite L3).
- quota **450**-12 000 m (§0.2 per il minimo, massimo come la FAB-500), velocità 500-1180 km/h,
  level/dive/loft, dive (0, 60). **B/M**: dato diretto non trovato, famiglia documentata.

### FAB-1500M54 (667 kg)
- quota fino a **16 000** m, velocità fino a **1200** km/h, *"testata fino a 12 500 m a 930 km/h"*
  [F15], **A** per i massimi. Si propone `max_altitude` **12 500**, il valore testato.
- `min_altitude` **850** m (§0.2), **B**. `min_speed` **500** km/h per analogia con la FAB-500,
  **B**.
- `modes`: **level, dive**, con dive (0, 30). Bomba pesante da bombardiere: in DCS è su Su-24M/Su-34.
  Una picchiata ripida con 1,5 t non è realistica. **B**.
- `drag` low.

### FAB-100 (39 kg) / FAB-50 (20 kg)
Nessun dato d'impiego trovato: le fonti riportano solo masse e dimensioni.
- FAB-100: 330-12 000 m, 500-1150 km/h, level/dive/loft, dive (0, 60), drag low. **B**.
- FAB-50: 270-8000 m, 400-1000 km/h, level/dive, dive (0, 60), drag low. **B**. È un modello
  d'epoca (anni '50 nel registro), per cui sono stati ridotti il tetto e la velocità massima.

### BetAB-500 (perforante antipista; carica reale ~76 kg, vedi anomalia A2)
- L'unica fonte trovata [F16] dà **30-5000 m, 600-1000 km/h**. Il minimo di 30 m **non è
  credibile** per una bomba non frenata da 500 kg: sembra confuso con la BetAB-500ShP
  (paracadute + razzo, 170-1000 m, 700-1100 km/h, livellato o picchiata ≤ 30° [F17]).
- Proposta: level e dive, `min_altitude` **400** m (§0.2, carica 76 kg), `max_altitude` **5000** m
  [F16], velocità **600-1000** km/h [F16], dive **(0, 60)**. Per perforare conviene un impatto
  ripido. Drag low.
- Confidenza **B** su tutto.

---

## 4. Bombe a grappolo e dispenser

### Mk-20 Rockeye (CBU-99/100, 247 submunizioni Mk-118)
- Spoletta a tempo Mk-339: apertura **1,2 s** dopo lo sgancio (primaria) oppure **4,0 s**
  (opzione) [F18], **A**. Con l'apertura a 1,2 s quasi tutta la caduta è delle submunizioni, quindi
  `drag` **high**.
- `min_altitude` **150** m, **B**. Serve tempo per l'apertura, la dispersione e l'armamento delle
  submunizioni. È più alto delle frenate (60 m), più basso delle Mk-82 LD (450 m).
- `max_altitude` **3000** m, **B/M**. Nella Guerra del Golfo gli sganci da media quota ne hanno
  degradato molto l'efficacia (rosa e inesplosi).
- velocità **370-1110** km/h, come la famiglia Mk-80, **B**.
- `modes`: level, dive, con dive (0, 45), **B**.

### CBU-52B (SUU-30, 220 submunizioni BLU-61)
- Stesso tipo di spoletta, Mk-339 o di prossimità [F19].
- Proposta: level e dive, **300-3000** m, 370-1110 km/h, dive (0, 45), drag high. **B**. Il minimo è
  più alto del Rockeye perché le BLU-61 sono sferette a frammentazione più pesanti (1,2 kg) e
  armate dalla rotazione.

### BLG66 Belouga (151 submunizioni frenate)
- Arma progettata per il **rilascio radente**: contenitore con paracadute, submunizioni frenate.
- Proposta: solo **level**, **60-500** m, **650-1020** km/h (350-550 kt), drag **high**.
- Confidenza **M** su 60 m e sulla finestra di velocità: valori noti in letteratura, ma non
  riverificati su una fonte aperta in questa sessione. **B** sul massimo di 500 m.

### BK-90MJ1 / BK-90MJ1-2 / BK-90MJ2 (DWS 39 Mjölner, planante, 72 submunizioni)
- Dispenser **planante** con navigazione inerziale e radaraltimetro [F20]. La fonte dà sgancio a
  bassa quota **50-500 m**, **Mach 0,6-0,9** (≈ 735-1100 km/h), gittata **~5-10 km**. La fonte è
  un'enciclopedia secondaria generata: **M/B**.
- Proposta, uguale per le tre varianti (cambiano solo le submunizioni): solo **level**, 50-500 m,
  735-1100 km/h, drag low.
- **`glide_ratio` non è adatto**: da 100 m percorre 7 km grazie all'energia cinetica, non alla
  planata. Un rapporto 70:1 sarebbe assurdo. Proposta: `glide_ratio: None` più un nuovo campo
  opzionale `standoff_range_km: (5, 10)` (decisione D3). **B** sul campo.

### RBK-250AO (RBK-250, 250 kg)
- Il registro non dice quale carico: "AO" fa pensare ad AO-1SCh (frammentazione), ma il registro
  ha una riga `Armored` (anomalia A3). Il dato trovato riguarda la **RBK-250 PTAB-2,5M**: livellato,
  picchiata e cabrata, **250-15 000 m**, fino a **1400** km/h [F21], **M**.
- Proposta: level/dive/loft, `min_altitude` 250, `max_altitude` **5000** (vedi §0.4 e il RBK-500
  qui sotto: 15 000 m è il limite d'impiego sicuro, non di efficacia), 500-1400 km/h, dive (0, 30)
  come la RBK-500. **M/B**.
- `drag`: **low**, **B**. Le RBK si aprono a tempo o a quota prefissata, non subito dopo lo
  sgancio: una parte importante della caduta è quella del contenitore intero.

### RBK-500AO (RBK-500 AO-2,5RT/RTM)
- **Da 300 m in su, 500-2300 km/h, picchiata e cabrata fino a 30°** [F4], **A**. Una seconda fonte
  dà **400-5000 m, 500-1900 km/h** [F22].
- Proposta: level/dive/loft, **300-5000** m, **500-2300** km/h (limite dell'arma, intersecato poi
  con il loadout), dive **(0, 30)**, drag low (come RBK-250). **A/M**.

### RBK-500PTAB (RBK-500 PTAB-1M, 268 submunizioni)
- **Da almeno 300 m, 500-2300 km/h, picchiata e cabrata fino a 30°** [F23], **A**. Il massimo non è
  documentato: 5000 m per analogia con l'AO, **B**.
- Proposta: level/dive/loft, 300-5000 m, 500-2300 km/h, dive (0, 30), drag low.

### KGBU-2AO / KGBU-2PTAB / KGBU-96r → **ipotesi: KMGU-2**
- Nessuna arma reale si chiama "KGBU". L'ipotesi più solida è il **KMGU-2**, il contenitore
  universale per piccoli carichi con blocchi BKF. In DCS esiste come "KMGU-2 - 96 x AO-2.5RT" e
  "KMGU-2 - 96 x PTAB-2.5KO": "96r" sembra derivare da "96 x AO-2.5**R**T". **KGBU-96r sarebbe
  quindi un doppione di KGBU-2AO** (anomalia A4).
- Il KMGU **resta sull'aereo** ed espelle i blocchi BKF a intervalli [F5]. Non è una bomba che cade.
- Dati [F5], **A** sul KMGU: quota di sgancio **30-1000 m**, velocità **500-1100** km/h. Peso
  carico **525 kg**, contro i 250 kg "??" del registro (anomalia A5).
- Proposta per le tre voci: solo **level**, 30-1000 m, 500-1100 km/h, drag **high**. Confidenza
  **A** sui numeri, **M** sull'identificazione.
- Impatto sul DES: la distanza di sgancio è di fatto **zero** (sorvolo del bersaglio). Il futuro
  `release_range` deve trattarla come una caduta frenata da bassissima quota, oppure con un flag
  `dispenser: True` (decisione D4).

---

## 5. Fonti

- [F1] ru.wikipedia, *ФАБ-500*: M-62 "570 — 12 000 м", "500 — 1 900 км/ч"; serie M-54 per la stiva,
  M-62 per il trasporto esterno. <https://ru.wikipedia.org/wiki/ФАБ-500>
- [F2] mass-destruction-weapon.blogspot.com, *ФАБ-500 M62*: "570 - 12000 м при скоростях
  500 - 1180 км/ч" (via ricerca). Rosoboronexport (roe.ru) scheda FAB-500 M-62: 570-12 000 m,
  500-1900 km/h (via estratto di ricerca, pagina non raggiungibile).
- [F3] GlobalSecurity, *Bombs for Beginners*: limiti di velocità FMU-54/FMU-139 per Mk-82 AIR/SE e
  Mk-84 AIR; "safe escape data … 450 KTAS and 600 KTAS". Via ricerca per Mk-82 AIR: "200 to 700
  knots", "low drag deliveries … 600 knots".
  <https://www.globalsecurity.org/military/systems/munitions/intro-bombs.htm>
- [F4] sovetarmy.forum2x2.ru, *РБК-500 АО-2,5РТМ*: "с высоты 300 м и более", "500-2300 км/ч",
  "пикирования и кабрирования под углами до 30 град." <https://sovetarmy.forum2x2.ru/t219-topic>
- [F5] ru.wikipedia, *КМГУ*: "высота сброса 0,03-1 км", "скорость сброса 500 - 1100 км/ч", massa
  carica 525 kg. <https://ru.wikipedia.org/wiki/КМГУ>
- [F6] en.wikipedia, *GBU-16 Paveway II* / *GBU-12 Paveway II* (gittata ~14,8 km; impiego da media
  quota). <https://en.wikipedia.org/wiki/GBU-16_Paveway_II>
- [F7] GlobalSecurity, *GBU-12 Paveway II*.
  <https://www.globalsecurity.org/military/systems/munitions/gbu-12.htm>
- [F8] FAS / GlobalSecurity, *GBU-24 Paveway III*: "low-level, standoff capability of more than 10
  nautical miles", "larger delivery envelope for the dive, glide and loft modes", "primary delivery
  mode (low-altitude level delivery)". <https://man.fas.org/dod-101/sys/smart/gbu-24.htm>
- [F9] designation-systems.net, *Raytheon Paveway III*: ~30 km da 10 000 m; >18 km a bassa quota.
  <https://www.designation-systems.net/dusrm/app5/paveway-3.html>
- [F10] ru.wikipedia, *КАБ-500*: CEP, distanza minima di lancio "не менее 2-9 км". Tetto 10 km della
  Kr-E (via ricerca). <https://ru.wikipedia.org/wiki/КАБ-500>
- [F11] National Museum of the USAF, *MK82 Air Inflatable Retarder Bomb*.
  <https://www.nationalmuseum.af.mil/Visit/Museum-Exhibits/Fact-Sheets/Display/Article/197591/mk82-air-inflatable-retarder-bomb/>
- [F12] METIS, *SAMP Type 25*. <https://metis.fenixinsight.com/munition/bomb/samp-type-25>
- [F13] War Thunder wiki, *M/71 (120 kg)*: configurazioni high/low drag. Solo riscontro, fonte di
  gioco. <https://old-wiki.warthunder.com/M/71_(120_kg)>
- [F14] en.wikipedia, *KAB-500L*: "altitude from 500 metres to 5000 metres … airspeed of 500–1150
  km/h". <https://en.wikipedia.org/wiki/KAB-500L>
- [F15] sovetarmy.forum2x2.ru, *ФАБ-1500М-54*: "с высот до 16 000 м при скорости полета до 1200
  км/час (испытана до высоты 12 500 м при скорости 930 км/час)".
  <https://sovetarmy.forum2x2.ru/t234-topic>
- [F16] бетонобойная.рф, *БЕТАБ-500*: "30-5000 м", "600-1000 км/ч".
  <https://xn--b1agacl3aeas4a.xn--p1ai/armament/betab-500/>
- [F17] airwar.ru, *БЕТАБ-500ШП* (via ricerca): 170-1000 m, 700-1100 km/h, picchiata ≤ 30°.
  <https://airwar.ru/weapon/ab/betab-500shp.html>
- [F18] GlobalSecurity, *MK-20 Rockeye* e ricerca: Mk-339 "1.2 seconds", opzione "4.0 seconds".
  <https://www.globalsecurity.org/military/systems/munitions/mk20.htm>
- [F19] GlobalSecurity, *CBU-52*: SUU-30, 220 BLU-61, spolette Mk-339 o di prossimità.
  <https://www.globalsecurity.org/military/systems/munitions/cbu-52.htm>
- [F20] Grokipedia, *Bombkapsel 90* (50-500 m, M 0,6-0,9, ~7 km). Fonte secondaria generata, da
  verificare. en.wikipedia conferma solo "gliding stand-off submunitions dispenser", 72
  submunizioni. <https://en.wikipedia.org/wiki/Bombkapsel_90>
- [F21] mass-destruction-weapon.blogspot.com, *РБК-250 ПТАБ-2,5М*: "с высот от 250 м до 15 000 м
  при скорости бомбометания до 1400 км/час" (via ricerca).
  <http://mass-destruction-weapon.blogspot.com/2021/04/250-25.html>
- [F22] svoboda.org, *РБК-500 АО-2,5РТ*: "400 - 5000 м", "500 - 1900 км/ч" (via ricerca).
  <https://www.svoboda.org/a/30076799.html>
- [F23] vistat.org / sovetarmy, *РБК-500 ПТАБ-1М*: "не менее 300 м", "500 - 2300 км/ч", "до 30
  градусов" (via ricerca). <https://vistat.org/objects/rbk-500-209>

Non consultabili in questa sessione (rete): armedman.ru, militaryrussia.ru, roe.ru, fsvts.gov.ru,
airbase.ru. Il PDF DTIC *MK 81 and MK 82 Bomb Release Curves* (AD0486328) e *Safe Arming Times
for MK 81…84 and M117 Low Drag Bombs* (AD860933) sono le fonti primarie giuste per le Mk-80, non
lette: sono il primo passo se si vuole alzare la confidenza delle quote minime NATO.

---

## 6. Tabella riassuntiva (da approvare)

Quote in m, velocità in km/h. Conf. = confidenza complessiva della riga (A/M/B).

| Arma | modes | min_alt | max_alt | min_spd | max_spd | dive_angle | drag | glide | Conf. |
|---|---|---|---|---|---|---|---|---|---|
| Mk-84 | level, dive, loft | 750 | 12000 | 370 | 1110 | (0, 60) | low | None | M |
| Mk-83 | level, dive, loft | 570 | 12000 | 370 | 1110 | (0, 60) | low | None | M |
| Mk-82 | level, dive, loft | 450 | 12000 | 370 | 1110 | (0, 60) | low | None | M |
| Mk-82AIR | level, dive | 60 | 1500 | 520 | 1300 | (0, 30) | high | None | M |
| GBU-10 | level, dive, loft | 750 | 10000 | 370 | 1110 | (0, 45) | low | None | M |
| GBU-16 | level, dive, loft | 570 | 10000 | 370 | 1110 | (0, 45) | low | None | M |
| GBU-12 | level, dive, loft | 450 | 10000 | 370 | 1110 | (0, 45) | low | None | M |
| GBU-24 | level, dive, loft | 60 | 12000 | 550 | 1110 | (0, 45) | low | 3.0 | M |
| GBU-27 | level, dive | 600 | 10000 | 370 | 1110 | (0, 45) | low | None | B |
| Mk-20 | level, dive | 150 | 3000 | 370 | 1110 | (0, 45) | high | None | B |
| BLG66 | level | 60 | 500 | 650 | 1020 | — | high | None | M |
| CBU-52B | level, dive | 300 | 3000 | 370 | 1110 | (0, 45) | high | None | B |
| BK-90MJ1 | level | 50 | 500 | 735 | 1100 | — | low | None (*) | M/B |
| BK-90MJ1-2 | level | 50 | 500 | 735 | 1100 | — | low | None (*) | M/B |
| BK-90MJ2 | level | 50 | 500 | 735 | 1100 | — | low | None (*) | M/B |
| M/71 | level, dive | 50 | 1500 | 500 | 1100 | (0, 30) | high | None | B |
| SAMP-400LD | level, dive, loft | 570 | 12000 | 370 | 1110 | (0, 60) | low | None | B |
| SAMP-250HD | level, dive | 60 | 1500 | 520 | 1100 | (0, 30) | high | None | B |
| FAB-1500M54 | level, dive | 850 | 12500 | 500 | 1200 | (0, 30) | low | None | M |
| FAB-500M62 | level, dive, loft | 570 | 12000 | 500 | 1180 | (0, 60) | low | None | A |
| FAB-250M54 | level, dive, loft | 450 | 12000 | 500 | 1180 | (0, 60) | low | None | B/M |
| FAB-100 | level, dive, loft | 330 | 12000 | 500 | 1150 | (0, 60) | low | None | B |
| FAB-50 | level, dive | 270 | 8000 | 400 | 1000 | (0, 60) | low | None | B |
| RBK-250AO | level, dive, loft | 250 | 5000 | 500 | 1400 | (0, 30) | low | None | M/B |
| RBK-500AO | level, dive, loft | 300 | 5000 | 500 | 2300 | (0, 30) | low | None | A/M |
| RBK-500PTAB | level, dive, loft | 300 | 5000 | 500 | 2300 | (0, 30) | low | None | A/M |
| BetAB-500 | level, dive | 400 | 5000 | 600 | 1000 | (0, 60) | low | None | B |
| KAB-500L | level, dive | 500 | 5000 | 500 | 1150 | (0, 50) | low | None | M/A |
| KAB-500Kr | level, dive | 500 | 5000 | 500 | 1150 | (0, 50) | low | None | M |
| KGBU-2AO | level | 30 | 1000 | 500 | 1100 | — | high | None | A/M |
| KGBU-2PTAB | level | 30 | 1000 | 500 | 1100 | — | high | None | A/M |
| KGBU-96r | level | 30 | 1000 | 500 | 1100 | — | high | None | A/M |

(*) più il campo opzionale proposto `standoff_range_km: (5, 10)`, decisione D3.

Conteggio per confidenza di riga: **A** 1 (FAB-500M62); **A/M** 5 (RBK-500AO, RBK-500PTAB e i tre
KMGU); **M** 12 (Mk-84, Mk-83, Mk-82, Mk-82AIR, GBU-10, GBU-16, GBU-12, GBU-24, BLG66, FAB-1500M54,
KAB-500L, KAB-500Kr); **B** o **M/B** 14 (GBU-27, Mk-20, CBU-52B, i tre BK-90, M/71, SAMP-400LD,
SAMP-250HD, FAB-250M54, FAB-100, FAB-50, RBK-250AO, BetAB-500). Totale 32.
Nessuna riga è interamente **A**. Anche le migliori hanno almeno un campo stimato: tipicamente
`dive_angle` e `modes`.

---

## 7. Anomalie trovate nel registro (fuori scope, da non correggere ora)

- **A1** GBU-27 `warhead: 429`: è il valore della Mk-84. La GBU-27 usa la BLU-109, con ~240 kg di
  esplosivo. Anche la GBU-24 ha 429 (vero se su Mk-84, non se su BLU-109).
- **A2** BetAB-500 `warhead: 92`, `cost: 2.7`: identici alla Mk-82/SAMP-250, probabile copia-incolla.
  La BetAB-500 reale pesa ~477 kg con ~76 kg di esplosivo.
- **A3** RBK-250AO: il nome indica la frammentazione (AO), ma la voce ha una riga `Armored`. I dati
  d'impiego trovati sono per la RBK-250 PTAB-2,5M (anticarro).
- **A4** "KGBU-*" non esiste come designazione reale. È quasi certamente il **KMGU-2**, e KGBU-96r
  sembra un doppione di KGBU-2AO (commento "?? VERIFY" già presente).
- **A5** KGBU-* `weight: 250  # ??`: il KMGU-2 carico pesa 525 kg [F5].
- **A6** M/71 e i SAMP: DCS e la realtà hanno varianti LD e HD separate. Il registro ne ha una sola
  per la M/71 e una per peso per i SAMP (SAMP-400 solo LD, SAMP-250 solo HD).
- **A7** Mk-20 commentata "aka CBU-100": corretto (CBU-99/100 = Rockeye con spolette diverse).

## 8. Limiti noti della proposta

- **L1** Nessun manuale d'impiego primario (serie -34, AFTTP 3-3, manuali sovietici d'impiego) è
  stato letto. Le quote minime NATO sono dedotte da una legge di scala ancorata a un dato russo
  (§0.2).
- **L2** La quota minima reale dipende dalla **spoletta** (istantanea o ritardata), che il registro
  non modella. Con la spoletta ritardata il minimo delle LD scende molto. Il valore proposto vale per
  la spoletta istantanea, cioè il caso peggiore.
- **L3** `drag` binario non distingue il coefficiente balistico: una M-54 tozza e una M-62
  affusolata risultano entrambe `low`. Per la balistica minima del §2.4 della proposta B basta.
- **L4** Per le armi a sgancio distanziato (GBU-24, BK-90) `min_altitude` non esprime il vincolo
  vero, che è una **distanza minima** di lancio (KAB: 2-9 km [F10]). Il DES ha già il limite
  dichiarato "la sfera non ha una distanza minima" (proposta B §2.5).
- **L5** Le coppie quota/velocità non sono indipendenti (ad esempio: Mk-82AIR a 60 m solo sopra
  ~450 kt). Lo schema proposto è rettangolare e quindi un po' permissivo.

## 9. Decisioni richieste all'utente

- **D1** Approvare la tabella §6 (anche per righe: si può approvare solo il sottoinsieme A/M e
  lasciare le B come stime marcate).
- **D2** Armi con doppia modalità LD/HD (Mk-82AIR, M/71, SAMP): una voce con un solo `drag` (proposta
  attuale: il profilo frenato) oppure `drag: 'selectable'` con due finestre?
- **D3** BK-90: introdurre `standoff_range_km` opzionale, oppure spostare le BK-90 fra le armi con
  `range` (come gli ASM)?
- **D4** KMGU ("KGBU-*"): flag `dispenser: True` con distanza di sgancio nulla, e chiarimento di
  KGBU-96r (doppione da eliminare?).
- **D5** Correggere le anomalie A1-A5 in un intervento separato, prima o dopo l'inserimento di
  `release`?
