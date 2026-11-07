# Ricerca dati missili aria-superficie — Prova comparativa (modello: V4 Pro)

Prova su tre sole voci dei registri, per classificazione (§5.1 della Proposta
`Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`, blocco 0). Denominazioni lette dal registro
`Code/Dynamic_War_Manager/Source/Asset/Aircraft_Weapon_Data.py`.

Voci cercate (con la denominazione esatta del registro) e trovate:
- `AGM-65D` → riga 2499 del registro (famiglia AGM-65 Maverick, imaging infrared).
- `AGM-84A` → riga 2239 (Harpoon air-launched, Block IA).
- `Kh-22N` → riga 3243 (commento nel registro: `# radar antiship`).

## 1. Tabella riassuntiva

| Voce | Classe proposta | Diametro | Lunghezza | Massa al lancio | RCS | Fonte (URL) | Estratto letterale | Confidenza |
|---|---|---|---|---|---|---|---|---|
| AGM-65D (Maverick) | `tactical` | 12 in = 30 cm ≈ **305 mm** | 2.49 m | **220 kg** (485 lb) | non trovato | https://en.wikipedia.org/wiki/AGM-65_Maverick | "Diameter: 12 in (30 cm)" | A (diametro/massa) |
| AGM-84A (Harpoon) | `anti_ship` | 13.5 in ≈ **343 mm** | 3.8–3.85 m (air-launched) | **515–556 kg** (discordante, v. sotto) | non trovato | https://missilethreat.csis.org/missile/harpoon/ | "Diameter: 0.343 m" | A (diametro); M (massa) |
| Kh-22N (AS-4 Kitchen) | `anti_ship` (fonte lo qualifica anche `cruise`, v. §3) | 92 cm = **920 mm** | 11.65 m | **5 820 kg** | non trovato | https://en.wikipedia.org/wiki/Kh-22 | "Diameter: 92 cm (36 in)" | M |

Nota sulle classi: proposta coerente con la tabella §2.2 della Proposta (AGM-65D `tactical` in
famiglia Maverick; AGM-84A e Kh-22N elencati sotto `anti_ship`). La decisione finale è dell'utente.

## 2. Dettaglio valori e fonti (URL esatto, estratto, confidenza)

### AGM-65D (Maverick, imaging infrared)

Voce del registro (già presente, solo contesto): `warhead: 57` (kg, WDU-20/B shaped-charge),
`range: 15`, `max_speed: 320` (m/s), `task: ["Anti_Ship","Strike","SEAD"]`, `start_service: 1986`.

| Campo | Valore | URL esatto | Estratto letterale (≤25 parole) | Confidenza |
|---|---|---|---|---|
| Diametro | 12 in = 30 cm ≈ 305 mm | https://en.wikipedia.org/wiki/AGM-65_Maverick | "Diameter 12 in (30 cm)" | A |
| Diametro (2ª fonte) | 1 ft = 30.48 cm | https://man.fas.org/dod-101/sys/smart/agm-65.htm | "Diameter: 1 foot (30.48 centimeters)" | A |
| Massa al lancio | 220 kg (485 lb) | https://en.wikipedia.org/wiki/AGM-65_Maverick | (colonna AGM-65D della tabella "Variants") "Weight 220 kg (485 lb)" | A |
| Massa (2ª fonte) | 218.25 kg (485 lb) | https://man.fas.org/dod-101/sys/smart/agm-65.htm | "Launch Weight … AGM-65D … 485 lbs (218.25 kg)" | A |
| Lunghezza | 2.49 m (8 ft 2 in) | https://en.wikipedia.org/wiki/AGM-65_Maverick | "Length 2.49 m (8 ft 2 in)" | M |
| RCS | non trovato | — | — | — |

Nota: il diametro/la massa concordano su due fonti → A. La lunghezza è data solo da Wikipedia
(FAS non la elenca) → M. La scheda ufficiale USAF (https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104547/agm-65-maverick/)
ha risposto **403** (non accessibile al fetch): non usata.

### AGM-84A (Harpoon air-launched, Block IA)

Voce del registro (contesto): `warhead: 221` (kg), `range: 50`, `max_speed: 240` (m/s),
`task: ["Anti_Ship"]`, `start_service: 1970`.

