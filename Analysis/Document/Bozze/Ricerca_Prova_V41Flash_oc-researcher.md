# Ricerca dati missili ASM — prova comparativa (AGM-65D, AGM-84A, Kh-22N)

**Data**: 2026-11-07
**Agente**: `oc-researcher` (prova comparativa, modello V4.1 Flash)
**Ambito**: blocco 0 della Proposta `Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`, §5.1; letta anche la §2.2. Nessuna decisione di classificazione: la classificazione finale e' dell'utente.
**Registro**: `Code/Dynamic_War_Manager/Source/Asset/Aircraft_Weapon_Data.py` (checkout del 2026-11-07).

> **Nota sugli strumenti**: `websearch` **non e' disponibile** tra gli strumenti di questa sessione. Ho usato solo `webfetch` su pagine note (Wikipedia, CSIS Missile Threat, FAS, siti specialistici russi) e, per trovare gli URL, due pagine di risultati DuckDuckGo HTML. Lo dichiaro qui e nella sezione "Metodo".

---

## 0. Voci cercate nel registro

| Voce cercata (`grep -n`) | Voce trovata | Riga | Nota |
|---|---|---|---|
| `AGM-65D` | `"AGM-65D"` | `Aircraft_Weapon_Data.py:2499` | Cercata la variante **D** (IIR), non la K: dati diversi. |
| `AGM-84A` | `"AGM-84A"` | `Aircraft_Weapon_Data.py:2239` | Cercata la **A** (aviolanciata), non la D/L: dati diversi. |
| `Kh-22N` | `"Kh-22N"` | `Aircraft_Weapon_Data.py:3243` | Cercata la **N**, non la Kh-22/Kh-22M. |

## 1. Dati del registro (letti, [V])

| Voce | Riga | `task` | `warhead` | `range` | `max_speed` | Altro |
|---|---|---|---|---|---|---|
| `AGM-65D` | 2499 | `Anti_Ship`, `Strike`, `SEAD` | 57 kg (commento: `WDU-20/B shaped-charge`) | 15 | 320 m/s | `start_service` 1986 |
| `AGM-84A` | 2239 | `Anti_Ship` | 221 kg | 50 | 240 m/s | `start_service` 1970 |
| `Kh-22N` | 3243 | `Anti_Ship` | 1000 kg | 330 | 1190 m/s | commento `# radar antiship`; `start_service` 1967 |

**Unita' di `range`**: il registro non le dichiara. Le interpreto come **km** `[S]` perche' i valori (15, 50, 330) sono coerenti con le portate web (22–27 km, 124+ km, 400–600 km); se fossero nmi sarebbero ~1,85 volte piu' grandi e incoerenti. Non modifico il registro.

---

## 2. Tabella richiesta (sintesi)

| voce | classe proposta | diametro | lunghezza | massa al lancio | RCS | fonte (URL esatto) | estratto letterale (max 25 parole) | confidenza |
|---|---|---|---|---|---|---|---|---|
| **AGM-65D** | `tactical` | 300–304,8 mm | 2,49 m | 218,25–220 kg | non trovato | https://en.wikipedia.org/wiki/AGM-65_Maverick ; https://fas.org/man/dod-101/sys/smart/agm-65.htm | "Diameter 30 cm (12 in)"; "Length 2.49 m (8 ft 2 in)"; "Weight 220 kg (485 lb)"; "485 lbs (218.25 kg)" | **A** (diametro, massa, classe); **M** (lunghezza) |
| **AGM-84A** | `anti_ship` (profilo anche `cruise`) | 343 mm | 3,79–3,85 m (aviolanciato) | 515,25 kg (aviolanciato; 556 kg in CSIS testo) | non trovato | https://fas.org/man/dod-101/sys/smart/agm-84.htm ; https://missilethreat.csis.org/missile/harpoon/ ; https://en.wikipedia.org/wiki/AGM-84_Harpoon | "Length: 12 feet, 7 inches (3.79 meters)"; "Weight: 1,145 pounds (515.25 kilograms)"; "The AGM-84A is 3.85 m in length and 0.343 m in diameter, with a launch weight of 556 kg" | **A** (diametro, lunghezza, massa 515,25); **M** (massa 556, discorde) |
| **Kh-22N** | `anti_ship` / `cruise` (vedi §4) | 900–920 mm | 11,65–11,67 m (11,0 m in una fonte, discorde) | 5.820 kg (altre fonti ~5.9 t, non leggibili con certezza) | non trovato | https://en.wikipedia.org/wiki/Kh-22 ; http://airwar.ru/weapon/kr/x22.html ; https://web.archive.org/web/20190608090916/http://vs.milrf.ru/armament/marine/krm_x22.htm | "Length 11.65 m (38.2 ft)"; "Diameter 92 cm (36 in)"; "Mass 5,820 kg (12,800 lb)"; "a large, long-range anti-ship cruise missile" | **A** (diametro, lunghezza, classe); **M** (massa) |

