# Proposta: revisione della regola L1 del risolutore d'ingaggio (lanciatore bersaglio immediato, zona dell'arma che intercetta)

**Cronologia.** 2026-11-24: scritta (`des-planner`). 2026-11-25: corretta dopo la rilettura
(`Rapporti/Revisione_L1_des-reviewer.md`); scelta A su condizione (2); B e guida del missile annotati come upgrade
(§5.1, UF-1 e UF-2).

**Stato: PIANO ESEGUIBILE.** Scritta il 2026-11-24 da `des-planner` sulla VM osboxes, codice letto al commit `0c7263cd`
(working tree con le sole modifiche di memoria, nessun file di codice modificato). Le decisioni di design sono
dell'utente (2026-11-24, riportate sotto e **non** rimesse in discussione); il piano di §4 e' un contratto completo per
l'esecutore (`des-developer` o `oc-developer`) per i blocchi 1-3; il blocco 4 (sonda) e' della sessione principale; il
blocco 5 (accensione) e il blocco 6 (pulizia) si eseguono **solo** dopo una decisione esplicita dell'utente; il blocco 6
e' **da ripianificare** sul codice di allora (§4.6).

**Convenzioni.** **[V]** = verificato leggendo il codice (`file:riga`, checkout `0c7263cd`) o eseguendolo; **[M]** =
misurato con una sonda di sola lettura (§1.5); **[C]** = calcolo mostrato; **[I]** = ipotesi o conoscenza generale non
verificata; **[S]** = stima o scelta di progetto, mai dato tarato. Percorsi di codice relativi a
`Code/Dynamic_War_Manager/Source/`. Decisioni dell'utente **a, c, d, e** (sigle date dall'utente il 2026-11-24);
scelte derivate dall'analista **SD-1..SD-6** (§2.4, confermabili); domande residue **Q-L1-1..** (§3).

**Nessun file di codice o di test e' modificato da questo documento.** Le sonde (§1.5) sono script fuori dal repository,
nella cartella temporanea della sessione: sostituiscono `_may_intercept` **in memoria** e rieseguono la cattura.

---

## Glossario delle sigle

