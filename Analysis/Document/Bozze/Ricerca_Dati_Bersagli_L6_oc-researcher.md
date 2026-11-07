# Ricerca dati — Blocco 0 BI, Lotto L6 (Cruise e Kh-22N)

Bozza del ricercatore `oc-researcher` per la Proposta
`Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` (§2.2 tabella armi->classe; §5.1 blocco 0).
Data: 2026-11-07. Lotto **L6**.

Scopo: per ogni voce del lotto raccogliere diametro, lunghezza, massa al lancio, RCS (se pubblicata) e la
proposta di classe (`cruise` / `anti_ship` / `arm` / `tactical`), con fonte, estratto letterale e confidenza.
La classificazione finale non e' del ricercatore: qui c'e' una proposta motivata.

Ancore di confronto (dette dal compito, non ricercate qui):
- **Maverick AGM-65D**: diametro 304,8 mm, lunghezza 2,49 m, massa 218,25-220 kg.
- **Harpoon AGM-84A aviolanciato**: diametro 343 mm, lunghezza 3,79-3,85 m, massa 515,25 kg.

Confronto di taglia richiesto: "non maggiore del Maverick", "non minore dell'Harpoon" o "zona grigia".

**Nota di lettura**: tutte le voci di questo lotto con dati sono molto piu' grandi dell'Harpoon. Il confronto
con le due ancore dà quindi, per tutte, **"non minore dell'Harpoon"** (diametro > 343 mm e massa > 515,25 kg);
il confronto col Maverick non serve mai (nessuna voce e' piccola). Il KD-63B, privo di dati propri, e'
"non determinabile" ma appartiene alla famiglia KD-63 (760 mm, ~2.000 kg).

---

## 1) Tabella riassuntiva

| Voce | Variante cercata | Classe proposta (ipotesi piano) | Diametro | Lunghezza | Massa lancio | RCS | Confronto ancore | Conf. |
|---|---|---|---|---|---|---|---|---|
| Kh-55 | Kh-55 (AS-15 Kent) | `cruise` — confermata | 514 mm | 6,04 m | 1.210 kg | non trovata | non minore dell'Harpoon | M/A |
| Kh-555 | Kh-555 (convenzionale, derivata Kh-55) | `cruise` — confermata | non trovato specifico (derivata: 514 mm) | non trovato | non trovato | solo "reduced RCS" (qualitativo) | non minore (per derivazione) | B |
| Kh-101 | Kh-101 (AS-23 Kodiak) | `cruise` — confermata | 510 mm | 7,45 m | 2.300-2.400 kg | non trovata (materiale RAM, qualitativo) | non minore dell'Harpoon | A |
| Kh-65 | Kh-65SE (export, 600 km/410 kg) | `cruise` — confermata | 514 mm (derivata Kh-55) | 6,04 m | 1.650 kg | non trovata | non minore dell'Harpoon | M |
| KD-20 | CJ-10K aviolanciato (KD-20) | `cruise` — confermata | non trovato specifico (famiglia CJ-10: 514-750 mm) | non trovato specifico (famiglia 6,3-7,2 m) | non trovato specifico (famiglia 1.090-2.500 kg) | non trovata | non minore (minimo di famiglia 514 mm/1.090 kg) | B |
| Kh-59 | Kh-59 (AS-13 Kingbolt) | `cruise` (tattico) — confermata | 380 mm | 5,37 m | 760-790 kg | non trovata | non minore dell'Harpoon | M |
| Kh-59M | Kh-59M (AS-18 Kazoo) | `cruise` (tattico) — confermata | 380 mm | 5,70 m | 930 kg | non trovata | non minore dell'Harpoon | M |
| KD-63 | KD-63 / K/AKD-63 (YJ-63) | `cruise` (tattico) — confermata; **corretta la piattaforma: solo bombardiere H-6** | 760 mm | 7 m | ~2.000 kg | non trovata | non minore dell'Harpoon | M |
| KD-63B | KD-63B | `cruise` (tattico) — confermata per famiglia, dati specifici **non trovati** | non trovato | non trovato | non trovato | non trovata | non determinabile (per famiglia non minore) | B |
| Kh-22N | Kh-22N (AS-4 Kitchen, variante antinave con ARH) | `anti_ship` confermata; **e' anche un cruise missile** (vedi §2) | 900-920 mm | 11,65-11,67 m | 5.635-5.780 kg | non trovata | non minore dell'Harpoon | A |

Legenda confidenza: **A** = fonte primaria o due secondarie concordi; **M** = una secondaria; **B** = stima o
fonte debole.

---

## 2) Voci nel dettaglio

### Kh-55

- **Voce cercata**: `"Kh-55"` in `Aircraft_Weapon_Data.py:3095`; `model "Kh-55"`, users USSR/Russia/Ukraine,
  task Strike, range 2500 km, warhead 400 kg, start_service 1983.
- **Variante**: Kh-55 base / Kh-55SM (AS-15 Kent). Il registro non distingue SM; i dati sotto sono per la
  famiglia Kh-55/Kh-55SM.
- **Diametro**: 514 mm.
  - CSIS: «Diameter 0.514 m» — https://missilethreat.csis.org/missile/kh-55/
  - Wikipedia: «Diameter 51.4 cm (20.2 in) (Kh-55/Kh-55SM)» — https://en.wikipedia.org/wiki/Kh-55
  - Confidenza A (due secondarie concordi).
- **Lunghezza**: 6,04 m. CSIS: «Length 6.04 m» (stessa URL). Confidenza M.
- **Massa al lancio**: 1.210 kg. CSIS: «Launch weight 1,210 kg» (stessa URL). Confidenza M.
  - *Discordanza*: Wikipedia non dà la massa del Kh-55, ma del Kh-65SE (1.650 kg). CSIS dà 1.210 kg per il
    Kh-55. Non sono la stessa variante: vedi §3.
- **RCS**: non trovata come valore. CSIS, per la variante Kh-555, dice solo «Reduced radar cross-section»
  (qualitativo, senza cifre). Per il Kh-55 base nessun valore.
- **Classe**: `cruise` — **confermata**.
  - Wikipedia: «Type Air-launched cruise missile» e «Kh-55 is launched exclusively from bomber aircraft».
  - CSIS: «Class Subsonic cruise missile».
- **Piattaforme**: bombardieri. Wikipedia: Tu-95MS, Tu-142M, Tu-160 (e prove sul Tu-22M); CSIS cita Tu-95MS6,
  Tu-95MS16, Tu-142M, Tu-160.
- **Confronto ancore**: 514 mm > 343 mm; 1.210 kg > 515,25 kg -> **non minore dell'Harpoon**.

### Kh-555

- **Voce cercata**: `"Kh-555"` in `Aircraft_Weapon_Data.py:4286`; `model 'Kh-555'`, users USSR/Russia/Ukraine,
  task Strike, range 3500 km, warhead 400 kg, start_service 1992.
- **Variante**: Kh-555 convenzionale, derivata del Kh-55.
- **Diametro / lunghezza / massa**: non trovati specifici.
  - CSIS: «The Kh-555 is a conventional variant of the Kh-55» — https://missilethreat.csis.org/missile/kh-55/
  - CSIS elenca solo le differenze: «Larger conformal fuel tanks (compared to the Kh-55SM)», «Reduced radar
    cross-section», «Increased range, 3,500 km». Nessuna dimensione o massa del Kh-555.
  - Non riporto i valori del Kh-55 come se fossero del Kh-555.
- **RCS**: solo qualitativa, «Reduced radar cross-section» (CSIS), senza valore numerico.
- **Classe**: `cruise` — **confermata**. Wikipedia: «Kh-555 ... conventionally armed version»; CSIS:
  «conventional variant of the Kh-55».
- **Piattaforme**: bombardieri. CSIS: «13 Tu-160 which can carry 12 Kh-55SM or Kh-555 missiles; 32 Tu-95MS6
  which can carry six Kh-55 and Kh-555 missiles» (stessa URL).
- **Confronto ancore**: per derivazione dal Kh-55 (514 mm, 1.210 kg) -> **non minore dell'Harpoon**, ma i
  valori specifici del Kh-555 non sono stati trovati (confidenza B).

### Kh-101

- **Voce cercata**: `"Kh-101"` in `Aircraft_Weapon_Data.py:3169`; `model "Kh-101"`, users Russia,
  task Strike/Pinpoint_Strike, range 5500 km, warhead 400 kg, start_service 2013.
- **Diametro**: 510 mm. CSIS: «Diameter 0.51 m» — https://missilethreat.csis.org/missile/kh-101-kh-102/
  Confidenza M.
- **Lunghezza**: 7,45 m.
  - CSIS: «Length 7.45 m» (stessa URL).
  - Wikipedia: «Length 745 cm (24 ft 5 in) (Kh-101)» — https://en.wikipedia.org/wiki/Kh-101
  - Confidenza A (due secondarie concordi).
- **Massa al lancio**: 2.300-2.400 kg.
  - CSIS: «At launch the missile weighs 2,300-2,400 kg and is fired without a booster».
  - Wikipedia: «Mass 2,400 kg (5,300 lb) (Kh-101)».
  - Confidenza A.
- **RCS**: non pubblicata. Wikipedia/CSIS dicono qualitativamente «radar absorbing composite material makes the
  missile challenging to detect» (CSIS). Nessun valore numerico.
- **Classe**: `cruise` — **confermata**. Wikipedia: «Type Air-launched cruise missile»; CSIS: «Class
  Air-launched Cruise Missile (ALCM)».
- **Piattaforme**: bombardieri. Wikipedia: «Launch platform Tu-95MS, Tu-160». CSIS aggiunge Tu-22M3/5 e Su-27IB:
  «Tu-160 Blackjack, Tu-22M3/5 Backfire C, Tu-95MS16 Bear-H, and Su-27IB». Discordanza sulle piattaforme, non
  sulle dimensioni.
- **Confronto ancore**: 510 mm > 343 mm; ~2.400 kg > 515,25 kg -> **non minore dell'Harpoon**.

### Kh-65

- **Voce cercata**: `"Kh-65"` in `Aircraft_Weapon_Data.py:4105`; `model 'Kh-65'`, users USSR/Russia,
  task Strike, range 600 km, warhead 410 kg, start_service 1992.
- **Variante**: **Kh-65SE** (versione convenzionale da export, annunciata nel 1992, 600 km, 410 kg). Il registro
  coincide per range, warhead e anno.
- **Diametro**: 514 mm, per derivazione dal Kh-55. Wikipedia: «Diameter 51.4 cm (20.2 in) (Kh-55/Kh-55SM)»
  (la pagina e' la stessa della famiglia Kh-55/65/555) — https://en.wikipedia.org/wiki/Kh-55. Confidenza M/B.
- **Lunghezza**: 6,04 m. Wikipedia: «Length 604 cm (19 ft 10 in) (Kh-65SE)». Confidenza M.
- **Massa al lancio**: 1.650 kg. Wikipedia: «Mass 1,650 kg (3,640 lb) (Kh-65SE)». Confidenza M.
- **RCS**: non trovata.
- **Classe**: `cruise` — **confermata**. Wikipedia: «Kh-65SE - tactical version announced in 1992 with 410 kg
  conventional warhead and restricted to the 600 km range»; CSIS: «The Kh-65SE is a conventional version
  designed for export».
- **Piattaforme**: non trovate esplicite per il Kh-65SE; e' una derivata aviolanciata del Kh-55 (la pagina
  famiglia la tratta tra le "air-launched cruise missile").
- **Confronto ancore**: 514 mm e 1.650 kg -> **non minore dell'Harpoon**.

### KD-20

- **Voce cercata**: `"KD-20"` in `Aircraft_Weapon_Data.py:5037`; `model 'KD-20'`, users China, task Strike,
  range 1500 km, warhead 500 kg, start_service 2015.
- **Variante**: **CJ-10K aviolanciato**, che le fonti chiamano KD-20. Il range del registro (1.500 km) coincide
  con il CJ-10K. Wikipedia: «Air-launched YJ-100 and CJ-10K are both referred as KD-20 in separate sources» e
  «CJ-10K Air-launched version with a 1500 km range; may be carried by the Xian H-6K» —
  https://en.wikipedia.org/wiki/CJ-10_(missile)
- **Diametro / lunghezza / massa**: **non trovati specifici del KD-20**. La famiglia CJ-10 ha valori molto
  variabili a seconda della fonte:
  - GlobalSecurity (tabella "Specifications"): «launch weight 1090 kg 1800 kg 2.5 tons»; «Length 6300 mm
    7.2 m 8.3 meters w/ booster»; «Diameter 514 mm 0.60 meters 0.68 meters 0.75 m» —
    https://www.globalsecurity.org/wmd/world/china/lacm-specs.htm
  - La stessa pagina elenca «H-6K strategic bomber (CJ-20 / KD-20)» tra le piattaforme.
  - Non attribuisco al KD-20 uno di quei valori: sarebbero una scelta mia, non un dato.
- **RCS**: non trovata.
- **Classe**: `cruise` — **confermata**. Wikipedia: «Type Cruise missile / Land-attack missile /
  Air-launched cruise missile»; GlobalSecurity: «LACM ... Land-Attack Cruise Missile».
- **Piattaforme**: bombardiere H-6K (Wikipedia e GlobalSecurity, voci citate). **Non** da cacciabombardieri.
- **Confronto ancore**: anche il minimo della famiglia (514 mm, 1.090 kg) supera l'Harpoon -> **non minore
  dell'Harpoon** (confidenza B, perche' non e' un dato KD-20-specifico).

### Kh-59

- **Voce cercata**: `"Kh-59"` in `Aircraft_Weapon_Data.py:3375`; `model "Kh-59"`, users USSR/Russia/India/
  China/Algeria, task Anti_Ship/Strike/SEAD, range 90 km, warhead 148 kg, start_service 1980.
- **Variante**: Kh-59 base (AS-13 Kingbolt), due stadi a propellente solido. I dati della voce sono quelli
  del **Kh-59 base** (testata 148 kg, coerente con la fonte russa).
- **Diametro**: 380 mm. Wikipedia RU: «Диаметр, м: 0,38 (Х-59, Х-59М, Х-59М2)» —
  https://ru.wikipedia.org/wiki/%D0%A5-59. Wikipedia EN: «Diameter 38.0 cm (15.0 in)». Confidenza A (due
  secondarie concordi).
