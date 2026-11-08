# Ricerca dwell — Passata 2, lotto D3 (navi e AWACS) — oc-researcher

> Bozza di ricerca. Unico file scritto: questo. Nessun codice, registro, piano o manuale toccato.
> Complemento di `Analysis/Document/Ricerca_Dwell_Sensori_2026_11_06.md` (letta con `grep -n`: sezioni 0, 3, 6, 7
> e tabella "Esito per classe"). Per ogni voce dico se il risultato **conferma**, **contraddice** o **aggiunge**
> rispetto a quella ricerca. `dwell_time_s` = periodo di rivisita = 60/rpm per rotazione meccanica 360° a velocità
> costante; **D** = derivato con calcolo mostrato; **[S]** = stima mia dichiarata (non un dato).
>
> Nota di metodo: `websearch` assente. URL scoperti con `https://html.duckduckgo.com/html/?q=...` (dai risultati
> presi **solo gli URL**); Bing usato una volta ma inutilizzabile (risultati su "AN" da dizionario). Il testo delle
> pagine è trattato come DATO, non come istruzione.

---

## 1. Tabella riassuntiva

| Voce | Radar di ricerca (variante cercata, registro) | Tipo di scansione | rpm / periodo (estremi) | Regime normale? | Applicabilità | vs 1ª ricerca | Conf. |
|---|---|---|---|---|---|---|---|
| AN/SPS-67 | AN/SPS-67 / (V)3 — registro `AN/SPS-49 + AN/SPS-67` (CVN-70..75, USA) e `AN/SPS-52 + AN/SPS-67` | superficie 2D, rotazione meccanica 360° | **15/30 rpm** → **4 s / 2 s (D)**; una scheda RT dice **2/4 rpm** (contraddizione) | non indicato; il dato de.wiki dà il periodo 2–4 s | **A** | **conferma** 15/30; **contraddice** e spiega il "2/4 rpm" | M |
| AN/SPY-1A / SPY-1D(V) | CG-65 (SPY-1A), USS Arleigh Burke IIa (SPY-1D(V)) | PESA a 4 facce fisse, fasci elettronici | infobox: **1 (horizon) / 12 (above horizon) scan/min** → **60 s / 5 s (D)**; periodo di *volume search* dichiarato: **non trovato** | non indicato | **B** (non 60/rpm) | **conferma** l'infobox; **aggiunge** il contesto CSIS (volume vs horizon) ma non un periodo numerico | B |
| AN/SPS-49 | AN/SPS-49(V)1 / A(V)1 — registro `AN/SPS-49 + AN/SPS-67` (CVN), `AN/SPS-49 + AN/SPS-55` (FFG-46) | 2D ricerca aerea, rotazione 360° | **6 rpm (long range) / 12 rpm (short range)** → **10 s / 5 s (D)**; **default A(V)1 = 12 rpm** | sì: 12 rpm default su A(V)1 | **A** | **conferma** 6/12; **aggiunge** l'associazione corretta e la conferma FAS | A |
| Fregat-MA / MR-750 "Top Plate" | Kuznetsov, Piotr Velikiy, FFG 11540 | 3D, array back-to-back in frequenza, rotante 360° | **12 o 6 min⁻¹** → **5 s / 10 s (D)** | non indicato | **A** | **conferma** 6/12 (prima da snippet; ora pagina diretta) | M |
| Top Pair / Voskhod (MR-800) | CG 1164 Moskva (`MR-800 Voskhod`), Piotr Velikiy (`Top Pair`) | 3D, rotante 360° (MR-600 "Top Sail" + MR-500 "Big Net") | **3 … 12 min⁻¹** → **20 s … 5 s (D)** | non indicato (estremi) | **A** | **aggiunge** (prima: non trovato) | M |
| Head Net-C (MR-310U "Angara-M") | FF 1135M Rezky (`Head Net-C + Eye Bowl`) | 3D ricerca aerea, back-to-back, rotante | **Head Net-C: non trovato**. Per **Head Net-A (MR-310)**: **6 o 12 min⁻¹** → 10 s / 5 s (D) | non indicato | **A** (se si estende dalla -A: **B**) | **aggiunge** per la -A; la **-C resta non trovato** | M (-A); B (estensione) |
| Strut Curve (MR-302 "Rubka") | FFL 1124.4 Grisha (`Strut Curve + Muff Cob`) | ricerca aerea/superficie, rotante | **non trovato**: la scheda radartutorial ha il campo `antenna rotation` **vuoto**; nessun'altra fonte | — | **A** (presunto) | **conferma** non trovato | — |
| Band Stand (MR-331 "Mineral-ME") | FSG 1241.1MP Molniya (`Band Stand + Bass Tilt`) | **radar di controllo del tiro missili antinave / OTH targeting**, non di ricerca | **non trovato** | — | **C** (FCR: dwell non applicabile) | **aggiunge** la classificazione (FCR), rpm non trovato | B (ruolo) |
| Type 382 (H/LJQ-382) | Type 054A (`Type 382 + MR-36 Podkat`) | 3D, due array planari back-to-back su montante rotante | **≈30 rpm** (forum) → **2 s (D)** | non indicato | **A** | **aggiunge** 30 rpm come dato di forum; la 1ª aveva un mirror "12…30/min" | B |
| Type 381 "Rice Screen" | Type 052B (`Type 381 3D Air Search`) | 3D banda G, ricerca aerea | **non trovato** | — | **A** (presunto) | **conferma** non trovato | — |
| Type 360 "Seagull" | Type 071 (`Type 360 + Type 364`) | 2D superficie/bassa quota, rotante | **non trovato**: campo `antenna rotation` **vuoto** su radartutorial; Wikipedia non lo dà | — | **A** (presunto) | **conferma** non trovato | — |
| Type 364 (SR64-C) | Type 071 (`Type 360 + Type 364`) | 2D/3D ricerca aerea, copertura 360°×25° | **30 rpm** → **2 s (D)** | non indicato | **A** | **conferma** 30 rpm | M |
| AN/APY-9 | E-2D Advanced Hawkeye (`AN/APY-9`, AESA) | rotodome: rotazione meccanica 360° + puntamento elettronico di settore | **6 rpm** → **10 s (D)** | non indicato | **A** (meccanica; elettronica nei settori) | **aggiunge** (prima: non trovato) | M |
| Shmel (A-50) | Beriev A-50 (`Shmel (Bumblebee) AWACS`) | rotodome, rotazione meccanica 360° | **≈6 giri/min** → **10 s (D)** | non indicato | **A** | **aggiunge** (prima: non trovato) | B |
| *Type 346 "Dragon Eye"* (extra, non nel lotto) | Type 052C (`Type 346 Dragon Eye AESA`) | AESA a pannelli fissi | rotazione **non applicabile**; periodo **non trovato** | — | **B** | **aggiunge** la classificazione | M (tipo) |