| Campo | Valore | URL esatto | Estratto letterale (≤25 parole) | Confidenza |
|---|---|---|---|---|
| Diametro | 13.5 in ≈ 343 mm | https://en.wikipedia.org/wiki/Harpoon_(missile) | "Diameter 13.5 in (34 cm)" | A |
| Diametro (2ª fonte) | 0.343 m | https://missilethreat.csis.org/missile/harpoon/ | "Diameter: 0.343 m" | A |
| Lunghezza (air-launched) | 3.8 m | https://en.wikipedia.org/wiki/Harpoon_(missile) | "12.6 ft (3.8 m), air-launched" | A |
| Lunghezza (air-launched, 2ª fonte) | 3.8 m / 3.85 m | https://missilethreat.csis.org/missile/harpoon/ | "Length: 3.8 m (air launched) 4.6 m (ship- & sub- launched)"; testo: "The AGM-84A is 3.85 m in length and 0.343 m in diameter, with a launch weight of 556 kg" | A (con lieve discordanza 3.8 vs 3.85) |
| Massa al lancio (air-launched) | 515.25 kg | https://missilethreat.csis.org/missile/harpoon/ | "Launch weight: 515.25 kg (air-launched) 690.8 kg (surface- & sub-launched)" | M |
| Massa al lancio (air-launched, discorde) | 556 kg | https://missilethreat.csis.org/missile/harpoon/ | "The AGM-84A is 3.85 m in length and 0.343 m in diameter, with a launch weight of 556 kg" (cita IHS Jane's Weapons: Strategic 2015-2016) | M |
| Massa (Wikipedia, solo "con booster") | 691 kg (1 523 lb) | https://en.wikipedia.org/wiki/Harpoon_(missile) | "Mass 1,523 lb (691 kg) including booster" | M |
| RCS | non trovato | — | — | — |