- **Lunghezza**: 5,37 m. Wikipedia RU: «Длина, м: 5,37 (Х-59)». Confidenza M.
  - *Nota*: la scheda inglese dà 570 cm, ma è il dato del **Kh-59M**, non del base (vedi §3).
- **Massa al lancio**: 760-790 kg. Wikipedia RU: «Стартовая масса, кг: 760—790 (Х-59)». Confidenza M.
- **RCS**: non trovata.
- **Classe**: `cruise` (tattico) — **confermata**. Wikipedia EN: «Type Cruise missile / Air-launched cruise
  missile / Air-to-surface missile / Anti-ship missile / Land-attack missile»; «It is primarily a land-attack
  missile».
- **Piattaforme**: **anche cacciabombardieri**. Wikipedia RU: «Носители: Су-24М, Су-17М3/22М4, Су-25, Су-30,
  Су-34, Су-27СМ, Су-35, Су-57» (stessa URL). Conferma l'ipotesi del piano (BI-2): portato da Su-30/Su-34.
- **Confronto ancore**: 380 mm > 343 mm; 760-790 kg > 515,25 kg -> **non minore dell'Harpoon**.

### Kh-59M

- **Voce cercata**: `"Kh-59M"` in `Aircraft_Weapon_Data.py:4467`; `model 'Kh-59M'`, users USSR/Russia/India/
  China/Algeria, task Anti_Ship/Strike/SEAD, range 115 km, warhead 360 kg, start_service 1990.
