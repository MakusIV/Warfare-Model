# Ricerca dati — Blocco 0 BI, LOTTO L3 (tattici russi corti e Kh-29)

Bozza di `oc-researcher`, 2026-11-07. Fonti web lette in questa sessione; nessun valore inventato. `websearch`
non disponibile: ricerca con `webfetch` e pagine risultati DuckDuckGo HTML. Le due ancore (AGM-65D e AGM-84A
aviolanciato) sono quelle fornite dal principale e non sono state ricercate: qui vengono solo usate per il
confronto.

Riferimenti nel repo (letti con `grep -n` / `sed -n`):
- §2.2 (tabella armi→classe) e §5.1 (blocco 0): `Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`.
- `Code/Dynamic_War_Manager/Source/Asset/Aircraft_Weapon_Data.py` — voci `AIR_WEAPONS['MISSILES_ASM']`:
  `Kh-66` (riga 3301), `Kh-25ML` (3449), `Kh-25MR` (3523), `Kh-25MPU` (3597), `Kh-25MP` (3626), `Kh-29L`
  (3655), `Kh-29T` (3728), `Kh-29TE` (3804). Nessuna di queste voci è nei registri navali.

Ancore di confronto (non ricercate; dal compito):
- **Maverick AGM-65D**: diametro 304,8 mm, lunghezza 2,49 m, massa 218,25–220 kg.
- **Harpoon AGM-84A aviolanciato**: diametro 343 mm, lunghezza 3,79–3,85 m, massa 515,25 kg.

## 1) Tabella riassuntiva

| Voce (registro) | Variante cercata | Classe proposta (ipotesi del piano) | Diametro | Lunghezza | Massa al lancio | RCS | Confronto con le ancore | Confidenza |
|---|---|---|---|---|---|---|---|---|
| **Kh-25ML** (`:3449`) | Kh-25ML, izd. 713, laser semi-attiva, AS-10 Karen | `tactical` — **confermata** | 275 mm | 3,705 m (3,57 m FAS; 3,75 m airwar) | 299 kg (299±8) / 300 kg | non pubblicata | **non maggiore del Maverick** per diametro (275 < 304,8 mm); massa 299 kg > 218–220 kg ma molto < 515,25 kg → proposta **False** | A (diametro, massa); A con discordanza (lunghezza) |
| **Kh-25MR** (`:3523`) | Kh-25MR/Kh-25R, izd. 714, radiocomando, AS-10 | `tactical` — **confermata** | 275 mm (0,27 m Astronautix) | 3,830 m (ru-wiki) / 3,69 m (Astronautix) | 320 kg (ru-wiki) / 300 kg (Astronautix) | non pubblicata | **non maggiore del Maverick** per diametro (275 < 304,8 mm); massa 300–320 kg > 218–220 kg ma < 515,25 kg → proposta **False** | M (una fonte per valore; v. discordanze) |
| **Kh-25MP** (`:3626`) | Kh-25MP, izd. 711, antiradar passiva, AS-12 Kegler | `arm` — **confermata** | 275 mm | 4,194/4,294 m (ru-wiki); 4,255/4,355 m (en-wiki) | 315 kg (315±8) / 320 kg FAS | non pubblicata | **non maggiore del Maverick** per diametro (275 < 304,8 mm); massa 315–320 kg > 218–220 kg ma < 515,25 kg → proposta **False** | A (diametro, massa); M (lunghezza, discorde) |
| **Kh-25MPU** (`:3597`) | Kh-25MPU, MP modernizzato (gamme Roland/Crotale, guida inerziale) | `arm` — **confermata** | 275 mm | 4,255 m | 315 kg | non pubblicata | **non maggiore del Maverick** per diametro (275 < 304,8 mm); massa 315 kg > 218–220 kg ma < 515,25 kg → proposta **False** | M (fonte specifica unica; coerente con la cellula MP) |
| **Kh-66** (`:3301`) | Kh-66, izd. 66, beam-riding, AS-7 Kerry | `tactical` — **confermata** | 275 mm | 3,63 m | 278 kg (FAS) / 290 kg (airwar) | non pubblicata | **non maggiore del Maverick** per diametro (275 < 304,8 mm); massa 278–290 kg > 218–220 kg ma < 515,25 kg → proposta **False** | A (diametro, lunghezza); M (massa, discorde) |
| **Kh-29L** (`:3655`) | Kh-29L, izd. 63, laser semi-attiva, AS-14 Kedge-A | `tactical` — **confermata**; zona grigia **risolta: True** | 380 mm | 3,90 m (en-wiki) / 3,875 m (FAS) | 660 kg (en-wiki) / 657 kg (FAS) | non pubblicata | **non minore dell'Harpoon** (380 > 343 mm; 657–660 > 515,25 kg; 3,875–3,90 > 3,79–3,85 m) → proposta **True** | A (due secondarie concordi) |
| **Kh-29T** (`:3728`) | Kh-29T, izd. 64, TV, AS-14 Kedge-B | `tactical` — **confermata**; zona grigia **risolta: True** | 380 mm | 3,90 m (en-wiki) / 3,875 m (FAS) | 685 kg (en-wiki) / 680 kg (FAS) | non pubblicata | **non minore dell'Harpoon** (380 > 343 mm; 680–685 > 515,25 kg; 3,875–3,90 > 3,79–3,85 m) → proposta **True** | A (due secondarie concordi) |
| **Kh-29TE** (`:3804`) | Kh-29TE, sviluppo export a lungo raggio (30 km) del Kh-29T | `tactical` — **confermata**; zona grigia **risolta: True** | 380 mm | 3,875 m | 690 kg | non pubblicata | **non minore dell'Harpoon** (380 > 343 mm; 690 > 515,25 kg; 3,875 > 3,79–3,85 m) → proposta **True** | M (una secondaria; dato Rosoboronexport via Wikipedia) |

