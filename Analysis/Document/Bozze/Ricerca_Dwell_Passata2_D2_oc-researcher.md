# Ricerca dwell — Passata 2, Lotto D2 (SAM a ricerca rotante, valori discordanti)

> Bozza di ricerca (`oc-researcher`). Oggetto: periodo di rivisita (`dwell_time_s`) del radar di **ricerca** di
> 4 sistemi SAM: 9K37 Buk, 2K12 Kub, 9K331 Tor, S-300PS. Complemento di
> `Analysis/Document/Ricerca_Dwell_Sensori_2026_11_06.md` (Passata 1).
> Data: 2026-11-08. Stato: **completa** (sintesi e lacune in fondo).
>
> **D = valore derivato** con calcolo mostrato (non dichiarato dalla fonte). **M = una fonte secondaria seria.**
> **A = fonte tecnica primaria o due fonti secondarie indipendenti concordi.** **B = stima/forum/gioco/mirror.**
> `[S]` = mia stima ragionata, mai un dato. "non trovato" = cercato e non reperito (esito valido).

## 0. Varianti cercate nei registri

Nomi letti con `grep -n` e `sed -n` in `Code/Dynamic_War_Manager/Source/Asset/Vehicle_Data.py`; chiave `radar`.

| Voce registro | `model` registro | Variante cercata sul web | Anni/utenti registro |
|---|---|---|---|
| `9K37-Buk` | `9S35 Fire Dome` (tracking); `acquisition_range` 85 km | Radar di ricerca **9S18 / 9S18M1 «Kupol» / «Snow Drift»** (9S18 base = «Tube Arm») | 1979; Russia, Ucraina, Bielorussia, Egitto, Siria… |
| `2K12-Kub` | `1S91 Straight Flush` | Antenna di ricerca **1S11** e antenna di inseguimento/illuminazione **1S31** del 1S91 | 1967; USSR, Russia, Siria, Egitto, India… |
| `9K331-Tor` | `Multifunction 3D Radar` | Radar di acquisizione 3D del Tor (nome NATO collettivo **«Scrum Half»** per TAR+TTR); TAR del 9K331 Tor-M1 | 1986; Russia, Grecia, Cipro, Egitto, Iran… |
| `S-300PS` | `30N6 Flap Lid` (ingaggio); `acquisition_range` 150 km | Radar di ricerca **5N64S «Big Bird B»**; ricerca a bassa quota **76N6 «Clam Shell»**; confronto **64N6/64N6E** (S-300PM) | 1982; Russia, Bielorussia, Slovacchia, Bulgaria… |

## 1. Tabella riassuntiva