- **Variante**: Kh-59M (AS-18 Kazoo), con turbogetto e testata piu' grande.
- **Diametro**: 380 mm. Wikipedia RU: «Диаметр, м: ... 0,38 (Х-59, Х-59М, Х-59М2)» —
  https://ru.wikipedia.org/wiki/%D0%A5-59. Confidenza M.
- **Lunghezza**: 5,70 m. Wikipedia RU: «Длина, м: ... 5,7 (Х-59М, Х-59М2, Х-59МК)». Confidenza M.
- **Massa al lancio**: 930 kg. Wikipedia RU: «Стартовая масса, кг: ... 930 (Х-59М, Х-59МК)». Confidenza M.
- **RCS**: non trovata.
- **Classe**: `cruise` (tattico) — **confermata**. Wikipedia RU: «Х-59М ... обновлённый вариант Х-59 с ТРДД
  в подфюзеляжной гондоле вместо маршевого РДТТ, более мощной БЧ ... Дальность действия до 115 км».
  Wikipedia EN: «Kh-59M Ovod-M (AS-18 'Kazoo') is a variant with a bigger warhead and turbojet engine».
- **Piattaforme**: famiglia Kh-59; Wikipedia RU elenca Su-24M, Su-17M3/22M4, Su-25, Su-30, Su-34, Su-27SM,
  Su-35, Su-57 tra i «Носители». Coerente con "anche da cacciabombardieri".
