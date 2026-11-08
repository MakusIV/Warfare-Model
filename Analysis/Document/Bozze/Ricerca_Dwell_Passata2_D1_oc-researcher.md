# Ricerca dwell — Passata 2, Lotto D1 (tiratori a corto raggio)

> Bozza di ricerca (`oc-researcher`). Oggetto: periodo di rivisita (`dwell_time_s`) del radar di **ricerca** di
> 5 tiratori a corto raggio. Complemento di `Analysis/Document/Ricerca_Dwell_Sensori_2026_11_06.md` (Passata 1).
> Data: 2026-11-08. Stato: **completa** (sintesi e lacune in fondo).
>
> **D = valore derivato** con calcolo mostrato (non dichiarato dalla fonte). **M = una fonte secondaria seria.**
> **A = fonte tecnica primaria o due fonti secondarie indipendenti concordi.** **B = stima/forum/gioco.**
> `[S]` = mia stima ragionata, mai un dato.

## 0. Varianti cercate nei registri

Nomi letti con `grep -n` in `Code/Dynamic_War_Manager/Source/Asset/Vehicle_Data.py`; chiave `radar`.

| Voce registro | `model` registro | Variante cercata sul web | Anni/utenti registro |
|---|---|---|---|
| `ZSU-23-4-Shilka` | `1RL33 Gun Dish` | RPK-2 «Tobol» / 1RL33; **trovato il manuale della variante 1RL33M3** (ZSU-23-4M) | 1965; USSR, Russia, Siria, Egitto, India… |
| `9A33-Osa` | `Land Roll` | 1S51M3 «Land Roll» del 9K33 Osa (9A33) | 1971; USSR, Russia, India, Grecia… |
| `2K22-Tunguska` | `1RL144 Search + 1A26 Tracking` | 1RL144 «Hot Shot A» (ricerca) del 2S6/2K22; 1A26 = computer, non radar | 1982; USSR, Russia, India… |
| `Flakpanzer-Gepard` | `Search and Tracking Radar` | MPDR-12 (ricerca) + radar di inseguimento J-band | 1976; Germania, Paesi Bassi, Belgio… |
| `MIM-115-Roland` | `MPDR 16` | MPDR-16 (ricerca) del Roland-1/-2 | 1977; Francia, Germania, USA… |

## 1. Tabella riassuntiva

| Voce | Radar di ricerca (variante cercata) | Tipo di scansione | rpm / periodo (estremi) | Regime normale? | Applicabilità | Rispetto alla Passata 1 | Conf. |
|---|---|---|---|---|---|---|---|
| ZSU-23-4 Shilka | RPK-2 / 1RL33 «Gun Dish» — dati dal manuale **1RL33M3** | **Circolare 360°** + **settore 30–100°** (oscillante) + inseguimento | Circolare **20°/s → 18 s** (D); accelerata **45–60°/s → 6–8 s** (D); settore 30–100° a **20°/s → rivisita 3–10 s** (D) | Sì: circolare 20°/s e settore 20°/s sono i due modi normali; l'accelerato è modo a parte | **A** (360°) e **B** (settore); in inseguimento **C** | **AGGIUNGE**: la Passata 1 aveva «non trovato» (solo gioco) | **M** |
| 9A33 Osa | 1S51M3 «Land Roll» (antenna di acquisizione) | Circolare 360°, antenna a parabola stabilizzata; fascio 1°–4° az, 19° el | **33 rpm → 1,82 s** (D) | Sì | **A** (ricerca); tracker **C** | **AGGIUNGE**: la Passata 1 aveva «rpm non trovato» | **A** |
| 2K22 Tunguska | 1RL144 «Hot Shot A» (ricerca 3D S-band) | Circolare 360°; fascio ~5° az × 15° el | **non trovato** (nessuna fonte leggibile dà rpm o periodo) | — (tipo normale, numero ignoto) | **A** per la ricerca; 1A26/tracking **C** | **CONFERMA/AGGIUNGE** il tipo (360°); il periodo resta **non trovato** | **A** (tipo) / — (periodo) |
| Flakpanzer Gepard | MPDR-12 (ricerca, banda E, pulse-Doppler) | Rotazione continua 360° | **60 rpm → 1,0 s** (D) | Sì | **A** (ricerca); tracker J-band **C** | **CONFERMA** il 60 rpm (Passata 1: media-bassa) | **A** |
| MIM-115 Roland | MPDR-16 (ricerca, pulse-Doppler, 360°) | Rotazione continua 360° | **60 rpm → 1,0 s** (D) | Sì | **A** (ricerca); tracker **C** | **CONFERMA** il 60 rpm | **A** |