Sintesi del confronto: **tutti i Kh-25 e il Kh-66 sono più stretti del Maverick** (275 mm contro 304,8 mm), anche
se pesano 278–320 kg contro 218–220 kg. **Tutti i Kh-29 sono più grandi dell'Harpoon aviolanciato in diametro,
massa e lunghezza**: la "zona grigia" ipotizzata dal piano si risolve quindi verso l'alto (True), non verso il
basso. Nessuna RCS è pubblicata per queste armi.

## 2) Dettaglio per voce

### 2.1 Kh-25ML (`Aircraft_Weapon_Data.py:3449`)

Voce del registro: `model` "Kh-25ML", `users` USSR/Russia/India/Syria/Iraq/Libya/Algeria/Vietnam, `task`
Anti_Ship/Strike/SEAD, `start_service` 1975, `warhead` 90 kg, `range` 11 km, `max_speed` 870 m/s, commento
"laser guided". Variante identificata: **Kh-25ML** (izdeliye 713, laser semi-attiva 24N1, NATO AS-10 Karen).

- **Diametro 275 mm.** Fonti:
  - `https://en.wikipedia.org/wiki/Kh-25`, infobox: "Diameter 27.5 cm (10.8 in)".
  - `https://ru.wikipedia.org/wiki/Х-25`, tabella TTC, riga "диаметр, мм": "275".
  - `https://web.archive.org/web/20160304051639/http://fas.org/man/dod-101/sys/missile/row/as-10.htm`,
    tabella: "Diameter 0.275 m".
  - `https://airwar.ru/weapon/avz/x25.html`, tabella finale (numeri ASCII leggibili, etichette in windows-1251):
    "0,275".
  Confidenza **A** (quattro fonti concordi).
- **Lunghezza 3,705 m.** Fonte: `https://en.wikipedia.org/wiki/Kh-25`, infobox: "Kh-25ML :370.5 cm (12 ft 2 in)";
  `https://ru.wikipedia.org/wiki/Х-25`, tabella, riga "длина, мм": "3705" (colonna Kh-25ML). Confidenza **A**
  (due concordi), ma con discordanza: FAS dà "Total length 3.57 m" e airwar.ru "3,75" (v. §3).
- **Massa al lancio 299 kg (299±8).** Fonti: Wikipedia EN "Kh-25ML :299 kg (659 lb)"; ru-wiki, riga
  "стартовая масса, кг": "299±8". FAS dà "300 kg": tre valori concordi entro 1 kg → confidenza **A**.
  (airwar.ru dà 316–320 kg per la famiglia Kh-25, non per la ML: v. §3.)
- **RCS: non pubblicata** (nessuna delle fonti consultate riporta una RCS).