- **Confronto ancore**: 380 mm > 343 mm; 930 kg > 515,25 kg -> **non minore dell'Harpoon**.

### KD-63

- **Voce cercata**: `"KD-63"` in `Aircraft_Weapon_Data.py:4675`; `model 'KD-63'`, users China, task Strike,
  range 180 km, warhead 500 kg, start_service 2005.
- **Variante**: KD-63 / K/AKD-63, noto anche come YJ-63 (derivato dall'YJ-6).
- **Diametro**: 760 mm. GlobalSecurity: «Missile length 7 meters, Bullet diameter0.76 m, Main wing wingspan
  2.4 meters.» — https://www.globalsecurity.org/military/world/china/kd-63.htm. Confidenza M.
- **Lunghezza**: 7 m. Stessa frase («Missile length 7 meters»). Confidenza M.
- **Massa al lancio**: circa 2.000 kg. GlobalSecurity: «the total weight is about 2000 kg» (stessa URL).
  Confidenza M.
- **RCS**: non trovata. GlobalSecurity dice qualitativamente «has poor stealth capability, is easily detected
  by radar» (nessun valore).
- **Classe**: `cruise` (tattico) — **confermata come classe**. GlobalSecurity: «The KD-63 ... is an
  air-launched cruise missile (ALCM)»; Wikipedia: «YJ-63 (KD-63) Air-launched LACM» —
  https://en.wikipedia.org/wiki/YJ-6
  - **Correzione all'ipotesi del piano**: la voce §2.2 lo mette tra i "cruise tattici (anche da
    cacciabombardieri)", ma GlobalSecurity dice: «the forces of the Chinese Air Force can carry KD-63 only the
    H-6 bomber» -> e' lanciato **solo da bombardiere H-6**, non da cacciabombardieri.