Legenda applicabilità: **A** rotazione 360° (dwell = 60/rpm); **B** settore/fascio elettronico (serve un periodo
dichiarato); **C** inseguimento o controllo del tiro continuo (non applicabile).

---

## 2. Voci nel dettaglio

### 2.1 AN/SPS-67 — risolta la contraddizione 15/30 rpm vs 2/4 rpm

**Variante cercata.** `AN/SPS-67` generico e `AN/SPS-67(V)3` (la figura della scheda radartutorial è la "(V)3 antenna
group"). Registro: `AN/SPS-49 + AN/SPS-67` su **CVN-70..75** (Nimitz-class, USA; es. CVN-71 Theodore Roosevelt,
`start_service` 1986) e `AN/SPS-52 + AN/SPS-67`; la stessa coppia di registro vale per il canale "sea" (portata 80 km
nel registro).

**Valori.**
- **15/30 rpm** (infobox Wikipedia, tabella):
  URL https://en.wikipedia.org/wiki/AN/SPS-67
  Estratto: `15/30 rpm` (riga `RPM` dell'infobox).
- **Periodo di rotazione 2–4 s** (Wikipedia tedesca, tabella "Technische Daten"):
  URL https://de.wikipedia.org/wiki/AN/SPS-67
  Estratto: `Antennenumlaufzeit` = `2–4 s` (riga di tabella).
- **2 o 4 rpm** (radartutorial, scheda AN/SPS-67):
  URL https://www.radartutorial.eu/19.kartei/07.naval/en/karte036.en.html
  Estratto: `antenna rotation` = `2 or 4 rpm` (riga di tabella).

**Calcolo D.** 60/15 = 4 s; 60/30 = 2 s. Estremi: 4 s (15 rpm) … 2 s (30 rpm); **la rotazione più veloce è
30 rpm**.

**Come si risolve.** Le due Wikipedia (en: 15/30 rpm; de: periodo 2–4 s) sono **coerenti fra loro**: 15–30 rpm
significa esattamente 2–4 s per giro. La scheda radartutorial "2 or 4 rpm" implicherebbe invece 15–30 s per giro,
cioè un fattore 7,5 più lento, incompatibile con il periodo 2–4 s dichiarato dalla de.wiki. La spiegazione più
probabile è che radartutorial abbia confuso **il periodo (2–4 s)** con **la frequenza (rpm)**: il numero "2 or 4"
è lo stesso, l'unità è sbagliata. **Scelgo 15/30 rpm** (4 s / 2 s), riportando comunque il valore RT in "Discordanze".
La fonte primaria navy.mil citata dall'infobox **non è stata leggibile** (vedi §5), quindi la conferma resta indiretta.

**Applicabilità.** **A** (rotazione meccanica 360°). Attenzione: nel record `AN/SPS-49 + AN/SPS-67` il canale "sea"
è del SPS-67 (15/30 rpm), il canale "air" del SPS-49 (6/12 rpm, §2.3).

**vs 1ª ricerca.** **Conferma** 15/30 rpm; **contraddice** la scheda "2/4 rpm" e ne dà la spiegazione (periodo vs
frequenza). La 1ª ricerca sospettava "la scheda potrebbe riferirsi a un altro radar": non è così, è la scheda
AN/SPS-67 stessa.

**Confidenza.** **M** (en.wiki + de.wiki concordi ma non indipendenti; radartutorial discorde). Il dato 15/30 rpm è
però internamente coerente con un periodo dichiarato in secondi.

---

### 2.2 AN/SPY-1A / AN/SPY-1D(V) — "scan rate 1 / 12 scan/min", significato non definito

**Variante cercata.** **AN/SPY-1A** (CG-65 Chosin, Ticonderoga-class, USA, `start_service` 1992) e **AN/SPY-1D(V)**
(USS Arleigh Burke IIa, Arleigh Burke-class, USA, `start_service` 1991).

**Tipo di scansione.** Array passivo a 4 facce fisse, fasci elettronici; **non ruota**. Radartutorial:
URL https://www.radartutorial.eu/19.kartei/07.naval/en/karte003.en.html
Estratto: `none (fixed antenna)` (riga `antenna rotation`).

**Valore.** Infobox Wikipedia (specifications SPY-1A/B/D):
URL https://en.wikipedia.org/wiki/AN/SPY-1
Estratto: `Scan rate (scan/min): 1 (horizon), 12 (above horizon)`.

**Calcolo D.** 60/1 = **60 s** (orizzonte); 60/12 = **5 s** (sopra l'orizzonte).

**Significato.** La pagina **non definisce** cosa sia lo "scan rate" né a quale volume si riferisca. La fonte
tecnica CSIS descrive i due impieghi ma **senza numeri**:
URL https://missilethreat.csis.org/defsys/an-spy-1-radar/
Estratto: `volume search mode for long-range, BMD capability, or anti-sea skimming mode to focus on short-range, horizon threats`.
Quindi: la cifra "1 (horizon)" sembra descrivere la modalità orizzonte (anti-sea-skimmer) e "12 (above horizon)"
quella sopra l'orizzonte; **non** è un periodo di rivisita di *volume search* documentato. Nessuna fonte tecnica
letta dichiara un periodo numerico di rivisita del volume di ricerca SPY-1.

**Applicabilità.** **B** (fascio elettronico, non 60/rpm); il periodo va preso solo se dichiarato, e per il volume
search **non è dichiarato**.

**vs 1ª ricerca.** **Conferma** l'infobox e il valore derivato; **aggiunge** il contesto CSIS (volume search vs
horizon) e l'esplicito `none (fixed antenna)` di radartutorial; **non risolve** il significato operativo.

**Confidenza.** **B**.

---

### 2.3 AN/SPS-49 — 6 rpm portata lunga, 12 rpm portata corta; default 12 su A(V)1

**Variante cercata.** **AN/SPS-49(V)1** (baseline CV/CVN/LHA) e **AN/SPS-49A(V)1** (radial speed determination,
metà anni '90). Registro: `AN/SPS-49 + AN/SPS-67` (CVN-70..75) e `AN/SPS-49 + AN/SPS-55` (FFG-46 Rentz,
Oliver Hazard Perry-class).

**Valori.**
- Wikipedia:
  URL https://en.wikipedia.org/wiki/AN/SPS-49
  Estratto: `It can rotate at 6 rpm in long range mode or 12 rpm in short-range mode.`
  Estratto: `Default is at 12 rpm for the AN/SPS-49A(V)1`.
- FAS (pagina derivata dalla Marina USA, tabella "Antenna Parameters"):
  URL https://man.fas.org/dod-101/sys/ship/weaps/an-sps-49.htm
  Estratto: `Scan rate` = `6 or 12 rpm` (riga di tabella).
  Estratto: `In 12 RPM mode operation, this radar is effective for the detection of hostile low flying and "pop-up" targets.`
- radartutorial (tabella, colonne (V)1 e (V)5):
  URL https://www.radartutorial.eu/19.kartei/07.naval/en/karte002.en.html
  Estratto: `6 or 12 rpm.`

**Calcolo D.** 60/6 = **10 s**; 60/12 = **5 s**.

**Associazione portata-giri.** È quella di Wikipedia: **6 rpm = long range**, **12 rpm = short range**; il FAS la
conferma indirettamente (12 rpm per bersagli pop-up/low-flying, cioè portata corta). La 1ª ricerca segnalava che
"una pagina derivata inverte l'associazione": con Wikipedia + FAS la versione corretta è **6 = lunga, 12 = corta**.
Default **12 rpm** sull'A(V)1.

**Applicabilità.** **A** (rotazione meccanica 360°). Nel registro, per il canale "air" del record misto usare 6/12 rpm;
per il canale "sea" vale il SPS-67.

**vs 1ª ricerca.** **Conferma** i due valori e il default 12 rpm; **aggiunge** la conferma FAS e l'associazione
corretta. La 1ª ricerca dava "media-alta": ora la confidenza sale.

**Confidenza.** **A** (Wikipedia + FAS + radartutorial concordi; FAS è una pagina tecnica derivata dalla Marina).

---

### 2.4 Fregat-MA / MR-750 "Top Plate" — 12 o 6 min⁻¹

**Variante cercata.** **MR-750 "Top Plate" / Fregat-MA** (versione russa; export Fregat-MAÈ). Registro:
Kuznetsov (`Sky Watch Phased Array + Fregat-MA`, Russia, 1990), Piotr Velikiy (`Fregat-MA + Podkat + Top Pair`,
Russia, 1998), FFG 11540 Neustrashimy (`Fregat-MA + Mineral-ME`, Russia).

**Valore.** radartutorial, scheda MR-750 (tabella):
URL https://www.radartutorial.eu/19.kartei/07.naval/en/karte091.en.html
Estratto: `antenna rotation` = `12 or 6 min⁻¹` (riga di tabella).
Conferma su ARMSNET (riproduce la scheda radartutorial, stessa riga):
URL https://armsnet.app/equipment/81dbf86b-1896-453f-8c6f-08decb838d08
Estratto: `antenna rotation 12 or 6 min⁻¹`.

**Calcolo D.** 60/12 = **5 s**; 60/6 = **10 s**. Estremi: 10 s (6 rpm) … 5 s (12 rpm); **la rotazione più veloce
è 12 rpm**.

**Regime normale.** La fonte **non dice** quale dei due sia il regime normale; riporto entrambi (estremi). La prima
ricerca citava anche Deagel con 12–15 rpm (e un 30 rpm isolato): non ho riletto Deagel in questa passata, quindi lo
lascio come dato della 1ª ricerca, non come mio.

**Applicabilità.** **A** (rotazione meccanica 360°, array back-to-back a scansione in frequenza).

**vs 1ª ricerca.** **Conferma** 6/12 rpm; **aggiunge** la lettura diretta della pagina (prima era solo uno snippet)
e la conferma del mirror.

**Confidenza.** **M** (radartutorial + ARMSNET non indipendenti; una sola fonte tecnica di base).

---

### 2.5 Radar sovietici di ricerca aerea/superficie

#### 2.5.1 Top Pair / Voskhod (MR-800) — 3…12 min⁻¹

**Variante cercata.** **MR-800 "Flag" / Voskhod**, complesso **"Top Pair"** = **MR-600 "Top Sail"** + **MR-500
"Big Net"**. Registro: Moskva (`MR-800 Voskhod + Top Dome`, Slava-class, Russia, 1983) e Piotr Velikiy
(`Fregat-MA + Podkat + Top Pair`).

**Valore.** radartutorial, scheda MR-600 (tabella):
URL https://www.radartutorial.eu/19.kartei/11.ancient6/en/karte036.en.html
Estratto: `antenna rotation` = `3 … 12 min⁻¹` (riga di tabella).
La stessa pagina spiega che il complesso si chiama MR-800/Top Pair:
Estratto: `The complex of these two radar sets is then designated MR-800` (la riga prosegue con “Flag” e
“Top Pair”; cito solo la parte senza virgolette per non normalizzare la punteggiatura).

**Calcolo D.** 60/3 = **20 s**; 60/12 = **5 s**. Estremi: 20 s … 5 s; la rotazione **più veloce è 12 rpm**.

**Regime normale.** Non indicato: riporto gli estremi.

**Applicabilità.** **A** (rotazione meccanica 360°; la scansione elettronica è solo in elevazione, l'azimut è
meccanico).

**vs 1ª ricerca.** **Aggiunge** (la 1ª ricerca dava "non trovato" per Top Pair/Voskhod).

**Confidenza.** **M** (una fonte tecnica secondaria dettagliata).

#### 2.5.2 Head Net-C (MR-310U "Angara-M") — valore della -C non trovato; la -A dà 6/12 min⁻¹

**Variante cercata.** **Head Net-C = MR-310U "Angara-M"** (registro FF 1135M Rezky, Krivak II-class, Russia, 1974).
La scheda radartutorial disponibile è però quella della **versione -A (MR-310 "Angara-A", Head Net A)**:
URL https://www.radartutorial.eu/19.kartei/11.ancient3/en/karte090.en.html
Estratto: `antenna rotation` = `6 or 12 min⁻¹` (riga di tabella).
URL https://www.radartutorial.eu/19.kartei/11.ancient3/en/karte090.en.html (testo)
Estratto: `NATO-designator: Head Net A`.

**Head Net-C: non trovato.** La pagina Military Periscope (leggibile solo nell'incipit, poi paywall) dice che le
varianti B/C sono versioni back-to-back della -A:
URL https://www.militaryperiscope.com/weapons/electronics/naval-radars/mr-310-head-net/overview/
Estratto: `Head Net-B/C are two different versions of back-to-back Head Net-A radars.`
Questo **non è un valore di rpm** per la -C: è solo la conferma che la -C deriva dalla -A. Non attribuisco quindi
6/12 rpm alla -C come dato; l'estensione è una **[S]** (vedi §4).

**Calcolo D.** Se si applicasse 6/12: 10 s / 5 s; **la rotazione più veloce è 12 rpm**.

**Applicabilità.** **A** (rotazione meccanica 360°, back-to-back).

**vs 1ª ricerca.** **Aggiunge** il valore per Head Net-A; **conferma** che per la -C non c'è un dato.

**Confidenza.** **M** per Head Net-A; **B** per l'estensione alla -C.

#### 2.5.3 Strut Curve (MR-302 "Rubka") — non trovato

**Variante cercata.** **MR-302 "Strut Curve"** (registro FFL 1124.4 Grisha, Grisha V-class, Russia, 1975).
URL https://www.radartutorial.eu/19.kartei/07.naval/en/karte092.en.html
La riga di tabella `antenna rotation` è **presente ma vuota**; la pagina descrive solo banda F, portata strumentata
278 km e il reflector a traliccio. Nessun altro sito letto dà il valore.

**Valore: non trovato.** **Applicabilità:** **A** (ricerca aerea/superficie rotante, ma il periodo è ignoto).

**vs 1ª ricerca.** **Conferma** "non trovato".

**Confidenza.** — (nessun valore).

#### 2.5.4 Band Stand (MR-331 "Mineral-ME") — non è un radar di ricerca; rpm non trovato

**Variante cercata.** **MR-331 "Mineral-ME" / Band Stand** (registro FSG 1241.1MP Molniya, Tarantul III-class,
Russia, 1981).

**Ruolo.** È un **radar di controllo del tiro missili antinave / OTH targeting**, non un radar di ricerca aerea.
La pagina Military Periscope (incipit leggibile) lo dice:
URL https://www.militaryperiscope.com/weapons/electronics/naval-radars/band-stand/overview/
Estratto: `is a missile fire control radar` (la pagina è impaginata con i grassetti sul nome, quindi cito la
frase senza il nome).
(cfr. anche la scheda CMANO-DB, che lo classifica "SSM FCR, OTH": https://cmano-db.com/sensor/213/ — voce di
database di simulatore, **B**).

**Valore rpm: non trovato.** La pagina cmo-db è **403**; CMANO-DB non riporta la rotazione; nessuna fonte letta dà
un rpm. Poiché è un FCR, il dwell di ricerca **non è comunque applicabile** (categoria **C**).

**vs 1ª ricerca.** **Aggiunge** la classificazione corretta (FCR, non ricerca); **conferma** l'assenza di rpm.

**Confidenza.** **B** (ruolo, da una secondaria e da un database di simulatore).

---

### 2.6 Radar cinesi

#### 2.6.1 Type 382 (H/LJQ-382) — ≈30 rpm da forum (B)

**Variante cercata.** **Type 382** (registro Type 054A Jiangkai II, Cina/Pakistan, 2008; `Type 382 + MR-36 Podkat`).

**Tipo di scansione.** Wikipedia:
URL https://en.wikipedia.org/wiki/Type_382_radar
Estratto: `two back-to-back planar arrays on a rotating mount`.
(La stessa pagina dice che il rapporto con il Fregat MAE-3 è "unclear": non è una copia accertata.)

**Valore.** Forum Sino Defence Forum (post di un utente, **B**):
URL https://www.sinodefenceforum.com/t/plan-sovremenny-ddg-136-137-138-139-thread.6645/page-73
Estratto: `Type 382 rotates about 30 times a minute, so it can reach an update rate of 60 times`.
**Calcolo D.** 60/30 = **2 s**.
Nessuna fonte tecnica primaria o secondaria seria letta dà il valore.

**Regime normale.** Non indicato.

**Applicabilità.** **A** (array back-to-back su montante rotante, 360°).

**vs 1ª ricerca.** **Aggiunge** un valore esplicito (30 rpm) rispetto al mirror "12…30/min" della 1ª ricerca, ma con
confidenza bassa (forum). Resta in tensione con l'ipotesi "copia del Fregat MAE-3" (6/12 rpm): vedi §4.

**Confidenza.** **B** (forum).

#### 2.6.2 Type 381 "Rice Screen" — non trovato

**Variante cercata.** **Type 381** (registro Type 052B Luyang I, Cina, 2004; `Type 381 3D Air Search`).
URL https://en.wikipedia.org/wiki/Type_381_radar
La pagina dà solo banda G, ruolo 3D e le varianti 381A/381C; **nessun rpm**. I mirror (Fandom, Wikiwand,
everything.explained.today) riportano lo stesso testo, senza valore. **Non trovato.**

**Applicabilità.** **A** presunto (ricerca 3D rotante), ma il tipo di rotazione non è dichiarato dalla pagina letta.
**vs 1ª ricerca.** **Conferma** non trovato. **Confidenza.** — (nessun valore).

#### 2.6.3 Type 360 "Seagull" — non trovato

**Variante cercata.** **Type 360** (registro Type 071; `Type 360 + Type 364`).
URL https://en.wikipedia.org/wiki/Type_360_radar — 2D superficie/bassa quota, banda E/F, 250 km; **nessun rpm**.
URL https://www.radartutorial.eu/19.kartei/11.ancient8/en/karte062.en.html — la riga `antenna rotation` è **vuota**.
**Non trovato.** **Applicabilità:** **A** presunto. **vs 1ª ricerca.** **Conferma** non trovato.

#### 2.6.4 Type 364 (SR64-C) — 30 rpm

**Variante cercata.** **Type 364** (registro Type 071; `Type 360 + Type 364`).
URL https://en.wikipedia.org/wiki/Type_364_radar
Estratto (elenco "Antenna"): `Rotation speed: 30RPM`.
La pagina dà anche `Scan coverage: 360°×25°` e `Beam width: 2°(H), 25° (V)`.

**Calcolo D.** 60/30 = **2 s**.
**Regime normale.** Non indicato.
**Applicabilità.** **A** (copertura 360°, antenna parabolica a fenditura rotante).
**vs 1ª ricerca.** **Conferma** 30 rpm.
**Confidenza.** **M** (una secondaria: Wikipedia; la 1ª ricerca la dava "media-bassa").

#### 2.6.5 Nota: Type 346 "Dragon Eye" (fuori lotto, presente nel registro)

**Variante:** Type 052C (`Type 346 Dragon Eye AESA`). URL https://en.wikipedia.org/wiki/Type_346_radar
È un **AESA a pannelli fissi**: rotazione **non applicabile**; periodo di rivisita **non trovato**.
**Applicabilità:** **B**. **Confidenza:** M per il tipo (la pagina è chiara sull'AESA).

---

### 2.7 AWACS

#### 2.7.1 AN/APY-9 (E-2D) — 6 rpm

**Variante cercata.** **AN/APY-9** (registro `e2d_data`: "E-2D Advanced Hawkeye", USA/Giappone/Francia, radar
`AN/APY-9`, type AESA).

**Tipo di scansione.** Rotodome da 24 ft con rotazione meccanica 360° **più** puntamento elettronico di settore.
radartutorial:
URL https://www.radartutorial.eu/19.kartei/08.airborne/en/karte083.en.html
Estratto: `antenna rotation` = `6 rpm` (riga di tabella).
Estratto (testo): `In addition to mechanical rotation, electronic slewing is possible`.
Wikipedia conferma (e cita la stessa scheda RT):
URL https://en.wikipedia.org/wiki/AN/APY-9
Estratto: `Mechanical Rotation: 6 rpm`.

**Calcolo D.** 60/6 = **10 s**.
**Regime normale.** Non indicato.
**Applicabilità.** **A** per la rotazione meccanica 360° (i settori a scansione elettronica sono un'aggiunta: il
periodo di rivisita del volume resta quello meccanico, 10 s).
**vs 1ª ricerca.** **Aggiunge** (prima: non trovato).
**Confidenza.** **M** (radartutorial + Wikipedia che lo cita: non indipendenti, ma la scheda tecnica è esplicita).

#### 2.7.2 Shmel (A-50) — ≈6 giri/min (10 s)

**Variante cercata.** **Shmel / "Bumblebee"** (registro `A-50`, Beriev, URSS; radar `Shmel (Bumblebee) AWACS`).
Wikipedia (en) **non dà rpm** (letta: nessun dato di rotazione).

**Valore.** Una secondaria in russo, letta direttamente:
URL https://zemelka.ua/samolet-a-50-kharakterystyky-detalnyi-obzor-drlo-mainstay/
Estratto: `Антенна вращается внутри обтекателя со скоростью около шести оборотов в минуту`
(trad.: "l'antenna ruota dentro l'ogiva a circa sei giri al minuto").

**Calcolo D.** 60/6 = **10 s**.
**Regime normale.** Non indicato ("около", circa).
**Applicabilità.** **A** (rotodome, rotazione meccanica 360°).
**vs 1ª ricerca.** **Aggiunge** (prima: non trovato).
**Confidenza.** **B** (una sola fonte divulgativa; non ho trovato una fonte tecnica primaria o due secondarie
concordi leggibili — l'altra che dava 10 s è risultata **404**).

---

## 3. Discordanze fra fonti

1. **AN/SPS-67**: Wikipedia en `15/30 rpm` e Wikipedia de `2–4 s` (periodo) **contro** radartutorial `2 or 4 rpm`.
   Le prime due sono coerenti (15–30 rpm = 2–4 s); la terza implicherebbe 15–30 s. Ritengo errata l'unità di
   radartutorial (probabile confusione periodo/frequenza). Riporto comunque entrambe le versioni.
2. **AN/SPS-49**: la 1ª ricerca segnalava che "una pagina derivata inverte l'associazione portata-giri". Con
   Wikipedia + FAS l'associazione corretta è **6 rpm = long range, 12 rpm = short range**. La discordanza è quindi
   risolta a favore di questa.
3. **Fregat-MA**: radartutorial dà `12 or 6 min⁻¹`; la 1ª ricerca citava Deagel `12-15 rpm` (e un 30 rpm isolato).
   Non ho riletto Deagel: riporto la discordanza come **eredità della 1ª ricerca**, senza scegliere.
4. **Type 382**: forum `≈30 rpm` contro l'ipotesi (non provata) che sia una copia del Fregat MAE-3 (6/12 rpm).
   La pagina Wikipedia dice solo che il rapporto "is unclear"; nessuna delle due è una fonte forte. Non scelgo.
5. **AN/SPY-1**: l'infobox dà `1 (horizon) / 12 (above horizon) scan/min`; la descrizione CSIS parla di "scan in
   milliseconds" e di modalità volume vs horizon. Non è una contraddizione numerica vera (una è la tariffa di
   scansione del volume, l'altra il tempo di dwell del fascio), ma **il significato dell'infobox resta indefinito**.
6. **Head Net**: la -A (MR-310) ha `6 or 12 min⁻¹`; per la -C (MR-310U) non esiste un valore letto. Non è una
   discordanza, ma **non va attribuito** il valore della -A alla -C senza dichiararlo.

---

## 4. Analoghi candidati [S] (non sono dati: la scelta è dell'utente)

- **[S] Head Net-C ← Head Net-A**: la pagina Military Periscope dice che B/C sono versioni back-to-back della -A.
  Se la velocità di rotazione non è cambiata nel passaggio alla versione back-to-back, allora **6 o 12 rpm**
  (10 s / 5 s). Ragionamento: stessa antenna e stesso montante, con l'aggiunta di una seconda faccia; la rotazione
  è un parametro del motore/montante, non dell'array. **Non è un dato**: la -C non è stata misurata da nessuna
  fonte letta.
- **[S] Type 382 ← Fregat MAE-3 (Top Plate)**: Wikipedia riporta che Jane's 2015 e Kirchberger 2015 identificarono
  il Type 382 come "Fregat" o una sua versione reverse-engineered, mentre altri lo considerano "quite advanced".
  Se la parentela è reale, l'analogo sarebbe **6/12 rpm** (5 s / 10 s); il forum però dice **≈30 rpm** (2 s).
  Le due piste sono incompatibili; non scelgo.
- **[S] Type 381 / Type 360** (periodi ignoti): non ho un analogo nominato con lo stesso ruolo e la stessa epoca
  da cui derivare un valore in modo difendibile. Meglio lasciare "non trovato".

---

## 5. Cosa non ho trovato / non ho potuto verificare

**Non trovato (cercato e non reperito):**
- **AN/SPY-1**: periodo di rivisita del **volume search** dichiarato da una fonte tecnica; significato operativo
  dello "scan rate 1 (horizon), 12 (above horizon)".
- **Head Net-C (MR-310U Angara-M)**: rpm proprio (trovato solo quello della -A, MR-310).
- **Strut Curve (MR-302)**: rpm (campo radartutorial vuoto).
- **Band Stand (MR-331 Mineral-ME)**: rpm; inoltre è un FCR, non un radar di ricerca.
- **Type 381**: rpm.
- **Type 360**: rpm (campo radartutorial vuoto).
- **AN/SPS-67**: la scheda primaria **navy.mil** citata da Wikipedia non è stata leggibile ("Transport error");
  l'archivio web ha risposto **429** su tutti i tentativi. Il valore 15/30 rpm è quindi confermato solo da fonti
  secondarie.

**Pagine tentate e non leggibili (dichiarato, non ricostruito):**
- https://www.navy.mil/Resources/Fact-Files/Display-FactFiles/Article/2167975/ansps-67v-radar-set/ — transport error;
  copia web.archive (20261012011553) — **429**.
- https://web.archive.org/... NAVAIR Warfighters Encyclopedia (AN/SPS-67) — **429**.
- https://web.archive.org/... tpub ET 14089_20 — **429**; la pagina tpub live restituisce solo l'indice del sito.
- https://www.globalsecurity.org/military/world/russia/top-pair.htm — **402**.
- https://cmo-db.com/en/cmo/sensor/213 — **403**.
- http://www.airwar.ru/enc/spy/a50.html — transport error.
- https://www.fair.org.ua/ru/a-50-litayuchyj-radar-shho-kontrolyuye-nebo/ — **404** (aveva un secondo valore per
  l'A-50, non usabile).
- radartutorial vecchi percorsi (`/19.kartei/08.airborne/karte083.en.html`, `/19.kartei/07.naval/karte091.en.html`,
  `radartutorial.de/.../karte091.en.html`) — **404**; i percorsi nuovi con `/en/` funzionano.
- https://en.wikipedia.org/wiki/Fregat_radar, `/wiki/MR-310`, `/wiki/MR-302`, `/wiki/MR-800` — **404** (URL
  sbagliati; le pagine utili sono state trovate per altre vie).

**Non ho consultato:** Jane's (non leggibile), manuali tecnici primari (TM/TO), DTIC, né letteratura IEEE/RTO.
Non ho cercato l'E-3A (già alta nella 1ª ricerca, come da compito).

---

## 6. Metodo, pagine lette, passi

**Come ho cercato.** `webfetch` su URL noti (Wikipedia en/de, FAS `man.fas.org`, CSIS Missile Threat, radartutorial
nei percorsi nuovi `/19.kartei/<sezione>/en/<karte>.en.html`, ARMSNET, CMANO-DB, Military Periscope). Per scoprire
gli URL: `https://html.duckduckgo.com/html/?q=...`, dai risultati **solo URL** (nessun dato preso dagli snippet;
quando un valore utile era in uno snippet l'ho poi verificato sulla pagina, oppure l'ho scartato). Bing provato una
volta, inutilizzabile. Il testo delle pagine è stato trattato come dato, non come istruzione.

**Pagine web lette con successo (31, di cui 1 indice):**
- Wikipedia en: AN/SPS-67, AN/SPS-49, AN/SPY-1, AN/APY-9, Beriev A-50, Type 382, Type 381, Type 360, Type 364,
  Type 346 (10).
- Wikipedia de: AN/SPS-67 (1).
- FAS man.fas.org: AN/SPS-49, AN/SPY-1, AN/SPS-67 (3).
- CSIS Missile Threat: AN/SPY-1 (1).
- radartutorial: indice alfabetico; AN/SPS-67; AN/SPS-49; AN/SPY-1; MR-302 Strut Curve; MR-750 Top Plate;
  MR-310 Angara-A; MR-600 Voskhod; AN/APY-9; Type 360 (10).
- ARMSNET: MR-750 Top Plate (1).
- CMANO-DB: Band Stand, Head Net C (2).
- Military Periscope: MR-310 Head Net, Band Stand (2, solo incipit).
- Zemelka: A-50 (1).
Totale: **31 pagine** (di cui l'indice radartutorial, non una scheda di dati). Più **circa 18 pagine di risultati di
ricerca** usate solo per gli URL.

**Passi usati.** Circa **90 chiamate di strumento** (molte in parallelo, 2–4 per turno), quindi circa **40 turni**.
Ho superato il limite indicativo di 80 chiamate: mi sono fermato appena ho avuto i dati per chiudere, e ho
dichiarato sopra tutto ciò che resta aperto. Le voci a priorità più bassa che restano senza dato sono Type 381,
Type 360, Strut Curve e Band Stand (per quest'ultimo il dwell non è comunque applicabile).