Classe: **`tactical`** — missile aria-superficie tattico a corto raggio (10–11 km), guida laser. Ipotesi del piano
**confermata**. Confronto: diametro 275 mm < 304,8 mm (Maverick) → **non maggiore del Maverick**; la massa (299 kg)
è superiore a quella del Maverick ma molto inferiore all'Harpoon. Proposta: **`ad_detectable` False** (il diametro,
proxy della sezione radar, è sotto l'ancora bassa; la massa non raggiunge l'ancora alta).

### 2.2 Kh-25MR (`Aircraft_Weapon_Data.py:3523`)

Voce del registro: `model` "Kh-25MR", `users` USSR/Russia/India/Syria/Iraq/Libya/Algeria, `task`
Anti_Ship/Strike/SEAD, `start_service` 1975, `warhead` 140 kg, `range` 11 km, `max_speed` 870 m/s, commento
"radar guided". Variante identificata: **Kh-25MR / Kh-25R** (izdeliye 714, guida **radiocomandata**, non radar;
NATO AS-10 Karen). Il commento del registro "radar guided" è impreciso rispetto alle fonti (che dicono
radio-command / Delta), ma la variante è quella.

- **Diametro 275 mm.** Fonte: `https://ru.wikipedia.org/wiki/Х-25`, tabella, riga "диаметр, мм": "275";
  `https://en.wikipedia.org/wiki/Kh-25` dà il diametro 27,5 cm per la famiglia ("Diameter 27.5 cm (10.8 in)").
  `https://www.astronautix.com/k/kh-25mr.html` dà "Diameter0.27 m (0.90 ft)" (arrotondato). Confidenza **A**
  (due fonti a 275 mm; Astronautix arrotonda a 0,27 m).
- **Lunghezza 3,830 m.** Fonte: `https://ru.wikipedia.org/wiki/Х-25`, tabella, riga "длина, мм": "3830" (colonna
  Kh-25MR). **Discordanza**: `https://www.astronautix.com/k/kh-25mr.html` dà "Height3.69 m (12.09 ft)". Riporto
  entrambe, non scelgo. Confidenza **M** per ciascuna.
- **Massa al lancio 320 kg.** Fonte: `https://ru.wikipedia.org/wiki/Х-25`, tabella, riga "стартовая масса, кг":
  "320" (colonna Kh-25MR). **Discordanza**: Astronautix dà "Gross mass300 kg (660 lb)". Riporto entrambe.
  Confidenza **M** per ciascuna.
- **RCS: non pubblicata.**

Classe: **`tactical`** — missile tattico a corto raggio con guida radiocomandata. Ipotesi del piano
**confermata**. Confronto: diametro 275 mm < 304,8 mm → **non maggiore del Maverick**; massa 300–320 kg >
218–220 kg ma < 515,25 kg. Proposta: **`ad_detectable` False**.

### 2.3 Kh-25MP (`Aircraft_Weapon_Data.py:3626`)

Voce del registro: `model` "Kh-25MP", `users` USSR/Russia/India/Syria/Iraq/Libya, `task` SEAD, `start_service`
1975, `warhead` 90 kg, `range` 18 km, `max_speed` 870 m/s, commento "antiradiation". Variante identificata:
**Kh-25MP** (izdeliye 711, seeker passivo PRGS-1VP/2VP, NATO AS-12 Kegler).

- **Diametro 275 mm.** Fonti: `https://en.wikipedia.org/wiki/Kh-25` ("Diameter 27.5 cm (10.8 in)");
  `https://ru.wikipedia.org/wiki/Х-25`, tabella, "275". Confidenza **A**.
- **Lunghezza 4,194/4,294 m.** Fonte: `https://ru.wikipedia.org/wiki/Х-25`, tabella, riga "длина, мм":
  "4194/4294" (due versioni del seeker, 1VP/2VP). **Discordanza**: `https://en.wikipedia.org/wiki/Kh-25` dà
  "Kh-25MP 1VP :425.5 cm (167.5 in)" e "Kh-25MP 2VP :435.5 cm (171.5 in)" (10 cm in più). Riporto entrambe,
  confidenza **M** per ciascuna.