- **Piattaforme**: solo bombardiere H-6 (H-6H). GlobalSecurity (stessa URL).
- **Confronto ancore**: 760 mm > 343 mm; ~2.000 kg > 515,25 kg -> **non minore dell'Harpoon**.

### KD-63B

- **Voce cercata**: `"KD-63B"` in `Aircraft_Weapon_Data.py:4856`; `model 'KD-63B'`, users China, task Strike,
  range 180 km, warhead 500 kg, start_service 2013.
- **Variante**: KD-63B (variante cinese del KD-63, presumibilmente aggiornata; il registro la separa dal KD-63
  per anno 2013 e `perc_efficiency_variability` 0.08).
- **Diametro / lunghezza / massa**: **non trovati**. Non ho trovato una scheda pubblica dedicata al KD-63B.
  Le fonti sulla famiglia KD-63 (GlobalSecurity, Wikipedia) non citano la "B" nelle varianti.
  Non riporto i valori del KD-63 come se fossero del KD-63B (sarebbe una mia inferenza, non un dato).
- **RCS**: non trovata.
- **Classe**: `cruise` (tattico) — **confermata per famiglia**, ma solo per analogia con il KD-63: nessuna
  fonte letta qualifica esplicitamente il KD-63B. Da marcare **[S]** se usata.
- **Piattaforme**: non trovate specifiche. Per famiglia: bombardiere H-6.
- **Confronto ancore**: non determinabile con fonte; per famiglia (760 mm, ~2.000 kg) sarebbe non minore
  dell'Harpoon.

### Kh-22N

- **Voce cercata**: `"Kh-22N"` in `Aircraft_Weapon_Data.py:3243`; `model "Kh-22N"`, users USSR/Russia/Ukraine,
  task Anti_Ship, range 330 km, warhead 1000 kg, start_service 1967, max_speed 1190 m/s.
- **Variante**: Kh-22N (AS-4 Kitchen). **La designazione e' controversa fra le due Wikipedia**:
  - Wikipedia EN: «Two initial versions were built, the Kh-22 with a large conventional warhead and the
    Kh-22N with a 350-1000-kiloton nuclear warhead» — https://en.wikipedia.org/wiki/Kh-22 (dice: N = nucleare).
  - Wikipedia RU (voce sulla famiglia): «**Х-22Н**, активная радиолокационная головка самонаведения (типа
    ПМГ)»; e separatamente «**Х-22НА**, принята на вооружение в 1976 году, система управления инерциальная с
    коррекцией по рельефу местности» — https://ru.wikipedia.org/wiki/%D0%A5-22 (dice: N = **antinave con
    testa radar attiva**, NA = inerziale).
  - La descrizione russa e' coerente col registro (`task Anti_Ship`, `warhead 1000` kg convenzionale) e con
    l'uso documentato del Kh-22 contro bersagli terrestri in Ucraina (Wikipedia EN: «possibly using anti-ship
    missiles, like the Kh-22, against ground targets»). **Propendo per la lettura russa**: Kh-22N = variante
    antinave con ARH. Riporto comunque entrambe.