| Sigla | Significato |
|---|---|
| DES | *Discrete Event Simulation*: il motore di sessioni virtuali a coda di eventi (`Logic/Engagement_Resolver.py` e chiamanti) |
| salva | gruppo di colpi lanciati insieme da un tiratore contro un bersaglio (`Salvo`: lanciatore, bersaglio, istante di lancio `t_launch`, istante d'impatto `t_impact`, colpi) |
| intercettore | asset della difesa che puo' fermare colpi in volo (missili, bombe guidate) prima che arrivino al modello di danno |
| V_I | volume d'intercettazione di oggi: cilindro con raggio = portata massima di **tutte** le armi antiaeree dell'asset e fascia di quota fra la quota minima e massima di quelle armi (`Mobile.air_defense_volume`, `Asset/Mobile.py:1396-1464`) |
| zona dell'arma | (nuovo) cilindro di **una** arma intercettrice: raggio = portata dell'arma, fascia = sue quote minima e massima, relativi alla posizione dell'intercettore |
| regola D | intercetta solo un'arma che dichiara il task `Anti_Missile` nel registro (`Mobile.INTERCEPTOR_TASK`, `Asset/Mobile.py:208`; selezione `interceptor_weapons_from_registry`, `:1059-1129`) |
| regola F | ordine di consumo: dentro l'asset prima i cannoni poi i missili; fra asset prima quelli a soli cannoni, poi per id |
| L1 | regola del 2026-09-28: un intercettore non ferma i colpi di una salva lanciata da **dentro** il suo V_I (`_may_intercept`, `Logic/Engagement_Resolver.py:3719-3742`) |
| L2 | priorita' di bersaglio: un aereo che ha lanciato armi aria-superficie contro la forza del tiratore, gia' a portata, passa davanti agli altri bersagli (`_schedule_next`: commento `:2901-2903`, pool `priority` `:2904-2906` con `_in_range_at` a `:2906`, sui candidati gia' filtrati da `viable`, `:2860-2896`) |
| L3 | prelazione: al primo lancio aria-superficie i tiratori che hanno il lanciatore a portata ridecidono dopo il proprio `refire_interval` (`_register_launcher`, `:3325-3375`) |
| R-INT | regola del 2026-09-30: un intercettore ferma un colpo solo se ne ha una traccia e il tempo di reagire prima dell'impatto (`_in_time`, `:3824-3849`) |
| BI | regola dei bersagli intercettabili per classe di munizione e dominio della difesa (`_admissible`, `:3711-3717`), interruttore `BI_AD_TARGET_RULE`, **spento** (`:625`) |
| FP, FP-5 (d) | rilevamento per passaggio nella portata propria; per R-INT "aveva gia' rilevato il lanciatore" vale solo per un rilevamento nel passaggio che contiene il lancio (`_detection_time_of`, `:3744-3767`) |
| VA | quota nel volume d'ingaggio, interruttore `VA_ENGAGEMENT_ALTITUDE_BAND`, spento (`:636`) |
| candidato | bersaglio rilevato da un tiratore, ingaggiabile nell'intervallo `[t_ready, t_end]` (`_Candidate`, `:1794-1807`); `t_ready` = istante del rilevamento + latenza totale di reazione |
| RIV, VAL, COM, ATT | fasi del profilo di reazione (rilevamento, valutazione, comando, attuazione); `total` = somma, `refire_interval` = VAL+COM+ATT |
| CIWS | *Close-In Weapon System*: cannone navale a tiro rapido antimissile (Phalanx, AK-630, Type-730) |
| fire-and-forget | missile che dopo il lancio non ha bisogno del lanciatore per arrivare al bersaglio |
| fotografia | `Test/baseline/scenario_baseline.json`: gli esiti registrati delle 1219 esecuzioni di scenario; la installa **solo l'utente** |
| sonda | script di sola lettura che cambia una regola in memoria e rifa' la cattura, per misurare gli effetti |
| UF-1, UF-2 | upgrade futuri annotati il 2026-11-25 (§5.1), **non** parte del piano: UF-1 = ROE a tempo (`_is_deferred`) nella condizione (2) (scelta B della rilettura); UF-2 = tipo di guida del missile e dipendenza dal lanciatore (nota SD-6 della rilettura) |

---

## Regola finale dell'utente (2026-11-24, vincolante)

Decisioni: **a = 2** (esclusione condizionata), **c = 2** (bersaglio immediato = gia' rilevato e ingaggiabile),
**d = 2** (zona = raggio dell'arma che intercetta, solo armi `Anti_Missile`), **e = 1** (confronto netto, margine zero,
bordo = dentro, nessuna fascia di transizione, nessuna costante nuova).

> Un intercettore **NON** intercetta i colpi di un lanciatore **solo se** (1) il punto di lancio e' dentro la zona
> dell'arma che intercetta **E** (2) il lanciatore e' un suo bersaglio immediato (gia' rilevato dall'intercettore, per
> asset, e l'intercettore ha un'arma con scorta e portata per colpirlo). In ogni altro caso il colpo e' intercettabile,
> subordinato a R-INT, canali, scorta, BI.

Conseguenza accettata dall'utente: le navi la cui arma `Anti_Missile` piu' lunga e' anche la loro arma antiaerea piu'
lunga (Arleigh Burke, CG-65, Type 052C, Kuznetsov, ...) conservano la zona di oggi (§1.4).

---

## 1. Problema e comportamento attuale

### 1.1 Che cosa fa L1 oggi [V]

`_EngagementRun._may_intercept(shadow, salvo)` (`Logic/Engagement_Resolver.py:3719-3742`) restituisce `False`
(l'intercettore **non** puo' fermare i colpi della salva) se il punto di lancio, all'istante `t_launch`, e' dentro il V_I
dell'intercettore:

- zona: `_interception_zone` (`:3684-3702`) legge `asset.air_defense_volume()` (cilindro) e lo trasforma in
  `(raggio, quota base, quota tetto)` relativi alla posizione dell'asset; memoizzato in `zone_cache` (`:2044`);
- posizioni: `_position_at` (`:3669-3682`), dai tratti di rotta o dalla posizione ferma;
- confronto: `allowed = not (horizontal <= radius and bottom <= height <= top)` (`:3738`): bordo = dentro;
- dato mancante (nessuna zona, nessuna posizione): nessun vincolo (`:3729`, `:3734`);
- memo per coppia `(intercettore, salva)` in `may_intercept_cache` (`:2050`, `:3726-3742`); nessuna estrazione casuale.

E' chiamata nel ciclo di allocazione per salva di `_on_resolve` (`:3917-3938`), condizioni in OR (`:3929-3930`):
`free <= 0 or not _admissible or not _may_intercept or not _in_time` -> l'intercettore salta la salva. L'ordine e' quindi
canali/scorta -> BI -> L1 -> R-INT; con BI acceso e colpo non ammesso L1 non e' nemmeno valutata.

Il V_I comprende armi che **non** intercettano: per una nave `air_defense_volume` legge solo i `MISSILES_SAM`
(`Asset/Mobile.py:1429-1432`), mentre gli intercettori navali sono i SAM con `Anti_Missile` **piu' i CIWS**
(`interceptor_weapons_from_registry`, `:1094-1123`); per un veicolo legge tutte le armi con task `Anti_Air`, anche
senza `Anti_Missile` (`:1440`).

Origine: dottrina dell'utente del 2026-09-28 (`Proposta_Regole_Allocazione_SAM.md` §7.1, §7.3, decisioni §7.7 Q1
"zona del singolo intercettore", Q2 "i colpi lanciati dentro la zona non si intercettano mai", Q5 "il lanciatore deve
essere gia' rilevato" — Q5 valeva per L2/L3, **non** per L1). Manuale: `Manuale_Motore_DES/05_Strato2_Risolutore_Ingaggio.md`
§4.24 "Regola L1" e §4.26; `10_Limiti_Estensioni_Divergenze.md` §9.1.

### 1.2 Perche' va rivista (dati della sonda del 2026-11-24) [M]

Sonda di sola lettura sulle 1219 esecuzioni (confronto con la fotografia: IDENTICAL, la sonda non altera gli esiti):

- L1 valuta **412** coppie (intercettore, salva; il riepilogo del 2026-11-24 diceva 410, il file della sonda ne conta 412:
  S2 46, S6 113, S11 30, S16 152, S19AD 20, S35-ADTGT 51) ed **esclude 13**, tutte in tre unita': **S16** (7: corvetta
  `FSG 1241.1MP Molniya` contro i colpi `test:anti_ship` degli F/A-18C, tempo di volo 60 s), **S19AD** (2: Tor contro
  AGM-65D dell'A-10C, 23 s), **S35-ADTGT** (4: fregata `FF 1135M Rezky` contro AGM-65D).
- In **tutte le 13** R-INT avrebbe lasciato intercettare (c'era tempo di reagire).
- In **9 su 13** (S16, S19AD) l'intercettore **non aveva rilevato il lanciatore** all'istante del lancio: oggi non
  intercetta i colpi di un aereo che non vede e a cui non spara. Nelle 4 di S35 il lanciatore era rilevato.
- Distanze di lancio dal 19% al 92% del raggio del V_I.
- Con L1 spenta del tutto cambiano **6 esecuzioni su 1219**: `S16/S16-3`,
  `S19AD/S19-4/tor_forward_ifv_only`, `S35-ADTGT/S35-ADTGT-0..3/naval_maverick_off`.

Il difetto e' doppio: (i) la condizione "il lanciatore e' un bersaglio" e' presunta dalla sola geometria, anche quando
l'intercettore non lo vede o non puo' colpirlo; (ii) la zona e' quella di armi che non intercettano (SA-N-4 della
Rezky e della Molniya, 12 km, al posto dell'AK-630, 4 km).

### 1.3 Che cosa leggono gia' le altre regole (riuso) [V]

- **Rilevamento per asset, all'istante del lancio**: `_detection_time_of(observer, target, at)` (`:3744-3767`), usato da
  R-INT (`:3840-3842`: lancio osservato se `seen is not None and seen <= t_launch + TIME_EPS`). Nessuna estrazione.
- **"Il tiratore puo' colpirlo adesso"**: `_in_range_at(shooter, index, candidate, t_fire)` (`:3301-3322`), usato da
  L2 (`:2906`) e L3 (`:3367`): prima opzione della fire control con scorta (`_first_with_stock`, `:3404-3421`), ripiego
  VA (`_altitude_deferral`, `:3508-3557`, attivo solo con VA acceso), controllo di portata (`_range_entry`,
  `:3423-3465`). Richiede un **candidato** del tiratore sul lanciatore e il suo indice. **Attenzione**: in L2
  `_in_range_at` e' solo l'ultimo controllo; i candidati sono prima filtrati dal ciclo `viable` di `_schedule_next`
  (`:2860-2896`): `exhausted` (`:2861`), bersaglio non `operative` o `_gone` (`:2866`), `t_fire` spostato a
  `candidate.not_before` (`:2874-2875`) e oltre `t_end` (`:2877`), fine attivita' del tiratore (`:2881`), tiratore a
  terra a `t_fire` (`:2885`), ROE dipendente dal tempo `_is_deferred` (`:2892`, metodo `:3141-3154`). La condizione (2)
  della regola rivista riusa **solo** `_in_range_at` e il controllo su `t_end` (§2.1, SD-1).
- I candidati nascono a ogni rilevamento riuscito (`_detect_direction`, `:2421-2428`; `_detect_passes`, `:2639-2646`),
  per **ogni** osservatore, con `t_ready = istante del rilevamento + total` e `t_end` = fine finestra o del passaggio.

**Effetti collaterali di `_in_range_at`** [V]: chiama la fire control iniettata (`_fire_control`, `:3230-3243`; quella
dei registri e' deterministica e memoizzata, `Logic/Fire_Control.py:898-985`, e "nessun uso del modulo `random`",
`:200`), le regole di bersaglio di missione (`apply_target_rules`; le funzioni d'appoggio `_is_designated`,
`_is_hostile`, `_attack_over`, `:3069-3139`, sono pure o memoizzate) e `_range_entry` (memo `range_cache`). Puo'
impostare una volta `fire_control_knows_grounded` e scrivere un warning se il lanciatore e' un aereo **a terra**
(`:3263-3268`), caso non pertinente (un lanciatore aereo e' in volo). **Nessuna estrazione casuale** (le sole estrazioni
del risolutore sono `:2402`, `:2623`, `:3977`, `:4107`). La sonda lo conferma: chiamarla per tutte le 223 coppie di
S16/S19AD/S35 lasciando il verdetto di oggi da' esiti IDENTICAL (§1.5, sonda `old`).

**Canali e scorta** [V]: i canali per evento-salva (`_on_resolve`, `:3906-3911`) **non** sono ridotti dal tiro
offensivo dell'intercettore sul lanciatore (si sottraggono solo i canali spesi per altre forze dello stesso dominio
nello stesso istante, `:3887-3892`, `:3910`). La **scorta** invece e' condivisa per arma: un missile sparato al
lanciatore e' tolto anche dalla scorta di intercettori (vista sulle stesse voci, `_Shadow.interceptor_stock`,
`:1766-1768`; `Asset/Weapon_Stores.py`). La revisione non cambia nessuna delle due cose.

### 1.4 Zona dell'arma contro V_I, per modello (dati di registro) [M]

Calcolo dai registri (`Vehicle_Data`, `Ship_Data`, `Ground_Weapon_Data`, `Ship_Weapon_Data`) con la stessa selezione di
`interceptor_weapons_from_registry`; raggi in km, quote in m relative all'asset. Sono **dati di registro**, non stime
nuove (le quote dei CIWS sono gia' dichiarate "STIMA B" nel registro, `Asset/Ship_Weapon_Data.py:1562-1563`,
`:1578-1579`, `:1594-1595`).

| Modello | V_I oggi (raggio; fascia) | Armi `Anti_Missile` (raggio; fascia) | Raggio zona nuova (max) |
|---|---|---|---|
| 9K331-Tor | 12; 10-6000 | 9M331 12; 10-6000 | 12 (uguale) |
| 9K37-Buk | 35; 15-22000 | 9M38 35; 15-22000 | 35 (uguale) |
| S-300PS | 75; 25-27000 | 5V55R 75; 25-27000 | 75 (uguale) |
| 2K22-Tunguska | 8; 0-3500 | 2A38M 4; 0-3500 + 9M311 8; 15-3500 | 8 (fascia per arma diversa) |
| Flakpanzer-Gepard | 4; 0-3000 | Oerlikon-KDA 4; 0-3000 | 4 (uguale) |
| USS Arleigh Burke IIa, CG-65 | 240; 15-33000 | SM-2ER 240; 25-33000 + ESSM 50; 15-15000 + Phalanx 1,5; 0-1500 | 240 |
| Type 052C | 200; 25-27000 | HHQ-9 200; 25-27000 + Type-730 3; 0-3000 | 200 |
| CG 1164 Moskva | 150; 25-27000 | S-300F 150 + AK-630 4; 0-3000 | 150 |
| CGN 1144.2 Piotr Velikiy, CV 1143.5 Admiral Kuznetsov | 150; 10-27000 | S-300F 150 + SA-N-9 15 + AK-630 4 | 150 |
| Type 054A | 70; 15-12000 | HHQ-16 70 + Type-730 3 | 70 |
| CVN-70 Carl Vinson ... CVN-75 Harry S. Truman (sei voci) | 50; 15-15000 | ESSM 50 + Sea Sparrow 19 + Phalanx 1,5 | 50 |
| CV-59 USS Forrestal, LHA-1 Tarawa | 19; 15-6000 | Sea Sparrow 19 + Phalanx 1,5 | 19 |
| FFG 11540 Neustrashimy | 15; 10-6000 | SA-N-9 15 + AK-630 4 | 15 |
| Type 052B Guangzhou-class, Type 071 | 13; 8-5000 | HHQ-7 13 + Type-730 3 | 13 |
| **FF 1135M Rezky, FFL 1124.4 Grisha, FSG 1241.1MP Molniya** | **12; 10-6000** (SA-N-4) | **AK-630 4; 0-3000** | **4** |
| **FFG-46** | **74; 60-24000** (SM-1) | **Phalanx 1,5; 0-1500** | **1,5** |

Nomi della colonna "Modello" = chiavi esatte dei registri (`'model'` di `Asset/Ship_Data.py` e `Asset/Vehicle_Data.py`,
verificate il 2026-11-25); i nomi delle **armi** nelle colonne 2-3 sono **abbreviati** (es. SM-2ER = chiave
`RIM-156-SM-2ER`, ESSM = `RIM-162-ESSM`, Phalanx = `Mk-15-Phalanx`): per controlli o test si leggono le chiavi dai
record `weapons` del modello e da `Ship_Weapon_Data.SHIP_WEAPONS` / `Ground_Weapon_Data.GROUND_WEAPONS`, non da questa
tabella.

Per tutte le navi la fascia cambia (il CIWS scende a 0 m); con la zona **per arma** (SD-2) un punto conta "dentro" solo
se e' nella fascia e nel raggio della **stessa** arma.

### 1.5 Sonde eseguite per questa Proposta (2026-11-24, sola lettura) [M]

Script: `/tmp/claude-1000/-home-marco-Sviluppo-Warfare-Model/db4537e6-f512-41af-b45f-1c8dabc15406/scratchpad/l1rev/sonda_L1_nuova.py`
(prototipo della regola di §4.2 in memoria; **non** nel repository, cartella temporanea della sessione). Modi: `old`
(verdetto di oggi, controllo della sonda), `full` (regola proposta, §4.2). In ogni modo registra, per ogni coppia
valutata, i verdetti delle varianti (`old`, `full`, `detonly` = solo "rilevato", `zoneonly` = solo zona per arma,
`l3t` = `full` con `t_fire = t_launch + refire_interval` come L3, `oldzone_full` = V_I di oggi + condizione (2)).

**L-1 — controllo della sonda (`old`, unita' S16, S19AD, S35-ADTGT, 60 esecuzioni, 37 s).** Confronto con la
fotografia: **IDENTICAL**. Quindi chiamare in fase di risoluzione `_detection_time_of`, `_in_range_at` e la fire control
per ogni coppia, lasciando il verdetto di oggi, non cambia nulla (nessuna estrazione, nessuno stato alterato). Sulle 223
coppie valutate in quelle unita' i verdetti delle varianti sono:

| Variante | Coppie escluse | Dove |
|---|---|---|
| `old` (regola di oggi) | 13 | S16 7, S19AD 2, S35 4 (le 13 della sonda del 2026-11-24) |
| `full` (regola proposta) | **0** | — |
| `detonly` (C-ripiego) | 0 | — |
| `l3t` (`t_fire` come L3) | 0 | — |
| `zoneonly` (solo zona per arma, senza condizione (2)) | 2 | S19AD: la zona del Tor e' quella di oggi (12 km), il lanciatore non era rilevato |
| `oldzone_full` (V_I di oggi + condizione (2)) | 4 | S35: la Rezky vedeva l'A-10C e lo aveva a portata della SA-N-4: e' la zona per arma (d) che libera queste 4 |

Le 13 esclusioni di oggi cadono per due ragioni distinte: in S16 e S19AD (9) per la condizione (2) — lanciatore **non
rilevato**; in S35 (4) per la zona — lanci a 10,74-11,05 km, dentro i 12 km della SA-N-4 ma fuori dai 4 km
dell'AK-630, l'unica arma `Anti_Missile` della Rezky. Le 7 coppie di S16 restano fuori dalla zona dell'AK-630 anche
quando il lancio e' a 2,3-3,0 km in orizzontale: gli F/A-18C sono 6000 m sopra la corvetta, oltre i 3000 m della fascia
dell'AK-630.

**L-2 — cattura completa con la regola proposta (`full`, 1219 esecuzioni, 1146 s sulla VM osboxes).** Risultato
principale:

- Coppie (intercettore, salva) valutate: **414** (S2 46, S6 113, S11 30, S16 152, S19AD 19, S35-ADTGT 54). La regola
  proposta **non esclude nessuna coppia** in nessuna delle 1219 esecuzioni.
- Confronto con la fotografia: **6 CHANGED, 1213 UNCHANGED, 0 NEW, 0 MISSING**; le 6 sono **le stesse** della sonda con
  L1 spenta del tutto, e per le 60 esecuzioni di S16, S19AD e S35-ADTGT la cattura e' **identica** a quella con L1
  spenta (confronto diretto fra le due catture: 0 differenze). Sulle esecuzioni fotografate la regola rivista equivale
  quindi a "nessuna L1"; la sua differenza da "nessuna L1" sta solo nei casi oggi non esercitati (lanciatore rilevato,
  a portata, dentro la zona di un'arma intercettrice), coperti dai test unitari del blocco 2.
- Le 6 esecuzioni cambiate (prima = fotografia, dopo = regola proposta):

| Esecuzione | Intercettazioni | Colpi al danno (`damage_events`) | Esito della forza difesa | Altro |
|---|---|---|---|---|
| `S16/S16-3` | 34 -> **44** (fsg0 20 -> 24, fsg1 14 -> 20, AK-630) | 20 -> 15 | Red-Port `destroyed` -> **`held`** | le due Molniya sopravvivono (distrutti 13 -> 11) |
| `S19AD/S19-4/tor_forward_ifv_only` | 0 -> **2** (Tor, 9M331) | 10 -> 6 | Red-Line `held` -> `held` | BMP-2 distrutti 2 -> 1; il Tor spara 8 -> 6 missili sugli A-10C (2 spesi per intercettare) |
| `S35-ADTGT/S35-ADTGT-0/naval_maverick_off` | 2 -> **6** (AK-630) | 5 -> 4 | Red-Navy `destroyed` -> **`held`** | la Rezky sopravvive; colpi su Blue-CAS 4 -> 6 |
| `S35-ADTGT/S35-ADTGT-1/naval_maverick_off` | 2 -> **6** | 6 -> 4 | `destroyed` -> **`held`** | come seme 0 |
| `S35-ADTGT/S35-ADTGT-2/naval_maverick_off` | 0 -> **4** | 6 -> 6 | `destroyed` -> **`held`** | colpi su Blue-CAS 2 -> 4, la Rezky spara 6 -> 8 colpi |
| `S35-ADTGT/S35-ADTGT-3/naval_maverick_off` | 2 -> **4** | 5 -> 4 | `destroyed` -> **`held`** | — |

- **Distanze dei lanci rispetto ai bordi** (anche quelli appena fuori, che la prima sonda non registrava), sulle 414
  coppie della cattura `full`; rapporto = distanza orizzontale / raggio della zona dell'arma piu' vicina con la quota
  nella fascia:

| Unita', intercettore | Coppie | Rapporto minimo / massimo | Note |
|---|---|---|---|
| S19AD, Tor | 19 | **0,808** / 1,475 | l'**unica** coppia dentro una zona per arma in tutte le 1219 esecuzioni: `S19-4`, `cas1` a 9,70 km, non rilevato -> si intercetta. I lanci del Tor arretrato sono a 17,69-17,70 km (1,475) |
| S35-ADTGT, Rezky (AK-630, 4 km) | 26 | **1,778** / 12,48 | il lancio piu' vicino e' a 7,11 km: nessun lancio vicino al bordo. Per il V_I di oggi (12 km) i lanci fuori piu' vicini erano a 14,70 km (1,225); il margine di 12,2 km citato nel manuale (§9.1, `10_Limiti_Estensioni_Divergenze.md:368-370`) non compare nelle coppie valutate oggi |
| S35-ADTGT, Tor (`land_tactical`) | 12 | 1,475 / 1,475 | 17,69-17,70 km |
| S35-ADTGT, Buk (`land_cruise`) | 16 | 2,594 | Kh-59 da ~90,8 km |
| S6, S-300PS | 13 | 1,585 / 1,663 | ~119-125 km |
| S6, Molniya (vs colpi navali di Burke e CG-65) | 100 | 27,0 / 31,5 | 108-126 km |
| S2, Buk | 46 | 2,154 / 2,700 | |
| S11, Tor / Gepard | 15 / 15 | 4,48 / 13,4 (minimi) | |
| S16, Molniya | 152 | — | tutte **fuori fascia** (lanciatori 6000 m sopra la nave, AK-630 fino a 3000 m); 2 coppie entro i 4 km in orizzontale |

  Rispetto al V_I di oggi, i lanci appena fuori dal bordo sono: S16 a 1,198 e 1,221 x 12 km, S35 a 1,225 x 12 km
  (Rezky; lanciatore rilevato ma **non** a portata della SA-N-4), tutti gia' intercettabili oggi.

**L-3 — test esistenti con la regola proposta in memoria.** Script
`/tmp/claude-1000/-home-marco-Sviluppo-Warfare-Model/db4537e6-f512-41af-b45f-1c8dabc15406/scratchpad/l1rev/suite_con_regola.py`:
suite completa (`unittest discover`, come `verifica.sh`) con `_may_intercept` sostituita dal prototipo della regola
rivista (zone per arma lette dal registro per modello; senza modello nessun vincolo, come SD-4). Esito sulla VM osboxes:
**`Ran 4973 tests`, `FAILED (failures=6, skipped=7)`**, 1226 s. I 6 test falliti:
1. `Test_Engagement_Resolver.TestLauncherInsideInterceptionZone.test_launch_inside_the_zone_is_never_intercepted`;
2. `...TestLauncherInsideInterceptionZone.test_zone_boundary_counts_as_inside`;
3. `...TestLauncherInsideInterceptionZone.test_zone_is_per_interceptor`;
4. `Test_Engagement_Resolver.TestCoordinationDomainSalvoDefence.test_launch_inside_the_escort_zone_is_not_intercepted` (x = 8000);
5. `Test_Engagement_Resolver.TestAirDefenceTargetRule.test_switch_on_filter_is_applied_before_not_instead_of_l1`;
6. `Test_Session_Scenarios_S19_Air_Defence.TestS19AirDefenceAllocation.test_forward_tor_engages_launchers_inside_its_zone` (seme `S19-4`).

I primi 5 descrivono la regola del 2026-09-28 con stub senza zone per arma: il blocco 2 li fissa a interruttore spento
(§4.2, test (a) e (a2)). Il sesto e' l'unico vero cambio di esito di scenario e si riscrive all'accensione (§4.5
punto 3). Nessun test di S16 o S35 fallisce. (Una prima passata sui soli quattro moduli interessati aveva dato gli
stessi 6 fallimenti su 465 test.)

---

## 2. Alternative e raccomandazione

Le decisioni a, c, d, e fissano la regola. Restano tre scelte di realizzazione: come verificare "bersaglio immediato"
(§2.1), come costruire la zona di un asset con piu' armi intercettrici (§2.2), dove calcolarla (§2.3).

### 2.1 Condizione (2), "bersaglio immediato"

**C-pieno (raccomandata).** Lanciatore rilevato dall'intercettore all'istante del lancio (come R-INT:
`_detection_time_of(intercettore, lanciatore, t_launch)` non None e `<= t_launch + TIME_EPS`) **e** almeno un candidato
dell'intercettore sul lanciatore, del passaggio del lancio, per cui `_in_range_at` e' vero a
`t_fire = max(candidate.t_ready, t_launch)` (entro `candidate.t_end`). Quali filtri di L2 si applicano e quali no:
riquadro "Scelta dell'utente del 2026-11-25" qui sotto.
- Pro: realizza la decisione c = 2 (rilevato e ingaggiabile per portata e scorta, con lo stesso controllo che L2 usa
  per il pool prioritario); riusa codice esistente senza modificarlo; nessuna estrazione; la ROE e l'arma designata
  della missione dell'intercettore entrano attraverso la fire control (`_fire_control` -> `apply_target_rules`,
  `:3230-3243`: con `only_designated` e un lanciatore non designato la fire control restituisce None: non e' un
  bersaglio immediato, i suoi colpi si intercettano); **non** entrano le ROE dipendenti dal tempo di `_is_deferred`
  (UF-1).
- Contro: piu' invasiva del ripiego (cerca il candidato per indice; chiama la fire control in fase di risoluzione);
  valuta scorta e regole di bersaglio (designati distrutti, ostili noti) all'istante della risoluzione, non del lancio
  (§5, R-1).
- Fattibilita' [V]: i candidati sono gia' in `self.candidates[intercettore]` (lista), l'indice e' la posizione nella
  lista; `_in_range_at` non muta il candidato (docstring `:3304-3306`, ramo VA `:3312`). Nessuna struttura nuova oltre a
  una cache.

**Scelta dell'utente del 2026-11-25 (opzione A della rilettura): la condizione (2) usa SOLO portata e scorta.** Oltre al
rilevamento, conta solo `_in_range_at` sul candidato del passaggio del lancio, con `t_fire = max(candidate.t_ready,
t_launch)` e `t_fire <= candidate.t_end + TIME_EPS`. **Non** si applicano gli altri filtri del ciclo `viable` di
`_schedule_next` (`:2860-2896`):
- `candidate.not_before` (`:2874-2875`; ingresso in portata o rinvio VA: la portata a `t_fire` e' gia' ricontrollata da
  `_in_range_at`);
- `_is_deferred`, cioe' le ROE dipendenti dal tempo (`:2892`; aggiungerlo e' l'upgrade futuro UF-1, §5.1);
- fine attivita' del tiratore (`activity_end`, `:2881`);
- intercettore a terra a `t_fire` (`self.grounded`, `:2885`);
- `candidate.exhausted` (`:2861`) e lo stato del bersaglio del candidato, cioe' del lanciatore (`operative`, `_gone`,
  `:2866`; v. SD-6).

Quindi la condizione (2) **non** e' "la stessa condizione del pool prioritario di L2": L2 filtra prima i candidati
in `_schedule_next` (`:2860-2896`) e poi applica `_in_range_at` (`:2906`); L1 rivista riusa **solo** il controllo di
portata e scorta `_in_range_at` (con il controllo su `t_end`), cioe' l'ultimo passo del pool prioritario.

**C-ripiego.** Solo "rilevato all'istante del lancio" (come R-INT per il lancio osservato).
- Pro: una riga, nessuna chiamata alla fire control.
- Contro: un intercettore che vede il lanciatore ma non ha armi per colpirlo (fuori portata, senza scorta, ROE)
  ignorerebbe comunque i suoi colpi: e' il difetto (i) in forma ridotta.

**Raccomandazione: C-pieno.** E' fattibile senza toccare `_in_range_at`, e la sonda (§1.5) mostra che sulle esecuzioni
fotografate le due varianti danno lo stesso esito (0 coppie diverse su 414 nella cattura `full`, 0 su 223 nella sonda
`old`): la scelta conta per la correttezza nei casi non ancora esercitati
(lanciatore visto ma fuori portata o fuori ROE), non per la fotografia di oggi.

### 2.2 Zona di un asset con piu' armi intercettrici (decisione d = 2)

"La zona dell'arma che intercetta" e' ambigua quando l'asset ha piu' armi `Anti_Missile` (Burke: SM-2, ESSM, Phalanx),
perche' l'allocazione non sceglie l'arma per salva: il consumo segue la regola F (cannoni prima). Tre letture:

- **Z-unione (raccomandata, SD-2).** Dentro se il punto e' nel cilindro di **almeno una** arma `Anti_Missile`
  (raggio e fascia della stessa arma). Statica (dal registro), nessuna costante. Il Burke resta a 240 km come accettato
  dall'utente. Un lanciatore a 8 km e 0 m di quota relativa da un Tunguska non e' "dentro" il 9M311 (fascia da 15 m)
  ma e' fuori dai 4 km del 2A38M: fuori.
- **Z-involucro.** Un solo cilindro: raggio massimo, fascia dalla quota minima alla massima di tutte le armi (la forma di
  `air_defense_volume`). Pro: identica nella forma a oggi. Contro: include punti che nessuna arma copre (per ogni nave
  la fascia scende a 0 m per il CIWS anche a 240 km: un lanciatore radente a 200 km dal Burke sarebbe "dentro").
- **Z-arma-di-turno.** La zona della prima arma che la regola F consumerebbe (il cannone): il Burke scenderebbe a 1,5 km,
  in contrasto con la conseguenza accettata dall'utente. Scartata.

Una variante dinamica di Z-unione (solo armi con scorta all'istante della risoluzione) non e' proposta: la zona
cambierebbe durante la sessione, e la condizione (2) guarda gia' la scorta dell'arma con cui si colpirebbe il
lanciatore.

### 2.3 Dove calcolare la zona per arma (core indifferente al simulatore)

**M-Mobile (raccomandata, SD-3).** Nuovo metodo `Mobile.interceptor_envelopes()` in `Asset/Mobile.py`, accanto a
`interceptor_weapons_from_registry`, con lo **stesso filtro** estratto in una funzione di modulo (una sola selezione:
il docstring di `interceptor_weapons_from_registry`, `:1062-1065`, chiede che capacita' e scorta "non possano
divergere"). Legge solo i registri del core (`Vehicle_Data`, `Ship_Data`, `Ground_Weapon_Data`, `Ship_Weapon_Data`): nessuna
dipendenza dall'adapter DCS. Non richiede la posizione (restituisce valori relativi all'asset).

**M-Risolutore.** Ricostruire la zona nel risolutore da `shadow.interceptor_weapons` (solo nomi) cercando il tipo d'arma
nei registri: duplica la conoscenza del formato dei registri nel motore (km per le navi, `range['direct']` in m per i
veicoli). Scartata.

### 2.4 Scelte derivate dall'analista (confermabili; il piano le adotta)

| Sigla | Scelta | Motivo |
|---|---|---|
| SD-1 | C-pieno (§2.1) con `t_fire = max(candidate.t_ready, t_launch)` e candidato del passaggio del lancio: `candidate.t_ready <= seen + total + TIME_EPS` e `t_fire <= candidate.t_end + TIME_EPS`, poi `_in_range_at`. **Solo portata e scorta** (scelta A dell'utente, 2026-11-25): **non** si applicano `candidate.not_before`, `_is_deferred` (ROE a tempo; upgrade UF-1, §5.1), fine attivita' (`activity_end`), intercettore a terra (`grounded`), `candidate.exhausted`, `operative`/`_gone` del lanciatore. Il filtro su `t_ready` lascia passare anche candidati di passaggi **precedenti** del lancio; li esclude poi il controllo su `t_end` (un passaggio precedente finisce prima di `t_launch`) | "Ingaggiabile" e' il controllo di portata e scorta che L2 applica al pool prioritario (`_in_range_at`, `:2906`), all'istante utile piu' vicino al lancio, senza i filtri di `_schedule_next` che lo precedono (`:2860-2896`); il flag `exhausted` riflette decisioni del tiratore prese dopo il lancio (es. finestra superata quando ridecide), mentre portata e scorta sono ricontrollate da `_in_range_at`. Con `t_fire = t_launch + refire_interval` (forma di L3) la sonda da' lo stesso esito sulle esecuzioni fotografate (0 coppie diverse): la scelta non e' misurabile oggi, si preferisce la forma di L2 perche' la decisione c = 2 cita L2 |
| SD-2 | Z-unione (§2.2) | fedele a "la zona dell'arma", nessuna costante, Burke invariato |
| SD-3 | M-Mobile (§2.3) | una sola selezione delle armi intercettrici, core indipendente dall'adapter |
| SD-4 | Senza `interceptor_envelopes` (stub, oggetti non `Mobile`) o con risultato None: **nessun vincolo** L1 (si intercetta, salvo R-INT, canali, scorta, BI); **nessun** ripiego su `air_defense_volume` | "dato mancante = non modellato", come L1 di oggi senza V_I (`:3723-3724`); ripiegare sul V_I reintrodurrebbe la zona di armi che non intercettano |
| SD-5 | Un solo interruttore per le due condizioni (zona per arma e bersaglio immediato) | la regola dell'utente e' unica; le varianti parziali sono misurate dalla sonda (`zoneonly`, `oldzone_full`) senza bisogno di interruttori nel motore |
| SD-6 | Lo stato del lanciatore **dopo** il lancio (abbattuto, a terra, forza rotta) non entra nella condizione (2) | la regola descrive la scelta del difensore al lancio; il caso "lanciatore abbattuto, missile ancora in volo" e' il punto di dottrina aperto PD-1 (§5); il tipo di guida del missile come criterio e' l'upgrade futuro UF-2 (§5.1) |

### 2.5 Interruttore e criterio di permanenza

Nome **`L1_IMMEDIATE_TARGET_RULE`**, default **`False`** (comportamento attuale), letto **una volta per run**
all'inizio di `_EngagementRun` come `BI_AD_TARGET_RULE` (`:2058`), cosi' i test lo sostituiscono con
`patch.object(ER, 'L1_IMMEDIATE_TARGET_RULE', True)` attorno all'intera esecuzione.

**L1 precedente e' un'alternativa valida?** Parere dell'analista: **no**. Le decisioni a = 2, c = 2, d = 2 la
sostituiscono; la regola di oggi impedisce di intercettare i colpi di un lanciatore che l'intercettore non vede (9 casi su
13) e usa la portata di armi che non intercettano. Per il criterio di progetto sugli interruttori (si tengono solo se lo
stato precedente e' un'alternativa valida, si eliminano se sostituiti; rimozione con nuova fotografia decisa
dall'utente) l'interruttore e' **temporaneo**: serve a introdurre la regola a fotografia invariata, a misurarla
(blocco 4) e ad accenderla (blocco 5); dopo l'accensione e la fotografia nuova installata dall'utente si elimina
(blocco 6). La conferma e' la domanda Q-L1-1 (§3).

---

## 3. Decisioni aperte per l'utente

Le decisioni di design della regola sono prese (a, c, d, e). Restano solo decisioni di **processo**, nessuna bloccante
per i blocchi 1-4:

**Q-L1-1 — Interruttore temporaneo o permanente.** *Ruoli*: l'interruttore `L1_IMMEDIATE_TARGET_RULE` decide quale L1
usa il motore; spento = regola del 2026-09-28, acceso = regola del 2026-11-24. *Esempio*: S19AD, seme `S19-4`, Tor
avanzato: spento il Tor non ferma le due salve di `cas1` (2+2 AGM-65D lanciati a ~9,7 e ~9,5 km, dentro i suoi 12 km) anche se
non vede l'A-10C; acceso ne ferma 2 colpi (misura §1.5; R-INT lo permette, 23 s di volo). *Opzioni*: (A) temporaneo, eliminato dopo
l'accensione e la fotografia nuova (blocco 6). Pro: un solo comportamento nel motore, meno codice e test da mantenere.
Contro: la regola di oggi non si puo' piu' riprodurre se non da git. (B) permanente. Pro: confronto sempre possibile.
Contro: mantiene una regola che l'utente ha sostituito, con `_interception_zone` e 7 test che la descrivono.
*Raccomandazione*: **(A)**, perche' la regola di oggi contraddice la regola dell'utente (esclude colpi di lanciatori
non visti); da decidere solo al momento del blocco 6.

**Q-L1-2 — Accensione.** Dopo il blocco 4 (rapporto delle esecuzioni cambiate) l'utente decide se accendere
(blocco 5); e' la stessa forma di PB (Pd al bordo). Raccomandazione: accendere se il rapporto conferma l'esito atteso di
§4.8 (6 esecuzioni, tutte spiegate in §1.5, L-2).

**Q-L1-3 — Ordine con BI.** `Stato_Progetto_DES.md` (n. 1) lega l'accensione di BI alla revisione di L1, perche' S35
dipende da entrambe. Con L1 rivista la dipendenza di S35 da L1 cambia (§4.7.3). Raccomandazione: accendere prima L1
(blocco 5), installare la fotografia, poi riaprire la decisione su BI con una sonda propria: due cambi di fotografia
separati, ciascuno attribuibile alla sua causa (come per la F4: deviazione 2 del piano della Missione).

**Q-L1-4 — Uno scenario che eserciti l'esclusione (facoltativo).** *Fatto*: sulle 1219 esecuzioni la regola rivista
non esclude mai nulla (§1.5, L-2), quindi accesa la fotografia coincide con "nessuna L1" e l'esclusione (lanciatore
visto, a portata, dentro la zona) e' provata solo dai test unitari. *Opzioni*: (A) nessuno scenario nuovo (questo
piano). Pro: nessuna esecuzione nuova, nessuna fotografia in piu'. Contro: la parte "bersaglio immediato" non ha una
regressione di scenario. (B) uno scenario S37 dedicato (es. Tor con scorta abbondante che vede l'A-10C prima del lancio
da ~9 km), in una Proposta separata. Pro: copertura di scenario della regola. Contro: esecuzioni nuove (NEW) e
geometria da cercare con una sonda. *Raccomandazione*: **(A)** ora; (B) solo se l'utente vuole la copertura prima di
accendere.

Punti di **dottrina** aperti (non da decidere qui): PD-1 e PD-2 in §5. Upgrade futuri annotati il 2026-11-25 (non da
decidere ora, da riconsiderare con PD-1/PD-2): UF-1 (ROE a tempo nella condizione (2)) e UF-2 (guida del missile) in
§5.1.

Decisione presa il 2026-11-25 dopo la rilettura: condizione (2) = **solo portata e scorta** (opzione A; §2.1, SD-1,
§4.2 punto 5); l'opzione B (con `_is_deferred`) e' l'upgrade UF-1.

---

## 4. Piano di intervento (C-pieno, Z-unione, M-Mobile, interruttore spento nei blocchi 1-4)

Blocchi piccoli, ciascuno con verifica parziale; suite e confronto **completi solo a fine blocco 3** con
`tools/ai/verifica.sh`, **mai in parallelo**. `<python>` = interprete stampato nell'ESITO di `verifica.sh` (sulla VM
osboxes `python3`; sul ProArt `.direnv/python-3.12/bin/python3`). Comandi dalla root del repo.