---

## 3. Dettaglio delle fonti (valore per valore)

### 3.1 AGM-65D

| Dato | Valore | Fonte (URL esatto) | Estratto letterale (max 25 parole) | Conf. |
|---|---|---|---|---|
| Diametro | 300 mm | https://en.wikipedia.org/wiki/AGM-65_Maverick | "Diameter 30 cm (12 in)" (infobox e tabella varianti) | **A** |
| Diametro | 304,8 mm | https://fas.org/man/dod-101/sys/smart/agm-65.htm | "Diameter: 1 foot (30.48 centimeters)" | **A** |
| Lunghezza | 2,49 m | https://en.wikipedia.org/wiki/AGM-65_Maverick | "Length 2.49 m (8 ft 2 in)" | **M** |
| Massa al lancio | 220 kg | https://en.wikipedia.org/wiki/AGM-65_Maverick | "Weight 220 kg (485 lb)" (tabella varianti, colonna AGM-65D) | **A** |
| Massa al lancio | 218,25 kg | https://fas.org/man/dod-101/sys/smart/agm-65.htm | "485 lbs (218.25 kg)" (colonna AGM-65D) | **A** |
| RCS | non trovato | — | — | — |
| Classe | `tactical` | https://fas.org/man/dod-101/sys/smart/agm-65.htm | "The AGM-65 Maverick is a tactical, air-to-surface guided missile designed for close air support" | **A** |
| Classe (conferma) | `tactical` | https://en.wikipedia.org/wiki/AGM-65_Maverick | "air-to-ground missile (AGM) designed for close air support" | **A** |

**Nota**: la pagina Wikipedia contiene anche i dati delle altre varianti (A/B/E/F/G/H/J/K). Ho preso la colonna **AGM-65D** (massa 220 kg; testata 57 kg WDU-20/B; guida IIR), non i valori generici "463–670 lb" ne' quelli della K (306 kg). La portata web e' "Greater than 22 km (12 nmi)" (Wikipedia) / "17+ miles ... 27 km" (FAS), contro `range` 15 del registro.

### 3.2 AGM-84A

| Dato | Valore | Fonte (URL esatto) | Estratto letterale (max 25 parole) | Conf. |
|---|---|---|---|---|
| Diametro | 343 mm | https://fas.org/man/dod-101/sys/smart/agm-84.htm | "Diameter: 13.5 inches (34.29 centimeters)" | **A** |
| Diametro | 0,343 m | https://missilethreat.csis.org/missile/harpoon/ | "0.343 m in diameter" | **A** |
| Lunghezza (aviolanciato) | 3,79 m | https://fas.org/man/dod-101/sys/smart/agm-84.htm | "Length: 12 feet, 7 inches (3.79 meters)" | **A** |
| Lunghezza (aviolanciato) | 3,85 m | https://missilethreat.csis.org/missile/harpoon/ | "The AGM-84A is 3.85 m in length and 0.343 m in diameter, with a launch weight of 556 kg" | **A** |
| Massa (aviolanciato) | 515,25 kg | https://fas.org/man/dod-101/sys/smart/agm-84.htm | "Weight: 1,145 pounds (515.25 kilograms)" | **A** |
| Massa (aviolanciato) | 515,25 kg | https://missilethreat.csis.org/missile/harpoon/ | "Launch weight 515.25 kg (air-launched) 690.8 kg (surface- & sub-launched)" | **A** |
| Massa (aviolanciato) | 556 kg | https://missilethreat.csis.org/missile/harpoon/ | "with a launch weight of 556 kg" | **M** (discorde) |
| Massa (con booster) | 691 kg | https://en.wikipedia.org/wiki/AGM-84_Harpoon | "Mass 1,523 lb (691 kg) including booster" | **M** (non e' l'AGM-84A puro) |
| RCS | non trovato | — | — | — |
| Classe | `anti_ship` | https://fas.org/man/dod-101/sys/smart/agm-84.htm | "Primary Function: Air-to-surface anti-ship missile" | **A** |
| Classe (conferma) | `anti_ship` / `cruise` | https://missilethreat.csis.org/missile/harpoon/ | "The Harpoon (RGM-84/UGM-84/AGM-84) is a U.S.-designed subsonic antiship cruise missile" | **A** |