**Sintesi in una riga.** Quattro dei cinque sistemi hanno ora un periodo di rivisita utilizzabile; il quinto
(Tunguska 1RL144) ha la geometria di ricerca confermata (360°) ma **nessun numero di rotazione** nelle fonti
pubbliche leggibili. Per lo Shilka — l'osservatore più usato negli scenari — il dato c'è, ma viene da un manuale
della variante **M** (1RL33M3), non dal 1RL33 del 1965.

## 2. Voci

### 2.1 ZSU-23-4 Shilka — RPK-2 «Tobol» / 1RL33 (manuale 1RL33M3)

**Voce cercata:** `1RL33 Gun Dish` (registro, 1965). **Trovato:** manuale didattico «Устройство и эксплуатация
ЗСУ-23-4М. РПК-2М. Часть 1. Устройство РЛС 1РЛ33М3» (Tomsk Polytechnic Univ., 2005), pubblicato su studfile;
descrive la stazione **1РЛ33М3** della ZSU-23-4**M**. Il tipo di scansione è esplicito e la velocità è in
gradi/secondo. **Non è il 1RL33 base del 1965**: la variante è una cautela da tenere presente.

**Modi di ricerca elencati (sezione 2.7.1):**
- URL: https://studfile.net/preview/6224112/page:20/
- Estratti letterali (tabella/elenco):
  - «Круговой поиск цели со скоростью 20 град/с.»
  - «Ускоренный круговой поиск цели со скоростью 45–60 град/с.»
  - «Секторный поиск цели, ширина которого может плавно изме­няться по азимуту в пределах 30 – 100 град.»
- Confidenza **M** (una fonte tecnica secondaria seria, riproduzione di un manuale tecnico).

**Dettaglio dei modi (sezione 2.7.2):**
- URL: https://studfile.net/preview/6224112/page:22/
- Estratti letterali:
  - «антенна начинает вращаться по азимуту с постоянной ско­ростью 20 град/с по ходу часовой стрелки»
    (ricerca circolare, 360°).
  - «антенна будет вращаться со скоростью 45–60 град/с» (ricerca circolare accelerata).
  - «Антенна совершает колебания по азимуту в секторе З0–1000.» (settore oscillante; il testo ha l'OCR del
    simbolo ° reso «0», quindi 30–100°).
  - «Скорость движения антенны при любой ширине сектора постоянна и равна 20 град/с.»
- Confidenza **M**.

**Valori derivati (D):**
| Modo | Calcolo | Periodo di rivisita |
|---|---|---|
| Circolare 360°, 20°/s | 360 / 20 | **18,0 s** |
| Circolare accelerata, 45°/s | 360 / 45 | **8,0 s** |
| Circolare accelerata, 60°/s | 360 / 60 | **6,0 s** |
| Settore 30°, 20°/s (andata+ritorno) | 2 × 30 / 20 | **3,0 s** |
| Settore 100°, 20°/s (andata+ritorno) | 2 × 100 / 20 | **10,0 s** |

> Nota: il «periodo di rivisita» del settore è il tempo fra due passaggi consecutivi dello stesso punto, cioè una
> andata e un ritorno dell'antenna; per questo il fattore 2. Se il modello DES vuole solo il tempo di una
> passata sul settore, usare metà (1,5–5 s).

**Elemento da NON usare:** nella sezione 2.1 compare «Частота сканирования – 63 Гц» (URL page:4
https://studfile.net/preview/6224112/page:4/). 63 Hz NON è la rotazione dell'antenna (63 giri/s sono
meccanicamente impossibili per quella torretta); è una frequenza di scansione elettronica/indicatore. Non la
uso come dwell. `[S]` (mia interpretazione, non un dato).

**Inseguimento (C, non applicabile):** lo stesso complesso passa in «автосопровождение цели» (page:22); in
quel modo il dwell continuo non si applica. Il registro ha però solo una voce radar (ricerca+inseguimento
fusi): il `dwell_time_s` va preso dal modo di **ricerca**.