| Voce | Radar di ricerca (variante cercata) | Tipo di scansione | rpm / periodo (estremi) | Regime normale? | Applicabilità | Rispetto alla Passata 1 | Conf. |
|---|---|---|---|---|---|---|---|
| **9K37 Buk** | 9S18M1 «Kupol»/«Snow Drift» | Rotazione meccanica in azimut + fascio elettronico in elevazione; 360° o settore 30°/90–120° | 9S18: **settore 30° = 2,5–4,5 s**; **circolare = 4,5–18 s**. 9S18M1-3: **settore 30° = 2,5 s**; **circolare = 4,5 s**; tabella «Review period, s: 4; five; 6; 9, -6» (cella sporca, vedere §2.1) | Sì, dipende dal settore e dal disturbo (non un unico regime) | **A** (circolare) / **B** (settore) | **CONFERMA** i valori della Passata 1 (GlobalSecurity ora letto direttamente) e **AGGIUNGE** la variante 9S18M1-3 | **M** |
| **2K12 Kub** | **1S11** (ricerca) del 1S91 | Parabola rettangolare rotante in azimut 360°; 1S31 separata per inseguimento/illuminazione | **15 o 20 min⁻¹ → 4 s o 3 s** (D) | Non indicato | **A** (1S11) / **C** (1S31) | **CONFERMA** 15/20 rpm; **AGGIUNGE** la lettura diretta (HTML: il valore è nella colonna 1S11, 1S31 vuota) | **M** |
| **9K331 Tor** | TAR 3D del Tor («Scrum Half» collettivo) | **Settore**, fascio elettronico in elevazione (32°), antenna orientabile meccanicamente di 32°; **non** 360° | **intervallo di scansione 1 s** (modo a 3 fasci); **intera zona di elevazione 32° in 3 s** | Sì: 3 s è il programma normale, 1 s il modo a 3 fasci | **B** (settore/fascio elettronico), non 60/rpm | **CONFERMA** il valore 1 s ma **ne cambia il significato**; **CONTRADDICE** l'attribuzione «9S18» della Passata 1 (il 9S18 è del Buk) | **A** |
| **S-300PS** | **5N64S «Big Bird B»**; **76N6 «Clam Shell»** (bassa quota); 30N6 = ingaggio | 5N64S: array bifacciale + rotazione meccanica in azimut. 76N6: rotazione meccanica 360°. 30N6: array a fascio elettronico su torretta | **5N64S: non trovato**. **76N6: 20 rpm → 3 s** (D). **64N6/64N6E (solo confronto): rotazione ogni 12 s → 5 rpm**, settore di inseguimento 6/12 s | 76N6: n/a (valore unico); 64N6E: sì, 12 s è il «regular» | **A** (76N6); **B** (30N6, non 60/rpm); **—** (5N64S) | **AGGIUNGE** il 76N6 a 20 rpm; **CONFERMA** il 12 s del 64N6E; il **5N64S resta non trovato** | **A** (76N6); **M** (64N6E); **—** (5N64S) |

**Sintesi in una riga.** Tre sistemi su quattro hanno ora un valore utilizzabile e con significato chiarito (Buk:
4,5–18 s circolare; Kub: 3–4 s; Tor: 3 s di settore, non 60/rpm); per l'S-300PS il radar principale 5N64S resta
**non trovato**, ma il suo radar di ricerca a bassa quota 76N6 ha un dato di fabbrica **20 rpm → 3 s**.

## 2. Voci

### 2.1 9K37 Buk — radar di ricerca 9S18 / 9S18M1 «Kupol» / «Snow Drift»