**Nota**: per l'AGM-84A **aviolanciato** la massa piu' sostenuta e' **515,25 kg** (FAS e tabella CSIS, due fonti concordi). Il testo CSIS da' 556 kg e Wikipedia da' 691 kg "including booster" (valore che si riferisce alle versioni RGM/UGM con booster, non all'AGM). La lunghezza aviolanciata e' 3,79–3,85 m; il valore "4,6 m" di Wikipedia e' per le versioni superficie/sottomarino. La testata e' 221 kg (registro) / 224 kg (CSIS) / 488 lb = 221 kg (FAS): coerente.

### 3.3 Kh-22N

| Dato | Valore | Fonte (URL esatto) | Estratto letterale (max 25 parole) | Conf. |
|---|---|---|---|---|
| Diametro | 920 mm | https://en.wikipedia.org/wiki/Kh-22 | "Diameter 92 cm (36 in)" | **A** |
| Diametro | 900–920 mm | http://airwar.ru/weapon/kr/x22.html | "0,9-0,92" (tabella varianti) | **A** |
| Diametro | 920 mm | https://web.archive.org/web/20190608090916/http://vs.milrf.ru/armament/marine/krm_x22.htm | "0,92" (tabella Х-22Н) | **A** |
| Lunghezza | 11,65 m | https://en.wikipedia.org/wiki/Kh-22 | "Length 11.65 m (38.2 ft)" | **A** |
| Lunghezza | 11,67 m | http://airwar.ru/weapon/kr/x22.html | "11,67" (tabella Х-22Н) | **A** |
| Lunghezza | 11,0 m | https://web.archive.org/web/20190608090916/http://vs.milrf.ru/armament/marine/krm_x22.htm | "11,0" (tabella Х-22Н) | **M** (discorde) |
| Massa al lancio | 5.820 kg | https://en.wikipedia.org/wiki/Kh-22 | "Mass 5,820 kg (12,800 lb)" | **M** |
| Massa al lancio | ~5.635–5.780 kg (famiglia Kh-22/MA) | http://airwar.ru/weapon/kr/x22.html | "5,635-5,78" (tabella Х-22/Х-22МА) | **M** (corroborante, non specifico N) |
| RCS | non trovato | — | — | — |
| Classe | `cruise` + `anti_ship` | https://en.wikipedia.org/wiki/Kh-22 | "a large, long-range anti-ship cruise missile developed by MKB Raduga" | **A** |
| Classe (conferma) | `cruise` | http://airwar.ru/weapon/kr/x22.html | "Крылатая ракета Х-22Н" (titolo; pagina in windows-1251) | **A** |