**Confronto con la Passata 1:** la Passata 1 riportava «tipo di scansione della ricerca: non trovato» e solo il
gioco War Thunder. **AGGIUNGE**: ora ci sono i tre modi, l'ampiezza del settore e le velocità. Resta la cautela
sulla variante M3.

### 2.2 9A33 Osa — «Land Roll» / 1S51M3

**Voce cercata:** `Land Roll` (registro, 1971). **Trovato:** «Land Roll engagement radar package» del 9K33 Osa,
componente di acquisizione; 33 rpm.

- URL: https://www.ausairpower.net/APA-9K33-Osa.html (Carlo Kopp, Technical Report APA-TR-2009-0704)
  - Estratto letterale: «mechanically steered stabilised paraboloid section antenna, providing a 1° - 4° mainlobe
    in azimuth … sweeping at 33 RPM.»
  - Confidenza **M** (una fonte tecnica secondaria).
- URL: https://en.missilery.info/missile/osa (Missilery.info, scheda 9K33)
  - Estratto letterale: «The radar carried out a circular search by rotating the antenna at a speed of 33 rpm»
  - Confidenza **M**.
- **Due fonti secondarie indipendenti concordi → confidenza A** per «33 rpm» e «ricerca circolare».

**Valore derivato (D):** 60 / 33 = **1,818 s ≈ 1,82 s** per giro (periodo di rivisita di un punto).
Il fascio in azimut è 1°–4° (ausairpower) / 1° (missilery), in elevazione 19° (fascio alto) con settore totale
27° su tre posizioni (missilery).

**Inseguimento (C):** il tracker è un'antenna separata a conical scan/monopulse (Passata 1); non applicabile.

**Confronto con la Passata 1:** la Passata 1 diceva «rpm/periodo: non trovato». **AGGIUNGE**: 33 rpm → 1,82 s.

### 2.3 2K22 Tunguska — 1RL144 «Hot Shot A»

**Voce cercata:** `1RL144 Search + 1A26 Tracking` (registro, 1982). Attenzione: **1A26 non è un radar**, è il
computer di controllo del tiro (radartutorial: «The radar feeds its data into a central computer, designated
1A26»). Il radar di ricerca è il **1RL144**; il tracker è lo «Hot Shot B» in banda X.

**Tipo di scansione (confermato 360°):**
- URL: https://www.ausairpower.net/APA-96K6-Pantsir-2K22-Tunguska.html
  - Estratto: «with a 360º search radar for acquisition and coarse tracking» — confidenza **M**.
- URL: https://missilery.info/missile/tunguska/st_sopr
  - Estratto: «когерентно-импульсную РЛС кругового обзора дециметрового диапазона волн» («РЛС кругового
    обзора» = radar a vista circolare) — confidenza **M**.
- URL: https://ru.wikipedia.org/wiki/Тунгуска_(зенитный_ракетно-пушечный_комплекс) (sez. «Характеристики»)
  - Estratto (tabella): «по азимуту — не ограничено» nella zona di scoperta della СОЦ — confidenza **M**.

**Geometria del fascio (utile, non è il dwell):**
- URL: https://missilery.info/missile/tunguska/st_sopr
  - Estratto: «ширине диаграммы направленности антенны по азимуту 5° и по углу места 15°» — **M**.

**Periodo di rotazione / rpm: NON TROVATO.**
- https://www.radartutorial.eu/19.kartei/04.battle/en/karte057.en.html : nella tabella la riga «antenna
  rotation:» è **vuota**; il testo dice solo «The rotation of the antenna is electromechanically
  position-stabilized and can also be used while the vehicle is in motion.» (rotazione stabilizzata, **nessun
  numero**).
- https://man.fas.org/dod-101/sys/land/row/2s6m.htm : tabella radar con Detection Range 18-20 km e Frequency
  2-3 GHz, **nessuna** voce di rotazione/periodo.
- https://armsnet.app/equipment/2c62d650-d479-4940-89d7-08decb838d08 : descrizione identica a radartutorial,
  **nessun** numero di rotazione.
- https://ru.wikipedia.org/wiki/Тунгуска_(зенитный_ракетно-пушечный_комплекс) : nessun periodo di rotazione.