Nota massa: il valore Wikipedia da 691 kg è della versione con booster (RGM/UGM, nave/sommergibile),
**non** dell'AGM-84A air-launched. Le due cifre air-launched (515 e 556 kg) sono discordanti e
provengono dalla stessa pagina CSIS (tabella "at a glance" vs paragrafo "Block IA" che cita Jane's):
riportate entrambe, nessuna promossa a A.

### Kh-22N (AS-4 "Kitchen")

Voce del registro (contesto): `warhead: 1000` (kg), `range: 330`, `max_speed: 1190` (m/s),
`task: ["Anti_Ship"]`, `start_service: 1967`, commento `# radar antiship`.

| Campo | Valore | URL esatto | Estratto letterale (≤25 parole) | Confidenza |
|---|---|---|---|---|
| Diametro | 92 cm = 920 mm | https://en.wikipedia.org/wiki/Kh-22 | "Diameter 92 cm (36 in)" | M |
| Lunghezza | 11.65 m (38.2 ft) | https://en.wikipedia.org/wiki/Kh-22 | "Length 11.65 m (38.2 ft)" | M |
| Massa al lancio | 5 820 kg (12 800 lb) | https://en.wikipedia.org/wiki/Kh-22 | "Mass 5,820 kg (12,800 lb)" | M |
| Qualifica di tipo | "Anti-ship cruise missile / Air-to-surface missile" | https://en.wikipedia.org/wiki/Kh-22 | "Type … Anti-ship cruise missile … Air-to-surface missile"; testo: "a large, long-range anti-ship cruise missile" | M |
| RCS | non trovato | — | — | — |

Nota variante: la voce del registro chiama `Kh-22N` la versione "radar antiship" con testata 1000 kg.
La Wikipedia inglese descrive invece il **Kh-22N come la versione a testata nucleare**
(350–1000 kt): «Two initial versions were built, the Kh-22 with a large conventional warhead and the
Kh-22N with a 350–1000-kiloton nuclear warhead» (https://en.wikipedia.org/wiki/Kh-22, sez. Variants).
Possibile ambiguità di denominazione (v. §4): i parametri fisici (massa 5.8 t, L 11.65 m, Ø 92 cm,
testata 1000 kg) valgono per la famiglia Kh-22 a prescindere dalla sigla.

## 3. Il Kh-22N è qualificato come missile da crociera?

Sì. La pagina Wikipedia lo classifica esplicitamente come "cruise missile" nell'infobox (Type:
"Anti-ship cruise missile" + "Air-to-surface missile") e nel testo («large, long-range anti-ship
cruise missile»). Motivazione a supporto: gittata dichiarata 600 km (Kh-22M/MA, da Wikipedia;
il registro ha `range: 330`), propulsione a razzo a propellente liquido R-201 con volo autonomo
a lunga distanza, massa ~5.8 t — tratti coerenti con la definizione di `cruise` del compito
("volo autonomo a lunga distanza"). È però insieme un missile **antinave** (il tipo primario
dichiarato è "anti-ship"), quindi entrambe le etichette sono difendibili; la tabella §2.2 lo
elenca sotto `anti_ship` con la nota "molti sono 'cruise antinave' [I]". Non decido: riporto solo
che le fonti lo qualificano "anti-ship cruise missile". La classificazione finale spetta all'utente.

## 4. Discordanze fra fonti

- **AGM-84A massa al lancio (air-launched)**: CSIS "at a glance" = 515.25 kg vs CSIS paragrafo
  "Block IA" (citando IHS Jane's 2015-2016) = 556 kg; Wikipedia dà solo 691 kg "including booster"
  (riferito alla versione RGM/UGM con booster, non all'air-launched).
- **AGM-84A lunghezza (air-launched)**: 3.8 m (Wikipedia e tabella CSIS) vs 3.85 m (testo CSIS).
- **Kh-22N denominazione**: registro = "radar antiship" con testata convenzionale 1000 kg;
  Wikipedia EN = versione a testata nucleare (Kh-22N = 350–1000 kt). Da verificare su fonte
  primaria russa (non raggiunta in questa prova).
- **AGM-65 diametro**: sostanzialmente concordi (12 in = 304.8 mm; Wikipedia arrotonda a "30 cm",
  FAS a "1 foot = 30.48 cm"): nessuna vera discordanza, solo arrotondamento.

## 5. Cosa NON ho trovato / non ho potuto verificare

- **RCS (sezione radar)**: non trovato per nessuno dei tre (come atteso): l'RCS dei missili non è
  pubblicato dalle fonti pubbliche consultate (neanche la scheda CSIS del Harpoon, che non riporta RCS).
- **Lunghezza del Maverick da una seconda fonte**: presente solo su Wikipedia (FAS non la elenca;
  scheda USAF inaccessibile, 403).
- **Fonte primaria russa per il Kh-22N** (ad es. rbase.new-factoria.ru o airwar.ru, citate nelle
  note di Wikipedia): non consultate direttamente in questa prova.
- **Scheda ufficiale USAF del Maverick**: bloccata (HTTP 403) al fetch.
- **Pagina CSIS dedicata al Kh-22**: non esiste (404 su entrambi gli URL tentati).

## Metodo

- Strumenti: **`websearch` NON disponibile** in questa sessione → usato solo `webfetch` su pagine note
  (Wikipedia EN, CSIS Missile Threat, FAS Military Analysis Network, scheda USAF af.mil).
- URL interrogati: 8 totali. **Pagine lette con esito OK: 5** (Wikipedia AGM-65, Wikipedia Harpoon,
  Wikipedia Kh-22, CSIS Harpoon, FAS AGM-65). **Tentativi falliti: 3** (af.mil → 403; CSIS
  `.../missile/kh-22/` → 404; CSIS `.../kh-22-burya-as-4-kitchen/` → 404).
- Passi (invii di strumenti): 6 (letture di registro/piano + 3 round di webfetch + verifica dir).
- Confidenza: A = fonte primaria o due concordi; M = una secondaria; B = stima (nessuna usata).
  Wikipedia e FAS trattate come secondarie/enciclopediche; CSIS (Missile Threat) come fonte di un
  centro di ricerca, con riferimenti a Jane's.
- Nessun valore inventato. Dove le fonti discordano (massa AGM-84A) le ho riportate entrambe senza
  scegliere. Nessuna stima mia ([S]) necessaria.