- **Massa al lancio 315 kg (315±8).** Fonti: `https://en.wikipedia.org/wiki/Kh-25`, "Kh-25MP :315 kg (694 lb)";
  `https://ru.wikipedia.org/wiki/Х-25`, tabella, "315±8". FAS dà "Kh-25MP 320 kg" (`.../as-10.htm`). Tre valori
  concordi entro 5 kg → confidenza **A**.
- **RCS: non pubblicata.**

Classe: **`arm`** — missile antiradiazione (SEAD). Ipotesi del piano **confermata**. Confronto: diametro 275 mm <
304,8 mm → **non maggiore del Maverick**; massa 315–320 kg > 218–220 kg ma < 515,25 kg. Proposta:
**`ad_detectable` False** (coerente con il piano: ARM piccoli non rilevabili; il Kh-25MP è nella stessa classe
dimensionale del Maverick, non dell'Harpoon). Nota: la portata delle fonti (40 km) è maggiore del `range` 18 km
del registro (v. §4).

### 2.4 Kh-25MPU (`Aircraft_Weapon_Data.py:3597`)

Voce del registro: `model` "Kh-25MPU", `users` USSR/Russia/India/Syria, `task` SEAD, `start_service` 1975 (con
commento "1978 --1982 vers. U"), `warhead` 90 kg, `range` 30 km, `max_speed` 870 m/s, commento "antiradiation".
Variante identificata: **Kh-25MPU** (MP modernizzato: seeker a banda estesa per Roland/Crotale, guida inerziale
per riaggancio; NATO AS-12 Kegler). Le fonti specifiche sono poche: i valori sotto sono quelli della scheda
dedicata.

- **Diametro 275 mm.** Fonte: `https://www.redstar.gr/en/russian-aerial-means/weapons/anti-radiation-missile-arm/x-25mpu-kh-25mpu-modular-anti-radiation-variant.html`,
  tabella "DIMENSIONS", riga "Diameter, m": "0,275". Confidenza **M** (una secondaria), coerente con la cellula
  Kh-25MP (275 mm, §2.3).
- **Lunghezza 4,255 m.** Fonte: stessa pagina redstar.gr, riga "Length, m": "4,255". Confidenza **M**.
- **Massa al lancio 315 kg.** Fonte: stessa pagina, riga "Maximum missile weight, kg": "315". Confidenza **M**.
  Coerente con il Kh-25MP (315±8 kg).
- **RCS: non pubblicata.**
- **Dato specifico mancante**: nessuna fonte consultata distingue nettamente i valori di MPU da quelli di MP;
  l'ipotesi che la cellula sia la stessa è coerente con la descrizione della pagina ("Evolution of the Kh-25MP
  missile") ma non è un dato esplicito. La portata della fonte ("until 60") differisce dal `range` 30 km del
  registro.

Classe: **`arm`** — missile antiradiazione. Ipotesi del piano **confermata**. Confronto: **non maggiore del
Maverick** per diametro (275 < 304,8 mm), massa 315 kg tra le due ancore ma più vicina al Maverick. Proposta:
**`ad_detectable` False**.

### 2.5 Kh-66 (`Aircraft_Weapon_Data.py:3301`)

Voce del registro: `model` "Kh-66", `users` USSR/Russia/Syria/Libya/Iraq/Egypt, `task` Anti_Ship/Strike/SEAD,
`start_service` 1967, `warhead` 111 kg, `range` 10 km, `max_speed` 600 m/s, commento "radar beam-riding".
Variante identificata: **Kh-66** (izdeliye 66, beam-riding, cellula del K-8; NATO AS-7 Kerry), il primo missile
aria-superficie tattico sovietico.

- **Diametro 275 mm.** Fonti: `https://web.archive.org/web/20160828045904/http://fas.org/man/dod-101/sys/missile/row/as-7.htm`,
  tabella "Specifications", riga "Diameter": "0.275 m"; `https://airwar.ru/weapon/avz/x66.html`, tabella finale:
  "275". Confidenza **A**.
- **Lunghezza 3,63 m.** Fonti: FAS, riga "Total length": "3.63 m"; airwar.ru, tabella: "3,63". Confidenza **A**
  (due concordi). (Per la variante rumena A921 Wikipedia dà 3,525 m: è un'altra variante, v. §3.)
- **Massa al lancio 278 kg / 290 kg.** FAS: "Weight 278 kg"; airwar.ru, tabella: "290". **Discordanza** di
  12 kg, riporto entrambe senza scegliere. Confidenza **M** per ciascuna.
- **RCS: non pubblicata.**
- Nota: il `warhead` del registro (111 kg) non coincide con le fonti (103 kg in FAS e airwar.ru); non modifico il
  registro, lo segnalo in §4.

Classe: **`tactical`** — missile tattico a corto raggio (8–10 km) con guida beam-riding. Ipotesi del piano
**confermata**. Confronto: diametro 275 mm < 304,8 mm → **non maggiore del Maverick**; massa 278–290 kg >
218–220 kg ma < 515,25 kg. Proposta: **`ad_detectable` False**.

### 2.6 Kh-29L (`Aircraft_Weapon_Data.py:3655`)

Voce del registro: `model` "Kh-29L", `users` USSR/Russia/India/China/Syria/Algeria, `task`
Anti_Ship/Strike/SEAD, `start_service` 1980, `warhead` 320 kg, `range` 10 km, `max_speed` 900 m/s, commento
"laser guided". Variante identificata: **Kh-29L** (izdeliye 63, laser semi-attiva, NATO AS-14 Kedge-A).

- **Diametro 380 mm.** Fonti: `https://en.wikipedia.org/wiki/Kh-29`, infobox: "Diameter 38.0 cm (15.0 in)";
  `https://web.archive.org/web/20160308073302/http://fas.org/man/dod-101/sys/missile/row/as-14.htm`, tabella:
  "Diameter 0.38 m". Confidenza **A** (due concordi).
- **Lunghezza 3,90 m / 3,875 m.** Fonti: Wikipedia, "Kh-29L/T: 390 cm (12 ft 10 in)"; FAS, "Total length
  3.875 m". Confidenza **A** per la fascia 3,875–3,90 m (due concordi entro 2,5 cm).
- **Massa al lancio 660 kg / 657 kg.** Fonti: Wikipedia, "Kh-29L: 660 kg (1,460 lb)" (dato Rosoboronexport);
  FAS, "Weight 657 kg (Kh-29T 680 kg)". Confidenza **A** per la fascia 657–660 kg.
- **RCS: non pubblicata.**

Classe: **`tactical`** — missile aria-superficie tattico a corto raggio (8–10 km), testata da 320 kg. Ipotesi del
piano **confermata**. Confronto: diametro 380 mm > 343 mm (Harpoon), massa 657–660 kg > 515,25 kg, lunghezza
3,875–3,90 m > 3,79–3,85 m → **non minore dell'Harpoon**. Proposta: **`ad_detectable` True** (la zona grigia del
piano si risolve verso l'alto; con il test di coerenza §5.1 non può essere False).

### 2.7 Kh-29T (`Aircraft_Weapon_Data.py:3728`)

Voce del registro: `model` "Kh-29T", stessi `users`, `task` e `start_service` del Kh-29L, `warhead` 320 kg,
`range` 12 km, `max_speed` 900 m/s, commento "TV guided". Variante identificata: **Kh-29T** (izdeliye 64, guida
TV, NATO AS-14 Kedge-B).

- **Diametro 380 mm.** Fonti: Wikipedia, "Diameter 38.0 cm (15.0 in)"; FAS, "Diameter 0.38 m". Confidenza **A**.
- **Lunghezza 3,90 m / 3,875 m.** Fonti: Wikipedia, "Kh-29L/T: 390 cm (12 ft 10 in)"; FAS, "Total length
  3.875 m". Confidenza **A** (fascia 3,875–3,90 m).
- **Massa al lancio 685 kg / 680 kg.** Fonti: Wikipedia, "Kh-29T: 685 kg (1,510 lb)"; FAS, "Weight 657 kg
  (Kh-29T 680 kg)". Confidenza **A** (fascia 680–685 kg).
- **RCS: non pubblicata.**

Classe: **`tactical`** — missile tattico aria-superficie TV a corto raggio (12 km). Ipotesi del piano
**confermata**. Confronto: 380 mm > 343 mm, 680–685 kg > 515,25 kg, 3,875–3,90 m > 3,79–3,85 m → **non minore
dell'Harpoon**. Proposta: **`ad_detectable` True**.

### 2.8 Kh-29TE (`Aircraft_Weapon_Data.py:3804`)

Voce del registro: `model` "Kh-29TE", stessi `users`, `task` e `start_service`, `warhead` 320 kg, `range` 30 km,
`max_speed` 900 m/s. Variante identificata: **Kh-29TE**, sviluppo export a lungo raggio (30 km) del Kh-29T.

- **Diametro 380 mm.** Fonte: `https://en.wikipedia.org/wiki/Kh-29`, infobox: "Diameter 38.0 cm (15.0 in)".
  Confidenza **M** (una secondaria; il FAS non copre la TE). Coerente con la famiglia Kh-29 (due fonti per L/T).
- **Lunghezza 3,875 m.** Fonte: Wikipedia, "Kh-29TE: 387.5 cm (12 ft 9 in)". Confidenza **M**.
- **Massa al lancio 690 kg.** Fonte: Wikipedia, "Kh-29TE: 690 kg (1,520 lb)". Confidenza **M** (dato
  Rosoboronexport citato da Wikipedia; non ho potuto leggere il catalogo Rosoboronexport, v. §4).
- **RCS: non pubblicata.**

Classe: **`tactical`** — missile tattico aria-superficie TV export a più lungo raggio (30 km). Ipotesi del piano
**confermata**. Confronto: 380 mm > 343 mm, 690 kg > 515,25 kg, 3,875 m > 3,79–3,85 m → **non minore
dell'Harpoon**. Proposta: **`ad_detectable` True**.

## 3) Discordanze fra fonti

| Voce / campo | Valori discordanti | Fonti |
|---|---|---|
| Kh-25ML lunghezza | **3,705 m** vs **3,57 m** vs **3,75 m** | Wikipedia EN + ru-wiki (3,705); FAS (3,57); airwar.ru (3,75, che però è la tabella della famiglia Kh-25 base) |
| Kh-25ML massa | **299 kg** vs **300 kg** vs **316–320 kg** | Wikipedia EN (299) + ru-wiki (299±8); FAS (300); airwar.ru (316–320, tabella della famiglia Kh-25 base) |
| Kh-25MR lunghezza | **3,830 m** vs **3,69 m** | ru-wiki (3,830); Astronautix (3,69) |
| Kh-25MR massa | **320 kg** vs **300 kg** | ru-wiki (320); Astronautix (300) |
| Kh-25MP lunghezza | **4,194/4,294 m** vs **4,255/4,355 m** | ru-wiki (4194/4294); Wikipedia EN (425,5/435,5 cm) |
| Kh-25MP massa | **315±8 kg** vs **315 kg** vs **320 kg** | ru-wiki; Wikipedia EN; FAS |
| Kh-66 massa | **278 kg** vs **290 kg** | FAS (278); airwar.ru (290) |
| Kh-66 lunghezza (variante rumena A921) | **3,63 m** (Kh-66) vs **3,525 m** (A921) | FAS/airwar (Kh-66); Wikipedia Kh-23 (A921) — varianti diverse, non contraddizione |
| Kh-29 lunghezza | **3,90 m** vs **3,875 m** | Wikipedia EN; FAS |
| Kh-29 massa | **660 kg (L) / 685 (T) / 690 (TE)** vs **657 kg (L) / 680 (T)** | Wikipedia EN (Rosoboronexport); FAS |
| Kh-25MR guida | registro: "radar guided"; fonti: **radio-command** (Delta) | `Aircraft_Weapon_Data.py:3523`; FAS AS-10; Wikipedia |
| Portata Kh-25MP/MPU | registro **18/30 km**; fonti **40 km (MP)** e **60 km (MPU)** | registro; FAS (40); Wikipedia EN (40 nel testo, 60 nell'infobox per MP); redstar (60 per MPU) |

## 4) Cosa non ho trovato / non ho potuto verificare

- **RCS**: non pubblicata per nessuna delle otto voci. Non ho trovato valori di RCS né per i Kh-25 né per i Kh-29;
  non invento.
- **Kh-25MPU**: non ho trovato una scheda completa e indipendente con lunghezza/massa specifiche distinte dal
  Kh-25MP. I valori riportati vengono da una sola fonte secondaria (redstar.gr) e sono coerenti con la cellula MP;
  non posso escludere che la MPU abbia una lunghezza leggermente diversa. La portata (60 km) non è verificata su
  fonte primaria.
- **Kh-25MR**: non ho trovato una seconda fonte concorde con la tabella ru-wiki per lunghezza (3,830 m) e massa
  (320 kg); Astronautix dà 3,69 m e 300 kg. Non scelgo.
- **Kh-29TE**: i valori (690 kg, 3,875 m, 380 mm) vengono dal solo Wikipedia che cita Rosoboronexport. Ho tentato
  `https://roe.ru/eng/catalog/aerospace-systems/air-to-air-missile/kh-29te/` ma la richiesta è fallita
  ("Transport error"), quindi **non ho letto** il catalogo del costruttore. Confidenza M, non A.
- **FAS man.fas.org**: le pagine `man.fas.org/dod-101/sys/missile/row/as-10.htm`, `as-7.htm` e `as-14.htm`
  restituiscono **404**. Ho letto le copie archiviate su `web.archive.org` (link esatti nelle sezioni sopra).
  Non ho ricostruito testo non letto.
- **airwar.ru**: le pagine sono in windows-1251 e il testo russo è illeggibile (mojibake); ho letto solo i numeri
  ASCII della tabella finale. Per il Kh-29 la pagina `https://airwar.ru/weapon/avz/x29.html` dà **404**; non ho
  cercato un URL alternativo.
- **Kh-25MPU portata e anno di servizio**: il registro dice 1975 (commento "1978 --1982 vers. U"), redstar.gr dice
  "Entered service: 1990". Non ho una fonte primaria che sciolga la questione; non modifico il registro.
- **Testate**: il registro dà Kh-66 111 kg contro 103 kg delle fonti; Kh-25ML 90 kg (le fonti danno 89,6 kg in
  FAS e 140 kg nella tabella ru-wiki, probabilmente testata tandem totale). Non è un campo richiesto da questo
  lotto, ma lo segnalo perché potrebbe servire al blocco 1.

## 5) Metodo

- **Passi usati**: **34 chiamate a tool** (10 `bash` per leggere piano e registri, 20 `webfetch`, 1 `read` del
  modello L1, 1 `write` del file, 2 `edit` di correzione). Pagine web lette con successo: **11** (Wikipedia EN
  Kh-25; Wikipedia EN Kh-29; Wikipedia EN Kh-23 Grom; Wikipedia RU Kh-25; FAS AS-10 archiviato; FAS AS-7
  archiviato; FAS AS-14 archiviato; airwar.ru X-66; airwar.ru X-25; Astronautix Kh-25MR; redstar.gr X-25MPU).
  Oltre a 2 pagine di risultati DuckDuckGo HTML (usate solo per gli URL). Pagine tentate e fallite: FAS
  `man.fas.org` (3, 404), airwar.ru `x25m.html` e `x29.html` (404), `roe.ru` Kh-29TE (transport error),
  `weaponsystems.net` Kh-25MP (transport error) = 7 tentativi falliti.
- **Come ho cercato**: `websearch` non disponibile. Ho usato `webfetch` su URL noti (Wikipedia, FAS via
  `web.archive.org`, airwar.ru, Astronautix, redstar.gr) e su pagine di risultati
  `https://html.duckduckgo.com/html/?q=...` per scoprire gli URL; dai risultati ho preso solo gli URL, mai i dati.
  Le citazioni sono estratte letteralmente dalle pagine lette (estratto ≤ 25 parole); per le tabelle ho indicato
  la riga.
- **Confronto con le ancore**: per ogni voce ho confrontato diametro e massa con AGM-65D (304,8 mm; 218,25–220 kg)
  e AGM-84A aviolanciato (343 mm; 515,25 kg). Il diametro è usato come proxy della sezione radar; la massa come
  secondo criterio. Per i Kh-25/Kh-66 il diametro è sotto l'ancora bassa; per i Kh-29 tutti e tre i parametri
  superano l'ancora alta.
- **Classificazione**: le classi proposte sono una proposta [S] motivata, non un dato; la decisione finale è
  dell'utente. Il piano ipotizzava `tactical` per Kh-25ML/MR/Kh-66 e Kh-29, `arm` per Kh-25MP/MPU: tutte le
  ipotesi di classe sono **confermate**. L'unica correzione riguarda la zona grigia dei Kh-29, che dai dati
  risulta **sopra** l'ancora Harpoon (quindi `ad_detectable` True, non una zona grigia).