**Inseguimento (C, non applicabile):** la stazione di accompagnamento 1RL144M/«Hot Shot B» ha un **settore di
ricerca** di 120° in azimut (missilery:
«Сектор поиска составлял 120° по азимуту и 0-15° по углу места»), ma è un modo del **tracker**, non della
ricerca; per il dwell di ricerca non si usa.

**Confronto con la Passata 1:** la Passata 1 aveva «A presumibile (ricerca rotante), periodo ignoto». Ora il
tipo 360° è **confermato** da tre fonti, ma il **periodo resta non trovato**. Non è un dato utilizzabile.

### 2.4 Flakpanzer Gepard — MPDR-12 (ricerca)

**Voce cercata:** `Search and Tracking Radar` (registro, 1976). **Trovato:** MPDR-12, radar di acquisizione
(banda E, pulse-Doppler), su braccio rotante.

- URL: https://www.radartutorial.eu/19.kartei/11.ancient/en/karte031.en.html
  - Estratto (tabella «Specifications», riga «antenna rotation»): «60 rpm»
  - Estratto (testo): «It is an E band pulse Doppler radar with high subclutter visibility and high data rate
    (60 rpm).»
  - Confidenza **M** (fonte tecnica secondaria).
- URL: https://www.militaryperiscope.com/weapons/electronics/ground-radars/mpdr-12/overview/
  - Estratto: «It has a high data rate (60 rpm)»
  - Confidenza **M**.
- **Due fonti secondarie concordi → A** per il valore 60 rpm (cautela: entrambe potrebbero derivare dal
  datasheet Siemens, quindi non completamente indipendenti).

**Valore derivato (D):** 60 / 60 = **1,0 s** per giro.
Il tracker è un radar J-band monopulse separato (radartutorial: «The J band tracking radar … monopulse pulse
Doppler equipment, it has an operating range of 15 km»); **C, non applicabile**.

**Confronto con la Passata 1:** la Passata 1 dava 60 rpm con confidenza «media-bassa (due fonti divulgative,
probabilmente non indipendenti)». **CONFERMA** il valore, con una fonte tecnica radar (radartutorial) in più;
la cautela sull'indipendenza resta. Se si vuole essere prudenti: **A** per il numero, ma non «primaria».

### 2.5 MIM-115 Roland — MPDR-16 (ricerca)

**Voce cercata:** `MPDR 16` (registro, 1977). **Trovato:** radar di sorveglianza Siemens MPDR-16, banda D,
pulse-Doppler, antenna rotante 360°.

- URL: https://en.missilery.info/missile/roland-2
  - Estratto: «pulsed Doppler surveillance radar of Siemens MPDR-16 D-band type, whose antenna rotates at a
    speed of 60 rpm.»
  - Confidenza **M**.
- URL: https://www.militaryperiscope.com/weapons/electronics/ground-radars/mpdr-16/overview/
  - Estratto: «its antenna can scan a 360-degree sector» (il resto è dietro paywall; la Passata 1 aveva letto
    «rotates at 60 rpm» nella stessa scheda). Confidenza **M** per il 360°.
- **Due fonti concordi sul 60 rpm** (Missilery + scheda Military Periscope citata dalla Passata 1) → **A**;
  la rilettura diretta della scheda MP è oggi troncata/paywall.

**Valore derivato (D):** 60 / 60 = **1,0 s** per giro.
Il tracker è il Thomson-CSF Domino 30 monopulse (missilery: «two-channel monopulse Doppler station type
Thomson-CSF Domino 30»); **C, non applicabile**.

**Confronto con la Passata 1:** **CONFERMA** il 60 rpm (la Passata 1 lo dava con una fonte, confidenza media).

## 3. Discordanze fra fonti

- **Nessuna discordanza numerica** fra le fonti lette: 33 rpm (Osa) e 60 rpm (Gepard, Roland) sono concordi;
  per lo Shilka le velocità vengono da un solo manuale, quindi non c'è confronto.
- **Cautela di variante (non è una discordanza):** il manuale Shilka è per **1RL33M3 / ZSU-23-4M**, mentre il
  registro nomina **1RL33** e data 1965 (variante base). Le velocità di scansione potrebbero differire; non ho
  trovato il TO del 1RL33 base.
- **Tunguska:** il dato «360°» è concorde, ma **nessuna** fonte dà il periodo; non c'è un valore alternativo da
  riportare.