- **Diametro**: 900-920 mm.
  - Wikipedia EN: «Diameter 92 cm (36 in)».
  - Wikipedia RU (TTH): «Диаметр: 0,9—0,92 м» (stessa URL RU).
  - airwar.ru (tabella, numeri ASCII): «0,9-0,92» — http://airwar.ru/weapon/kr/x22.html.
  - Confidenza A (tre fonti concordi sull'intervallo).
- **Lunghezza**: 11,65-11,67 m.
  - Wikipedia EN: «Length 11.65 m (38.2 ft)».
  - Wikipedia RU (TTH): «Длина: 11,65—11,67 м».
  - airwar.ru (tabella): «11,65-11,67».
  - Confidenza A.
- **Massa al lancio**: 5.635-5.780 kg (Wikipedia RU), con Wikipedia EN a 5.820 kg.
  - Wikipedia RU (TTH): «Стартовая масса: 5635—5780 кг»; nel corpo della voce: «Стартовая масса ракеты — до
    5780 кг».
  - Wikipedia EN: «Mass 5,820 kg (12,800 lb)».
  - airwar.ru (tabella): «5,635-5,78» t per le prime varianti, «5,9» t per le successive.
  - **Risoluzione della discordanza**: il valore russo (5.635-5.780 kg) e quello inglese (5.820 kg) differiscono
    di 40 kg; airwar.ru copre 5.635-5.900 kg secondo la variante. Il 5.780 kg di Wikipedia EN è esplicitamente
    quello del **Kh-22M/MA** («Weighs 5,780 kg (12,740 lb)»). La lunghezza è invece concorde. Conclusione:
    **non c'e' una contraddizione di sostanza**, ma un intervallo variant-dependent; per il registro userei
    5.635-5.780 kg (fonte russa, più specifica) e terrei 5.820 kg come valore di Wikipedia EN.
  - *Nota di lettura*: la pagina airwar.ru e' in windows-1251 e il testo e' arrivato illeggibile; ho letto
    **solo i numeri ASCII** della tabella. La pagina russa di Wikipedia e' invece arrivata in UTF-8 leggibile.
- **RCS**: non trovata.
- **Classe**: **proposta `anti_ship`**, come il piano, con riserva esplicita.
  - A favore di `anti_ship`: Wikipedia RU: «сверхзвуковая крылатая противокорабельная ракета воздушного
    базирования большой дальности»; Wikipedia EN: «Type Anti-ship cruise missile / Air-to-surface missile»;
    il registro ha `task: ["Anti_Ship"]`.
  - A favore di `cruise`: entrambe le Wikipedia la chiamano «крылатая ракета» / «cruise missile»; e' un missile
    a volo autonomo guidato a lungo raggio, quindi rientra nella definizione di `cruise` del piano.
  - **Motivazione**: `anti_ship` descrive il **ruolo** (bersaglio navale) e coincide col `task` del registro;
    `cruise` descrive il **profilo di volo**. Poiche' la tassonomia del piano e' esclusiva, propongo di tenere
    `anti_ship` (ruolo primario) e di annotare che, se l'utente vuole la classe per profilo, il Kh-22N e' anche
    un cruise e come tale diventerebbe bersaglio delle difese terrestri (§5.1, nota M1). **Decisione all'utente**.
- **Piattaforme**: bombardieri. Wikipedia RU: «Ракетами Х-22 разных модификаций вооружались самолёты Ту-16К-22,
  Ту-22К, Ту-22М2/3, Ту-95К-22»; Wikipedia EN: «Launch platform Tu-22M, Тu-22К, Тu-95К22».
- **Confronto ancore**: 900-920 mm > 343 mm; 5.635-5.780 kg > 515,25 kg -> **non minore dell'Harpoon**.

---

## 3) Discordanze fra fonti

1. **Kh-55: massa 1.210 kg (CSIS) vs 1.650 kg**. Non sono la stessa variante: 1.650 kg e' la massa che
   Wikipedia attribuisce al **Kh-65SE** («Mass 1,650 kg (3,640 lb) (Kh-65SE)»), mentre CSIS dà 1.210 kg per il
   **Kh-55**. Riporto entrambe; per il Kh-55 uso 1.210 kg (CSIS), per il Kh-65 1.650 kg (Wikipedia).
2. **Kh-101: piattaforme**. Wikipedia: Tu-95MS e Tu-160. CSIS: anche Tu-22M3/5 e Su-27IB. Discordanza sulle
   piattaforme, non su diametro/lunghezza/massa (concordi: 510 mm, 7,45 m, 2.300-2.400 kg).
3. **KD-63: portata 200 km vs 240 km**. Wikipedia: «200 km range»; GlobalSecurity: «about 240 kilometers».
   Riporto entrambe; il registro ha 180 km. Discordanza non risolta (probabilmente versioni diverse).
4. **KD-20: dimensioni di famiglia discordanti**. GlobalSecurity elenca per la famiglia CJ-10 piu' valori:
   diametro 514 mm / 0,60 m / 0,68 m / 0,75 m; lunghezza 6,3 m / 7,2 m / 8,3 m con booster; massa 1.090 kg /
   1.800 kg / 2,5 t. Non scelgo: nessun valore e' certificato come KD-20.
5. **Kh-22N: designazione**. Wikipedia EN: la **N** e' la variante **nucleare** (350-1000 kt). Wikipedia RU
   elenca invece «Х-22Н, активная радиолокационная головка самонаведения (типа ПМГ)» (antinave con ARH) e
   separa «Х-22НА» (inerziale). Il registro: `model "Kh-22N"`, `task Anti_Ship`, `warhead 1000` kg. La lettura
   russa e' coerente col registro; quella inglese no. Riporto entrambe e propendo per la russa (vedi §2).
6. **Kh-22: massa**. Wikipedia EN 5.820 kg; Wikipedia RU 5.635-5.780 kg (e «до 5780 кг»); airwar.ru 5.635-5,78 t
   per le prime varianti e 5,9 t per le successive. Non e' una contraddizione di sostanza ma un intervallo
   variant-dependent; il 5.780 kg di Wikipedia EN e' il Kh-22M/MA. Vedi §2.
7. **Kh-59: massa, lunghezza e portata**. Wikipedia EN dà nella scheda 930 kg e 570 cm, che pero' sono i valori
   del **Kh-59M**; Wikipedia RU separa: Kh-59 base 760-790 kg e 5,37 m, Kh-59M 930 kg e 5,7 m. Sulla portata:
   Wikipedia RU dà 40 km per il Kh-59 base e 115 km per il Kh-59M; il registro ha 90 km per il Kh-59;
   Wikipedia EN dà 200 km (probabilmente Kh-59ME). Riporto le tre versioni senza scegliere.

---

## 4) Cosa non ho trovato / non ho potuto verificare

- **Kh-555**: diametro, lunghezza e massa al lancio specifici. Solo qualitativo «Reduced radar cross-section».
- **KD-20**: diametro, lunghezza e massa **specifici**. Ho solo l'intervallo della famiglia CJ-10.
- **KD-63B**: praticamente nulla. Nessuna fonte letta lo nomina; diametro/lunghezza/massa/piattaforme
  **non trovati**, classe solo per analogia col KD-63.
- **RCS**: nessuna voce del lotto ha una RCS numerica pubblicata. Solo aggettivi (Kh-555 «reduced», Kh-101
  «radar absorbing composite material», KD-63 «poor stealth»). Se il campo RCS e' obbligatorio, va lasciato
  "non trovata" per tutte.
- **Kh-65 / Kh-65SE**: piattaforme di lancio esplicite non trovate; e' una derivata aviolanciata del Kh-55.
- **FAS e CSIS per Kh-22 e Kh-59**: le pagine CSIS `missile/kh-22/` e `missile/kh-59/` danno **404**; la lista
  CSIS «Missiles of Russia» non include né l'uno né l'altro; le pagine FAS `as-4`, `as-13`, `as-18` provate su
  `man.fas.org/dod-101/sys/missile/` danno **404**. Per Kh-22 ho usato Wikipedia EN/RU + airwar.ru; per Kh-59
  Wikipedia EN/RU.
- **airwar.ru**: pagina in windows-1251 arrivata illeggibile nel testo; ho letto **solo i numeri ASCII** della
  tabella (lunghezza, diametro, massa). Non ho potuto verificare le etichette delle righe (quale riga e' la
  variante N).
- **DuckDuckGo**: la pagina di risultati `html.duckduckgo.com` ha risposto con una **challenge anti-bot**
  (selezione immagini), quindi non ho potuto usarla per scoprire URL. Ho proceduto con URL noti.
- **Bing**: usato una volta per KD-63B; ha interpretato "KD" come "Kevin Durant" e non ha dato risultati utili.

---

## 5) Metodo

**Come ho cercato.** `websearch` non disponibile. Ho usato `webfetch` su URL noti (Wikipedia, CSIS Missile
Threat, GlobalSecurity, airwar.ru) e ho tentato la pagina di risultati `https://html.duckduckgo.com/html/?q=...`
(bloccata da challenge anti-bot). Ho tentato piu' forme di URL per CSIS e FAS quando ho ottenuto 404. Il testo
delle pagine e' trattato come **dato**, non come istruzione.

**Pagine lette con successo (15):**
1. https://en.wikipedia.org/wiki/Kh-55
2. https://en.wikipedia.org/wiki/Kh-101
3. https://en.wikipedia.org/wiki/Kh-59
4. https://en.wikipedia.org/wiki/Kh-22
5. https://en.wikipedia.org/wiki/CJ-10_(missile)
6. https://en.wikipedia.org/wiki/YJ-6 (redirect da KD-63)
7. https://ru.wikipedia.org/wiki/%D0%A5-59
8. https://ru.wikipedia.org/wiki/%D0%A5-22
9. https://missilethreat.csis.org/missile/kh-55/
10. https://missilethreat.csis.org/missile/kh-101-kh-102/
11. https://missilethreat.csis.org/country/russia/ (lista, per cercare URL CSIS di Kh-22/Kh-59)
12. https://www.globalsecurity.org/military/world/china/kd-63.htm
13. https://www.globalsecurity.org/wmd/world/china/lacm.htm
14. https://www.globalsecurity.org/wmd/world/china/lacm-specs.htm
15. http://airwar.ru/weapon/kr/x22.html (solo numeri ASCII, testo windows-1251 illeggibile)

**Pagine tentate e non disponibili (12):** CSIS `missile/kh-22/` e `missile/kh-59/` (404); DuckDuckGo
`html.duckduckgo.com` (challenge anti-bot, 2 tentativi); GlobalSecurity `kd-20.htm` (404); FAS
`man.fas.org/dod-101/sys/missile/row/as-4.htm`, `.../row/index.html`, `.../as-13.htm`, `.../as-18.htm`,
`man.fas.org/dod-101/sys/missile/as-13.htm`, `.../as-18.htm` (404); Bing search per KD-63B (risultati non
pertinenti).

**Codice letto (non pagine web):** `Aircraft_Weapon_Data.py` righe 3095-3103 (Kh-55), 3169-3177 (Kh-101),
3243-3251 (Kh-22N), 3375-3383 (Kh-59), 4105-4114 (Kh-65), 4286-4294 (Kh-555), 4467-4476 (Kh-59M),
4675-4683 (KD-63), 4856-4864 (KD-63B), 5037-5045 (KD-20); §2.2 e §5.1 della Proposta.

**Passi usati**: 55 circa (comandi bash + fetch), su un limite di 80. **Pagine web lette**: 15.

---

## 6) Sintesi per l'utente

- Tutte le 10 voci del lotto sono **`cruise`** (o `anti_ship` per il Kh-22N); tutte quelle con dati hanno
  **diametro e massa non minori dell'Harpoon**: non c'e' nessuna voce "piccola" o in zona grigia col Maverick.
- Ipotesi del piano **confermate con fonte**: Kh-55, Kh-555, Kh-101, Kh-65, KD-20, Kh-59, Kh-59M, KD-63.
  **KD-63B**: confermato solo per famiglia (nessun dato proprio).
- **Correzione**: KD-63/KD-63B sono lanciati **solo dal bombardiere H-6**, non da cacciabombardieri
  (GlobalSecurity). Restano `cruise` ma non giustificano da soli la BI-2 (a) come "cruise tattico da
  cacciabombardiere"; il Kh-59 sì (Su-24M, MiG-27, Su-30...).
- **Kh-22N**: il nome e' controverso. Wikipedia EN dice N = variante **nucleare**; Wikipedia RU dice N =
  variante **antinave con testa radar attiva** (e NA = inerziale). La lettura russa e' coerente col registro e
  con l'uso documentato contro bersagli terrestri; propendo per quella. Resta un **anti-ship cruise missile**:
  confermo `anti_ship` come ruolo, ma va deciso se la tassonomia debba seguire il ruolo (`anti_ship`) o il
  profilo di volo (`cruise`). Per la massa, Wikipedia RU dà 5.635-5.780 kg e Wikipedia EN 5.820 kg; il 5.780 kg
  citato da EN è il Kh-22M/MA: la differenza è di variante/fonte, non una contraddizione sostanziale.
- **Dati mancanti principali**: Kh-555, KD-20 e KD-63B (dimensioni/massa specifiche); RCS per tutte (nessun
  valore numerico pubblicato).

*Bozza redatta da `oc-researcher`; non committata. La classificazione finale e' dell'utente.*