**Nota sulle fonti russe**: `vs.milrf.ru` e `airwar.ru` sono in windows-1251 e il `webfetch` le ha restituite con caratteri corrotti. Ho letto solo i **numeri ASCII** delle tabelle e li ho confrontati con Wikipedia. La tabella di `vs.milrf.ru` da' per la Kh-22N lunghezza 11,0 m e diametro 0,92 m; `airwar.ru` da' 11,67 m e 0,90 m. La discordanza di lunghezza (11,0 vs 11,65–11,67) e' riportata sotto. La massa della Kh-22N non e' estraibile con certezza dalle due pagine russe (la tabella di `airwar.ru` riporta "5,635-5,78" per la famiglia Kh-22/MA e "5,9-6,0" che, dal contesto, e' la **quota di lancio in km**, non la massa); per questo la massa resta **M** da Wikipedia.

---

## 4. Il Kh-22N e la classe `cruise`

**Sì: le fonti consultate lo qualificano esplicitamente come missile da crociera (anti-nave).**

- Wikipedia, infobox: tipo **"Anti-ship cruise missile Air-to-surface missile"**; testo: *"a large, long-range anti-ship cruise missile developed by MKB Raduga"*.
- `airwar.ru`, titolo della pagina: **"Крылатая ракета Х-22Н"** = "missile da crociera Kh-22N" (la parola *крылатая ракета* e' il termine russo per missile da crociera).

**Motivazione**: la Kh-22N ha un profilo di volo autonomo a lunga distanza (portata dichiarata 400 km nella tabella `vs.milrf.ru`, 600 km per le versioni M/MA in Wikipedia), motore a razzo liquido, guida inerziale con radar attivo terminale. E' quindi un **missile da crociera** a tutti gli effetti. E' pero' anche, e primariamente, un **missile antinave** (`task: Anti_Ship` nel registro; testata da 1.000 kg; impiego contro portaerei e gruppi navali).

**Proposta (non decisione)**: la tassonomia del §2.2 lo mette in `anti_ship`; la nota §2.3/§5.1 dice che, se classificato `cruise`, diventa bersaglio delle difese terrestri. Le fonti dimostrano che **entrambe le qualificazioni sono vere**: `anti_ship` descrive il ruolo, `cruise` descrive il profilo di volo. Nella tabella ho scritto **`anti_ship` / `cruise`**: l'utente deve scegliere quale criterio prevale. Se prevale il criterio "e' un missile da crociera lanciato da bombardiere", la classe corretta e' `cruise`.

---

## 5. Discordanze fra fonti

1. **AGM-84A, massa aviolanciata**: **515,25 kg** (FAS; tabella CSIS) vs **556 kg** (testo CSIS) vs **691 kg** (Wikipedia, "including booster", riferito alle versioni RGM/UGM). La massa dell'AGM-84A puro e' con ogni probabilita' 515,25 kg; 691 kg non e' confrontabile (include il booster).
2. **AGM-84A, lunghezza aviolanciata**: **3,79 m** (FAS) vs **3,85 m** (testo CSIS) vs **3,8 m** (Wikipedia e tabella CSIS). Differenza ~1,6%.
3. **AGM-65D, diametro**: **30 cm** (Wikipedia) vs **30,48 cm** (FAS). Differenza ~1,6%, coerente con arrotondamento.
4. **AGM-65D, massa**: **220 kg** (Wikipedia) vs **218,25 kg** (FAS). Differenza <1%.
5. **Kh-22N, lunghezza**: **11,65 m** (Wikipedia) / **11,67 m** (airwar) vs **11,0 m** (vs.milrf.ru). Il valore 11,0 m e' un outlier; potrebbe riferirsi a una sotto-variante o essere un errore di tabella. Riporto entrambi.
6. **Kh-22N, diametro**: **0,92 m** (Wikipedia, vs.milrf.ru) vs **0,9 m** (airwar). Differenza 2 cm.
7. **Kh-22N, massa**: **5.820 kg** (Wikipedia) vs **5.635–5.780 kg** (airwar, famiglia Kh-22/MA) vs **~5.900 kg** (prosa di vs.milrf.ru, dicitura ambigua). La massa della variante N non e' pubblicata in modo univoco.
8. **Kh-22N, testata**: registro **1.000 kg**; Wikipedia *"1,000 kg RDX or 350–1,000 kt thermonuclear"*; airwar indica la variante N come **nucleare** con 1.000 kg. Non e' solo una discordanza numerica: e' una discordanza di **tipo** (convenzionale vs nucleare). Il registro la tratta come 1.000 kg; la fonte primaria non e' disponibile.
9. **Registro vs web, portata**: AGM-65D 15 vs 22–27 km; AGM-84A 50 vs >124 km (aviolanciato; CSIS 90–240 km); Kh-22N 330 vs 400–600 km.
10. **Registro vs web, velocita'**: AGM-65D 320 m/s vs 1.150 km/h ≈ 319 m/s (coerente); AGM-84A 240 m/s vs 240 m/s (coerente); Kh-22N 1.190 m/s vs Mach 3,5–4,6 (≈1.190–1.400 m/s a quota; il valore del registro e' plausibile per il profilo basso).
11. **Kh-22N, entrata in servizio**: Wikipedia 1968; registro 1967. Differenza di un anno, non rilevante ai fini della classe.

---

## 6. Cosa non ho trovato / non ho potuto verificare

- **RCS (sezione radar equivalente)**: **non trovato** per tutti e tre. Nessuna fonte pubblica consultata dichiara una RCS. Non e' una dimenticanza: la RCS non e' di norma pubblicata (dipende dall'angolo di aspetto, dalla frequenza e dalla configurazione) ed e' spesso classificata. Non invento un valore.
- **Fonti primarie ufficiali**: la scheda USAF dell'AGM-65 ha restituito **403**; la pagina CSIS dell'AGM-65 e quella del Kh-22 hanno restituito **404**; GlobalSecurity (AS-4) ha restituito **404**. Per Maverick e Kh-22 mi sono quindi appoggiato a fonti secondarie (Wikipedia, FAS, airwar.ru, vs.milrf.ru).
- **AGM-65D, lunghezza da una seconda fonte indipendente**: non trovata (FAS non riporta la lunghezza). La lunghezza 2,49 m resta **M** (solo Wikipedia).
- **Kh-22N, massa e lunghezza variante-specifiche**: le due pagine russe sono in windows-1251 e sono state restituite con encoding corrotto; ho potuto leggere con sicurezza solo i numeri ASCII. La massa resta **M**; la lunghezza ha un outlier (11,0 m) che non ho potuto verificare ulteriormente.
- **Kh-22N, tipo di testata**: non risolto (nucleare vs convenzionale 1.000 kg). Wikipedia e airwar indicano la N come nucleare; il registro la usa come 1.000 kg. Da verificare con una fonte primaria russa, non disponibile in questa prova.
- **AGM-84A, massa esatta**: non risolta (515,25 vs 556 kg; 691 kg include il booster). La coppia FAS + tabella CSIS rende 515,25 kg il valore piu' solido, ma il testo CSIS discorda.
- **Unita' di `range` nel registro**: non dichiarate; ho assunto km `[S]` (ragionamento nella §1).
- **`websearch`**: non disponibile; la ricerca e' stata fatta con `webfetch` su pagine note e con due pagine di risultati DuckDuckGo HTML per scoprire gli URL. Possibili fonti non raggiunte per questo motivo.

---

## 7. Metodo

- **`websearch` disponibile**: **no** (non e' tra gli strumenti della sessione). Usato **solo `webfetch`**.
- **Pagine lette (10)**: Wikipedia AGM-65 Maverick; Wikipedia AGM-84 Harpoon; Wikipedia Kh-22; CSIS Missile Threat Harpoon; FAS AGM-65; FAS AGM-84; airwar.ru Kh-22; vs.milrf.ru Kh-22 (via Wayback Machine); due pagine di risultati DuckDuckGo HTML (solo per trovare gli URL, nessun dato preso da li').
- **Tentativi di fetch (15)**: 10 riusciti + 5 falliti (CSIS Kh-22 due URL, 404; CSIS AGM-65, 404; scheda USAF AGM-65, 403; GlobalSecurity AS-4, 404).
- **Passi usati**: **17** (raccolta/verifica del codice e delle fonti, scrittura, rilettura e correzioni della bozza). Non conteggio il messaggio finale di sintesi.
- **Criteri di confidenza**: **A** = fonte primaria o due fonti secondarie concordi; **M** = una fonte secondaria; **B** = stima o fonte debole. Le stime personali sono marcate `[S]` (solo l'unita' di `range`).
- **Indipendenza**: non ho letto ne' usato la bozza comparativa `Ricerca_Prova_GLM53_oc-researcher.md` presente nella stessa cartella.

---

## 8. Elementi utili al blocco 0 (solo dati, nessuna decisione)

- **Ancora bassa (Maverick AGM-65D)**: 218,25–220 kg; 2,49 m; 300–304,8 mm. È la taglia "piccola" coerente con la decisione BI-6 (Maverick fisso piccolo).
- **Ancora alta (Harpoon AGM-84A aviolanciato)**: 515,25 kg; 3,79–3,85 m; 343 mm. Il diametro 343 mm era gia' a registro navale [V]; lunghezza e massa ora hanno fonte (FAS + CSIS).
- **Kh-22N**: 5.820 kg (M); 11,65–11,67 m (A, con outlier 11,0 m); 900–920 mm (A); classe `anti_ship` / `cruise` (vedi §4). È molto piu' grande di entrambe le ancore; se l'utente sceglie `cruise`, la §2.3 lo rende bersaglio delle difese terrestri.
- **RCS**: nessun valore pubblico per nessuno dei tre; la voce resta vuota.