- **Shilka, «Частота сканирования – 63 Гц»:** non è in contraddizione con 20°/s, perché non è la rotazione
  dell'antenna. `[S]` È una mia lettura, non un'affermazione della fonte.
- **Gepard, MPDR-12 vs MPDR-18:** il registro fonde ricerca e inseguimento in «Search and Tracking Radar». La
  Passata 1 citava sia MPDR-12 sia MPDR-18. Il valore 60 rpm è del **MPDR-12** (radartutorial, Military
  Periscope); per l'MPDR-18 non ho letto una fonte che dica 60 rpm. Non è una discordanza, è un perimetro.

## 4. Analoghi candidati [S]

Solo per la voce senza numero (**Tunguska 1RL144**). **Non sono dati**: sono ragionamenti, la scelta è
dell'utente.

| Analoghi candidati | Periodo noto (fonte) | Perché potrebbe somigliare | Perché no |
|---|---|---|---|
| 9A33 Osa «Land Roll» (stessa epoca, ricerca 360° S/C-band) | 33 rpm → 1,82 s (2.2) | Stessa generazione, stessa funzione (ricerca 360° + tracker separato), stessa scuola sovietica | Osa è del 1971, 1RL144 del 1982; antenne e bande diverse |
| Gepard MPDR-12 (ricerca 360°, occidentale, stessi anni) | 60 rpm → 1,0 s (2.4) | Ricerca 360° con antenna a sezione parabolica | Progettazione tedesca, non sovietica |
| Pantsir 2RL80 (successore del 1RL144 nella famiglia) | 15 o 30 rpm → 4 o 2 s (ausairpower: «circular scan in 2 or 4 seconds … at 15 or 30 RPM») | È il radar che sostituisce il 1RL144 nelle versioni Pantsir/Tunguska-M1; 360° | È un PESA successivo, non il 1RL144; usarlo come dato sarebbe un errore di variante |

**Ragionamento `[S]`:** il 1RL144 è un radar 3D in banda S con antenna a riflettore singolarmente curvo,
fascio ~5°×15°, rotazione meccanica stabilizzata. Un candidato plausibile per il DES è un periodo **fra 2 e 4 s**
(15–30 rpm) oppure, se si privilegia la continuità con l'Osa, **~1,8 s** (33 rpm). **Non ho una fonte** che
assegni al 1RL144 uno di questi valori: metterlo in `dwell_time_s` senza dichiararlo `[S]` sarebbe inventare.

## 5. Cosa non ho trovato / non ho potuto verificare

**Non trovato (nessuna fonte leggibile):**
1. **Tunguska 1RL144 — rpm o periodo di rotazione.** Cercato in radartutorial (EN/RU/DE/NL: campo vuoto),
   missilery.info (due pagine), ru.wikipedia, ausairpower (Kopp), FAS, ARMSNET, GlobalSecurity (402). Nessun
   numero. Resta il buco principale del lotto.
2. **ZSU-23-4 base (1RL33, 1965) — velocità di scansione proprie.** Il dato c'è solo per **1RL33M3 / ZSU-23-4M**
   (manuale 2005). Non ho letto il «Техническое описание 2А6М» (1980) né il «Устройство и эксплуатация РЛС»
   del 2005 nella sua veste PDF originale: ho letto la copia studfile del manuale didattico.