| Blocco | Chi | Contenuto | Verifica |
|---|---|---|---|
| 1 | esecutore | `Asset/Mobile.py`: filtro estratto + `interceptor_envelopes()`; test in `Test_Mobile` | test mirati, confronto parziale |
| 2 | esecutore | `Logic/Engagement_Resolver.py`: interruttore, zona per arma, bersaglio immediato; test unitari | test mirati, confronto parziale |
| 3 | esecutore | test di scenario con l'interruttore acceso (fuori dalla fotografia), docstring; rapporto | **suite e confronto completi** |
| 4 | sessione principale | sonda con l'interruttore vero acceso in memoria; rapporto delle esecuzioni cambiate e dei test che falliscono | sola lettura |
| 5 | esecutore, **solo dopo la decisione dell'utente** | accensione: default `True`, test adeguati | suite e confronto completi |
| 6 | esecutore, **solo dopo la fotografia nuova e Q-L1-1 = A**; **da ripianificare** (§4.6) | eliminazione dell'interruttore e della regola di oggi | suite e confronto completi |

### 4.1 Blocco 1 — Zona per arma in `Asset/Mobile.py` (nessun cambio di comportamento)

1. **Funzione di modulo** subito dopo `INTERCEPTOR_TASK = 'Anti_Missile'` (`Asset/Mobile.py:208`), prima del commento
   dei CIWS (`:210`):

   ```python
   def _is_interceptor_weapon(wdata) -> bool:
       """Filtro della regola D su un record d'arma del registro: dati di quota (min e max non None), task 'Anti_Air'
       se il record dichiara `task`, task INTERCEPTOR_TASK dichiarato, quota massima > 0. Una sola selezione per
       `interceptor_weapons_from_registry` (chi intercetta, scorta) e `interceptor_envelopes` (zona della regola L1)."""
       if (wdata is None or wdata.get('min_altitude') is None or wdata.get('max_altitude') is None
               or ('task' in wdata and GROUND_WEAPON_TASK['Anti_Air'] not in wdata['task'])
               or INTERCEPTOR_TASK not in (wdata.get('task') or ())):
           return False

       return not float(wdata.get('max_altitude', 0)) <= 0.0
   ```
   (`GROUND_WEAPON_TASK` e' gia' importato a livello di modulo, `:13-21`.) L'ultima riga e' la forma **letterale**
   del controllo di oggi `if float(wdata.get('max_altitude', 0)) <= 0.0: continue` (`:1119-1120`), negata: **non**
   scriverla come `> 0.0`, che differisce per `NaN` (oggi un'arma con quota massima `NaN` resta capace, perche'
   `NaN <= 0.0` e' falso; con `> 0.0` uscirebbe). Cosi' "comportamento identico" vale anche per quel caso.

2. **`interceptor_weapons_from_registry`** (`:1059-1129`): le righe `:1112-1120` (commento del filtro su due righe, `if`
   composto, `continue`, riga vuota, controllo `max_altitude <= 0.0`, `continue`) diventano

   ```python
                   # Filtro di air_defense_volume() (dati di quota, task Anti_Air) piu' la regola D: task INTERCEPTOR_TASK
                   # dichiarato (`_is_interceptor_weapon`). Senza campo `task` l'arma non e' capace.
                   if not _is_interceptor_weapon(wdata):
                       continue
   ```
   seguite dalla riga `result[valid[0]] = weapon_type in INTERCEPTOR_GUN_WEAPON_TYPES` invariata. Comportamento
   identico (stesse condizioni, stesso ordine, stessa forma del confronto sulla quota massima, anche per `NaN`; `wdata`
   None e' gia' gestito dalla funzione).

3. **Nuovo metodo** subito dopo `interceptor_weapons_from_registry` (prima di `interceptor_capability`, `:1131`):

   ```python
   def interceptor_envelopes(self) -> Optional[Tuple[Tuple[str, float, float, float], ...]]:
       """Zona di ciascuna arma INTERCETTRICE (regola D) del modello: ((modello, raggio [m], quota min [m], quota max [m]), ...).

       Stessa selezione di `interceptor_weapons_from_registry` (`_is_interceptor_weapon`, CIWS navali compresi), nello
       stesso ordine (tipi d'arma del registro, poi voci); un modello ripetuto conta una volta (la prima). Raggio: per le
       navi `range` [km] x 1000, per i veicoli `range['direct']` [m] (le stesse letture di `air_defense_volume`);
       quote AGL relative all'asset, come la base del cilindro di `air_defense_volume`. Armi con raggio <= 0 escluse.
       Usata dalla regola L1 rivista (Engagement_Resolver, interruttore L1_IMMEDIATE_TARGET_RULE): un lancio e'
       "dentro la zona dell'arma che intercetta" se e' nel cilindro di almeno una di queste armi. Non dipende dalla
       posizione. Dati di registro, nessuna stima nuova.

       Returns:
           tupla non vuota, oppure None — senza sollevare — se il modello non e' noto o non ha armi intercettrici con
           portata (stessi casi di `interceptor_weapons_from_registry`, piu' le armi senza portata).
       """
   ```
   Corpo: stessa struttura di `interceptor_weapons_from_registry` (import locali dei quattro registri, `model`,
   `data_record`, `weapons`, `is_ship`, `allowed`, `weapon_db`, ciclo su `self._valid_item(item)`), con
   `if not _is_interceptor_weapon(wdata): continue`; poi
   `radius = float(wdata.get('range', 0) or 0) * 1000.0` se `is_ship`, altrimenti
   `radius = float((wdata.get('range') or {}).get('direct', 0) or 0)` (se `range` non e' un dict per un veicolo:
   `radius = 0.0`); se `radius <= 0.0` o il modello e' gia' presente: `continue`; altrimenti accoda
   `(valid[0], radius, float(wdata['min_altitude']), float(wdata['max_altitude']))`. Alla fine
   `return tuple(result) if result else None`. Log solo a livello `debug` (come `interceptor_weapons_from_registry`),
   mai warning: e' chiamata una volta per intercettore e per run.

4. Nient'altro cambia in `Mobile` (`air_defense_volume`, `interceptor_capability`, scorte, `Military`).

**Test del blocco 1** — `Test/Test_Mobile.py`:
- aggiungere `'interceptor_envelopes'` a `_STORES_MEMBERS` (`:1481-1491`), cosi' `_InterceptorStub` lo porta;
- nuova classe `TestInterceptorEnvelopes(unittest.TestCase)` subito dopo `TestInterceptorStockFromRegistry`
  (`:1903-2057`), con **lo stesso** `setUp`/`tearDown` (registri finti `_FAKE_GW`, logger mockato):

| # | Nome | Asserzioni |
|---|---|---|
| 1 | `test_vehicle_missile_envelope` | `_FakeVehicleData._registry['buk'] = _WeaponsRecord({'MISSILES': [('9M38-SAM', 4)]})`; `interceptor_envelopes() == (('9M38-SAM', 3000.0, 0.0, 3000.0),)` (dati finti di `_AD`: `direct` 3000, quote 0-3000) |
| 2 | `test_gun_and_missile_are_two_envelopes` | tunguska finto (`AA_CANNONS` 2A38M + `MISSILES` 9M311): due voci, nell'ordine dei tipi del record, modelli `('2A38M-30mm', '9M311-SAM')` |
| 3 | `test_anti_air_without_anti_missile_has_no_envelope` | strela10 finto (`9M37-SAM`, solo `Anti_Air`): `None` (e `interceptor_weapons_from_registry()` None, coerente) |
| 4 | `test_ship_sam_and_ciws_in_km` | `Ship_Data._registry['test-envelope-ship'] = _ship_record({'MISSILES_SAM': [('RIM-162-ESSM', 32)], 'CIWS': [('Mk-15-Phalanx', 3)], 'MISSILES_ASM': [('RGM-84-Harpoon', 8)]})`: voci `('RIM-162-ESSM', 1000 * SHIP_WEAPONS['MISSILES_SAM']['RIM-162-ESSM']['range'], ...)` e `('Mk-15-Phalanx', 1500.0, 0.0, 1500.0)`; nessuna voce per l'Harpoon. Valori letti da `SHIP_WEAPONS` (registro vero), non scritti a mano |
| 5 | `test_same_selection_as_interceptor_weapons` | per i record dei test 1-4: `{m for m, *_ in interceptor_envelopes()} == set(interceptor_weapons_from_registry())` |
| 6 | `test_unknown_models_and_aircraft_are_none` | `model=None`, `'ignoto'`, un aereo finto in `_FakeAircraftData`: `None` |
| 7 | `test_malformed_items_and_missing_range_are_skipped` | `'odd'`: `{'MISSILES': [('9M33-SAM', 6), ('broken',), ('9M33-SAM', -5)]}` -> una sola voce `9M33-SAM`; `_FAKE_GW['MISSILES']['test-norange'] = dict(self._AD, range={'direct': 0})` e record `{'MISSILES': [('test-norange', 2)]}` -> `None` (mentre `interceptor_weapons_from_registry()` la conta: la portata non e' nel filtro della regola D) |
| 8 | `test_real_registry_rezky_is_the_ak630` | con `_vd_mod` non coinvolto (nave): `Ship_Data._registry['FF 1135M Rezky']` reale -> `_InterceptorStub(model='FF 1135M Rezky').interceptor_envelopes() == (('AK-630', 4000.0, 0.0, 3000.0),)`; e per `'USS Arleigh Burke IIa'` il raggio massimo e' `240000.0` |

Il test 8 usa il registro navale **vero** (importato dal modulo, `:31`), come gli altri test navali del file.

**Verifica parziale del blocco 1:**
```
<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Mobile
<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Military
<python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json --only '^(S6|S11|S16|S19AD|S35-ADTGT)/' --quiet --summary
```
Atteso: tutti OK (Test_Mobile con 8 test in piu' della base letta prima di iniziare); confronto parziale
`compared N runs: IDENTICAL` (N = esecuzioni di quelle cinque unita'). (Non esiste un `Test_Weapon_Stores`: la selezione
degli intercettori e' coperta da `Test_Mobile.TestInterceptorStockFromRegistry` e da `Test_Military`.)

### 4.2 Blocco 2 — Regola L1 rivista nel risolutore (interruttore SPENTO)

**File `Logic/Engagement_Resolver.py`.**

1. **Interruttore**, subito dopo `VA_ENGAGEMENT_ALTITUDE_BAND = False` (`:636`), prima del commento di `AD_DOMAINS`:

   ```python
   # Regola L1 rivista (Proposta_Revisione_L1_Lanciatore_Bersaglio.md, decisioni dell'utente del 2026-11-24), interruttore
   # dedicato e TEMPORANEO (si elimina dopo l'accensione e la fotografia nuova, se l'utente conferma Q-L1-1):
   #   * `L1_IMMEDIATE_TARGET_RULE` (SPENTO). Acceso: un intercettore NON ferma i colpi di una salva solo se (1) il punto di
   #     lancio e' dentro la zona di almeno una sua arma intercettrice (`Mobile.interceptor_envelopes`: raggio e fascia
   #     di quota della stessa arma; bordo = dentro) E (2) il lanciatore e' un suo bersaglio immediato: rilevato da lui
   #     all'istante del lancio (come R-INT) e ingaggiabile con un'arma con scorta e a portata (solo `_in_range_at`, il
   #     controllo di portata del pool prioritario di L2, senza gli altri filtri di `_schedule_next`: niente ROE a
   #     tempo `_is_deferred`, `not_before`, fine attivita', intercettore a terra, `exhausted`).
   #     Senza zone per arma (dato mancante) nessun vincolo. Spento: la regola del 2026-09-28 (V_I di
   #     `Mobile.air_defense_volume`, nessuna condizione sul lanciatore). Letto all'inizio di ogni run. Nessuna
   #     estrazione in piu' ne' in ordine diverso in nessuno dei due stati; nessuna costante nuova.
   L1_IMMEDIATE_TARGET_RULE = False
   ```

2. **`_EngagementRun.__init__`**: subito dopo `self.ad_domain_cache: Dict[str, str] = {}` (`:2059`):

   ```python
           # L1 rivista (2026-11-24): interruttore letto una volta per run e zone delle armi intercettrici per intercettore
           # ((raggio, quota min, quota max) relativi; None = non modellate), memoizzate per id.
           self.l1_immediate_target = L1_IMMEDIATE_TARGET_RULE
           self.envelope_cache: Dict[str, Optional[Tuple[Tuple[float, float, float], ...]]] = {}
   ```

3. **`_interception_zone`** (`:3684-3702`): invariata (serve alla regola spenta). Docstring: aggiungere in coda
   "Usata solo con L1_IMMEDIATE_TARGET_RULE spento."

4. **Nuovo metodo `_interceptor_envelopes(self, shadow)`**, subito dopo `_interception_zone`:

   ```python
       def _interceptor_envelopes(self, shadow: "_Shadow") -> Optional[Tuple[Tuple[float, float, float], ...]]:
           """Zone delle armi intercettrici dell'intercettore come ((raggio, quota base, quota tetto), ...) RELATIVE alla
           sua posizione, da `Mobile.interceptor_envelopes()` (L1 rivista); memoizzato. None = non modellate: metodo
           assente, None, tupla vuota o voci malformate (nessun ripiego su `air_defense_volume`)."""
           if shadow.id not in self.envelope_cache:
               zones = None
               envelopes_of = getattr(shadow.asset, 'interceptor_envelopes', None)
               raw = envelopes_of() if callable(envelopes_of) else None

               if raw:
                   try:
                       zones = tuple((float(radius), float(bottom), float(top)) for _, radius, bottom, top in raw) or None
                   except (TypeError, ValueError):
                       zones = None

               self.envelope_cache[shadow.id] = zones

           return self.envelope_cache[shadow.id]
   ```

5. **Nuovo metodo `_immediate_target(self, shadow, salvo) -> bool`**, subito dopo `_detection_time_of` (`:3744-3767`):

   ```python
       def _immediate_target(self, shadow: "_Shadow", salvo: Salvo) -> bool:
           """L1 rivista, condizione (2): il lanciatore della salva e' un bersaglio immediato dell'intercettore.

           Rilevato da lui all'istante del lancio (come il lancio osservato di R-INT: `_detection_time_of`, nel passaggio
           che contiene il lancio) E ingaggiabile: un suo candidato sul lanciatore, del passaggio del lancio
           (`t_ready <= rilevamento + total`; i candidati di passaggi precedenti passano questo filtro ma sono esclusi da
           `t_end`, che cade prima del lancio), con `t_fire = max(t_ready, t_launch)` entro la fine del candidato, per cui
           `_in_range_at` e' vero (prima opzione della fire control con scorta, portata: il controllo che L2 applica al
           pool prioritario). SOLO portata e scorta: NON si applicano gli altri filtri di `_schedule_next` (`not_before`,
           ROE a tempo `_is_deferred`, fine attivita', intercettore a terra, `exhausted`, stato del lanciatore).
           Scorta e regole di bersaglio allo stato della risoluzione. Deterministico, nessuna estrazione; non muta i
           candidati.
           """
           seen = self._detection_time_of(shadow.id, salvo.shooter_id, salvo.t_launch)

           if seen is None or seen > salvo.t_launch + TIME_EPS:
               return False

           latest_ready = seen + self._profile(shadow.id).total + TIME_EPS

           for index, candidate in enumerate(self.candidates.get(shadow.id, ())):
               if candidate.target_id != salvo.shooter_id or candidate.t_ready > latest_ready:
                   continue

               t_fire = max(candidate.t_ready, salvo.t_launch)

               if t_fire > candidate.t_end + TIME_EPS:
                   continue

               if self._in_range_at(shadow, index, candidate, t_fire):
                   return True

           return False
   ```

   **Elenco vincolante (scelta A dell'utente, 2026-11-25).** Il corpo di `_immediate_target` contiene **solo** i
   controlli scritti sopra: rilevamento (`_detection_time_of`), bersaglio del candidato, `t_ready <= latest_ready`,
   `t_fire <= t_end + TIME_EPS`, `_in_range_at`. L'esecutore **non** aggiunge: `candidate.not_before` (`:2874-2875`),
   `self._is_deferred(...)` (`:2892`; e' l'upgrade UF-1, §5.1), `activity_end` / `_activity_end_time` (`:2881`),
   `self.grounded.at(shadow.id, t_fire)` (`:2885`), `candidate.exhausted` (`:2861`), `operative` / `_gone` del
   lanciatore (`:2866`). Sul filtro `t_ready`: `latest_ready = seen + total + TIME_EPS` lascia passare anche i candidati
   dei passaggi **precedenti** a quello del lancio; li esclude il controllo `t_fire > candidate.t_end + TIME_EPS`, perche'
   un passaggio precedente finisce prima di `t_launch` e `t_fire >= t_launch`. Nel ripiego senza tratti (coppia assente
   da `own_passes_of`) `_detection_time_of` restituisce l'**ultimo** rilevamento (`:3757-3758`) e tutti i candidati
   precedenti passano il filtro su `t_ready`: anche qui decide `t_end` (fine della finestra del candidato).

6. **`_may_intercept`** (`:3719-3742`): il corpo di oggi diventa il metodo privato `_may_intercept_volume(self, shadow,
   salvo) -> bool` **senza** la cache (stesse righe `:3729-3738`, stesso ordine delle chiamate, `return allowed`), e
   `_may_intercept` resta il punto di chiamata con la cache:

   ```python
       def _may_intercept(self, shadow: "_Shadow", salvo: Salvo) -> bool:
           """Regola L1: True se l'intercettore puo' fermare i colpi della salva per la geometria del lancio.

           Con L1_IMMEDIATE_TARGET_RULE spento (default) la regola del 2026-09-28 (`_may_intercept_volume`: lancio fuori
           dal V_I); acceso la regola rivista del 2026-11-24 (`_may_intercept_revised`). Memoizzato per (intercettore,
           salva): ogni salva e' risolta una volta sola. Nessuna estrazione.
           """
           key = (shadow.id, salvo.salvo_id)

           if key not in self.may_intercept_cache:
               self.may_intercept_cache[key] = (self._may_intercept_revised(shadow, salvo) if self.l1_immediate_target
                                                else self._may_intercept_volume(shadow, salvo))

           return self.may_intercept_cache[key]

       def _may_intercept_revised(self, shadow: "_Shadow", salvo: Salvo) -> bool:
           """L1 rivista (2026-11-24): False solo se il punto di lancio (posizioni all'istante del lancio) e' nel cilindro
           di almeno un'arma intercettrice (bordo = dentro) E il lanciatore e' un bersaglio immediato
           (`_immediate_target`). Senza zone per arma o senza posizioni: True (dato mancante = non modellato)."""
           zones = self._interceptor_envelopes(shadow)
           launch = self._position_at(self.shadows[salvo.shooter_id], salvo.t_launch)
           here = self._position_at(shadow, salvo.t_launch)

           if zones is None or launch is None or here is None:
               return True

           horizontal = ((launch[0] - here[0]) ** 2 + (launch[1] - here[1]) ** 2) ** 0.5
           height = launch[2] - here[2]

           if not any(horizontal <= radius and bottom <= height <= top for radius, bottom, top in zones):
               return True

           return not self._immediate_target(shadow, salvo)
   ```
   Il docstring di `_may_intercept_volume` e' quello di oggi (`:3720-3725`) con in testa "Regola L1 del 2026-09-28
   (L1_IMMEDIATE_TARGET_RULE spento)".

7. **Commenti e docstring nel modulo** (testo, nessun effetto):
   - commento di `_on_resolve` (`:3894-3901`): dopo "(Mobile.air_defense_volume)" aggiungere "— con
     L1_IMMEDIATE_TARGET_RULE acceso solo se il lancio e' dentro la zona di una sua arma intercettrice E il lanciatore
     e' un suo bersaglio immediato (rilevato e a portata), v. `_may_intercept`";
   - docstring del modulo, punto 4 (`:44-52`): dopo "...i suoi colpi non si intercettano." aggiungere "Con
     `L1_IMMEDIATE_TARGET_RULE` acceso (SPENTO di default, Proposta_Revisione_L1_Lanciatore_Bersaglio.md) la zona e'
     quella delle armi intercettrici (`Mobile.interceptor_envelopes`) e l'esclusione vale solo se il lanciatore e' un
     bersaglio immediato dell'intercettore (rilevato all'istante del lancio e a portata di un'arma con scorta, con il
     controllo `_in_range_at` del pool prioritario di L2; nessun altro filtro di `_schedule_next`); nessuna estrazione."

**Ordine delle estrazioni RNG**: invariato per costruzione. `_may_intercept_revised`, `_interceptor_envelopes`,
`_immediate_target`, `_detection_time_of`, `_in_range_at` non chiamano `_draw` ne' `rng`/`pass_rng`/`breakpoint_rng`
[V, §1.3]. A interruttore spento il percorso eseguito e' quello di oggi riga per riga (stessa funzione, stessa cache).
Acceso, cambiano quali colpi arrivano al danno, quindi **quante** estrazioni di danno si fanno (`:3976-3978`, una per
colpo superstite) e tutto cio' che ne segue: e' l'effetto della regola, non uno spostamento.

**Determinismo**: nessun insieme/dizionario iterato in ordine non deterministico (la lista dei candidati e' in ordine di
rilevamento, fisso); nessuna dipendenza dall'ora o da `random`.

**Effetti sugli altri moduli e sui chiamanti** [V]: `_may_intercept` ha un solo chiamante (`_on_resolve`, `:3929`);
`_interception_zone` e `zone_cache` solo `_may_intercept` (ricerca `grep -rn "_may_intercept\|_interception_zone\|zone_cache"`:
nessun altro uso nel codice, solo il docstring `:298`). `Mobile.interceptor_envelopes` e' nuovo: nessun chiamante oltre al
risolutore. `Session_Simulator`, `Military.salvo_interceptors`, `Air_Route_Manager` (che usa `air_defense_volume` per
le rotte), `Scenario_Baseline` **non cambiano**. L'adapter DCS non e' toccato ne' importato.

**Test del blocco 2** — `Test/Test_Engagement_Resolver.py`:

(a) **`TestLauncherInsideInterceptionZone`** (`:1811-1874`): `_run` avvolge `ER.resolve_engagement` in
`patch.object(ER, 'L1_IMMEDIATE_TARGET_RULE', False)` (stato **spento esplicito**: i 7 test descrivono la regola del
2026-09-28 e restano validi dopo l'accensione, fino al blocco 6); docstring: aggiungere "Regola del 2026-09-28,
interruttore L1_IMMEDIATE_TARGET_RULE fissato spento; la regola rivista e' in TestL1ImmediateTarget."

(a2) **Due test d'altre classi che usano la geometria di L1 come leva** (falliscono con la regola rivista accesa,
misura L-3 di §1.5, perche' i loro intercettori stub non hanno `interceptor_envelopes` e non vedono il lanciatore):
- `TestCoordinationDomainSalvoDefence.test_launch_inside_the_escort_zone_is_not_intercepted` (`:3155-3164`);
- `TestAirDefenceTargetRule.test_switch_on_filter_is_applied_before_not_instead_of_l1` (`:4857-4860`).
In ciascuno il corpo del test va dentro `with patch.object(ER, 'L1_IMMEDIATE_TARGET_RULE', False):`, con il commento
"L1 del 2026-09-28 (la rivista richiede anche il bersaglio immediato: Proposta_Revisione_L1_Lanciatore_Bersaglio.md)".
Nient'altro cambia nelle due classi. Al blocco 6 vanno riscritti sulla regola rivista (stub con zone e rilevamento).

(b) **Nuova classe `TestL1ImmediateTarget(unittest.TestCase)`** subito dopo `TestLauncherInsideInterceptionZone`, con uno
stub nuovo (prima della classe):

```python
class _ArmedInterceptor(_ZonedInterceptor):
    """Intercettore con V_I (air_defense_volume) e zone delle armi intercettrici (Mobile.interceptor_envelopes)."""

    def __init__(self, asset_id, position, envelopes, vi_radius=12_000.0, **kwargs):
        super().__init__(asset_id, position, vi_radius, **kwargs)
        self._envelopes = envelopes

    def interceptor_envelopes(self):
        return self._envelopes
```

Costanti di classe: `ZONES = (('sam', 12_000.0, 0.0, 6_000.0),)`; `FIRE = _miss(rounds=1, max_range=20_000.0,
weapon='sam')` (l'arma con cui l'intercettore colpirebbe il lanciatore). Metodo comune
`_run(self, x, z=0.0, interceptors=None, observers=('r2',), see_from=0.0, fire=FIRE, spec=None, switch=True, rng=None)`,
costruito come `TestLauncherInsideInterceptionZone._run` (`:1821-1835`):
- `spec` di default `_miss(rounds=5, interceptable=True, time_of_flight=REACTION_TOF)` (salva di b1 a t = 2);
- `interceptors` di default `[_ArmedInterceptor('r2', (0.0, 0.0, 0.0), self.ZONES)]`; forza `red` = `[_Asset('r1')] +
  interceptors`, 3 canali ciascuno; tratti fermi per b1 in `(x, 0, z)`, r1 e ogni intercettore nella loro posizione;
- finestre: `ContactWindow('b1', 'r1', t_start=0.0, t_end=2.9, t_cpa=2.9, distance_cpa=x, range_a=50_000.0,
  range_b=None)` e, per ogni id in `observers`, `ContactWindow(id, 'b1', t_start=see_from, t_end=2.9, t_cpa=2.9,
  distance_cpa=x, range_a=50_000.0, range_b=None)` (l'osservatore rileva b1 a `see_from` con l'estrazione 0.0; il suo
  candidato ha `t_ready = see_from + 2`);
- fire control: `shooter.id == 'b1' and target.id == 'r1'` -> `spec`; `shooter.id != 'b1' and target.id == 'b1'` ->
  `fire`; altrimenti None;
- `rng` di default `_ScriptedRng([0.0] * 40)`; profili `_profiles({}, default=(2.0, 1.0))`;
- tutto dentro `patch.object(ER, 'L1_IMMEDIATE_TARGET_RULE', switch)` e `patch(_ER_LOGGER)`.
Si legge la risoluzione della salva di b1: `[r for r in result.resolutions if r.force_id == 'red'][0]` (con `fire`
l'intercettore spara anche a b1, quindi ci sono risoluzioni della forza `blue`). "Rilevato" = `observers` di default;
"non rilevato" = `observers=()`.

| # | Nome | Configurazione | Asserzioni |
|---|---|---|---|
| 1 | `test_switch_is_off_by_default` | — | `assertIs(ER.L1_IMMEDIATE_TARGET_RULE, False)` |
| 2 | `test_seen_launcher_in_range_inside_the_zone_is_not_intercepted` | x = 8000 | acceso: `intercepted == 0`; nessun `InterceptionEvent` di r2 |
| 3 | `test_unseen_launcher_inside_the_zone_is_intercepted` | x = 8000, `observers=()` | acceso: `intercepted == 3`, `interceptions_consumed() == {'r2': 3}`; **spento** (stessa configurazione): `0` (la differenza della revisione) |
| 4 | `test_launcher_seen_after_the_launch_is_intercepted` | x = 8000, `see_from=2.5` | acceso: `intercepted == 3` (rilevato dopo il lancio: non e' un lancio osservato) |
| 5 | `test_seen_launcher_out_of_weapon_range_is_intercepted` | x = 8000, `fire=_miss(rounds=1, max_range=5_000.0, weapon='sam')` | acceso: `intercepted == 3` |
| 6 | `test_seen_launcher_without_stock_is_intercepted` | x = 8000, `interceptors=[_ArmedInterceptor('r2', (0.0, 0.0, 0.0), ZONES, stores={'sam': 0, 'ciws': 1000}, interceptor_weapons={'ciws': True})]` | acceso: `intercepted == 3` (l'arma per il lanciatore non ha scorta; il CIWS intercetta: scorta 1000 // `Mobile.ROUNDS_PER_GUN_INTERCEPT`, letta dal modulo, >= 3) |
| 7 | `test_roe_none_means_not_an_immediate_target` | x = 8000, `fire=None` | acceso: `intercepted == 3` |
| 8 | `test_zone_is_the_interceptor_weapon_not_the_air_defence_volume` | x = 8000, `interceptors=[_ArmedInterceptor('r2', (0.0, 0.0, 0.0), (('ciws', 4_000.0, 0.0, 3_000.0),))]` (V_I di default 12 km) | acceso: `3` (fuori dai 4 km del CIWS, anche se rilevato e a portata della SAM: il caso Rezky); spento: `0` (dentro il V_I) |
| 9 | `test_zones_are_per_weapon_not_an_envelope` | intercettore con zone `(('ciws', 4_000.0, 0.0, 3_000.0), ('sam', 15_000.0, 10.0, 6_000.0))`; casi `(x, z, atteso)`: `(8000, 0, 3)` (sotto la fascia della SAM, fuori dal raggio del CIWS: Z-unione, un involucro direbbe "dentro"), `(8000, 1000, 0)`, `(3000, 5, 0)`, `(15_000, 1000, 0)` (bordo della SAM = dentro), `(15_000.5, 1000, 3)`, `(8000, 7000, 3)` (sopra il tetto di entrambe le armi) | acceso, `subTest` per caso |
| 10 | `test_without_envelopes_the_rule_does_not_apply` | `interceptors=[_ZonedInterceptor('r2', (0.0, 0.0, 0.0), 12_000.0)]` (V_I, nessun `interceptor_envelopes`), x = 8000, rilevato | acceso: `3`; spento: `0` (SD-4: nessun ripiego sul V_I) |
| 11 | `test_launch_outside_every_zone_is_the_same_in_both_states` | x = 15_000 | `result` acceso == `result` spento (dataclass `EngagementResult` uguale) e stesse chiamate a `rng` (`_ScriptedRng.calls`) |
| 12 | `test_rule_draws_nothing_from_the_rng` | x = 8000, `observers=()`, `rng` passato esplicitamente (due istanze): acceso intercetta, spento no | le liste `[(d.observer_id, d.target_id, d.draw) for d in result.detections]` sono uguali nei due stati; le estrazioni in piu' dello stato spento sono solo quelle di danno: `rng_off.calls - rng_on.calls == 3` (tre colpi in meno arrivano al danno da acceso) |
| 13 | `test_rule_is_per_interceptor` | `interceptors=[_ArmedInterceptor('r2', (0.0, 0.0, 0.0), ZONES), _ArmedInterceptor('r3', (0.0, 300.0, 0.0), ZONES)]`, `observers=('r2',)` (r3 non rileva b1); x = 8000 | acceso: `intercepted == 3`, `interceptions_consumed() == {'r3': 3}` (r2 escluso, r3 no: Q1 resta per intercettore) |
| 14 | `test_non_interceptable_rounds_are_unaffected` | x = 15_000, `spec=_miss(rounds=5, interceptable=False)` | acceso: `intercepted == 0`, nessun `InterceptionEvent` |
| 15 | `test_bi_admitted_round_then_the_revised_l1_applies` | BI **acceso** e colpo ammesso: ogni chiamata a `self._run(...)` dentro `with patch.object(ER, 'BI_AD_TARGET_RULE', True):` (BI e' letto all'inizio della run, `:2058`, quindi il `patch` esterno basta); x = 8000; `spec=_miss(rounds=5, interceptable=True, time_of_flight=REACTION_TOF, intercept_domains=frozenset({'land'}))` (lo stub e' un intercettore terrestre, come `_ZonedInterceptor` in `TestAirDefenceTargetRule`, `:4783`); due casi con `subTest`: rilevato (`observers` di default) e non rilevato (`observers=()`) | L1 accesa: rilevato -> `intercepted == 0` (BI ammette il colpo, poi la L1 rivista lo esclude: bersaglio immediato dentro la zona); non rilevato -> `intercepted == 3`, `interceptions_consumed() == {'r2': 3}`. Fissa l'ordine BI -> L1 rivista con un colpo **ammesso** (lo scenario S35 (B) n. 3 copre solo il colpo non ammesso) |

Gli attesi dei test 2-14 sono stati **provati** fuori dal repository con un prototipo che realizza §4.2 punti 4-6 alla
lettera e lo stub `_ArmedInterceptor` (script
`/tmp/claude-1000/-home-marco-Sviluppo-Warfare-Model/db4537e6-f512-41af-b45f-1c8dabc15406/scratchpad/l1rev/verifica_test_unitari.py`):
tutti come in tabella (test 11: 5 estrazioni in entrambi gli stati; test 12: 3 estrazioni di differenza) [M]. Il test 15
e' stato aggiunto il 2026-11-25 dopo la rilettura e **non** e' stato provato col prototipo: gli attesi derivano dalla
regola (BI ammette `land` per un intercettore terrestre, poi si comporta come i test 2 e 3). Se l'esito differisce,
l'esecutore **si ferma** e riferisce.

Test facoltativi suggeriti dalla rilettura e **non inclusi** in questo piano (decisione dell'utente del 2026-11-25): due
passaggi dell'intercettore sul lanciatore con rilevamento solo nel primo e lancio nel secondo (FP-5 (d)); intercettore
di un'altra forza dello stesso dominio (difesa di dominio, `_on_resolve`, `:3872-3880`).

Per il test 12 l'esecutore passa due istanze di `_ScriptedRng([0.0] * 40)` (`rng=`) e legge `.calls`; se la differenza misurata non e' 3, **si
ferma** e riferisce (indicherebbe un'estrazione nella regola).

Classi base: nessuna nuova; `TestL1ImmediateTarget` eredita da `unittest.TestCase` come le vicine; logger mockato
con `patch(_ER_LOGGER)` (`:46`).

**Verifica parziale del blocco 2:**
```
<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Engagement_Resolver
<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Mobile
<python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json --only '^(S6|S11|S16|S19AD|S35-ADTGT)/' --quiet --summary
```
Atteso: OK (15 test nuovi in `Test_Engagement_Resolver`); confronto parziale IDENTICAL.

### 4.3 Blocco 3 — Test di scenario con l'interruttore acceso (fuori dalla fotografia) e verifiche complete

Tre classi nuove, **non** aggiunte a `UNITS` di `Test/Scenario_Baseline.py` (i metodi di test non sono eseguiti dalla
fotografia, che esegue solo `setUpClass` delle unita' elencate; v. `TestS19AdTargetRule`,
`Test_Session_Scenarios_S19_Air_Defence.py:253-275`). **Attenzione**: la fotografia esegue `setUpClass` delle classi in
`UNITS`; le classi nuove sono in file gia' presenti ma non in `UNITS`, quindi non vengono catturate. Nessun nome stabile
di unita' o variante cambia.

I numeri nei docstring sono **misure** del prototipo (§1.5), non valori tarati; le asserzioni sono qualitative
(relazioni fra stati), come negli altri scenari.

**(A) S19AD — `TestS19AdL1ImmediateTarget(F.LoggerSilencer, unittest.TestCase)`**, in
`Test/Test_Session_Scenarios_S19_Air_Defence.py` dopo `TestS19AdTargetRule` (`:253-275`), prima di
`if __name__ == '__main__':`.

```python
class TestS19AdL1ImmediateTarget(F.LoggerSilencer, unittest.TestCase):
    """L1 rivista (Proposta_Revisione_L1_Lanciatore_Bersaglio.md) sul Tor avanzato, seme `S19-4`: l'unico caso della
    fotografia in cui la regola cambia l'esito. L'A-10C `cas1` lancia AGM-65D a ~9,7 e ~9,5 km dal Tor (dentro i 12 km
    del 9M331) a ~163 e ~164 s, PRIMA che il Tor lo rilevi (~184 s): misure della sonda della Proposta. Spento (regola
    del 2026-09-28): il Tor non ferma quei colpi. Acceso: il lanciatore non e' un bersaglio immediato del Tor, che li
    intercetta. Stessa sessione della fotografia; NON in `Scenario_Baseline` (i metodi di test non sono eseguiti dalla
    fotografia)."""

    AD = 'Red-Line/ad0'
    LAUNCHER = 'Blue-CAS/cas1'
    SEED = 'S19-4'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.off = cls._run(False)
        cls.on = cls._run(True)

    @classmethod
    def _run(cls, switch):
        """`(outcome, [EngagementResult, ...])` del Tor avanzato con l'interruttore `switch`."""
        results = []
        original = ER.resolve_engagement

        def spy(*args, **kwargs):
            result = original(*args, **kwargs)

            if result is not None:
                results.append(result)

            return result

        with patch.object(ER, 'L1_IMMEDIATE_TARGET_RULE', switch), \
                patch.object(ER, 'resolve_engagement', side_effect=spy):
            _, _, outcome = run_variant(cls.SEED, '9K331-Tor', TOR_FORWARD_X, 300.0, 4, OVERFLIGHT,
                                        targets_ifv_only=True)

        return outcome, results
```

| # | Nome | Asserzioni |
|---|---|---|
| 1 | `test_premise_the_launcher_fires_before_the_tor_sees_it` | per ciascuno stato: `launches = [s.t_launch for r in results for s in r.salvos if s.shooter_id == LAUNCHER and s.spec.weapon == MAVERICK]` non vuota; `seen = [d.time for r in results for d in r.detections if d.observer_id == AD and d.target_id == LAUNCHER and d.detected]`; `assertTrue(not seen or min(seen) > min(launches))` |
| 2 | `test_switch_off_the_tor_does_not_intercept` | `_interceptions(off_outcome, AD) == 0` (la fotografia) |
| 3 | `test_switch_on_the_tor_intercepts_the_unseen_launcher` | `_interceptions(on_outcome, AD) > 0`; per ogni `InterceptionEvent` del Tor nei risultati acceso almeno una delle sue `salvo_ids` e' una salva di `LAUNCHER` (mappa `salvo_id -> shooter_id` dalle `r.salvos`) |
| 4 | `test_switch_on_the_tor_still_fires_at_the_launchers` | `_rounds_fired(on_outcome, AD) > 0` (la priorita' L2/L3 non cambia) |

**(B) S35 — `TestS35L1Revised(F.LoggerSilencer, unittest.TestCase)`**, in coda a `Test/Test_Session_Scenarios_S35.py`
(prima di `if __name__ == '__main__':`).

```python
class TestS35L1Revised(F.LoggerSilencer, unittest.TestCase):
    """L1 rivista sulle varianti `naval_maverick`: la zona della Rezky e' quella dell'AK-630 (4 km, unica arma
    'Anti_Missile'), non quella della SA-N-4 (12 km). I Maverick partono a 7,1-14,7 km dalla nave (misura della
    Proposta): tutti fuori dalla zona, quindi intercettabili anche quando la nave vede l'A-10C e lo ha a portata. Con BI
    acceso (`naval_maverick_on`) la nave non ferma i Maverick per la classe (filtro prima di L1): l'interruttore L1 non
    cambia nulla. NON in `Scenario_Baseline`."""

    SEEDS = SEEDS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {}

        for variant in ('naval_maverick_off', 'naval_maverick_on'):
            for switch in (False, True):
                with patch.object(ER, 'L1_IMMEDIATE_TARGET_RULE', switch):
                    cls.runs[(variant, switch)] = [run_variant(seed, variant)[2] for seed in cls.SEEDS]
```

| # | Nome | Asserzioni |
|---|---|---|
| 1 | `test_switch_on_the_ship_intercepts_more_mavericks` | per seme (`subTest`), variante `naval_maverick_off`: `_interceptions(acceso, SHIP) > _interceptions(spento, SHIP)` (misura: 6 > 2, 6 > 2, 4 > 0, 4 > 2) |
| 2 | `test_switch_on_the_ship_is_destroyed_less_often` | `naval_maverick_off`: numero di semi con `F.force_outcome(o, 'Red-Navy').outcome == 'destroyed'` acceso `<` spento (misura: 0 < 4) |
| 3 | `test_bi_on_makes_the_l1_switch_irrelevant` | per seme, `naval_maverick_on`: `_events(acceso) == _events(spento)` e `_interceptions(acceso, SHIP) == 0` |

**(C) S16 — `TestS16L1Revised(F.LoggerSilencer, unittest.TestCase)`**, in
`Test/Test_Session_Scenarios_S10_S18.py` subito dopo `TestS16NavalInstallation` (che finisce a `:1279`), prima del
commento `# ── S17`.

```python
class TestS16L1Revised(F.LoggerSilencer, unittest.TestCase):
    """L1 rivista sul porto di S16, seme `S16-3` (l'unico seme che cambia): con la regola del 2026-09-28 le Molniya
    (V_I 12 km della SA-N-4) non fermano 6 salve 'test:anti_ship' lanciate a 2,3-10,7 km da F/A-18C che non hanno
    rilevato; con la regola rivista la zona e' quella dell'AK-630 (4 km, fino a 3000 m) e gli F/A-18C, a 6000 m, ne sono
    fuori. Misure della Proposta: intercettazioni 34 -> 44, Molniya perse 2 -> 0. NON in `Scenario_Baseline`."""

    SEED = 'S16-3'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.off = cls._run(False)
        cls.on = cls._run(True)

    @classmethod
    def _run(cls, switch):
        """`(porto, outcome)` della sessione di `TestS16NavalInstallation` con l'interruttore `switch`."""
        base = TestS16NavalInstallation
        strike, port, missions = base._build()
        blue_ids = frozenset(strike.assets)
        low_level = (lambda observer, target, ids=blue_ids: base.LOW_LEVEL_FACTOR if target.id in ids else 1.0)

        with patch.object(ER, 'L1_IMMEDIATE_TARGET_RULE', switch):
            outcome = F.run(cls.SEED, [strike], [port], F.make_fire_control(), duration=3_600.0, missions=missions,
                            thresholds=BOTH_HOLD, detection_factor=low_level,
                            order_kwargs={'salvo_window': base.SALVO_WINDOW})

        return port, outcome
```

| # | Nome | Asserzioni |
|---|---|---|
| 1 | `test_switch_on_the_corvettes_intercept_more` | `sum(e.interceptions for e in F.interceptions_by(on_outcome, TestS16NavalInstallation.SHIPS))` `>` lo stesso a spento |
| 2 | `test_switch_on_fewer_corvettes_are_lost` | numero di `SHIPS` con `port.assets[s].is_destroyed()` acceso `<` spento |

Le chiamate di (C) sono le stesse di `TestS16NavalInstallation.setUpClass` (`:1146-1170`) senza lo spy, che non cambia
l'esito. Se l'esito spento di (A) o (C) non coincide con la fotografia (Tor senza intercettazioni in `S19-4`; 34
intercettazioni delle Molniya in `S16-3`), l'esecutore **si ferma** e riferisce.

**Verifica parziale del blocco 3:**
```
<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S19_Air_Defence
<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S35
<python> -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S10_S18
```
Atteso: OK, con 4 + 3 + 2 test nuovi.

Docstring da aggiornare **gia' nel blocco 3** (interruttore spento, testo): `Test_Session_Scenarios_S19_Air_Defence.py:10-11`
aggiungere "(regola del 2026-09-28; con L1_IMMEDIATE_TARGET_RULE acceso l'esclusione vale solo se il lanciatore e' un
bersaglio immediato del Tor: v. TestS19AdL1ImmediateTarget)"; `Test_Session_Scenarios_S35.py:22-24` aggiungere "Con
L1_IMMEDIATE_TARGET_RULE acceso la zona della Rezky e' quella dell'AK-630 (4 km): v. TestS35L1Revised."

**Verifiche complete (fine blocco 3):**
```
bash tools/ai/verifica.sh suite start      # poi: bash tools/ai/verifica.sh suite wait  (ripetere fino a ESITO)
bash tools/ai/verifica.sh confronto start  # SOLO dopo l'ESITO della suite; poi: confronto wait
```
Atteso: suite `OK` con `Ran` = base + 32 = base + 8 (blocco 1) + 15 (blocco 2) + 9 (blocco 3) — la base si legge
dall'ESITO di una suite sul commit di partenza (al 2026-11-20 era `Ran 4973`), non da qui; confronto **1219 IDENTICHE,
0 CHANGED, 0 NEW, 0 MISSING** (interruttore spento).

**Rapporto** dell'esecutore: `Analysis/Document/Rapporti/Rapporto_Revisione_L1_<agente>.md` secondo
`Rapporti/TEMPLATE.md`, con i numeri letti dagli ESITI.

### 4.4 Blocco 4 — Sonda con l'interruttore vero acceso (sessione principale, sola lettura)

Dopo il merge dei blocchi 1-3, la sessione principale:
1. salva lo script dell'Appendice A in `Analysis/Document/Rapporti/Sonde_L1_Revisione/probe_l1.py` ed esegue
   `PYTHONPATH=. <python> Analysis/Document/Rapporti/Sonde_L1_Revisione/probe_l1.py on .ai-run/l1_on.json`
   (cattura completa, ~18-25 min sulla VM osboxes, ~10 sul ProArt; **mai** in parallelo con suite o confronto), poi
   `<python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json --against .ai-run/l1_on.json --summary`;
2. controlla che l'elenco delle esecuzioni cambiate coincida con §4.8 (stato "acceso"): ogni scarto e' un'anomalia da
   spiegare prima di proporre l'accensione;
3. esegue la suite con l'interruttore acceso in memoria (Appendice B) e annota i test che falliscono; atteso: quelli
   elencati in §4.5 punto 3, nessun altro;
4. scrive `Analysis/Document/Rapporti/L1_Esecuzioni_Cambiate.md`: per ogni esecuzione cambiata, prima/dopo di
   intercettazioni, colpi al danno, perdite ed esito di forza; la tabella delle coppie escluse (oggi e con la regola
   nuova, dal file `.rows.json` della sonda).

### 4.5 Blocco 5 — Accensione (SOLO dopo la decisione esplicita dell'utente, letto il rapporto del blocco 4)

1. `L1_IMMEDIATE_TARGET_RULE = True`; commento: "ACCESO dalla decisione dell'utente del <data>; prima spento" (forma di
   `D5_DWELL_TIME`, `:610-619`).
2. `TestL1ImmediateTarget.test_switch_is_off_by_default` -> `test_switch_is_on_by_default`, `assertIs(..., True)`. Gli
   altri test del blocco 2 impostano lo stato esplicitamente e non cambiano.
3. Test che falliscono acceso (misura L-3 di §1.5 con il prototipo; da riconfermare al blocco 4, Appendice B): dopo i
   blocchi 2-3 resta **solo** `TestS19AirDefenceAllocation.test_forward_tor_engages_launchers_inside_its_zone`
   (`Test_Session_Scenarios_S19_Air_Defence.py:200-212`), seme `S19-4` (gli altri cinque sono fissati spenti nel
   blocco 2, (a) e (a2)). Si riscrive cosi':
   - in `setUpClass` (`:131-146`) il ciclo di `cls.tor_forward` registra anche i risultati del risolutore, con uno spy
     identico a quello di `TestS19AdL1ImmediateTarget._run` (stesso schema di S16, `Test_Session_Scenarios_S10_S18.py:1159-1168`:
     l'esito non cambia, la fotografia nemmeno): `cls.tor_forward_results = [...]`, una lista di `EngagementResult`
     per seme, nello stesso ordine di `cls.tor_forward`;
   - il test diventa `test_forward_tor_engages_launchers_and_intercepts_only_unseen_ones`, docstring "Regola L
     (rivista il 2026-11-24): lanci da DENTRO i 12 km del Tor; il Tor spara ai lanciatori in ogni seme e intercetta
     solo colpi di lanciatori che non aveva rilevato al lancio (bersaglio immediato = rilevato e a portata)";
     asserzioni: la premessa `inside > 0` invariata; per seme `_rounds_fired(outcome, AD) > 0`; per seme, per ogni
     `InterceptionEvent` del Tor nei risultati, almeno una salva fra le sue `salvo_ids` ha un lanciatore **senza**
     `Detection` del Tor (`observer_id == AD`, `detected`, `time <= salvo.t_launch + 1e-9`). Con l'interruttore spento
     l'asserzione e' vera a vuoto (nessuna intercettazione), con l'interruttore acceso e' la regola. L'asserzione e'
     piu' stretta della regola (che guarda solo il rilevamento nel passaggio che contiene il lancio, FP-5 (d)): se
     fallisse per un rilevamento di un passaggio **precedente** (`Detection.pass_end` < `t_launch`), l'esecutore si
     ferma e riferisce invece di allargarla da solo. Oggi in `S19-4` il Tor rileva `cas1` una sola volta, a ~184 s.
   Se l'Appendice B elenca altri test, l'esecutore **si ferma** e la sessione principale aggiorna questo punto.
4. Docstring da aggiornare all'accensione: `Test_Session_Scenarios_S19_Air_Defence.py:10-23` (la regola L1 descritta
   e' quella nuova; la frase "il caso che solo L1 distingue..." resta vera per la regola di oggi, va riformulata);
   `Test_Session_Scenarios_S35.py:22-24` (la Rezky intercetta con l'AK-630, zona 4 km; il Burke resterebbe escluso
   solo per i lanciatori che vede e puo' colpire); `Test_Session_Scenarios_S10_S18.py` docstring di S16 se cita L1
   (oggi non la cita [V: `:1065-1120`]).
5. Verifiche: suite e confronto completi; atteso §4.8 stato "acceso". La fotografia nuova la installa **solo l'utente**.

### 4.6 Blocco 6 — Pulizia (SOLO dopo la fotografia nuova e Q-L1-1 = A)

Si elimina la regola di oggi: `L1_IMMEDIATE_TARGET_RULE` e `self.l1_immediate_target`; `_may_intercept_volume`,
`_interception_zone`, `zone_cache`; `_may_intercept` chiama direttamente la regola rivista (il corpo di
`_may_intercept_revised` entra in `_may_intercept` con la cache); `TestLauncherInsideInterceptionZone` si elimina
(i suoi casi hanno gia' un corrispondente in `TestL1ImmediateTarget`: zona per intercettore n. 13, bordo e sopra il
tetto n. 9, dato mancante n. 10, colpi non intercettabili n. 14, fuori zona n. 11);
i test che fissavano lo stato (`patch.object(..., False/True)`) perdono il `patch`; i test di §4.5 punto 3 restano.
Atteso: suite OK, confronto con la fotografia nuova **IDENTICO**. Piano di dettaglio da riscrivere al momento (riga
per riga sul codice di allora), come per la pulizia FP. **Il blocco 6 resta "da ripianificare"**: questa sezione ne
fissa solo il contenuto, non e' un contratto eseguibile oggi; prima di eseguirlo serve una Proposta nuova (o
un'integrazione di questa) scritta sul codice di allora.

### 4.6bis Vincoli per l'esecutore (tutti i blocchi)

- **RNG**: nessuna estrazione nuova, nessuno spostamento; non toccare `_draw`, `_detect_direction`, `_detect_passes`,
  `_on_resolve` fuori dai commenti indicati.
- **Interruttore**: nome `L1_IMMEDIATE_TARGET_RULE`, default `False` nei blocchi 1-4; letto una volta per run in
  `__init__` (mai altrove).
- **Costanti**: nessuna nuova. Raggi e quote delle zone sono **dati di registro** letti da `Mobile.interceptor_envelopes`;
  nei test i valori dei registri si leggono dai registri, non si scrivono a mano (tranne i dati finti di `Test_Mobile`).
- **Nomi stabili** in `Test/Scenario_Baseline.py`: nessuna unita', variante o chiave nuova; `UNITS`, `DETECTION_UNITS`,
  `DETECTION_FIELDS` invariati.
- **Core indifferente al simulatore**: nessun import dall'adapter DCS; nessuna dipendenza nuova.
- **Import** con il percorso completo; logger mockato come negli altri `Test_*.py`.
- **Fotografia**: mai installata dall'esecutore. Mai lavorare in un git worktree.
- Se una riga citata qui non corrisponde al codice (funzione spostata, firma diversa) o un esito parziale non e' quello
  atteso, **fermarsi e riferire**.

### 4.7 Test di scenario: dipendenze da L1 (revisione richiesta)

**4.7.1 S19AD** (`Test_Session_Scenarios_S19_Air_Defence.py`). La zona del Tor non cambia (9M331 = unica arma
antiaerea, 12 km). `tor_rear`: lanci a 17,69-17,70 km, fuori in entrambe le regole: invariato (anche
`TestS19AdTargetRule` e la variante `land_tactical` di S35, che lo riusano). Strela-10: non e' un intercettore
(regola D), L1 non si applica. `tor_forward`: tutti i lanci sono dentro i 12 km; oggi i colpi non si intercettano mai,
con la regola rivista solo se l'A-10C che lancia e' gia' rilevato dal Tor e a portata. In 5 semi su 6 l'esito non
cambia: nella sonda nessuna coppia (Tor avanzato, salva) di quei semi arriva a L1 (delle 20 coppie S19AD valutate, 18
sono del Tor arretrato a 17,7 km e 2 di `S19-4`); la condizione che le ferma prima e' `free <= 0` (`:3927-3929`), cioe'
il Tor senza capacita' libera all'istante della salva [I: causa non indagata seme per seme, coerente con la "scoperta
per tempistica" del docstring: il Tor spende gli 8 missili sui lanciatori]. Nel seme `S19-4` l'A-10C `cas1` lancia a ~163 s, il Tor lo rileva a ~184 s: con la regola rivista
intercetta 2 colpi (§1.5, L-2). Il test che oggi lo esclude e' riscritto all'accensione (§4.5 punto 3); il docstring
del modulo (`:10-23`) descrive la regola del 2026-09-28 e la "scoperta per tempistica" — resta vera per 5 semi su 6.

**4.7.2 S16** (`Test_Session_Scenarios_S10_S18.py`, `TestS16NavalInstallation`). La zona delle Molniya passa da 12 km
(SA-N-4) a 4 km fino a 3000 m (AK-630); gli F/A-18C volano a 6000 m: nessun lancio e' dentro la zona. Nel seme `S16-3`
le Molniya intercettano 10 colpi in piu' e sopravvivono (Red-Port `destroyed` -> `held`). Nessun test di
`TestS16NavalInstallation` fallisce (misura L-3: le asserzioni sono aggregate e qualitative). Il docstring non cita L1.

**4.7.3 S35** (`Test_Session_Scenarios_S35.py`). Dipendenze dopo la revisione:
- **da L1**: solo le varianti `naval_maverick_off` (4 esecuzioni). La Rezky passa da 12 km (SA-N-4) a 4 km (AK-630);
  i Maverick partono a 7,1-14,7 km: nessuno dentro, nessuno vicino al bordo (il piu' vicino a 1,78 volte il raggio).
  La sensibilita' segnalata nel manuale (§9.1: primo lancio del seme 2 "a circa 12,2 km, circa 200 m fuori dal V_I")
  **sparisce** con la regola rivista; nelle coppie valutate oggi quel lancio non compare (i lanci fuori dal V_I piu'
  vicini sono a 14,70 km). Esito: piu' intercettazioni e la nave sopravvive in tutti e 4 i semi (§1.5, L-2); le
  asserzioni 1-12 restano vere (misura L-3: nessun test di S35 fallisce). L'asserzione 10 ("spento: la nave ferma
  AGM-65D, totale sui semi") ne esce rafforzata (da 6 a 20 intercettazioni).
- **da BI** (`BI_AD_TARGET_RULE`): le varianti `_on` filtrano per classe **prima** di L1 (`:3929`): con BI acceso la
  Rezky non considera i Maverick bersagli, L1 non e' valutata, e l'interruttore L1 non cambia nulla (asserzione 3 di
  `TestS35L1Revised`). `naval` (AGM-84A da ~50 km) e `land_cruise` (Kh-59 da ~90 km) sono fuori da ogni zona in
  entrambe le regole; `land_tactical` e' il `tor_rear` di S19AD.
- La scelta della Rezky al posto dell'Arleigh Burke (decisione P-1 della BI: "con il V_I di 240 km del Burke L1 vieta
  ogni intercettazione dei lanci da aereo") **resta valida** con la regola rivista, ma per una ragione piu' stretta: il
  Burke (zona dell'SM-2 = 240 km) escluderebbe i colpi dei lanciatori che vede e che ha a portata, cioe' quasi tutti
  gli aerei che lo attaccano; i colpi di un lanciatore non visto diventano intercettabili. Il docstring di S35 va
  aggiornato all'accensione (§4.5 punto 4).

**4.7.4 Altre unita' con intercettori** (S2 Buk, S6 S-300PS e Molniya, S11 Tor e Gepard): oggi nessuna esclusione e
nessuna con la regola rivista (lanci da 1,6 a 31 volte il raggio, §1.5): invariate.

### 4.8 Esito atteso del confronto con la fotografia (installata: 1219 esecuzioni)

| Stato | Esito atteso |
|---|---|
| Dopo i blocchi 1, 2, 3 (interruttore spento) | **1219 IDENTICHE**, 0 CHANGED, 0 NEW, 0 MISSING: il percorso eseguito e' quello di oggi (§4.2, "Ordine delle estrazioni") |
| Sonda del blocco 4 e dopo il blocco 5 (acceso) | **6 CHANGED** (`S16/S16-3`, `S19AD/S19-4/tor_forward_ifv_only`, `S35-ADTGT/S35-ADTGT-0/naval_maverick_off`, `-1`, `-2`, `-3`), **1213 IDENTICHE**, 0 NEW, 0 MISSING |

Perche' le 6 cambiano e come: tabella di §1.5, L-2 (piu' intercettazioni in tutte; la forza difesa passa da
`destroyed` a `held` in `S16-3` e nelle 4 di S35; in `S19-4` il Tor intercetta 2 colpi e perde un BMP-2 in meno).
Perche' le altre 1213 restano identiche: la regola rivista non esclude nessuna coppia (§1.5, L-2), e la regola di oggi
escludeva coppie solo in S16, S19AD e S35; nelle altre esecuzioni di quelle unita' le esclusioni di oggi non cambiavano
l'esito (stesse 6 esecuzioni della sonda con L1 spenta). Le 6 esecuzioni attese sono **identiche** a quelle con L1
spenta del tutto: se il blocco 4 trova una differenza fra le due, e' un'anomalia (la regola rivista avrebbe escluso
qualcosa che il prototipo non escludeva).

Nessuna esecuzione nuova (le classi del blocco 3 non sono in `UNITS`), nessuna mancante.

### 4.9 Documenti da aggiornare

Dopo il blocco 3 (interruttore spento) e di nuovo dopo il blocco 5:
- `F4_Differenze_Scenari.md`: sezione nuova "L1 rivista (2026-11-24)" in coda: interruttore spento = nessuna
  differenza; acceso = rimando a `Rapporti/L1_Esecuzioni_Cambiate.md` e all'elenco di §4.8.
- `Piano_Implementazione_Missione.md`, tabella di stato (§5): riga "L1 rivista" (fuori dalla numerazione F, come BI).
- `Stato_Progetto_DES.md`: riga n. 3 della tabella delle decisioni aperte (solo la sessione principale).
- **Manuale** (blocco separato per `des-manual-writer`, dopo il blocco 3 e aggiornato dopo il blocco 5):
  - `05_Strato2_Risolutore_Ingaggio.md` §4.24, sottosezione "Regola L1" (`:1781-1797`): le due regole, l'interruttore,
    la zona per arma (`Mobile.interceptor_envelopes`), il bersaglio immediato (`_immediate_target`), SD-1..SD-6; le
    citazioni di riga di oggi sono vecchie (`:3019-3042` contro `:3719-3742` reali) e vanno riallineate; §4.24 testo
    introduttivo (`:1745-1746`, "salvo L1 e R-INT"); §4.26 R-INT: il rilevamento del lanciatore all'istante del lancio
    e' ora letto anche da L1 (stessa funzione, `_detection_time_of`); tabella iniziale (`:59`) e §4.5 (`:305`, `:314`);
  - `10_Limiti_Estensioni_Divergenze.md` §9.1: "Limiti introdotti dalle estensioni del 2026-09-28/30" (`:299`), "Bersagli
    intercettabili" (`:316`, `:364-367`: "S35 dipende da L1 ... se L1 cambia", da riscrivere con §4.7), i limiti nuovi di
    §5 (R-1..R-5); §9.3 punti di estensione (C2: bersaglio immediato per dominio invece che per asset; UF-1 e UF-2 di
    §5.1); tabella di stato
    (`:860`, `:890`); §9.6 solo se il manual-writer trova divergenze nuove;
  - `08_Supporto_Trasversale.md:287` (riferimento a L1).
- Commenti nel codice: quelli di §4.2 punto 7 (gia' nel blocco 2).

---

## 5. Rischi e limiti

- **R-1 — Scorta e regole di bersaglio allo stato della risoluzione.** La condizione (2) guarda la scorta dell'arma con
  cui l'intercettore colpirebbe il lanciatore quando la salva si risolve (dopo `salvo_window` e il tempo di volo), non
  al lancio. Un intercettore che nel frattempo ha finito i missili sul lanciatore intercetta i colpi rimasti. Allo
  stesso stato della risoluzione sono letti anche gli altri dati che la fire control consulta tramite le regole di
  bersaglio di missione: i bersagli designati distrutti (`_designated_destroyed`, `:3119-3130`, tramite `_attack_over`
  in `_fire_control`, `:3240-3243`) e gli ostili noti del dominio (`hostile_by_domain`, letti da `_is_hostile`,
  `:3086-3090`), che possono essere cambiati fra il lancio e la risoluzione. Deterministico, nessuna estrazione.
  Coerente con canali e scorta di intercettazione, gia' letti alla risoluzione (`:3906-3911`).
- **R-2 — Rilevamento per asset, non per dominio.** Come R-INT: il lanciatore visto da un'altra unita' dello stesso
  dominio non rende la salva "esclusa" per un intercettore che non lo vede (nessun quadro condiviso fino alla Fase 0
  C2). E' la decisione c = 2 (per asset).
- **R-3 — La regola rivista non e' esercitata dalla fotografia.** Sulle 1219 esecuzioni non esclude nessuna coppia
  (§1.5, L-2): accesa, la fotografia coincide con "nessuna L1". La differenza fra C-pieno e C-ripiego e' nulla; i rami
  "rilevato, a portata e dentro la zona" (esclusione) e "rilevato ma fuori portata / senza scorta / ROE" (nessuna
  esclusione) sono coperti **solo** dai test unitari del blocco 2. Uno scenario che eserciti l'esclusione (es. un Tor
  che vede l'A-10C prima del lancio dei Maverick da dentro i 12 km, con missili ancora disponibili) non esiste oggi:
  la "scoperta per tempistica" di S19AD (§7.8 della Proposta SAM) fa si' che il Tor spenda i missili prima. Crearlo e'
  fuori da questa Proposta (proponibile come S37 se l'utente lo chiede).
- **R-4 — Il caso Burke non e' esercitato** da nessuna esecuzione (oggi come dopo): un'esclusione a 240 km resta
  possibile per un lanciatore rilevato e alla portata dell'SM-2. Conseguenza accettata dall'utente (d = 2).
- **R-5 — Fascia dei CIWS.** Le quote massime dei CIWS (1500/3000 m) sono stime di registro ("STIMA B") e decidono se un
  aereo sopra la nave e' "dentro" (S16: F/A-18C a 6000 m sopra la Molniya entro 4 km = fuori dalla zona). Nessuna
  stima nuova introdotta qui.
- **PD-1 (dottrina, aperto, NON deciso qui) — Missile fire-and-forget gia' in volo.** Uccidere il lanciatore non ferma
  un missile fire-and-forget gia' partito (Maverick, Harpoon). La priorita' al lanciatore ha senso per la **salva
  successiva**, non per quella in volo: oggi (e con la revisione) un intercettore che ha il lanciatore come bersaglio
  immediato lascia passare la salva in volo anche se ha canali e scorta liberi. Una lettura alternativa (intercettare
  comunque con la capacita' che avanza dopo aver servito il lanciatore) era l'opzione scartata di Q2 del 2026-09-28
  (`Proposta_Regole_Allocazione_SAM.md` §7.6). Da riportare all'utente come punto aperto, con esempi, in una Proposta
  separata se lo chiede.
- **PD-2 (dottrina, aperto) — Lanciatore abbattuto prima della risoluzione.** Con SD-6 lo stato del lanciatore dopo il
  lancio non conta: se il Tor abbatte l'A-10C prima che i Maverick arrivino, i Maverick restano esclusi per il Tor.
  Lega con PD-1 e con l'upgrade UF-2 (§5.1).
- **R-6 — Copie di righe nel manuale** gia' disallineate (`:3019-3042` contro `:3719-3742`): il blocco del manuale le
  riallinea; il piano usa le righe del commit `0c7263cd`.

### 5.1 Upgrade futuri (annotati il 2026-11-25, NON parte del piano)

Due varianti emerse dalla rilettura (`Rapporti/Revisione_L1_des-reviewer.md`). Nessuna implementazione ora: l'esecutore
dei blocchi 1-5 **non** le realizza. Da riconsiderare insieme a PD-1 e PD-2.

**UF-1 — ROE a tempo nella condizione (2) (variante B della rilettura, problema n. 1).** Aggiungere `_is_deferred`
(`:3141-3154`, regole di bersaglio che dipendono dal tempo: `return_fire`, `priority_designated`) alla condizione (2):
un lanciatore che la ROE vieta al difensore di colpire in quel momento **non** e' un bersaglio immediato, e i suoi colpi
restano intercettabili.
- Pro: piu' fedele a L2, che scarta i candidati rimandati prima del pool prioritario (`:2892`).
- Contro: un ramo e almeno un test unitario in piu' (stub con `target_rules` e ROE a tempo); oggi nessuna esecuzione
  della fotografia lo esercita, quindi l'effetto non e' misurabile.
- Aggancio: solo in `_immediate_target`, dopo il calcolo di `t_fire` e prima di `_in_range_at`, con una riga della forma
  `if self.target_rules and self._is_deferred(shadow, self.shadows[salvo.shooter_id], t_fire): continue`; nient'altro
  cambia (stessa forma di `_schedule_next`, `:2892`). Nessuna estrazione. Se adottata dopo l'accensione, va dietro un
  interruttore proprio spento (regola di progetto).

**UF-2 — Tipo di guida del missile e dipendenza dal lanciatore (nota SD-6 della rilettura, §4).** Oggi tutti i colpi
sono trattati come autonomi dopo il lancio (payload congelato al lancio, danno all'impatto senza guardare il
lanciatore). Per le armi la cui guida dipende ancora dal lanciatore, mettere fuori uso il lanciatore potrebbe far
perdere la guida al colpo.
- Dati gia' presenti [V 2026-11-25]: campo `'guidance'` sulle voci missilistiche di `Asset/Ship_Weapon_Data.py` (25
  occorrenze, es. `'Active_Radar'`, `'Semi_Active_Radar'`, `:1053`, `:1069`); campo `"seeker"` in
  `Asset/Aircraft_Weapon_Data.py` (es. `"radar"`, letto a `:524-526`), che descrive il sensore terminale ma non dice in
  modo esplicito se il colpo dipende dal lanciatore; **nulla** in `Asset/Ground_Weapon_Data.py`. Nessun registro ha un
  campo diretto "dipende dal lanciatore": andrebbe derivato con una tabella di corrispondenza dichiarata come scelta
  di progetto [S] o aggiunto come campo nuovo, con fonte o stima dichiarata.
- Aggancio: un campo opzionale in coda alla `ShotSpec` (default None = "ignoto = autonomo", il comportamento di oggi),
  riempito da chi conosce l'arma (`Logic/Fire_Control.shot_spec_for`, `:824`), come `intercept_domains` della BI; la
  regola nel risolutore dietro un interruttore nuovo **spento** di default.
- Ordine consigliato: dottrina (PD-1/PD-2, Proposta separata con esempi) -> dati di guida nei registri -> regola nel
  motore.
- Legame con PD-1/PD-2: per un colpo dipendente dal lanciatore, abbattere il lanciatore ferma anche la salva in volo
  (PD-2 si risolve da solo e l'esclusione L1 e' coerente); per un colpo autonomo protegge solo dalla salva successiva
  (PD-1: intercettare comunque con la capacita' che avanza torna un'alternativa ragionevole). Un upgrade potrebbe
  rendere l'esclusione L1 condizionata anche alla guida. Dettaglio nella rilettura, §4.

---

## Appendice A — Script della sonda del blocco 4 (da salvare in `Analysis/Document/Rapporti/Sonde_L1_Revisione/probe_l1.py`)

Usa i metodi del blocco 2 (`_may_intercept_volume`, `_may_intercept_revised`): si esegue **dopo** il merge dei blocchi
1-3. Controllo minimo prima dell'uso: con `off` il confronto con la fotografia deve dare `IDENTICAL` (la spia chiama
anche la regola non in vigore, senza effetti: verificato con il prototipo, §1.5).

```python
"""Sonda L1 rivista (sola lettura, Proposta_Revisione_L1_Lanciatore_Bersaglio.md, blocco 4).

Imposta IN MEMORIA Engagement_Resolver.L1_IMMEDIATE_TARGET_RULE, esegue la cattura completa unita' per unita' e registra
le coppie (intercettore, salva) in cui la regola del 2026-09-28 o quella rivista escludono l'intercettazione.
Nessun file del repository modificato.

Uso (dalla root del repo):  PYTHONPATH=. <python> probe_l1.py on|off <out.json>
Poi:  <python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare <fotografia> --against <out.json> --summary
"""
import collections
import json
import re
import sys
import time

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB

MODE, OUT = sys.argv[1], sys.argv[2]

if MODE not in ('on', 'off'):
    raise SystemExit('modo: on | off')

ER.L1_IMMEDIATE_TARGET_RULE = MODE == 'on'
CUR = {'label': None}
ROWS = []
COUNTS = collections.Counter()
ORIGINAL = ER._EngagementRun._may_intercept


def spy(self, shadow, salvo):
    first = (shadow.id, salvo.salvo_id) not in self.may_intercept_cache
    verdict = ORIGINAL(self, shadow, salvo)

    if first:
        old = self._may_intercept_volume(shadow, salvo)
        new = self._may_intercept_revised(shadow, salvo)
        COUNTS[(CUR['label'], 'pairs')] += 1

        if not (old and new):
            launch = self._position_at(self.shadows[salvo.shooter_id], salvo.t_launch)
            here = self._position_at(shadow, salvo.t_launch)
            ROWS.append({'unit': CUR['label'], 'interceptor': shadow.id,
                         'interceptor_model': getattr(shadow.asset, '_model', None), 'shooter': salvo.shooter_id,
                         'weapon': salvo.spec.weapon, 'rounds': salvo.rounds, 't_launch': round(salvo.t_launch, 3),
                         'tof': round(salvo.t_impact - salvo.t_launch, 3),
                         'horizontal_m': None if launch is None or here is None else
                         round(((launch[0] - here[0]) ** 2 + (launch[1] - here[1]) ** 2) ** 0.5, 1),
                         'height_m': None if launch is None or here is None else round(launch[2] - here[2], 1),
                         'zones': self._interceptor_envelopes(shadow), 'vi': self._interception_zone(shadow),
                         'immediate_target': self._immediate_target(shadow, salvo),
                         'old_allows': old, 'new_allows': new, 'r_int_ok': self._in_time(shadow, salvo)})

    return verdict


ER._EngagementRun._may_intercept = spy
labels = []

for entry in SB.UNITS:
    if entry[0] not in labels:
        labels.append(entry[0])

runs, errors = {}, {}
started = time.perf_counter()

for label in labels:
    CUR['label'] = label
    snapshot = SB.capture(only='^' + re.escape(label) + '$', verbose=False)
    runs.update(snapshot['runs'])
    errors.update(snapshot['errors'])
    print(f'[{label}] {len(snapshot["runs"])} runs, {time.perf_counter() - started:.0f} s', file=sys.stderr, flush=True)

SB.dump({'meta': {'format': SB.FORMAT_VERSION, 'round_digits': SB.ROUND_DIGITS, 'filter': f'L1 {MODE}'},
         'errors': errors, 'runs': runs}, OUT)

with open(OUT + '.rows.json', 'w') as handle:
    json.dump({'rows': ROWS, 'counts': {f'{k[0]}|{k[1]}': v for k, v in COUNTS.items()}}, handle, default=str)

excluded_old = sum(1 for r in ROWS if not r['old_allows'])
excluded_new = sum(1 for r in ROWS if not r['new_allows'])
print(f'FINE {MODE}: {len(runs)} esecuzioni, {len(errors)} errori, {sum(COUNTS.values())} coppie valutate, '
      f'escluse: regola 2026-09-28 {excluded_old}, regola rivista {excluded_new}', flush=True)
```

Atteso (misura del prototipo, §1.5): con `on` 414 coppie valutate, escluse: regola 2026-09-28 **14** (sulla
traiettoria della regola rivista: S16 6, S19AD 1, S35 7), regola rivista **0**; confronto con la fotografia 6 CHANGED
(quelle di §4.8). Con `off`: 412 coppie (S2 46, S6 113, S11 30, S16 152, S19AD 20, S35-ADTGT 51), escluse 13 e 0, confronto IDENTICAL. I conteggi di coppie possono differire
di poco dal prototipo solo se l'esecutore ha cambiato l'ordine delle condizioni (non previsto): in quel caso fermarsi.

## Appendice B — Suite con l'interruttore acceso in memoria (blocco 4, punto 3)

Da salvare accanto alla sonda (`Analysis/Document/Rapporti/Sonde_L1_Revisione/suite_l1_on.py`); ~10 min sul ProArt,
~21 sulla VM osboxes; mai in parallelo con la cattura, la suite o il confronto.

```python
"""Suite completa con L1_IMMEDIATE_TARGET_RULE acceso IN MEMORIA (sola lettura); elenca i test falliti.

Uso (dalla root del repo):  PYTHONPATH=. <python> suite_l1_on.py
"""
import unittest

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER

ER.L1_IMMEDIATE_TARGET_RULE = True
suite = unittest.defaultTestLoader.discover('Code/Dynamic_War_Manager/Source/Test', pattern='Test_*.py')
result = unittest.TextTestRunner(verbosity=1).run(suite)
print('FALLITI:')

for test, _ in result.failures + result.errors:
    print(' ', test.id())
```

Atteso: falliscono `TestL1ImmediateTarget.test_switch_is_off_by_default` (per costruzione) e i test di §4.5 punto 3;
nessun altro. I test che impostano l'interruttore con `patch.object` non sono toccati dall'assegnazione globale (il
`patch` vince per la sua durata).