**Voce cercata:** `9K37-Buk`, `model` = `9S35 Fire Dome` (inseguimento), `acquisition_range` = 85 km.
**Trovato:** il radar di ricerca è il **9S18M1** (nome NATO «Snow Drift»); il 9S35 «Fire Dome» è il radar di
ingaggio e **non** è un radar di ricerca (per l'inseguimento il dwell non si applica).

**Valori (GlobalSecurity, pagina 9S18 «Kupol» / «Tube Arm», letta direttamente):**
- 9S18: «for a sector review of 30° - 2.5..4.5 s, for a circular one - 4.5..18 s»
- 9S18M1-3: «for a sector survey of 30° - 2.5 s, for a circular sector - 4.5 s»
- Tabella 9S18M1-3, cella «Review period, s»: il sorgente HTML contiene letteralmente **«4; five; 6; 9, -6»**
  (probabile resa di «4; 5; 6; 9,6»). È una cella sporca: **non la uso come valore**, la cito solo come indizio.

URL: https://www.globalsecurity.org/military/world/russia/9s18.htm
Estratti letterali: «for a sector review of 30° - 2.5..4.5 s, for a circular one - 4.5..18 s»;
«for a sector survey of 30° - 2.5 s, for a circular sector - 4.5 s».
Confidenza: **M** (una fonte secondaria seria, letta direttamente; il dato aggrega più varianti).
Tipo: **F** per i periodi; **D** per gli rpm equivalenti: 60/4,5 = **13,3 rpm** (circolare veloce),
60/18 = **3,3 rpm** (circolare lento), 60/2,5 = **24 rpm** (settore veloce).

**Nota di variante.** Il registro è del 1979 (9K37 base, 9S18 «Tube Arm»). I valori 2,5 s / 4,5 s sono della
variante **9S18M1-3** (Buk-M2E); il 9S18 base ha gli intervalli 2,5–4,5 s (settore) e 4,5–18 s (circolare).
La Passata 1 riportava anche 3–14 rpm da una scheda del 9S18M «Kupol-M» e 6,7/10/18 rpm da un forum: il dato
GlobalSecurity (2,5–18 s) è più solido ma non coincide esattamente con quegli rpm.

Rispetto alla Passata 1: **CONFERMA** i valori (che nella Passata 1 erano da snippet) e **AGGIUNGE** la
variante 9S18M1-3.

### 2.2 2K12 Kub — 1S91: quale antenna ruota?

**Voce cercata:** `2K12-Kub`, `model` = `1S91 Straight Flush`.
**Trovato (radartutorial, pagina letta direttamente, anche in HTML):** il 1S91 porta **due antenne indipendenti**:
- **1S11** («Surveillance radar»): parabola rettangolare sul tetto; «The search radar can be moved independently
  of the target tracking radar.»
- **1S31** («Target tracking radar»): parabola circolare per inseguimento fine e illuminazione; «The entire antenna
  unit can be rotated horizontally 360° independently of the search radar.»

La tabella ha due colonne, `1S11` e `1S31`. Nel sorgente HTML la riga «antenna rotation» vale
**«15 or 20 min-1»** nella cella **1S11**; la cella **1S31** è **vuota**. Quindi è la **1S11 (ricerca)** che ruota
a 15 o 20 giri/min. La 1S31 è l'antenna di inseguimento/illuminazione (dwell non applicabile).

URL: https://www.radartutorial.eu/19.kartei/06.missile/en/karte011.en.html
Estratti letterali: «antenna rotation: 15 or 20 min-1»; «The search radar can be moved independently of the target
tracking radar.»; «The entire antenna unit can be rotated horizontally 360° independently of the search radar.»
Confidenza: **M** (scheda tecnica secondaria seria; la struttura HTML risolve l'ambiguità della colonna).
Tipo: **F** (rpm), **D** (periodo): 60/15 = **4 s**; 60/20 = **3 s**.

Rispetto alla Passata 1: **CONFERMA** 15/20 rpm e **AGGIUNGE** la certezza che il valore è della 1S11 (non della
1S31) e la lettura diretta della scheda (non più tramite armsnet).

### 2.3 9K331 Tor — radar di acquisizione 3D («Scrum Half»)

**Voce cercata:** `9K331-Tor`, `model` = `Multifunction 3D Radar`.
**Trovato:** il radar di scoperta/acquisizione del Tor è un radar 3D in banda E/F, con **scansione elettronica in
elevazione** e antenna stabilizzata; **non è il 9S18** (che è del Buk). «Scrum Half» è il nome NATO **collettivo**
del pacchetto radar (TAR + TTR): «Together these radars carry the NATO reporting name "Scrum Half".» (Wikipedia,
letta) e «Tor-M1's target acquisition, and target engagement/missile tracking radars bear collective NATO
designation» (GlobalSecurity, letta). La Passata 1 attribuiva al Tor un «9S18 Scrum Half»: **è un errore di nome**.

**Valori da Air Power Australia (Kopp 2009-2012), che cita Drize & Luzan, Military Parade 1996:**
- «The scanning interval is 1 s, the beam flare (width) in the vertical plane is 4 deg»
- «The entire elevation zone covers 32 deg and can be scanned within 3 s.»
- «the antenna system of the radar can be revolved mechanically through 32 deg with a detection zone of 32 to 64 deg»
URL: https://www.ausairpower.net/APA-9K331-Tor.html

**Conferma indipendente da GlobalSecurity (pagina «Scrum Half», letta):**
- «In the main mode, the scanning speed of the detection zone is three seconds, while the lower part of the zone
  is scanned twice. Additionally, there is a three-beam viewing mode with a pace of 1 second.»
URL: https://www.globalsecurity.org/military/world/russia/scrum-half.htm
Estratti: «the scanning speed of the detection zone is three seconds»; «three-beam viewing mode with a pace of
1 second»; «The scanning interval is 1 s».
Confidenza: **A** (due fonti concordi; APA cita una pubblicazione industriale).

**Applicabilità:** **B** (scansione di settore/fascio elettronico). Il valore **1 s** è l'intervallo del modo a
3 fasci; il **3 s** è il tempo per l'intera zona di elevazione di 32°. **Non** è un periodo di rotazione 360° e
**non** va usato come 60/rpm: il TAR illumina un settore di 32° in azimut (Wikipedia: «with a 32 degree sector
view»), non l'orizzonte intero. L'inseguimento (TTR a PESA) è **C**, non applicabile.

Rispetto alla Passata 1: **CONFERMA** il valore «1 s» (che era da un riassunto Army Recognition su documenti
trapelati), ma **ne corregge il significato** (intervallo di scansione a 3 fasci, non giro d'antenna) e
**CONTRADDICE** l'attribuzione «9S18 Scrum Half».

### 2.4 S-300PS — 5N64S «Big Bird B» e 76N6 «Clam Shell»

**Voce cercata:** `S-300PS`, `model` = `30N6 Flap Lid`; `acquisition_range` = 150 km.
**Trovato:** il 30N6 è il radar di ingaggio/illuminazione (array a fascio elettronico su torretta): per esso il
dwell **non** è 60/rpm (categoria B; periodo di rivisita non trovato). La ricerca dell'S-300PS è il **5N64S
«Big Bird B»** (a livello di brigata/comando, non sempre di batteria); il **64N6/64N6E «Tombstone»** è il radar
dell'S-300PM, riportato **solo come confronto**. L'S-300PS di batteria ha inoltre il **76N6 «Clam Shell»** come
ricerca a bassa quota.

**5N64S:** architettura confermata (array bifacciale a scansione elettronica + rotazione meccanica in azimut):
- uk.wikipedia «С-300ПТ», letta: «антенний пост з антеною ФАР який обертається по азимуту (по колу)»
  («posto d'antenna con antenna a schieramento di fase che ruota in azimut, lungo il cerchio»).
- Air Power Australia, letta: «Early variants of the 5N64/64N6 BIG BIRD family of phased array acquisition
  radars were introduced as battle management radars … used with S-300PT and PS batteries.»
URL: https://uk.wikipedia.org/wiki/С-300ПТ ; https://www.ausairpower.net/APA-Rus-SAM-Site-Configs-B.html
**Periodo di rotazione o rpm: non trovato** (GlobalSecurity, APA, valka.cz, uk.wikipedia e ru.wikipedia letti non
lo riportano). → §5.

**76N6 «Clam Shell» (ricerca a bassa quota, dato di fabbrica LEMZ):** la tabella «Specifications (LEMZ)» riporta
- «Antenna head rotation rate [RPM] … 20» e «Data output rate … 3» (s);
- «Horizontal scan through through 360 degrees is achieved by antenna head rotation» (sic, «through through» nel
  testo).
URL: https://ausairpower.net/clamshell.html (Technical Report APA-TR-2004-1001, che riporta la brochure LEMZ 1994)
Estratti letterali: «Antenna head rotation rate [RPM] 20»; «Data output rate 3»; «Horizontal scan through through
360 degrees is achieved by antenna head rotation».
Confidenza: **A** (fonte di fabbrica citata; il periodo 3 s è coerente con 60/20 = 3 s, D).
Rispetto alla Passata 1: **AGGIUNGE** (la Passata 1 non aveva il 76N6).

**64N6/64N6E (solo confronto, NON attribuire all'S-300PS):**
- GlobalSecurity, pagina «64N6 / 91N6E TOMBSTONE / Big Bird», letta: «Its 3-D performance is obtained by rotation
  of the antenna once every 12 seconds and electronically scanning the antenna beam, in both azimuth and elevation.»
  URL: https://www.globalsecurity.org/military/world/russia/tombstone.htm
  Estratto: «rotation of the antenna once every 12 seconds». Valore **12 s → 5 rpm** (D). Confidenza **M**.
- Air Power Australia, letta: tabella 64N6E «Период обзора, с - регулярный обзор 12 - сопровождение целей 6/12».
  Confidenza **M**.
- valka.cz/armedconflicts (scheda 64N6E, letta): «štandartný režim - 12 s (5 ot/min) - sledovanie cieľov -
  6/12 s (10/5 ot/min)». Confidenza **B/M** (sito enciclopedico non primario).
Rispetto alla Passata 1: **CONFERMA** il 12 s del 64N6E, con citazione diretta (prima era da ricerca).

## 3. Discordanze fra fonti

- **Buk — regime «normale»**: la Passata 1 dava 3–14 rpm (scheda 9S18M «Kupol-M») e 6,7/10/18 rpm (forum
  army.ca). GlobalSecurity dà periodi 2,5–4,5 s (settore) e 4,5–18 s (circolare) per il 9S18, e 2,5/4,5 s per il
  9S18M1-3. Le famiglie non coincidono: 4,5 s ↔ 13,3 rpm; 18 s ↔ 3,3 rpm. Il «3–14 rpm» è compatibile solo in
  parte. **Non scelgo**: riporto entrambe; la fonte letta direttamente (GlobalSecurity) è la più solida.
- **Kub — quale antenna**: risolto. La tabella radartutorial mette 15/20 min⁻¹ nella colonna **1S11** e lascia
  vuota la 1S31. La Passata 1 aveva il dubbio perché leggeva la pagina attraverso un riassunto; il sorgente HTML
  lo chiarisce.
- **Tor — «1 s»**: la Passata 1 lo trattava come «tempo di scansione = 1 s → 60 rpm». Le fonti (APA, GlobalSecurity)
  dicono che è l'intervallo di un modo a 3 fasci e che la zona intera di elevazione richiede 3 s: **non è un giro
  d'antenna**. Usabile solo come periodo di aggiornamento della zona di scoperta (categoria B).
- **Tor — nome**: la Passata 1 chiamava il radar «9S18 Scrum Half». «9S18» è il radar del Buk; «Scrum Half» è il
  nome collettivo del pacchetto radar del Tor. **Contraddizione respinta.**
- **S-300PS**: 30N6 non è ricerca; il 5N64S non ha un periodo trovato. Il **64N6E (12 s / 5 rpm)** è del sistema
  successivo (S-300PM) e **non** va attribuito all'S-300PS.

## 4. Analoghi candidati [S]

Solo suggerimenti, **non dati**. La scelta finale è dell'utente.

- **5N64S ← 64N6/64N6E (12 s / 5 rpm) [S].** Stessa famiglia NIIIP «Big Bird», stesso principio (array bifacciale
  a scansione elettronica + rotazione meccanica in azimut). Il 5N64S è più vecchio e con array probabilmente
  diverso; 12 s è un ordine di grandezza plausibile, non un valore del 5N64S.
- **Tor-M2 ← Tor-M1 (1 s / 3 s) [S].** Kopp descrive per il Tor-M2 «a new planar array surveillance radar» che
  «retaining the range performance of the legacy system»; il programma di scansione può essere cambiato. I valori
  Tor-M1 non sono automaticamente quelli del Tor-M2.
- **9S18M1 (Buk-M1, 1984) ← 9S18 base (4,5–18 s circolare) [S].** Il passaggio all'antenna piatta (9S18M1) può
  aver cambiato la velocità; il dato GlobalSecurity per la M1-3 (4,5 s) suggerisce un aggiornamento più veloce.

## 5. Cosa non ho trovato / non ho potuto verificare

- **5N64S «Big Bird B»**: periodo di rotazione o rpm di fonte. Non nelle pagine GlobalSecurity, APA, valka.cz,
  uk.wikipedia e ru.wikipedia lette. Resta il buco principale dell'S-300PS.
- **Buk**: un unico «regime normale» dichiarato; la tabella 9S18M1-3 è in traduzione sporca («4; five; 6;
  9, -6»): i valori esatti della tabella non sono verificabili con sicurezza.
- **Kub**: la scheda non dice che la 1S11 ruoti a 15/20 rpm *in modo di ricerca* (lo si deduce dalla colonna);
  non ci sono due fonti indipendenti sullo stesso numero.
- **Tor**: distinzione Tor base / Tor-M1 / Tor-M2 sul periodo. I valori 1 s/3 s sono del **Tor-M1**; per il Tor
  base e per il Tor-M2 **non trovato**.
- **S-300PS**: periodo di rivisita del 30N6 (array a settore, non applicabile come rpm) **non trovato**; settore
  del 30N6 non ricercato a fondo (la Passata 1 dava 60°/100°, fonte secondaria).
- **Pagine non leggibili / non raggiunte**: radartutorial karte093 (9S18M) → **404** (supplito da GlobalSecurity);
  web.archive.org → **429**; zhihu → **403**; rbase.new-factoria.ru → errore di trasporto; FAS (le due URL
  provate) → **404**; ODIN → errore di trasporto. **Non** ho ricostruito testo che non ho letto.
- **Non** ho consultato manuali tecnici primari né Jane's.

## 6. Metodo

- **Strumenti**: `websearch` non disponibile; usato `webfetch`. Scoperta degli URL con
  `https://html.duckduckgo.com/html/?q=…`; Bing provato
  una volta e ha restituito risultati non pertinenti, quindi abbandonato. Nessun dato preso dalle pagine di
  risultati: solo URL.
- **Pagine di contenuto lette** (16): GlobalSecurity 9S18; GlobalSecurity 64N6/Tombstone; GlobalSecurity
  Scrum Half; radartutorial 1S91 (testo e HTML); radartutorial 76N6; Air Power Australia Acquisition-GCI;
  APA-9K331-Tor; APA Clam Shell; APA Rus-SAM-Site-Configs-B; Wikipedia Tor; Wikipedia (uk) С-300ПТ; Wikipedia
  (ru) С-300; valka.cz/armedconflicts 5N64/64N6; 1stvsc 1S91; cmano-db (solo per verifica, nessun rpm).
- **Pagine tentate e fallite**: radartutorial karte093 (404), radartutorial.de (errore di trasporto), ODIN
  (trasporto), web.archive.org (429 ×2), zhihu (403), rbase (trasporto), FAS (404 ×2), GlobalSecurity
  big-bird.htm e s-300ps.htm (404), APA-76N6 (404).
- **Passi usati**: **circa 60** chiamate di strumento (limite 80). La ricerca è stata chiusa quando il 5N64S non
  ha dato risultati dopo diversi tentativi diversi (GlobalSecurity, APA, valka, wiki uk/ru, thread, rbase, FAS).

**Riepilogo per la decisione.** (i) Buk: usare 4,5 s (circolare veloce, 13,3 rpm) oppure l'intervallo 4,5–18 s;
(ii) Kub: 3 s (20 rpm) o 4 s (15 rpm) per la 1S11, l'unica antenna di ricerca; (iii) Tor: usare 3 s come
aggiornamento della zona di scoperta (categoria B), non 60/rpm; (iv) S-300PS: il 5N64S non ha dato un periodo,
mentre il 76N6 dà 3 s (20 rpm) e il 64N6E 12 s (5 rpm, solo confronto). Il 30N6 non è un radar di ricerca.