3. **Gepard — sorgente primaria Siemens.** Il PDF «Radar Basics» su archive.org
   (https://ia800504.us.archive.org/4/items/d34ed7c2/flakpz_gepard-radar.pdf) è stato richiesto ma restituito
   in **binario non leggibile** (stream PDF compresso): non ho potuto estrarre il testo. Il frammento
   «Circular search radar antenna … high data rate (60 rpm)» l'ho visto solo nel risultato di ricerca DuckDuckGo,
   non nella pagina letta: **non lo uso come citazione**.
4. **Roland — dettaglio della scheda Military Periscope MPDR-16.** Pagina in parte dietro paywall: ho letto solo
   «its antenna can scan a 360-degree sector»; il «60 rpm» di quella scheda è quello citato dalla Passata 1, non
   da me riletto.

**Pagine tentate e non leggibili:**
- https://www.globalsecurity.org/military/world/russia/hot-shot.htm → **402 Payment Required**.
- https://pvo.guns.ru/tunguska/tunguska_03.htm → errore di trasporto.
- https://weaponsystems.net/system/60-2S6+Tunguska → errore di trasporto.
- https://btvt.info/1inservice/zsu23_4.htm → pagina in **windows-1251**: testo restituito illeggibile
  (caratteri sostituiti); non ho ricostruito nulla.
- https://ia800504.us.archive.org/4/items/d34ed7c2/flakpz_gepard-radar.pdf → binario PDF, non testo.

**Da verificare in una Passata 3 (se serve):**
- TO ufficiale del 1RL33 base (non M3) e del RPK-2 «Tobol» del 1965.
- Manuale/TO del 1RL144 (2S6) o del 2S6M: è l'unico posto plausibile per il periodo di rotazione.
- Eventuale scheda Siemens dell'MPDR-12 (datasheet) per chiudere l'indipendenza delle due fonti Gepard.

## 6. Metodo

- **websearch non disponibile.** Scoperta degli URL con pagine di risultati
  `https://html.duckduckgo.com/html/?q=...` (dai risultati ho preso **solo gli URL**, mai i dati); nessun
  blocco di DuckDuckGo in questa sessione. Nessun uso di Bing.
- **Lettura diretta** delle pagine con `webfetch`; estratti copiati letteralmente (russo/inglese come nella
  pagina, senza normalizzare). Per i valori derivati ho mostrato il calcolo e marcato **D**.
- **Fonti usate (URL letti):**
  - Shilka: https://studfile.net/preview/6224112/page:4/ ; …/page:20/ ; …/page:22/ (manuale 1RL33M3);
    https://www.radartutorial.eu/19.kartei/11.ancient4/ru/karte088.ru.html (RPK-2, campo rotazione vuoto);
    https://ru.wikipedia.org/wiki/Шилка_(ЗСУ) ; https://en.wikipedia.org/wiki/ZSU-23-4_Shilka (contesto, nessun
    dato di scansione).
  - Osa: https://www.ausairpower.net/APA-9K33-Osa.html ; https://en.missilery.info/missile/osa.
  - Tunguska: https://www.radartutorial.eu/19.kartei/04.battle/en/karte057.en.html ;
    https://missilery.info/missile/tunguska/st_sopr ; …/st_obn ;
    https://ru.wikipedia.org/wiki/Тунгуска_(зенитный_ракетно-пушечный_комплекс) ;
    https://www.ausairpower.net/APA-96K6-Pantsir-2K22-Tunguska.html ; https://man.fas.org/dod-101/sys/land/row/2s6m.htm ;
    https://armsnet.app/equipment/2c62d650-d479-4940-89d7-08decb838d08.
  - Gepard: https://www.radartutorial.eu/19.kartei/11.ancient/en/karte031.en.html ;
    https://www.militaryperiscope.com/weapons/electronics/ground-radars/mpdr-12/overview/.
  - Roland: https://en.missilery.info/missile/roland-2 ;
    https://www.militaryperiscope.com/weapons/electronics/ground-radars/mpdr-16/overview/.
- **Registri letti:** `Code/Dynamic_War_Manager/Source/Asset/Vehicle_Data.py` con `grep -n` e `sed -n` (righe
  3764-3800, 3885-3980, 4118-4160, 4230-4275).
- **Passata 1 riletta:** `Analysis/Document/Ricerca_Dwell_Sensori_2026_11_06.md` con `grep -n` (sezioni 0, 3,
  6, 7 e «Esito per classe»).
- **Conteggio:** **passi usati ≈ 38** (chiamate di strumento, incluse le ricerche e i tentativi falliti);
  **pagine/schede web richieste ≈ 35**, di cui **10 pagine di soli risultati DuckDuckGo** (usate solo per gli
  URL), **~22 pagine/schede lette in modo utile** e **5 non leggibili** (402, errore di trasporto, PDF binario,
  encoding). File locali letti: 3 (compito, Passata 1, registro).

**Giudizio finale per il motore.** Pronti per `dwell_time_s` (confidenza A/M e valore derivato dichiarato):
Osa **1,82 s**, Gepard **1,0 s**, Roland **1,0 s**, Shilka **18 s** (circolare) oppure **3–10 s** (settore,
secondo la larghezza scelta) — con la cautela variante M3. Tunguska: **lasciare vuoto** o scegliere un analogo
`[S]` dalla sezione 4; non inventare un numero.