# Proposta: allineamento dei volumi d'ingaggio fra DES (sfera) e pianificatore (cilindro) — VA

**Stato: DEFINITIVA, tutte le decisioni prese (2026-11-07).** **VA-1..VA-8, VA-2.1 e VA-8r DECISE** dall'utente il 2026-11-07 (§3):
VA-1 sfera ∩ fascia, **VA-2 = (d)** (fire control con la quota dell'istante di tiro, NON la (a) raccomandata),
**VA-3 = (b)** (tetto assoluto `max_target_z` anche per le armi d'aereo, NON la (a) raccomandata), VA-4 (a), VA-5
separare, VA-6 (a) (gia' scritta nel blocco 1 della Proposta FP), VA-7, VA-8 rivista in **VA-8r = raccomandata** (S34-BAND
a 8 varianti x 4 semi = 32 esecuzioni nuove, con `late_descend`), **VA-2.1 = (i) raccomandata** (rinvio della decisione di
tiro quando il bersaglio e' fuori fascia all'istante ma vi entrera' dopo). Il piano (§4) e' riscritto per le scelte;
nessuna decisione VA resta aperta. Sonde di sola
lettura **V-0, V-1 e V-2 eseguite** il 2026-11-07 sul ProArt (§1.7). Nessun file di codice o di test modificato;
scritti solo questo documento, lo script della sonda in
`Analysis/Document/Rapporti/Sonde_Allineamento_Volumi/probe_altitude.py` e il blocco 1 della Proposta FP (VA-6 (a)).
- **Ordine di esecuzione**: **BI -> VA** (`Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` prima), poi i blocchi
  della FP (§2.8, BI §6.1). Stato al 2026-11-08: BI blocchi 0-2 eseguiti e mergiati, restano BI blocchi 3-4 -> VA
  blocchi 1-2 -> FP blocchi 1-2; FP-5 e' decisa ((d), 2026-11-08), non c'e' piu' una ripresa di FP-5.
- **Richiesta dell'utente (2026-11-07, vincolante nella sostanza)**: nel pianificatore le minacce contraeree sono
  CILINDRI con quota minima e massima, prima approssimazione dei volumi di rilevamento e soprattutto d'ingaggio, perche'
  i dati disponibili per i sistemi contraerei distinguono l'altezza massima dalla distanza massima. Nel DES il volume
  proprio e' una SFERA. Anche nel DES il volume d'ingaggio di un'arma deve distinguere altezza massima e distanza
  massima, cosa incompatibile con una sfera (una semisfera sarebbe piu' corretta). Punto separato sull'allineamento
  delle due forme, con valutazione.
- **Esecutore previsto**: `des-developer` (Claude Sonnet, sforzo alto: risolutore e interruttori). Alternativa:
  `oc-developer`. L'esecutore segue §4 cosi' com'e'; se il codice reale non corrisponde (righe, firme, esiti) si ferma e
  riferisce.

**Convenzioni**: **[V]** = verificato leggendo il codice (`file:riga`, checkout del 2026-11-07, HEAD `b20e39cf`) o
eseguendolo; **[I]** = ipotesi o conoscenza generale, non verificata nel repository; **[S]** = stima o scelta di
progetto, mai dato tarato. Percorsi di codice relativi a `Code/Dynamic_War_Manager/Source/`.

**Termini** (come nelle altre Proposte): **finestra** = solo la finestra di contatto (`ContactWindow`); **passaggio** =
intervallo continuo in cui il bersaglio e' nel volume PROPRIO dell'osservatore; **finestra d'ingaggio** = intervallo
di validita' del candidato al tiro (`_Candidate.t_end`). In piu', qui: **fascia** = intervallo di quota del bersaglio
RELATIVA al tiratore `[min_altitude, max_altitude]` dell'arma; **sfera ∩ fascia** = punti entro la portata (distanza
3D) E dentro la fascia (in geometria: segmento sferico a due basi).

**Glossario delle sigle**

| Sigla | Significato | Fonte / verifica |
|---|---|---|
| DES | *Discrete Event Simulation*: il motore delle sessioni virtuali, a coda di eventi | `Logic/Session_Simulator.py` |
| VA | questa Proposta: "volumi allineati"; decisioni VA-1..VA-8, VA-2.1 e VA-8r (tutte prese il 2026-11-07), sonde V-0/V-1/V-2 | questo documento |
| BI | `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` (bersagli intercettabili dalla difesa aerea): campo `intercept_domains` della `ShotSpec`, interruttore `BI_AD_TARGET_RULE`, scenario S35-ADTGT; da eseguire prima di VA | quella Proposta, §6.1 |
| AAM | *Air-to-Air Missile* (missile aria-aria): armi d'aereo con tetto assoluto `max_height` [km] nel registro | `Asset/Aircraft_Weapon_Data.py`, `AIR_WEAPONS['MISSILES_AAM']` |
| EWR | *Early Warning Radar* (radar di scoperta lontana) | `Proposta_Dwell_Time_Rilevamento.md` |
| CPA | *Closest Point of Approach*: massimo avvicinamento fra due mobili | `Logic/Contact_Scheduler.py:181-195` |
| RNG | *Random Number Generator*: nel motore solo l'RNG di sessione | `Utility/Session_Rng.py` |
| Pd | probabilita' di rilevamento | `Logic/Engagement_Resolver.py:1119` (`detection_probability`) |
| SAM / AAA | missile superficie-aria / artiglieria contraerea | conoscenza generale [I] |
| SHORAD | *Short Range Air Defense*: SAM e AAA a corto raggio (Osa, Strela-10, Chaparral, Tunguska, ...) | conoscenza generale [I] |
| AGL / MSL | quota sopra il suolo (*Above Ground Level*) / sopra il livello del mare (*Mean Sea Level*) | `Command/Mission_Types.py:676` |
| ASL / BARO | riferimenti di quota dei dati DCS (`unit_alt_type`) | `Asset/Mobile.py:392` (commento) |
| D-5, DW-n | Pd dipendente dalla permanenza (`Proposta_Dwell_Time_Rilevamento.md`), interruttore `D5_DWELL_TIME` (spento); blocchi A (risolutore, `8943b292`) e B (pianificatore, `effb0dcf`) committati | `Logic/Engagement_Resolver.py:522-529` [V 2026-11-08, dopo il merge `4803424b`] |
| FP, FP-n | `Proposta_Finestre_Per_Passaggio_Portata_Propria.md` (finestre per passaggio): un'occasione di rilevamento per passaggio; tutte le decisioni FP-1..FP-10 prese (FP-5 = (d), 2026-11-08), Proposta riscritta e riletta (commit `8c440dba`); non ancora eseguita | quella Proposta, riga di stato |
| B-R / O3 | FP-1: passaggi calcolati nel risolutore dai tratti / FP-2: stream separato `pass_rng` per i passaggi dal secondo in poi | idem, §2.2-§2.3 |
| Attivita' D | volumi generici di rilevamento/ingaggio (interfaccia "volume" a intervalli di permanenza), accettata il 2026-09-24 | `Piano_Lavori_2026_09_24.md:82-86` |
| SA-6 / 3M9 | sistema 2K12-Kub e il suo missile 3M9 (registro: 24 km, fascia 100-14 000 m) | `Asset/Ground_Weapon_Data.py:2683` (record `3M9-SAM`) |
| Osa / 9M33 | sistema 9A33-Osa (SA-8) e il suo missile (registro: 10 km, fascia 25-5000 m) | `Asset/Vehicle_Data.py:4123`, `:4139`; `Asset/Ground_Weapon_Data.py:2603` |
| ZSU-57-2 / S-68 | semovente contraereo e il suo cannone binato da 57 mm (registro: 4000 m diretto, fascia 50-4000 m) | `Asset/Ground_Weapon_Data.py:2254-2269` |
| ZSU-23-4 / AZP-23 | Shilka e il suo cannone quadruplo (2500 m, fascia 0-1500 m) | `Asset/Ground_Weapon_Data.py:2270-2283` |
| CAS | *Close Air Support*, tipo di missione aerea | `Test/Test_Session_Scenarios_S32.py:103` |
| L2 / L3 | regole di precedenza dei lanciatori aria-superficie (2026-09-28) | `Logic/Engagement_Resolver.py:2525-2530`, `_register_launcher` |
| R4 | payload della salva congelato al lancio | `Logic/Engagement_Resolver.py:137-141` |
| `ShotSpec` | contratto fire control -> risolutore (arma, Pk, portata, ...) | `Logic/Engagement_Resolver.py:599-671` |
| `TIME_EPS` | 1e-9 s, tolleranza temporale del motore | `Logic/Contact_Scheduler.py:88-92` |

---

## 0. Sintesi

**Risposte brevi alle domande del compito.**

| Domanda | Risposta | Dove |
|---|---|---|
| a) Il DES ignora la fascia dell'arma? | **In parte, ed e' peggio di "ignora"**: il risolutore non la conosce (`ShotSpec` non ha quote, `_range_entry` usa solo la sfera), ma la fire control dei registri applica un **filtro di quota STATICO**, valutato sulla quota **di partenza** (`asset.position.z`, mai aggiornata in sessione) e non lungo i tratti. Un aereo che sale sopra la fascia dopo l'inizio viene ingaggiato fuori fascia; uno che parte sopra e scende nella fascia non viene mai ingaggiato. La fire control di test (`Scenario_Fixtures.SHOTS`) non ha alcuna fascia. | §1.2 |
| a) Quanti casi nella fotografia? | Sonde V-0/V-1 (1029 esecuzioni, 0 righe DIFF): con la fire control dei registri **nessuna** salva fuori fascia (0 su 242 salve contro aerei con un'arma dotata di fascia) e **nessuna** differenza fra filtro statico e filtro nel tempo (0 candidati esclusi a torto, 0 ammessi a torto, 0 su 978 istanti di tiro diversi con sfera ∩ fascia): negli scenari gli aerei volano alla quota di partenza. Il disallineamento col pianificatore esiste solo con la fire control **di test** (nessuna portata ne' fascia): **523** salve sopra il tetto del cilindro del pianificatore (504 della ZSU-23-4) in **42** esecuzioni (S5, S9, S12, S13, S14, S21). | §1.7 |
| b) AGL o MSL? | Una sola coordinata verticale assoluta (`z`, "MSL" per contratto della missione), **nessun terreno**. Le quote d'arma del registro sono **relative al tiratore** ("m AGL" = sopra il sito): si converte sottraendo la `z` del tiratore (fire control, `air_defense_volume`), mai con un modello del terreno. `altitude_reference='AGL'` dei punti di missione e' dichiarato ma **non letto** da nessun modulo `Logic/`. | §1.4 |
| c) Forma | **Sfera ∩ fascia** (**VA-1 DECISA**; per le armi d'aereo tetto assoluto, VA-3 (b)): usa i TRE dati del registro (portata, quota minima, quota massima), e' convessa, e' contenuta nel cilindro del pianificatore e nella sfera di oggi; formalizza nel tempo il filtro statico che la fire control applica gia'. Semisfera = caso particolare (fascia 0..R). Semi-ellissoide: usa due dati ma **sottostima** a media quota (SA-6 a 10 km: 16,8 km di raggio orizzontale contro 21,8) e azzera la portata al tetto. Cilindro nel DES: sovrastima gli angoli (fino a 1,41 x la portata per la ZSU-57-2) ed esce dalla sfera delle finestre. Portata minima e cono di silenzio: forme **non convesse**, nessun dato nel registro: fuori perimetro. | §2.1 |
| c) Effetto sui passaggi (FP) | I solidi convessi danno al piu' un passaggio per tratto rettilineo; le forme non convesse fino a due (sorvolo del sito con portata minima o cono di silenzio). La FP oggi lavora sul volume di **rilevamento**, non d'ingaggio: la scelta di forma dell'arma non la tocca. Per isolare la sostituzione futura del volume di rilevamento: un solo metodo `_own_intervals` del risolutore al posto delle 4 chiamate a `range_intervals` (**VA-6 (a) DECISA**: scritto nel blocco 1 della Proposta FP). | §2.3 |
| d) Rilevamento vs ingaggio | **Problemi distinti**: l'ingaggio e' un vincolo binario (si lancia o no) con dati presenti; il rilevamento cambia la **legge** di Pd (distanza normalizzata), richiede dati assenti (copertura in elevazione, altezza d'antenna, cono d'ombra) e l'orizzonte radar nel DES. **VA-5 DECISA**: separarli, qui solo l'ingaggio. | §2.5 |
| e) Interruttore | `Engagement_Resolver.VA_ENGAGEMENT_ALTITUDE_BAND = False` (**VA-7 DECISA**). Spento: fotografia **1009 identiche**, piu' le 32 esecuzioni nuove di S34-BAND. Acceso, con le scelte VA-2 (d) e VA-3 (b): la sonda V-2 non trova **nessuna** decisione della fire control che cambi con le quote all'istante (0 su 3091), nessun istante di tiro diverso (0 su 978 armi di superficie + 90 armi d'aereo), nessun bombardiere con quota di sgancio diversa, e i 48 rinvii possibili non trovano ingressi (calcolo esatto): atteso **1009 identiche anche acceso**; la regola si vede solo in S34-BAND, nei test e in campagna. | §2.7, §4.3 |
| f) Ordine | **BI -> VA**, poi blocchi FP (BI §6.1; FP-5 decisa il 2026-11-08, nessuna ripresa); prima dell'estensione dei dwell a SAM/AAA. Dimensione [S] con le scelte: ~215 righe di codice, ~680 di test (32 test: 23 + 9); circa il doppio del piano con le (a). | §2.8, §4.6 |

**Scelte dell'utente in breve (2026-11-07)**: nel DES l'ingaggio contro aerei diventa **sfera ∩ fascia nel tempo**
(VA-1): portata 3D dell'arma, fascia di quota relativa al tiratore per le armi di superficie e tetto assoluto
`max_target_z` per le armi d'aereo (VA-3 (b)); la fire control sceglie l'arma con le **quote dell'istante della
decisione** ricavate dai tratti (VA-2 (d)), e il risolutore verifica la stessa disuguaglianza nel tempo per l'istante
di lancio; tutto dietro un interruttore spento (VA-7). Il pianificatore resta col suo cilindro, **involucro
conservativo** del volume del DES (VA-4 (a)). Rilevamento, orizzonte radar, portata minima e cono di silenzio restano
attivita' separate (VA-5). **VA-2.1 = (i)**: rinvio della decisione fuori fascia (senza, la (d) non correggerebbe il
caso "rilevato fuori fascia, poi dentro"); **VA-8r**: S34-BAND a 8 varianti x 4 semi.

---

## 1. Problema e comportamento attuale

### 1.1 Pianificatore: un cilindro per sito [V]

- `Mobile.air_defense_volume()` (`Asset/Mobile.py:1395-1460`) costruisce un `Cylinder`: raggio = massima
  `range.direct` delle armi AD (m), base = `position.z` del sito + minima `min_altitude`, altezza fino alla massima
  `max_altitude` (docstring `:1396-1400`, "metres AGL").
- `AirThreat` (`Logic/Air_Route_Manager.py:83-137`) ne prende `min_altitude`/`max_altitude` **assolute**
  (`:103-104`: `bottom_center.z` e `bottom_center.z + height`); `ThreatAA` (`:140-283`) e `DetectionThreat`
  (`:286-335`) ereditano. Il cilindro e' **orizzontale** nel raggio (`DataType/Cylinder.py:85-105`: distanza dall'asse,
  non distanza 3D) e **piatto** nella fascia.
- La fascia del cilindro e' usata dal pianificatore in tre punti:
  1. **esclusione** delle minacce la cui fascia non contiene la quota di rotta (`excludeThreat`, `:1620`, con
     `consider_aircraft_altitude_route`): "sopra il tetto = nessuna minaccia";
  2. **cambio di quota** per passare sopra o sotto (`change_up`/`change_down`, `:2401-2481`);
  3. **quote di sgancio candidate** di `Weapon_Delivery` sui bordi della fascia (`Logic/Weapon_Delivery.py:526-548`:
     `threat.max_altitude`, `threat.min_altitude`).
- **Nessun chiamante di produzione** usa oggi `calcRoute` o `plan_attack_profile` (ricerca del 2026-11-07: solo i test);
  la divergenza e' quindi **latente** per la campagna, ma reale per chi usera' il pianificatore per generare le rotte
  che il DES esegue.

### 1.2 DES: sfera nel risolutore, filtro di quota statico nella fire control [V]

**Verifica del fatto (2) del compito.** La ricerca di `max_alt|min_alt|ceiling|altitude` in
`Logic/Engagement_Resolver.py` non trova nulla: **il risolutore non conosce la fascia**. Ma la conclusione "il DES
ignora la quota" va corretta:

- **Risolutore**: il tiro parte solo col bersaglio entro `ShotSpec.max_range` in distanza 3D (docstring `:117-141`;
  campo `:615-633`); l'istante viene da `engagement_intervals` = `range_intervals` (sfera, `:1731-1738`), memoizzato in
  `_range_entry` (`:3011-3044`) per `(tiratore, bersaglio, max_range)`; chiamato da `_schedule_next` (`:2568-2585`) e
  da `_in_range_at` (`:2893-2911`), che a sua volta decide le precedenze L2 (`:2528-2530`), i designati
  (`_designated_first`, `:2772-2784`) e la reazione agli ostili (`:2955`). `ShotSpec` non ha campi di quota.
- **Fire control dei registri** (`Logic/Fire_Control.py`): `rank_weapons` scarta le armi fuori inviluppo
  (`:741`, `in_altitude_envelope` `:644-671`): per le armi terrestri e navali `min_alt <= z_bersaglio - z_tiratore <=
  max_alt` (`:664-667`); per quelle d'aereo `z_bersaglio <= max_height` assoluto (`:652-654`); senza dati di quota,
  `quota relativa <= portata` (`:656-671`). Il docstring "Quota" (`:70-90`) lo dichiara: **la quota letta e'
  `asset.position.z`, che il motore non aggiorna durante la sessione** ("la quota letta e' quindi quella di
  partenza"). La scelta e' memoizzata per `(tiratore, bersaglio, dimensione, shooter_z, target_z)` (`:937-944`).
  Il filtro e' attivo di default (`make_registry_fire_control(altitude_filter=True)`, `:881`).
- **Fire control di test** (`Test/Scenario_Fixtures.py:801-826`, `SHOTS`): `ShotSpec` senza `max_range` e senza
  quote, quindi **nessun** vincolo geometrico al tiro.

Quindi oggi il volume d'ingaggio effettivo del DES, con la fire control dei registri, e':
**sfera nel tempo ∩ fascia valutata una volta alla quota di partenza**. Tre conseguenze:

| Caso | Oggi nel DES | Pianificatore | Corretto (sfera ∩ fascia nel tempo) |
|---|---|---|---|
| aereo a quota costante sopra il tetto | non ingaggiato (filtro statico) | sicuro | non ingaggiato |
| parte nella fascia, poi **sale sopra** il tetto prima del sito | ingaggiato **fuori fascia** | sicuro sopra il tetto | non ingaggiato sopra il tetto |
| parte sopra il tetto (o sotto la base), poi **entra** nella fascia | **mai** ingaggiato (escluso alla partenza) | minaccia dentro la fascia | ingaggiato quando entra |
| parte nella fascia, **scende sotto** la base (penetrazione a bassa quota) | ingaggiato sotto la base | sicuro sotto la base | non ingaggiato sotto la base |

Il secondo e il quarto caso sono quelli segnalati dall'utente (il pianificatore considera sicuro cio' che il DES
colpisce); il terzo e' l'errore opposto, prodotto dal filtro statico. In campagna un aereo che decolla in sessione
porta la quota della **base** per tutta la sessione (§2.4, "Caso della campagna"), quindi il filtro statico confronta
la quota della base con quella del sito SAM [V sul codice; I sulla frequenza]. La fotografia non contiene nessuno dei
casi 2-4 con la fire control dei registri (§1.7).

### 1.3 Esempio numerico [V sui registri, calcolo]

Osa (9M33: portata 10 000 m, fascia 25-5000 m) ferma a quota 0; A-10C in sorvolo del sito.
- A 6000 m costanti: filtro statico 6000 > 5000 -> nessun tiro (corretto). Sfera: dentro per distanza orizzontale
  <= sqrt(10² - 6²) = 8,0 km, cioe' **16 km di corda** in cui una fire control senza filtro (quella di test) sparerebbe.
- Partenza a 3000 m, salita a 6000 m prima dei 20 km dal sito: filtro statico (3000) superato, il 9M33 e' scelto; il
  tiro parte all'ingresso nella sfera, a 8,0 km orizzontali e **6000 m di quota, 1000 m sopra il tetto**.
- Partenza a 6000 m, discesa a 3000 m prima dei 20 km: filtro statico (6000) fallisce, nessuna arma: l'A-10C
  sorvola a 3000 m, dentro la fascia e a 1,0 km dal sito, **senza essere ingaggiato**.

### 1.4 Quota: AGL o MSL, e dove si converte (domanda b) [V]

- **Coordinata unica.** Asset, tratti e volumi usano `Point3D.z` [m] senza riferimento esplicito: `asset.position.z`
  (dal `.miz` `unit_alt`, `Asset/Mobile.py:392`, con il commento "nella gestione dello z devi tener conto se BARO o
  ASL", mai implementato), i punti di rotta (`Command/Mission_Types.py:676`: `'MSL'` = "quota assoluta, come
  `Waypoint.point.z`", default `:684`), i tratti (`Contact_Scheduler.route_legs`, `static_legs`; in sessione
  `Session_Simulator.py:2409`, `:2698` dalla `position`).
- **Nessun terreno.** Nessun modulo di `Logic/`, `Utility/`, `DataType/` modella il suolo (ricerca di
  `terrain|terreno|AGL|MSL`): `Logic/Air_Route_Manager.py:653-654` ("quota del bersaglio misurata rispetto alla quota
  del sito"), `Logic/Weapon_Delivery.py:83` ("Terreno non modellato: AGL = quota - quota del bersaglio"),
  `Logic/Fuel_Model.py:525`, `Logic/Session_Simulator.py:533`, `:1456` (quota trattata come altezza sulla base).
- **Registri.** `min_altitude`/`max_altitude` delle armi terrestri e navali sono "m AGL" (commenti nei record, es.
  `Asset/Ship_Weapon_Data.py:1050-1051`); la convenzione **usata** e' "relativa al tiratore": `Fire_Control.py:79-81`
  (`target.z - shooter.z`) e `Mobile.air_defense_volume` (base = `position.z + min_altitude`). `max_height` delle armi
  d'aereo e' in km e **assoluto** (`Fire_Control.py:82-83`).
- **Dove si converte**: solo in quei due punti (fire control e costruzione del cilindro), piu' l'orizzonte radar del
  pianificatore (`route_altitude - site_z`, `Air_Route_Manager.py:770`). `altitude_reference='AGL'` dei
  `MissionWaypoint` e' validato (`Mission_Types.py:700-703`) ma **non letto** da nessun modulo di `Logic/`: un punto
  dichiarato AGL verrebbe trattato come MSL [V, ricerca del 2026-11-07].
- **Conseguenza per questa Proposta**: la fascia del DES si esprime come `z_bersaglio(t) - z_tiratore(t)`, la stessa
  differenza della fire control e del cilindro; nessuna conversione nuova. Con un terreno futuro "AGL del sito" e
  "AGL del bersaglio" divergerebbero: limite dichiarato (§5), fuori perimetro.

### 1.5 Stato della Attivita' D [V]

| Pezzo | Stato |
|---|---|
| Decisione di principio (interfaccia volume a intervalli di permanenza, primitive sfera/cilindro/fascia/cono/orizzonte, combinatori, `detection_volume`/`engagement_volume` per asset e arma) | **accettata** il 2026-09-24 (`Piano_Lavori_2026_09_24.md:82-86`); **nessuna Proposta di progetto scritta**, nessun codice |
| Isolamento della geometria d'ingaggio nel DES | **fatto** (2026-09-24): `engagement_intervals` "primo caso particolare dei futuri volumi", attributo sostituibile `_EngagementRun.engagement_intervals` (`Engagement_Resolver.py:1716-1738`, `:1857-1859`); test `test_geometry_is_isolated_and_replaceable` (`Test/Test_Engagement_Resolver.py:2009-2022`) |
| Lato pianificatore, primo passo (solo `Cylinder`) | **fatto** con D-1..D-7 (`815dc35f`, 2026-09-26): `AirThreat`/`ThreatAA`/`DetectionThreat`, orizzonte radar alla quota di rotta, `ThreatMode` |
| Interfaccia `section_at(z)`/`altitude_band()` chiesta a D (`Proposta_Volumi_Rilevamento_Intercettazione.md` §5) | **non fatta**; `Cylinder._get_circle_at_z` resta l'embrione (`DataType/Cylinder.py:107-114`) |
| `DataType/Hemisphere.py` | esiste, **non usata** (importata solo da `DataType/Threat.py`, `Volume.py`, `Area.py`, `Utility/Utility.py`); lavora con `sympy` simbolico (`:1-10`), inadatta al motore a float |
| `DataType/Threat.py`, `Volume.py` | abbozzi non funzionanti (stessa Proposta §8 punto 4): da non riusare |
| Orizzonte radar nel DES | **non fatto**; rimandato da DW-7 (Proposta D-5) e dichiarato nel manuale (`Manuale_Motore_DES/10_Limiti_Estensioni_Divergenze.md:598-599`) |

Questa Proposta e' quindi il **primo passo della Attivita' D lato DES** per l'ingaggio: introduce le primitive "fascia
di quota" e "intersezione di intervalli" previste dal piano, senza introdurre un tipo "volume" generale (§2.2, VA-7).

### 1.6 Permanenza della D-5 su due forme diverse (fatto (3) del compito) [V]

- Blocco A (risolutore): `_exposure_time` somma gli intervalli di `range_intervals` con la portata propria: **sfera**
  di raggio `acquisition_range` nominale, senza orizzonte (`Engagement_Resolver.py:2247-2277`).
- Blocco B (pianificatore): `Path.compute_detection_metrics` usa `_segment_cylinder_interval` sul **cilindro** di
  rilevamento, raggio `min(acquisition_range, orizzonte(quota di rotta))`, alto `DETECTION_VOLUME_CEILING_M`
  (`Air_Route_Manager.py:741-804`, `:830-877`, `:1098-1211`); la Pd usa comunque la `R` nominale e la distanza 3D, e
  il docstring dichiara la divergenza (`:1112-1115`).
- A bassa quota il cilindro (tagliato dall'orizzonte) da' permanenze **piu' corte** della sfera; in quota vicino al
  bordo **piu' lunghe** (angoli del cilindro fuori dalla sfera). E' una divergenza del **rilevamento**, non
  dell'ingaggio: la tratta la decisione VA-5 (fuori da questo piano), non la forma d'arma.

### 1.7 Sonde V-0, V-1 e V-2 (sola lettura) — ESEGUITE il 2026-11-07 sul ProArt

Script: `Analysis/Document/Rapporti/Sonde_Allineamento_Volumi/probe_altitude.py` (versione V-2, che contiene anche
V-0 e V-1). Avvolge `_EngagementRun.run`, `_first_with_stock`, `_range_entry` e (V-2) `_call_fire_control` chiamando
gli originali, poi misura senza consumare l'RNG
e senza chiamare la fire control iniettata; riesegue `Scenario_Baseline --compare` con `--ignore probe_altitude`.
Comando (dalla root, ~11 minuti sul ProArt, mai in parallelo con suite o confronto):

    mkdir -p .ai-run/sonde_volumi/v2
    PYTHONPATH=. .direnv/python-3.12/bin/python3 Analysis/Document/Rapporti/Sonde_Allineamento_Volumi/probe_altitude.py \
        .ai-run/sonde_volumi/v2 > .ai-run/sonde_volumi/v2/log.txt 2>&1
    grep -E '^(compared|PROBE_RC|RUNS|TOTALS|FIRE_CONTROLS|ABOVE|BELOW|UNITS|CYL_|SWITCH|OUT)' .ai-run/sonde_volumi/v2/log.txt
    grep -cE '^(DIFF|CHANGED)' .ai-run/sonde_volumi/v2/log.txt     # deve essere 0

`PROBE_RC 1` e' atteso (le 20 righe NEW di S32-DWELL, non nella fotografia). Una sola riga DIFF/CHANGED significa che
la sonda ha alterato il motore: fermarsi e riferire. Una prova rapida su poche unita': aggiungere `'S19AD|S12'` come
secondo argomento (secondi). V-0 e' la prima esecuzione dello stesso script senza i contatori `entry_*` (stessi numeri).

Cosa misura, per ogni esecuzione:
- **salve contro aerei in volo**: posizione di tiratore e bersaglio all'istante di lancio dai tratti; se l'arma e'
  del registro, se il bersaglio e' sopra `max_altitude` o sotto `min_altitude` (quota relativa) (`sw_above_max`,
  `sw_below_min`); per ogni tiratore di superficie, se il bersaglio e' fuori dal **cilindro del pianificatore**
  (`cyl_above`, `cyl_below`, `cyl_outside_radius`);
- **candidati su aerei** di un osservatore con la fire control dei registri: se il filtro statico esclude ogni arma
  mentre in qualche istante della finestra d'ingaggio la sfera ∩ fascia sarebbe soddisfatta (`cand_static_excluded_dyn_ok`,
  campionamento di 40 istanti), o se ammette ma la sfera e' raggiunta solo fuori fascia (`cand_static_ok_dyn_never`);
- **previsione dell'interruttore acceso (V-1)**: a ogni chiamata di `_range_entry` contro un aereo con un'arma del
  registro dotata di fascia, l'istante che darebbe sfera ∩ fascia (calcolo analitico, la stessa regola del piano
  §4.1) confrontato con quello di oggi (`entry_differs`, di cui `entry_none_with_band` = candidato esaurito,
  `entry_later_with_band` = tiro rimandato). Copre anche le chiamate di `_in_range_at` (precedenze L2, designati,
  reazione), che possono cambiare un'esecuzione senza una salva fuori fascia.
- **previsione delle scelte VA-2 (d) e VA-3 (b) (V-2)**: a ogni chiamata della fire control dei registri in cui conta
  la quota (bersaglio aereo, o tiratore aereo contro la superficie), le armi adatte calcolate con `rank_weapons` alla
  quota di partenza e alla quota dei tratti all'istante della decisione (`fc_air_differs`); i casi in cui all'istante
  nessuna arma e' adatta ma una lo sarebbe senza filtro di quota, cioe' i rinvii di VA-2.1 (`fc_air_defer`, e
  `fc_air_defer_entry` = con un ingresso esatto in sfera ∩ fascia dopo l'istante, fino alla fine dei tratti); la quota
  di sgancio dei bombardieri (`fc_bomb_alt_differs`); le chiavi distinte della memoizzazione con le due quote
  (`fc_keys_static`, `fc_keys_dynamic`); in `_range_entry` anche le armi d'aereo con il tetto assoluto
  (`entry_checks_air_ceiling`, `entry_differs_air`). Le righe `SWITCH` elencano le esecuzioni che l'interruttore
  acceso potrebbe cambiare. V-2b: stessa sonda sulle sole unita' con rinvii (`S19`, `S21R`, `S31`), con il calcolo
  esatto `fc_air_defer_entry`.

**Esito** [V] (V-0 alle 11:36, V-1 alle 11:48, V-2 alle 15:57 e V-2b alle 16:06 del 2026-11-07, stessi numeri sui
contatori comuni; uscite in `.ai-run/sonde_volumi/v0/`, `v1/`, `v2/`, `v2b/`, fuori dal versionamento):

| Grandezza | Valore |
|---|---|
| Esecuzioni | 1029 (1009 della fotografia + 20 S32-DWELL); `compared 1029 runs: 20 difference lines`, tutte `NEW S32-DWELL/...`, **0 DIFF/CHANGED**: le sonde non alterano il motore |
| Ingaggi (`resolve_engagement`) | 1258; fire control di **test** (`Scenario_Fixtures.make_fire_control`, sola o dentro `restrict_by_policy`) 191 + 941 = **1132**; dei **registri** 12 + 114 = **126** |
| Salve totali / contro aerei in volo | 28 214 / 7 489 (tutte con i tratti: `salvos_air_no_legs` 0) |
| ... con un'arma del registro / di cui con fascia | 252 / 242 |
| ... bersaglio sopra `max_altitude` / sotto `min_altitude` all'istante di lancio | **0 / 0** |
| ... quota relativa al lancio diversa da quella di partenza (> 1 m) | **0** |
| ... con `ShotSpec` di test (`test:sam`, `test:aaa`, ...) | 6 977: nessuna portata, nessuna fascia |
| Salve contro aerei di un tiratore di superficie che ha il cilindro del pianificatore | 1 510: **sopra il tetto 523** (ZSU-23-4 `test:aaa` 504, Strela-10 `test:sam` 16, Tunguska `test:sam` 3), sotto la base 0, **oltre il raggio 1 238** (ZSU-23-4 487, S-300PS 374, Buk 256, Molniya 94, Strela-10 26, Tunguska 1) |
| Esecuzioni con almeno una salva sopra il tetto | **42**: S5 2, S9 6, S12 6, S13 6, S14 6, S21 16; con almeno una salva fuori dal cilindro (tetto o raggio): 162 (S2 10, S4 8, S5 96, S6 4, S9 6, S12 6, S13 6, S14 6, S16 4, S21 16) |
| Candidati su aerei con la fire control dei registri | 362; esclusi dal filtro statico **48**; di cui con sfera ∩ fascia soddisfatta in qualche istante della finestra d'ingaggio **0**; ammessi ma con la sfera raggiunta solo fuori fascia **0** |
| V-1: chiamate a `_range_entry` contro aerei con arma dotata di fascia | **978**; istante diverso con sfera ∩ fascia **0** (esaurimenti 0, rinvii 0) |
| V-2: chiamate a `_range_entry` contro aerei con arma d'aereo dotata di tetto (`max_height`) | **90**; istante diverso con sfera ∩ tetto **0** |
| V-2: chiamate della fire control dei registri in cui conta la quota | **3091** (senza tratti 0); armi adatte diverse fra quota di partenza e quota all'istante **0**; quota di sgancio dei bombardieri diversa **0** |
| V-2: rinvii VA-2.1 (all'istante nessuna arma, senza filtro di quota si') | **48** in 14 esecuzioni (S19 `run`/`replay` 4, S21R 6, S31 `vads_high` 4), di cui con un'arma adatta oggi 0; con un ingresso esatto in sfera ∩ fascia dopo l'istante **0** (V-2b) |
| V-2: chiavi distinte della memoizzazione della fire control (somma per esecuzione) | 353 con la quota di partenza, **353** con la quota all'istante (nessun aumento sulla fotografia) |

Letture:
1. **Con la fire control dei registri la fotografia non contiene il caso segnalato**: gli aerei degli scenari volano
   alla quota di partenza (o vi restano entro 1 m all'istante di lancio), quindi il filtro statico coincide con quello
   nel tempo. I 48 esclusi (14 esecuzioni: S19 `run`/`replay` 4, S21R 6, S31 `vads_high` 4) sono bersagli che non
   entrano mai nella fascia d'arma dentro la sfera durante la finestra d'ingaggio (es. S31 `vads_high`: A-10C a
   3000 m contro il Vulcan del M163, tetto 1000 m): esclusione corretta anche con il filtro nel tempo.
2. **Il disallineamento visibile oggi e' tutto nella fire control di test**, dichiarata "tabella di ruoli non
   calibrata" (`Test/Scenario_Fixtures.py:799-801`): le sue `ShotSpec` non hanno portata ne' fascia, quindi la ZSU-23-4
   spara sopra i 1500 m del suo tetto e S-300PS/Buk oltre i loro raggi. La regola VA **non le tocca** (nessuna fascia
   nella `ShotSpec`); allinearle richiederebbe di cambiare le fixture e rifare la fotografia: fuori perimetro (§5).
3. **Previsione dell'interruttore acceso con le scelte dell'utente** (VA-2 (d), VA-3 (b), rinvio VA-2.1 (i)): 0
   decisioni della fire control diverse su 3091, 0 istanti di tiro diversi su 1068 controlli (comprese le chiamate di
   precedenza), 0 rinvii che portino a un tiro: con l'interruttore acceso la fotografia resta **1009 identiche**. I 48
   rinvii eseguono codice in piu' (una chiamata alla fire control con quote ignote e un calcolo di intervalli per
   opzione) ma finiscono come oggi (candidato esaurito). La regola si osserva solo in S34-BAND, nei test e nella
   campagna (aerei che cambiano quota, decolli). Il costo della memoizzazione non cresce sulla fotografia (stesse
   chiavi: le quote dei tratti coincidono con quelle di partenza); in campagna crescera' con le rotte a quota variabile
   (non misurato).

### 1.8 Altri chiamanti e vincoli [V]

- `Contact_Scheduler.threat_windows`/`route_threat_windows` (`:554-736`) leggono il cilindro (`_cylinder_of`,
  `:536-539`) ma **non sono chiamati dalla sessione** (`Piano_Lavori_2026_09_24.md:83`).
- Le finestre di contatto (`contact_windows`, `:1023-1100`) sono intervalli della **sfera di rilevamento** di raggio
  massimo della coppia; la finestra d'ingaggio del candidato e' dentro la finestra. Qualunque volume d'ingaggio
  contenuto nella sfera di portata dell'arma (e quindi, nei dati, nella sfera di rilevamento, §2.2) non richiede
  finestre diverse: **lo scheduler non cambia**.
- `_range_entry` gestisce gia' **piu' intervalli** per coppia (ciclo `:3036-3042`: il primo che finisce dopo `t_from`):
  un volume d'ingaggio non convesso (portata minima) non richiederebbe di cambiare la logica di scelta dell'istante.

---

## 2. Alternative e raccomandazione

### 2.1 Forme del volume d'ingaggio (domanda c, decisione VA-1: DECISA = sfera ∩ fascia)

Dati del registro per un'arma contraerea: portata `R` (`range.direct` [m] terrestre, `range` [km] navale), quota
minima `h1` e massima `h2` relative al tiratore. Nessun dato di portata minima, di angolo di elevazione o di profilo
dell'inviluppo (ricerca di `min_range` nei registri d'arma terrestri e navali: nessun risultato).

| Forma | Dati usati | Convessa | Sovrastima | Sottostima | Contenuta nel cilindro del pianificatore? |
|---|---|---|---|---|---|
| **Sfera** (oggi, nel tempo) | R | si' | tutto cio' che sta sopra `h2` o sotto `h1` entro R | — | **no** (sopra il tetto) |
| **Semisfera** (proposta dall'utente) | R | si' | sopra `h2` fino a R; sotto `h1` | — | **no** |
| **Sfera ∩ fascia** (decisa, VA-1) | R, h1, h2 | si' (intersezione di convessi) | il profilo reale vicino al tetto [I] | il cilindro fuori dalla sfera (corretto: la portata e' 3D) | **si'** |
| **Semi-ellissoide** (semiassi R e h2) | R, h2 | si' | — | tutta la media quota; al tetto la portata e' zero | si' |
| **Cilindro** (come il pianificatore) | R, h1, h2 | si' | gli angoli: distanza 3D fino a sqrt(R² + h2²) | — | coincide |
| **Cono** (vertice nel sito) | angolo di elevazione (assente) | si' | dipende dall'angolo [I] | idem | — |
| **Portata minima** (sfera meno sfera interna) | R, R_min (assente) | **no** | — | — | — |
| **Cono di silenzio** (meno un cono verticale) | angolo massimo (assente) | **no** | — | — | — |

Raggio orizzontale a quota z (calcolo, [V] sui registri):

| Arma | z | Sfera | Sfera ∩ fascia | Cilindro | Semi-ellissoide |
|---|---|---|---|---|---|
| 3M9 (SA-6), R 24 km, fascia 100-14 000 m | 30 m | 24,00 km | 0 | 0 | 0 |
| | 5 000 m | 23,47 | 23,47 | 24,00 | 22,42 |
| | 10 000 m | 21,82 | 21,82 | 24,00 | **16,80** |
| | 14 000 m (tetto) | 19,49 | 19,49 | 24,00 | **0** |
| | 16 000 m | **17,89** | 0 | 0 | 0 |
| S-68 (ZSU-57-2), R 4000 m, fascia 50-4000 m | 30 m | 4,00 | 0 | 0 | 0 |
| | 1 000 m | 3,87 | 3,87 | 4,00 | 3,87 |
| | 3 000 m | 2,65 | 2,65 | **4,00** | 2,65 |
| | 4 000 m (tetto) | 0 | 0 | **4,00** | 0 |
| 9M33 (Osa), R 10 km, fascia 25-5000 m | 6 000 m | **8,00** | 0 | 0 | 0 |

Volumi [km³]: SA-6 cilindro 25 153, sfera ∩ fascia 22 279, semisfera 28 953, semi-ellissoide 16 708 (rapporti al
segmento sferico 1,13 / 1 / 1,30 / 0,75); ZSU-57-2 cilindro 198,5, sfera ∩ fascia 131,5, semisfera 134,0,
semi-ellissoide 131,5 (1,51 / 1 / 1,02 / 1,00).

Letture:
- **ZSU-57-2**: il registro ha `max_altitude` = portata (4000 = 4000): sfera ∩ fascia, semisfera e semi-ellissoide
  coincidono a meno dei 50 m di base; la sfera di oggi differisce solo sotto i 50 m. Il cilindro sovrastima gli angoli:
  a 4000 m di quota e 4000 m orizzontali la distanza 3D e' 5657 m, **1,41 volte** la portata.
- **SA-6**: il tetto (14 km) e' molto sotto la portata (24 km). La sfera sbaglia sopra i 14 km (quote rare, MiG-25 e
  ricognitori [I]); il semi-ellissoide sbaglia **a tutte le quote operative**: a 10 km riduce il raggio da 21,8 a 16,8
  km e al tetto lo annulla, mentre i diagrammi d'inviluppo dei SAM mostrano il tetto mantenuto su una fascia di
  distanze [I, conoscenza generale; nessun diagramma nel repository].
- **SHORAD** (Osa 10 km / 5 km, Chaparral 9 km / 3 km, Tunguska 8 km / 3,5 km, Strela-10 5 km / 3,5 km): la fascia
  fra il tetto e la portata e' la **media quota operativa** (3-8 km). E' qui che sfera e pianificatore divergono di piu'
  in pratica.
- **Semisfera**: e' sfera ∩ fascia con `h1 = 0` e `h2 = R`; non usa `h2` e quindi non risponde all'osservazione
  dell'utente (altezza massima distinta dalla distanza massima). Con tutti i `min_altitude` del registro >= 0, la
  sfera ∩ fascia e' sempre **dentro** la semisfera: la scelta raccomandata contiene l'intuizione dell'utente.
- **Cilindro nel DES**: possibile, ma (i) tratta la portata come orizzontale, contro la convenzione 3D del DES e della
  fire control, (ii) **esce dalla sfera di portata**, quindi un volume d'ingaggio cilindrico non sarebbe piu' contenuto
  nella finestra d'ingaggio derivata dal rilevamento senza un controllo in piu', (iii) richiede il moto relativo
  orizzontale (equazione 2D) piu' la fascia: costo simile a sfera ∩ fascia, risultato meno corretto.

**VA-1 DECISA dall'utente il 2026-11-07: sfera ∩ fascia** (era la raccomandazione). Usa i tre dati presenti, nessuna costante nuova; e' l'estensione nel tempo
del filtro che la fire control applica gia' (la stessa disuguaglianza, `Fire_Control.py:664-667`); e' convessa;
garantisce l'allineamento per involucro col pianificatore (§2.2).

### 2.2 Allineamento per involucro: niente da cambiare nel pianificatore (decisione VA-4: DECISA = (a)) [V, geometria]

Per ogni arma del sito: sfera ∩ fascia ⊆ cilindro(R, h1, h2) ⊆ cilindro del sito (raggio = massimo R, base = minimo
h1, tetto = massimo h2, `air_defense_volume`). Quindi, con il DES a sfera ∩ fascia:
- **fuori dal cilindro del pianificatore => fuori dal volume d'ingaggio del DES**: "sicuro" per il pianificatore e'
  sicuro anche per il DES (tetto, base, raggio orizzontale);
- il contrario non vale: dentro il cilindro ma fuori dalla sfera (angoli) il pianificatore vede pericolo dove il DES
  non spara. E' una **sovrastima conservativa** per chi attacca, la stessa gia' dichiarata per la corda
  d'intercettazione (`Proposta_Volumi_Rilevamento_Intercettazione.md` §6).

Oggi, con la sfera, la prima proprieta' **non vale** (§1.2, casi 2 e 4). Il pianificatore puo' quindi restare com'e':
l'allineamento si ottiene cambiando il solo DES. Le alternative per il pianificatore (VA-4):
- (a) **cilindro invariato**, dichiarato involucro conservativo (raccomandata; **DECISA dall'utente il 2026-11-07**);
- (b) sezione della sfera ∩ fascia alla quota di rotta (`section_at(z)` della Attivita' D: raggio
  `sqrt(R² - (z - z_sito)²)` nella fascia): rotte meno lunghe in quota, ma tocca l'aggiramento, il cambio di quota,
  la corda `calcMaxLenghtCrossSegmentInterception` (`:183-258`, che usa `cylinder.radius`) e i test del pianificatore;
  meglio dentro la Proposta della Attivita' D lato pianificatore;
- (c) nessun allineamento (DES a sfera): la divergenza resta.

### 2.3 Convessita', passaggi e isolamento di `range_intervals` (domanda c, decisione VA-6: DECISA = (a)) [V]

- **Convessi** (sfera, semisfera, sfera ∩ fascia, semi-ellissoide, cilindro, cono): sul moto relativo rettilineo
  uniforme di un sottointervallo fra due breakpoint (`_breakpoints`, `Contact_Scheduler.py:755-779`) il tempo dentro e'
  **un intervallo** (o vuoto). Una rotta a piu' tratti puo' comunque dare piu' intervalli (virate), come oggi.
- **Non convessi** (sfera meno sfera interna per la portata minima; meno un cono per il cono di silenzio; unione di
  volumi di sensori o armi diversi): **un solo tratto** puo' dare **due** intervalli (sorvolo del sito: dentro, buco,
  dentro).
- **Effetto sulla FP** (FP-1 = B-R): i passaggi della FP sono intervalli del volume di **rilevamento** proprio
  (`_own_passes`, `_pass_detection_time`, `_exposure_time` del piano FP §4.1.1). La forma dell'**arma** non li tocca:
  il volume d'ingaggio entra solo in `_range_entry`, che gestisce gia' piu' intervalli (§1.8). Se in futuro il volume
  di **rilevamento** diventera' non convesso (cono di silenzio di un radar), un sorvolo rettilineo dara' due passaggi e
  quindi, con la FP accesa, **due estrazioni** separate da pochi secondi: e' il caso della FP-10 (tolleranza di unione),
  che andrebbe allora rivista con un dato di memoria della traccia.
- **Isolamento (VA-6)**: nel risolutore le chiamate a `range_intervals` sul volume proprio sono oggi 2
  (`_detection_time` `:2233`, `_exposure_time` `:2265`) e diventano 4 con la FP (`_own_passes`, `_pass_detection_time`,
  piu' la nuova `_exposure_time`). Proposta: un solo metodo

  ```python
  def _own_intervals(self, observer_id: str, target_id: str, own_range: float,
                     radius: Optional[float] = None) -> Optional[List[Tuple[float, float]]]:
      """Intervalli in cui il bersaglio e' nel volume di rilevamento PROPRIO dell'osservatore (oggi la sfera di
      raggio own_range, o di raggio `radius` — il raggio estratto, per l'istante di rilevamento — se dato).
      None senza i tratti di entrambi. Unico punto da sostituire con un volume di rilevamento diverso."""
  ```

  con corpo `range_intervals(legs_o, legs_t, own_range if radius is None else radius)`, usato dalle 4 chiamate. La sostituzione futura del
  volume tocca solo questo metodo; la logica dei passaggi (estrazioni, CPA del passaggio, finestra d'ingaggio) no.
  Due vincoli da dichiarare per un volume futuro: (i) deve restare **contenuto nella sfera** di raggio `own_range`
  (altrimenti le finestre dello scheduler, costruite sulla sfera, non lo coprono); (ii) il raggio estratto passa come
  `radius` **invariato** (non come fattore: stessi float di oggi), cosi' la legge di Pd resta funzione di una distanza
  normalizzata.
- **Quando farlo**: (a) dentro il blocco 1 della FP, prima della sua esecuzione (refactor a comportamento identico,
  ~10 righe, la FP va aggiornata da chi pianifica); (b) dopo la FP, in un commit separato; (c) solo quando arrivera'
  un volume di rilevamento non sferico. Raccomandazione: **(a)**, perche' evita di riscrivere 4 chiamate nuove subito
  dopo averle scritte; e' a costo nullo sulla fotografia. **DECISA dall'utente il 2026-11-07: (a)**; scritta nel
  blocco 1 della Proposta FP (§4.1.1 punti 7 e 8-bis, test 20), con firma `_own_intervals(observer_id, target_id,
  own_range, radius=None)` (il raggio estratto passa invariato, non come fattore: stessi float di oggi).

### 2.4 Filtro statico della fire control con la regola accesa (decisione VA-2: DECISA = (d))

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| **(a) filtro statico invariato, fascia anche nel risolutore** | la fire control sceglie come oggi; il risolutore aggiunge la fascia nel tempo all'arma scelta | modifica locale (risolutore + 2 campi di `ShotSpec`); puo' solo **togliere o ritardare** tiri, mai aggiungerne; il confronto acceso e' prevedibile (V-1) | resta il caso 3 di §1.2 (partenza fuori fascia, poi dentro: mai ingaggiato) |
| (b) filtro nel tempo al posto di quello statico, con ripiego | con la regola accesa `rank_weapons` non scarta per quota le armi la cui fascia viaggia nella `ShotSpec` (le altre restano al filtro statico); il risolutore, fra le opzioni in ordine di preferenza, usa la **prima con scorta e con un ingresso nel proprio volume** nella finestra d'ingaggio | corregge anche il caso 3 | cambia `_first_with_stock`/`_schedule_next`/`_in_range_at` (ripiego sulla seconda arma, oggi assente anche per la sola portata); `Fire_Control` deve leggere l'interruttore del risolutore; aggiunge tiri, quindi puo' cambiare piu' esecuzioni |
| (c) come (b) ma senza ripiego | la fire control non scarta per quota le armi con fascia; il risolutore prova solo la prima arma con scorta, come oggi | corregge il caso 3 per i tiratori con una sola arma contraerea (la maggioranza dei SAM del registro) | per un tiratore con piu' armi l'arma preferita fuori fascia **esaurisce** il candidato anche se la seconda sarebbe in fascia: regressione rispetto al filtro statico, che oggi la scarta e passa alla seconda |
| (d) filtro statico ricalcolato alla quota dell'istante di tiro | la fire control riceve la quota dai tratti (estensione del protocollo per introspezione, come `target_grounded`) | nessun ripiego necessario all'istante | la fire control non sa se il bersaglio entrera' nella fascia piu' tardi: il candidato va comunque rivalutato nel tempo dal risolutore; due meccanismi per la stessa regola |

**Caso della campagna** [V sul codice letto; I sulla frequenza]: il filtro statico legge `asset.position.z`, che per un
aereo con missione e' la **posizione di partenza** (in campagna, la base: `Mission_Adapter.py:433-434`
`grounded_before`, "parcheggio prima del decollo"; `Session_Campaign.apply_final_positions`, `:62-110`, la aggiorna
solo a fine sessione). La quota relativa usata per tutta la sessione e' quindi **quota della base - quota del sito
SAM**: un SA-6 su un'altura di 200 m sopra la base nemica non ingaggia mai (-200 < 100), un SA-6 200 m sotto ingaggia
anche un aereo che penetra a 50 m. La fotografia non contiene questo caso (V-0: gli aerei degli scenari partono gia' in
volo alla quota di rotta, §1.7); la campagna si'.

Raccomandazione della prima stesura: (a) come primo passo, (b) prima della campagna, (c) no, (d) "duplica il
meccanismo".

**DECISA dall'utente il 2026-11-07: (d)**, filtro ricalcolato alla quota dell'istante di tiro. Il "contro" della
tabella (due meccanismi) si risolve con **una sola disuguaglianza valutata in due istanti** (piano §4.1.2-§4.1.3):

1. **Da dove viene la quota.** Con l'interruttore acceso il risolutore calcola, all'istante `t` della decisione (il
   `time` che oggi passa a `_call_fire_control`: `t_fire` in `_schedule_next` e in `_in_range_at`), le quote di
   tiratore e bersaglio dai tratti: `position_on_legs(self.legs[id], t)[2]` (`Contact_Scheduler.py:508-533`, gia'
   importata nel risolutore). Le passa alla fire control con la keyword nuova `altitudes=(z_tiratore, z_bersaglio)`,
   **solo** se la fire control la dichiara (introspezione `accepts_altitudes`, generalizzazione di
   `accepts_target_grounded`, `Engagement_Resolver.py:1695-1714`) e solo se entrambi i tratti esistono; altrimenti la
   chiamata e' quella di oggi. `restrict_by_policy` dichiara e inoltra la keyword solo se la base la dichiara.
2. **Fire control.** `make_registry_fire_control` usa `altitudes` al posto di `_z(shooter)`/`_z(target)`
   (`Fire_Control.py:933-934`) per **ogni** lettura di quota (filtro d'inviluppo contro gli aerei e quota di sgancio
   delle bombe, cosi' un colpo non mescola due quote). `rank_weapons` e `in_altitude_envelope` non cambiano.
3. **Memoizzazione** (`Fire_Control.py:937-944`): la chiave `(tiratore, bersaglio, dimensione, shooter_z, target_z)`
   resta la stessa e contiene le quote **effettivamente usate**, cioe' quelle dell'istante: esatta, nessun
   arrotondamento (arrotondare cambierebbe i risultati). Effetto: per un aereo a quota costante la chiave si ripete
   (la quota interpolata su un tratto orizzontale e' esattamente quella dei punti); per un aereo che sale o scende
   ogni decisione e' una chiave nuova. Sulla fotografia V-2 misura **353 chiavi in entrambi i casi** (§1.7).
4. **Risolutore.** Dopo la scelta dell'arma, `_range_entry` cerca il primo istante **da `t` in poi** in sfera ∩ fascia
   (o ∩ tetto per le armi d'aereo, VA-3 (b)), con i limiti copiati nella `ShotSpec` dagli stessi campi del registro
   che `in_altitude_envelope` legge. All'istante `t` la fire control ha gia' verificato la disuguaglianza; il
   risolutore la verifica sui tratti successivi (il bersaglio puo' uscire dalla fascia prima di entrare nella sfera).
   Stessi dati, stessa disuguaglianza: nessuna incoerenza possibile salvo l'arrotondamento al bordo, chiuso al punto 5.
5. **Rinvio (sotto-decisione VA-2.1, DECISA dall'utente il 2026-11-07 = (i)).** La (d) da sola non sa "piu' tardi": se all'istante della decisione il
   bersaglio e' fuori fascia (rilevato in quota, poi scende), la fire control restituisce None e oggi il candidato si
   esaurisce. **(i) Rinvio (raccomandato)**: il risolutore richiama la fire control con quote ignote
   (`altitudes=(None, None)`: nessun filtro di quota, politica gia' dichiarata in `Fire_Control.py:90-92`), calcola per
   ogni opzione con scorta il primo ingresso in sfera ∩ fascia nella finestra d'ingaggio e rinvia la decisione al
   minimo (`_Candidate.not_before`, il meccanismo gia' usato per la portata); all'istante del rinvio la fire control
   decide di nuovo con le quote di allora. Se l'ingresso e' gia' all'istante (bordo, arrotondamento), si usa subito la
   prima opzione con quell'ingresso. **(ii) Nessun rinvio**: candidato esaurito come oggi; il caso "rilevato fuori
   fascia, poi dentro" resta scoperto.

**Cosa succede nei profili di S34** (Osa, 9M33: 10 km, fascia 25-5000 m; radar 30 km) [calcolo dal registro, §4.2.1]:

| Profilo | Oggi (filtro statico alla quota di partenza) | (d) senza rinvio, VA-2.1 (ii) | (d) con rinvio, VA-2.1 (i) |
|---|---|---|---|
| costante 3000 m | salve in fascia | identico | identico |
| salita 3000 -> 6000 m (prima di 20 km dal sito) | salve a 6000 m, **fuori fascia** | nessuna salva | nessuna salva |
| discesa 6000 -> 3000 m (sotto 5000 m gia' a ~34 km, prima del rilevamento a 30 km) | **nessuna** salva (escluso alla partenza: caso 3) | **salve** a 3000 m: alla decisione l'A-10C e' gia' in fascia | salve, come (ii) |
| discesa tardiva: 6000 m fino a 12 km dal sito, 3000 m da 6 km (nuova, VA-8r) | nessuna salva | **nessuna** (di norma): alla decisione e' a 6000 m, candidato esaurito | **salve** dopo il rinvio, sotto i 5000 m |

Quindi con la (d) **`descend_on` cambia rispetto a `descend_off`**: l'Osa spara quando il bersaglio entra nella fascia
(il caso 3 di §1.2 e' corretto per questa geometria anche senza rinvio, perche' il rilevamento avviene gia' in fascia).
La variante `late_descend` serve a distinguere VA-2.1 (i) da (ii) (VA-8r).

**Caso della campagna con la (d)**: la quota non e' piu' quella della base ma quella dei tratti all'istante: un aereo
decollato in sessione e' valutato alla sua quota reale (il decollo da base a quota diversa dal SAM non decide piu'
l'esito). Resta la dipendenza dal rinvio (VA-2.1) per i bersagli rilevati in quota che scendono dopo.

### 2.5 Rilevamento e ingaggio: due problemi (domanda d, decisione VA-5: DECISA)

| Aspetto | Ingaggio (arma) | Rilevamento (sensore) |
|---|---|---|
| Effetto nel DES | vincolo binario al lancio (`_range_entry`) | legge di Pd `f(d/R)`, istante di rilevamento, permanenza D-5, passaggi FP |
| Dati di forma | **presenti**: R, h1, h2 per tutte le armi AD terrestri e navali | **assenti**: copertura in elevazione, quota massima di copertura, cono d'ombra; altezza d'antenna solo stimata nel pianificatore (`sensor_antenna_height`, D-4(a)) |
| Forma fisica | sfera ∩ fascia (prima approssimazione) | solido di rotazione col raggio che cresce con la quota (orizzonte), meno il cono di silenzio, tagliato dal terreno |
| Cambio di legge | nessuno | si': con un volume non sferico serve una distanza normalizzata per la Pd |
| Effetto su FP e D-5 | nessuno | diretto (passaggi, permanenza) |

**VA-5 DECISA dall'utente il 2026-11-07: separarli** (era la raccomandazione). Questa Proposta tratta solo l'ingaggio. Il rilevamento non sferico (orizzonte
radar nel DES, poi copertura in elevazione) e' una Proposta successiva della Attivita' D, gia' attesa da DW-7 e dal
manuale; l'aggancio e' il metodo `_own_intervals` (VA-6).

### 2.6 Armi d'aereo (decisione VA-3: DECISA = (b))

Le armi aria-aria (AAM) del registro hanno `max_height` **assoluto** in km e **nessuna quota minima** (nessun campo
`min_height`/`min_altitude` in `AIR_WEAPONS['MISSILES_AAM']`) [V, lettura del registro del 2026-11-07]; la fire control
lo converte in metri (`Fire_Control.py:389-390`) e lo confronta con la quota assoluta del bersaglio
(`in_altitude_envelope`, `:650-654`; docstring `:82-83`). Senza `max_height` vale `|z_bersaglio - z_tiratore| <=
portata` (`:658-659`), gia' implicato dalla sfera. Valori del registro (`Asset/Aircraft_Weapon_Data.py`, da `:1001`):

| `max_height` | Missili (portata del registro, km) |
|---|---|
| 18 km | AIM-7E/F/M/MH/P (45-70), AIM-9B/P/P5/L/M (4,6-18,5), R-550 (10), R-530IR (18), RB-24/24J/74 (4,6-18,5), PL-5EII (18) |
| 20 km | R-530EM (40), R-13M/M1 (15-17), R-60/R-60M (8), R-73 (30), R-3S/R-3R (8) |
| 21 km | PL-12 (80), PL-8A/B (20) |
| 24,8 km | AIM-54A/C (160) |
| 25 km | AIM-9X (37), R-24R/T, R-40R/T, R-27R/T/ER/ET, R-33 (15-130) |
| 30 km | R-37 (300) |

Il valore "AIM-9 18 km" della prima stesura e' **verificato** per AIM-9B/P/P5/L/M (18 km); l'AIM-9X ha 25 km. La
qualita' dei valori rispetto a fonti esterne non e' verificata qui.

Opzioni: (a) lasciarle al filtro statico (raccomandata in prima stesura); **(b) DECISA dall'utente il 2026-11-07**:
campo **`max_target_z`** [m, assoluto] in `ShotSpec`, valorizzato dalla fire control con `max_height_m` per le armi
d'aereo contro aerei; il risolutore lo applica nel tempo come la fascia: intervalli in cui `z_bersaglio(t) <=
max_target_z`, `altitude_intervals(..., z_min=None, z_max=max_target_z, relative=False)` (piano §4.1.1), intersecati
con la sfera di portata. Nessuna quota minima (dato assente). Esempio: AIM-9M (18,5 km di portata, tetto 18 km) da un
caccia a 15 km contro un bersaglio che sale da 16 a 20 km: con la (b) il tiro e' possibile solo finche' il bersaglio e'
sotto 18 km (e con la (d) la fire control lo scarta se alla decisione e' gia' sopra). Sulla fotografia: 90 controlli,
0 istanti diversi (V-2).

### 2.7 Interruttore (domanda e, decisione VA-7: DECISA)

`Engagement_Resolver.VA_ENGAGEMENT_ALTITUDE_BAND = False`, letto dal risolutore alla costruzione di `_EngagementRun`
(nessun parametro nuovo in `resolve_engagement` ne' in `Session_Simulator`: le quote le calcola il risolutore dai
tratti che ha gia', la fascia arriva nella `ShotSpec`); nessun tipo "volume" generale.
- **Spento**: `ShotSpec` porta i tre campi nuovi ma il risolutore non li legge; la fire control non riceve
  `altitudes` e legge le posizioni come oggi; nessun rinvio: stesse chiamate, stesse chiavi, stessi istanti.
  Fotografia **1009 identiche**; le 20 di S32 e le 32 di S35 (BI) identiche alla loro cattura; nuove le 32 di S34.
- **Acceso**: quote all'istante per la fire control (VA-2 (d)), sfera ∩ fascia/tetto nel tempo (VA-1, VA-3 (b)),
  rinvio fuori fascia (VA-2.1 (i)). Nessuna estrazione nuova ne' spostata, ma un tiro tolto, rimandato o reso
  possibile cambia le estrazioni di danno successive. Previsione V-2: **nessuna** esecuzione della fotografia cambia
  (§1.7). Lettura del confronto acceso: 1009 identiche piu' le nuove; ogni riga CHANGED e' fuori dall'atteso e va
  segnalata (difetto dell'implementazione o della sonda).
- Alternativa: nessun interruttore, parametro esplicito `altitude_band=False` di `resolve_engagement` passato da
  `Session_Simulator` (come `dwell_time_for` per la D-5). Piu' esplicito, ma tocca la firma di due moduli senza
  necessita' (la fascia non ha un "lettore" da iniettare).

### 2.8 Ordine di lavoro (domanda f)

| Lavoro | Stato | Relazione con VA |
|---|---|---|
| D-5 blocchi A e B | committati (`8943b292`, `effb0dcf`) | indipendente (rilevamento) |
| BI (bersagli intercettabili) | decisioni BI-1..BI-12 tutte prese; blocchi 0-2 eseguiti e mergiati (merge `4803424b`), blocchi 3-4 da eseguire | **prima di VA**: stessi file (`ShotSpec`, `shot_spec_for`, interruttori, docstring, `UNITS`); conflitti di riga, non di logica (tabella sotto) |
| FP (finestre per passaggio) | tutte le decisioni FP-1..FP-10 prese (FP-5 = (d), 2026-11-08), Proposta riscritta e riletta (commit `8c440dba`), non ancora eseguita; sonda P-0 fatta | indipendente sull'ingaggio; VA-6 (a) e' gia' nel suo blocco 1 (`_own_intervals`) |
| Estensione dei dwell a SAM/AAA (DW-9 rivista) | Proposta da scrivere | rende i SAM/AAA osservatori con dwell: piu' sensibili ai passaggi (FP) che alla forma d'arma |
| **VA (questa)** | DEFINITIVA (decisioni prese il 2026-11-07), non ancora eseguita | — |
| Orizzonte radar nel DES / rilevamento non sferico | non pianificato | dopo VA-6; usa `_own_intervals` |

Ordine proposto (coerente con BI §6.1, che sostituisce la raccomandazione "FP, poi VA" della prima stesura):
**BI -> VA -> FP blocchi 1-2 -> estensione dei dwell** (FP-5 decisa il 2026-11-08: nessuna ripresa; BI blocchi 0-2
gia' eseguiti e mergiati, restano BI blocchi 3-4). Mai due esecutori insieme su `Logic/Engagement_Resolver.py` o
`Logic/Fire_Control.py`.

Punti di conflitto fra BI e VA [V sui due piani scritti; BI blocchi 0-2 eseguiti (la colonna BI delle righe del
risolutore e di `shot_spec_for` e' gia' nel codice), VA non eseguita; righe ricontrollate il 2026-11-08 sul checkout
dopo il merge `4803424b`]:

| File / punto | BI | VA | Come si compongono |
|---|---|---|---|
| `Engagement_Resolver.py`, interruttori dopo `D5_DWELL_TIME` (`:522-529`; `BI_AD_TARGET_RULE` gia' presente a `:531-535`) | `BI_AD_TARGET_RULE` | `VA_ENGAGEMENT_ALTITUDE_BAND` | VA **dopo** BI |
| `ShotSpec` (`:599-671`), campi in coda | `intercept_domains` | `min_altitude`, `max_altitude`, `max_target_z` | VA **in coda dopo** `intercept_domains` (non "dopo `stock_per_round`" come diceva la prima stesura); validazioni nello stesso ordine |
| `_EngagementRun.__init__` | `self.ad_target_rule` | `self.altitude_band`, `self.fire_control_knows_altitudes` | righe vicine, indipendenti |
| `_on_resolve` (`:3318`, filtro a `:3396`) | filtro `_admissible` | — | nessun conflitto |
| `_call_fire_control`, `_fire_control`, `_schedule_next`, `_in_range_at`, `_range_entry`, introspezione (`:1692-1714`) | — | quote all'istante, rinvio, fascia | solo VA |
| docstring del modulo del risolutore | punto della catena BI | sezione "Quota nel volume d'ingaggio" | sezioni distinte |
| `Fire_Control.py` `shot_spec_for` (`:819-865`) | `intercept_domains=intercept_domains_for(weapon)` | tre argomenti di quota | stesso costruttore: argomenti aggiunti in coda, BI prima |
| `Fire_Control.py` `make_registry_fire_control`, `restrict_by_policy`, docstring "Quota" | — | `altitudes`, quattro varianti | solo VA |
| `Scenario_Baseline.UNITS` e docstring | S35-ADTGT | S34-BAND (dopo S35, nessuna rinumerazione) | in coda, nell'ordine di esecuzione |

Nessuna regola legge i campi dell'altra: un colpo con `intercept_domains` e quote nuove e' trattato da BI all'impatto
e da VA al lancio.

---

## 3. Decisioni dell'utente (2026-11-07), tutte prese

Premessa dalle sonde (§1.7): con la fire control dei registri la fotografia non ha salve fuori fascia ne' differenze
fra filtro statico e filtro nel tempo, e l'interruttore acceso, anche con le scelte VA-2 (d) e VA-3 (b), non
cambierebbe nessuna delle 1009 esecuzioni (V-2). Le decisioni si giudicano quindi sulla **correttezza del modello**
(campagna, rotte del pianificatore con cambi di quota, decolli) e su S34-BAND, non sul confronto. Il disallineamento
visibile oggi (523 salve sopra il tetto del cilindro) e' della fire control di test e non e' toccato da nessuna
opzione.

**VA-1 — Forma del volume d'ingaggio dell'arma nel DES. DECISA dall'utente il 2026-11-07: sfera ∩ fascia** (portata
3D e quota relativa fra minima e massima, nel tempo; era la raccomandazione). Esempio: SA-6 (24 km, 100-14 000 m)
contro un aereo a 10 km di quota: raggio orizzontale d'ingaggio sfera 21,8 km, **sfera ∩ fascia 21,8 km**,
semi-ellissoide 16,8 km, cilindro 24,0 km; a 16 km di quota: sfera 17,9 km (spara), **sfera ∩ fascia 0** (non
spara), come il pianificatore.

**VA-2 — Filtro di quota della fire control con la regola accesa. DECISA dall'utente il 2026-11-07: (d)**, filtro
ricalcolato alla quota dell'istante di tiro, con la quota passata dal risolutore (keyword `altitudes` per
introspezione, come `target_grounded`). **Non** e' la (a) raccomandata in prima stesura. Meccanismo unico in §2.4
(punti 1-4) e nel piano §4.1.2-§4.1.3. Esempio (Osa, §1.3): partenza a 3000 m e salita a 6000 m: oggi tiro a 6000 m;
(d) nessun tiro. Partenza a 6000 m e discesa a 3000 m prima del rilevamento: oggi nessun tiro; (d) tiro a 3000 m.

**VA-2.1 — Rinvio fuori fascia (nata dalla scelta (d)). DECISA dall'utente il 2026-11-07: (i) rinvio** (era la
raccomandazione). Se alla
decisione il bersaglio aereo e' fuori fascia ma un'arma entrera' in sfera ∩ fascia piu' tardi nella finestra
d'ingaggio, la decisione si rinvia a quell'istante invece di esaurire il candidato; (ii) nessun rinvio (candidato
esaurito come oggi). Esempio (S34 `late_descend`): l'Osa rileva l'A-10C a 30 km mentre e' a 6000 m; l'A-10C scende a
3000 m fra 12 e 6 km dal sito. (i): l'Osa spara quando l'A-10C entra in sfera ∩ fascia (~4100 m, 10 km); (ii): di
norma mai (solo se il rilevamento avviene cosi' tardi che l'A-10C e' gia' sotto i 5000 m). Sulla
fotografia le due opzioni coincidono (V-2b: 48 rinvii, 0 ingressi). Costo di (i): un metodo (~35 righe), due test,
due varianti di S34. Senza (i) la (d) corregge il caso 3 di §1.2 solo quando il rilevamento avviene gia' in fascia.

**VA-3 — Armi d'aereo. DECISA dall'utente il 2026-11-07: (b)**, campo `max_target_z` assoluto in `ShotSpec`, tetto
applicato nel tempo anche per le armi d'aereo (non la (a) raccomandata). Valori reali del registro e regola in §2.6
(18-30 km; nessuna quota minima).

**VA-4 — Pianificatore. DECISA dall'utente il 2026-11-07: (a) cilindro invariato**, involucro conservativo del volume
del DES (era la raccomandazione). Esempio: ZSU-57-2, aereo a 3000 m a 3,5 km orizzontali dal sito: dentro il cilindro
(4 km), fuori dalla sfera ∩ fascia (2,65 km a quella quota): il pianificatore aggira o attraversa un volume in cui il
DES non sparera'; mai il contrario.

**VA-5 — Rilevamento. DECISA dall'utente il 2026-11-07: separare** (era la raccomandazione): qui solo l'ingaggio; il
rilevamento non sferico in una Proposta successiva. Esempio: un P-18 (EWR, `acquisition_range` 180 km,
`Asset/Vehicle_Data.py:4754`) vede nel DES un aereo a 50 m fino a 180 km (nessun orizzonte); il pianificatore lo
taglia all'orizzonte a circa 47,6 km (antenna `SENSOR_HEIGHT_EWR_M` = 20 m, stima [S] di D-4(a),
`Logic/Air_Route_Manager.py:670`); il registro dichiara anche un profilo portata-quota (`acquisition_profile`, 60 km a
500 m, `Asset/Vehicle_Data.py:4762`) che nessun modulo del core legge.

**VA-6 — Isolamento del volume proprio di rilevamento (`_own_intervals`). DECISA dall'utente il 2026-11-07: (a),
dentro il blocco 1 della FP** (era la raccomandazione). Scritta il 2026-11-07 in
`Proposta_Finestre_Per_Passaggio_Portata_Propria.md` §4.1.1 (punti 7 e 8-bis) e §4.1.5 (test 20): unico punto di
chiamata per `_own_passes`, `_pass_detection_time`, `_exposure_time` e il metodo esistente `_detection_time`; raggio
passato invariato (stessi float).

**VA-7 — Interruttore e tipo "volume". DECISA dall'utente il 2026-11-07**:
`Engagement_Resolver.VA_ENGAGEMENT_ALTITUDE_BAND = False` letto dal risolutore; nessun tipo "volume" generale (bastano
tre campi della `ShotSpec` e due funzioni di intervalli). Lettura del confronto: spento 1009 identiche + 32 nuove
(S34-BAND); acceso, atteso 1009 identiche (V-2).

**VA-8 — Scenario. DECISA dall'utente il 2026-11-07: S34-BAND, 6 varianti x 4 semi**, "da rivedere se VA-2 (d) cambia
le attese". Le cambia: con la (d) `descend_on` **non** e' piu' uguale a `descend_off` (l'Osa spara; §2.4).

**VA-8r — Scenario rivisto. DECISA dall'utente il 2026-11-07: la raccomandazione, 8 varianti x 4 semi = 32
esecuzioni nuove**: le 6
decise, con le attese corrette per la (d) (`descend_on` con salve dell'Osa in fascia), piu' `late_descend_off` e
`late_descend_on` (rilevamento a 6000 m, discesa dopo), le sole che distinguono VA-2.1 (i) da (ii). Esempio atteso:
`late_descend_on` con salve dell'Osa sotto i 5000 m dopo il rinvio, `late_descend_off` nessuna. Sostituisce la
versione a 6 varianti di VA-8.

---

## 4. Piano di intervento (scelte dell'utente del 2026-11-07: VA-1 sfera ∩ fascia, VA-2 (d), VA-2.1 (i) rinvio, VA-3 (b), VA-4 (a), VA-5 separare, VA-6 (a) nella FP, VA-7, VA-8r a 8 varianti)

Il piano implementa tutte le scelte dell'utente; nessuna decisione resta aperta. VA-6 (a) non e' in questo piano: e' gia' scritta nel blocco 1 della Proposta FP (§4.1.1 punti 7 e 8-bis,
test 20 di quella Proposta).

### 4.0 Precondizioni (l'esecutore le verifica e si ferma se mancano)

1. Branch di lavoro creato dalla sessione principale; working tree pulito; `git stash list` vuota.
2. **La Proposta BI (`Proposta_Bersagli_Intercettabili_Difesa_Aerea.md`, bersagli intercettabili dalla difesa aerea) e'
   eseguita e integrata** (ordine BI -> VA, §2.8 e BI §6.1): `ShotSpec` ha gia' in coda `intercept_domains`,
   l'interruttore `BI_AD_TARGET_RULE` esiste, `Scenario_Baseline.UNITS` ha gia' S35-ADTGT. Se non lo e', fermarsi.
3. Tutte le decisioni (VA-1..VA-8, VA-2.1, VA-8r) sono registrate come prese in questa Proposta (riga di stato).
4. Base: `bash tools/ai/verifica.sh suite` -> annotare `Ran B`; il confronto della base deve dare 1009 identiche + le
   nuove note (20 S32-DWELL, 32 S35-ADTGT; piu' S33-PASSES se la FP fosse gia' eseguita).
5. Le righe citate qui sono quelle del checkout del 2026-11-07 (`b20e39cf`): dopo la BI il risolutore e la fire control
   sono spostati. L'esecutore cerca **per nome** (`ShotSpec`, `engagement_intervals`, `_range_entry`, `_schedule_next`,
   `_in_range_at`, `_call_fire_control`, `_fire_control`, `accepts_target_grounded`, `shot_spec_for`,
   `make_registry_fire_control`, `restrict_by_policy`, `in_altitude_envelope`); se una firma e' diversa da quella
   citata, si ferma.

### 4.1 Blocco 1 — fascia nel tempo, quota all'istante di tiro, tetto delle armi d'aereo

#### 4.1.1 `Logic/Contact_Scheduler.py` (primitive della Attivita' D: fascia di quota e intersezione)

Dopo `_merge_intervals` (`:938-952`), due funzioni pubbliche:

```python
def altitude_intervals(legs_a: Sequence[Leg], legs_b: Sequence[Leg], z_min: Optional[float],
                       z_max: Optional[float], relative: bool = True) -> List[Tuple[float, float]]:
    """Intervalli in cui la quota di B e' in [z_min, z_max] (None = nessun limite da quel lato): RELATIVA ad A
    (z_b - z_a) se `relative`, ASSOLUTA (z_b) altrimenti; i tratti di A servono comunque a delimitare il tempo comune.
    Primitiva "fascia di quota" della Attivita' D (Piano_Lavori_2026_09_24.md): stessi sottointervalli a velocita'
    costante di `range_intervals` (`_breakpoints`), sui quali la quota e' lineare nel tempo, quindi ogni sottointervallo
    da' al piu' un intervallo; fusi con `_merge_intervals`.

    Raises:
        ValueError: z_min > z_max (entrambi dati).
    """
```

Comportamento: `overlap = _overlap(legs_a, legs_b)`; None -> `[]`. `lo, hi = overlap`; `breakpoints =
_breakpoints(legs_a, legs_b, lo, hi)`. Limiti: `low = -inf if z_min is None else z_min`, `high = +inf if z_max is
None else z_max`. `dz(t) = position_on_legs(legs_b, t)[2] - (position_on_legs(legs_a, t)[2] if relative else 0.0)`.
Con un solo breakpoint: `[(t, t)]` se `low <= dz(t) <= high`, altrimenti `[]` (stessa forma di `range_intervals`,
`:903-907`). Per ogni coppia `(u, v)`: `d0 = dz(u)`, `d1 = dz(v)`. Se `v - u <= TIME_EPS` oppure `d1 == d0`: quota
costante, si aggiunge `(u, v)` se `low <= d0 <= high`. Altrimenti `slope = (d1 - d0) / (v - u)`, `t_low = u + (low -
d0) / slope`, `t_high = u + (high - d0) / slope` (con un limite infinito il relativo istante e' +-inf), `s1 =
max(min(t_low, t_high), u)`, `s2 = min(max(t_low, t_high), v)`, si aggiunge `(s1, s2)` se `s2 >= s1`. Ritorno
`_merge_intervals(found)`. **Nessuna costante nuova** (non riusare `VELOCITY_EPS`, `:98`: e' una soglia su |Δv|² in
m²/s², non su una pendenza).

```python
def intersect_intervals(first: Sequence[Tuple[float, float]],
                        second: Sequence[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Intersezione di due liste ORDINATE di intervalli disgiunti (combinatore "intersezione" della Attivita' D).
    Due intervalli che si toccano entro TIME_EPS danno un intervallo di durata nulla."""
```

Comportamento: scansione a due indici; per ogni coppia `lo = max(a0, b0)`, `hi = min(a1, b1)`; se `hi >= lo -
TIME_EPS` si aggiunge `(lo, max(lo, hi))`; avanza l'indice dell'intervallo che finisce prima (a parita', entrambi);
ritorno `_merge_intervals(risultato)`.

#### 4.1.2 `Logic/Engagement_Resolver.py`

1. **Interruttore**, subito dopo `BI_AD_TARGET_RULE` (che la BI mette dopo `D5_DWELL_TIME`), testo esatto:

```python
# Quota nel volume d'ingaggio (Proposta_Allineamento_Volumi_DES_Pianificatore.md, VA), interruttore dedicato:
#   * `VA_ENGAGEMENT_ALTITUDE_BAND` (SPENTO). Acceso: (1) la fire control che dichiara la keyword `altitudes`
#     (introspezione, come `target_grounded`) riceve le quote di tiratore e bersaglio ALL'ISTANTE della decisione,
#     ricavate dai tratti, invece di leggere la posizione di partenza degli asset (VA-2 (d)); (2) il controllo di portata
#     vale nel tempo su sfera (max_range) ∩ fascia della ShotSpec: `min_altitude`/`max_altitude` RELATIVE al tiratore,
#     `max_target_z` ASSOLUTA (VA-1, VA-3 (b)); (3) un bersaglio aereo fuori fascia all'istante della decisione non
#     esaurisce il candidato se un'arma adatta entrera' in sfera ∩ fascia piu' tardi nella finestra d'ingaggio: la
#     decisione e' rinviata a quell'istante (VA-2.1 (i)). Spento: chiamate, chiavi e istanti di prima. Nessuna
#     estrazione nuova ne' spostata in nessuno dei due stati.
VA_ENGAGEMENT_ALTITUDE_BAND = False
```

2. **`ShotSpec`**: tre campi **in coda**, dopo `intercept_domains` della BI:

```python
    min_altitude: Optional[float] = None
    max_altitude: Optional[float] = None
    max_target_z: Optional[float] = None
```

   Docstring degli attributi: "min_altitude/max_altitude: fascia di quota del bersaglio RELATIVA al tiratore [m]
   (armi di superficie: registro 'm AGL' = sopra il sito, senza terreno); max_target_z: quota ASSOLUTA massima del
   bersaglio [m] (armi d'aereo: `max_height` del registro). Usati dal controllo di portata solo con
   `VA_ENGAGEMENT_ALTITUDE_BAND` acceso (v. "Quota nel volume d'ingaggio"); None = nessun limite." Validazione in
   `__post_init__`, dopo quella di `max_range` (`:659-662`): ciascuno None o numero (int/float) non booleano,
   altrimenti `ValueError` (stessa eccezione di `max_range`); se `min_altitude` e `max_altitude` sono entrambi dati e
   `min_altitude > max_altitude` -> `ValueError`. Valori negativi ammessi.

3. **Docstring del modulo**: dopo "Controllo di portata" (`:117-141`), sezione nuova "Quota nel volume d'ingaggio (VA,
   2026-11-xx)" con: i tre effetti dell'interruttore (punto 1); la regola unica "una sola disuguaglianza, due
   istanti": la fire control la valuta all'istante della decisione (sceglie l'arma), il risolutore la stessa sui
   tratti dall'istante della decisione in poi (sceglie l'istante di lancio), con gli stessi dati di registro copiati
   nella `ShotSpec`; il ripiego senza tratti (nessuna quota all'istante: chiamata e controllo di prima); l'allineamento
   per involucro col cilindro del pianificatore (§2.2); il limite "prima arma con scorta" (§5.2).

4. **`engagement_intervals`** (`:1731-1738`):

```python
def engagement_intervals(legs_shooter: Sequence, legs_target: Sequence, max_range: float,
                         band: Optional[Tuple[Optional[float], Optional[float], Optional[float]]] = None) -> IntervalList:
```

   `band` = `(min_altitude, max_altitude, max_target_z)`. Corpo: `intervals = range_intervals(legs_shooter,
   legs_target, max_range)`; se `band is None`: `return intervals` (identico a oggi). Altrimenti: se `band[0]` o
   `band[1]` non e' None, `intervals = intersect_intervals(intervals, altitude_intervals(legs_shooter, legs_target,
   band[0], band[1]))`; se `band[2]` non e' None, `intervals = intersect_intervals(intervals,
   altitude_intervals(legs_shooter, legs_target, None, band[2], relative=False))`; `return intervals`. Import da
   `Contact_Scheduler` di `altitude_intervals` e `intersect_intervals` accanto a `range_intervals` (`:467-474`).

5. **Introspezione** (vicino a `accepts_target_grounded`, `:1692-1714`):

```python
ALTITUDES_KEYWORD = 'altitudes'


def accepts_keyword(fire_control: Callable, name: str) -> bool:
    """True se la fire control accetta la keyword `name` (o `**kwargs`); firma non leggibile -> False."""
```

   Il corpo e' quello attuale di `accepts_target_grounded` con `name` al posto di `TARGET_GROUNDED_KEYWORD`;
   `accepts_target_grounded(fc)` diventa `return accepts_keyword(fc, TARGET_GROUNDED_KEYWORD)` (stesso risultato per
   ogni firma); nuova `accepts_altitudes(fc) -> bool: return accepts_keyword(fc, ALTITUDES_KEYWORD)`.

6. **`_EngagementRun.__init__`**, accanto a `self.engagement_intervals = engagement_intervals` (`:1859`):

```python
        # VA (VA_ENGAGEMENT_ALTITUDE_BAND, letto qui una volta: i test lo sostituiscono nel modulo): quota all'istante
        # per la fire control, fascia nel controllo di portata, rinvio fuori fascia.
        self.altitude_band = bool(VA_ENGAGEMENT_ALTITUDE_BAND)
        self.fire_control_knows_altitudes: Optional[bool] = None
```

7. **Metodi nuovi** (vicino a `_range_entry`):
   - `_band_of(self, spec) -> Optional[Tuple[...]]`: None se `not self.altitude_band` o se i tre campi sono None;
     altrimenti `(spec.min_altitude, spec.max_altitude, spec.max_target_z)`.
   - `_altitudes_at(self, shooter_id, target_id, time) -> Optional[Tuple[float, float]]`: None se `not
     self.altitude_band`, se la fire control non dichiara `altitudes` (`self.fire_control_knows_altitudes`, calcolato
     alla prima chiamata con `accepts_altitudes(self.fire_control)`), se manca uno dei due tratti o
     `position_on_legs` restituisce None; altrimenti `(float(z_tiratore), float(z_bersaglio))` da
     `position_on_legs(self.legs[id], time)[2]`.
8. **`_call_fire_control(self, shooter, target, time, altitudes=None)`** (`:2862-2887`): se `altitudes` e' None, si
   calcola `altitudes = self._altitudes_at(shooter.id, target.id, time)`. **Se resta None, il metodo esegue
   esattamente il codice di oggi** (stesse chiamate, stessi warning). Altrimenti si costruisce `kwargs = {'altitudes':
   altitudes}`, piu' `target_grounded=True` con la stessa regola di oggi per il bersaglio a terra (introspezione e
   warning invariati), e si chiama `self.fire_control(shooter.asset, target.asset, **kwargs)`. Docstring: "con VA
   acceso le quote sono quelle dei tratti all'istante `time` (della decisione); `altitudes=(None, None)` = quote
   ignote: la fire control non filtra per quota (politica gia' dichiarata in `Fire_Control`, "Quota")".
9. **`_fire_control(self, shooter, target, time, altitudes=None)`** (`:2846-2859`): inoltra `altitudes` a
   `_call_fire_control`; il resto invariato.
10. **`_range_entry`** (`:3011-3044`): firma `_range_entry(self, shooter_id, candidate, max_range, t_from,
    band=None)`. Chiave: `(shooter_id, candidate.target_id, float(max_range))` se `band is None` (**identica a
    oggi**), altrimenti `(shooter_id, candidate.target_id, float(max_range), band)`. Con i tratti: `band is None` ->
    `self.engagement_intervals(legs_shooter, legs_target, float(max_range))` (**3 argomenti, come oggi**: il test
    `test_geometry_is_isolated_and_replaceable` sostituisce la funzione con una a 3 parametri e deve restare verde);
    altrimenti `self.engagement_intervals(legs_shooter, legs_target, float(max_range), band=band)`. Senza tratti:
    `engagement_intervals_without_legs(...)` come oggi, la fascia **ignorata** (ripiego dichiarato).
    Annotazione di tipo da estendere: `range_cache` (`:1860`) dichiara `Dict[Tuple[str, str, float], ...]`; con la
    chiave allargata a `band` l'annotazione va estesa di conseguenza (chiave larga con `band`). Scelta minore per
    l'esecutore, da elencare nel rapporto.
11. **Chiamanti di `_range_entry`**: `_schedule_next` (`:2576`) e `_in_range_at` (`:2910`) passano
    `band=self._band_of(spec)`.
12. **Rinvio fuori fascia (VA-2.1 (i))**, metodo nuovo:

```python
    def _altitude_deferral(self, shooter: _Shadow, candidate: _Candidate,
                           t_fire: float) -> Tuple[Optional[float], Optional[Tuple[ShotSpec, int]]]:
        """VA-2.1: la fire control, con le quote all'istante `t_fire`, non ha armi per il bersaglio aereo. Se con le
        quote ignote (`altitudes=(None, None)`: nessun filtro di quota) qualche opzione con scorta entra in sfera ∩
        fascia nella finestra d'ingaggio, restituisce `(istante, None)` col primo di questi ingressi (> t_fire: la
        decisione si rinvia li') oppure `(None, (spec, colpi))` se l'ingresso e' gia' a `t_fire` (bordo della fascia:
        stessa disuguaglianza, arrotondamento diverso); `(None, None)` altrimenti (candidato esaurito come oggi)."""
```

    Corpo: `(None, None)` se `self._altitudes_at(shooter.id, candidate.target_id, t_fire)` e' None (VA spento, fire
    control che non conosce `altitudes`, tratti mancanti) o se il bersaglio non e' un aereo in volo a `t_fire`
    (`validate_class(target.asset, 'Aircraft')` e `not self.grounded.at(target_id, t_fire)`). Poi `result =
    self._fire_control(shooter, target, t_fire, altitudes=(None, None))`; per ogni `spec` di `self._options(result)`
    in ordine: scorta come in `_first_with_stock` (`stock = shooter.available(spec.weapon)`; colpi = `spec.rounds` se
    None, altrimenti `min(spec.rounds, stock // spec.stock_per_round)`; si salta se < 1); si salta se `spec.max_range`
    e' None; `entry = self._range_entry(shooter.id, candidate, spec.max_range, t_fire, band=self._band_of(spec))`. Il
    minimo degli `entry` non None e' `t_next`; nessuno -> `(None, None)`. Se `t_next > t_fire + TIME_EPS` ->
    `(t_next, None)`. Altrimenti `(None, (spec, colpi))` della **prima** opzione, nell'ordine, con `entry <= t_fire +
    TIME_EPS`. Nessuna estrazione.

    Uso in `_schedule_next` (`:2560-2566`), al posto del ramo `if choice is None:`:

```python
            if choice is None:
                # VA-2.1: fuori fascia all'istante, ma un'arma entrera' in sfera ∩ fascia piu' tardi -> rinvio.
                t_next, choice = self._altitude_deferral(shooter, candidates[index], t_fire)

                if t_next is not None:
                    candidates[index].not_before = t_next
                    continue

            if choice is None:
                # ROE o arma inadatta (None), oppure nessuna delle armi adatte ha piu'
                # scorta: questo bersaglio non verra' piu' ingaggiato da lui.
                candidates[index].exhausted = True
                continue
```

    Uso in `_in_range_at` (`:2899-2905`): se `choice` e' None, `_, choice = self._altitude_deferral(shooter,
    candidate, t_fire)`; se resta None -> `return False` (un rinvio NON e' "a portata adesso"). Nessuna mutazione del
    candidato in `_in_range_at`.

#### 4.1.3 `Logic/Fire_Control.py`

1. **`make_registry_fire_control`** (`:881-946`): la funzione interna diventa

```python
    def fire_control(shooter, target, target_grounded: bool = False,
                     altitudes: Optional[Tuple[Optional[float], Optional[float]]] = None) -> Optional[Tuple[ShotSpec, ...]]:
```

   e la lettura delle quote (`:933-934`) diventa: se `altitudes` e' None, `shooter_z = _z(shooter)` e `target_z =
   _z(target)` come oggi; altrimenti `shooter_z, target_z = altitudes` (ciascuno puo' essere None = ignoto); in
   entrambi i casi solo `if is_air or bomber` (come oggi; altrimenti None). **La chiave di memoizzazione resta
   `(shooter_key, keys, dimension, is_air, shooter_z, target_z)`** (`:935`), con le quote effettivamente usate: con
   `altitudes` sono quelle dell'istante. La memoizzazione resta esatta ("cambia solo le prestazioni, mai il
   risultato"): **nessun arrotondamento delle quote** nella chiave (cambierebbe i risultati). Effetto sulle prestazioni:
   per un aereo che cambia quota ogni decisione e' una chiave nuova (rank e `shot_spec_for` ricalcolati); per un aereo a
   quota costante la chiave si ripete (la quota interpolata su un tratto orizzontale e' esattamente quella dei punti).
   Misura della sonda V-2 in §1.7. Docstring di `make_registry_fire_control`: voce `altitudes` ("quote [m] di tiratore
   e bersaglio all'istante della decisione, passate dal risolutore con VA acceso; None = posizione degli asset, come
   prima; un elemento None = quota ignota, nessun filtro per quel confronto").
2. **`shot_spec_for`** (`:819-865`): parametro in coda `is_air` gia' presente; prima del `return`:

```python
    # VA: quota nel volume d'ingaggio, letta dal risolutore solo con Engagement_Resolver.VA_ENGAGEMENT_ALTITUDE_BAND
    # acceso. Armi di superficie contro aerei: fascia RELATIVA al tiratore (min/max_altitude del registro). Armi d'aereo
    # contro aerei: tetto ASSOLUTO (max_height del registro, km -> m); nessuna quota minima nel registro (VA-3 (b)).
    min_altitude = max_altitude = max_target_z = None

    if is_air and weapon.domain in ('ground', 'ship') and weapon.min_alt is not None and weapon.max_alt is not None:
        min_altitude, max_altitude = weapon.min_alt, weapon.max_alt
    elif is_air and weapon.domain == 'air':
        max_target_z = weapon.max_height_m
```

   e i tre argomenti passati al costruttore di `ShotSpec` (insieme a `intercept_domains` della BI).
3. **`restrict_by_policy`** (`:1001-1053`): deve dichiarare `target_grounded` e `altitudes` **solo se** la base li
   dichiara (altrimenti l'introspezione del risolutore cambierebbe per le fire control di test avvolte). Quattro
   varianti esplicite, scelte con `ER.accepts_target_grounded(fire_control)` e `ER.accepts_altitudes(fire_control)`:
   nessuna keyword (come oggi), solo `target_grounded` (come oggi), solo `altitudes`, entrambe. Ognuna inoltra alla
   base **solo** le keyword ricevute con valore diverso dal default (`target_grounded=True`, `altitudes` non None),
   cosi' la chiamata alla base e' identica a quella che il risolutore farebbe da solo; `restrict(...)` invariata.
   Docstring aggiornata.
4. **Docstring del modulo, "Quota"** (`:70-90`): "Il motore NON aggiorna `position`... la quota letta e' quindi
   quella di partenza" resta vero **a VA spento**; aggiungere: "con `VA_ENGAGEMENT_ALTITUDE_BAND` acceso il risolutore
   passa le quote all'istante della decisione (`altitudes`), e copia nella `ShotSpec` la fascia (armi di superficie) o
   il tetto (armi d'aereo) che verifica poi nel tempo".
5. `rank_weapons`, `in_altitude_envelope`, `select_weapon`, `target_key`: **invariati** (la disuguaglianza e' una
   sola, `in_altitude_envelope`; il risolutore ne usa la versione nel tempo con gli stessi dati).

#### 4.1.4 Effetti sui chiamanti [V, ricerca del 2026-11-07]

- Il solo chiamante della fire control e' il risolutore (`_call_fire_control`); `Session_Simulator` la avvolge una volta
  con `restrict_by_policy` (`Logic/Session_Simulator.py:2276-2282`) e la passa a `resolve_engagement`; nessun altro
  modulo la chiama (`Area_Fire` usa `plan_shot`).
- La fire control di test (`Test/Scenario_Fixtures.make_fire_control`, `SHOTS`) non dichiara `altitudes`: con VA
  acceso riceve la chiamata di sempre, nessun rinvio (`_altitudes_at` None), `ShotSpec` senza quote -> nessun effetto
  sulle 1132 run di ingaggio che la usano (V-0).
- `ShotSpec(` costruita a mano nei test e nelle fixture: i tre campi hanno default None, nessun chiamante cambia;
  nessun test confronta per uguaglianza una `ShotSpec` della fire control con una costruita a mano (ricerca del
  2026-11-07).
- `summarize_run` registra `weapon` delle salve, non la `ShotSpec`: nessuna voce nuova nella fotografia.
- `engagement_intervals` e' usata solo da `_range_entry` e dai test (`Test/Test_Engagement_Resolver.py:2009-2030`).
- Pianificatore, `Mobile.air_defense_volume`, `ThreatAA`, `Weapon_Delivery`, `Contact_Scheduler.contact_windows`:
  invariati (VA-4 (a)).

#### 4.1.5 Vincoli

- **RNG**: nessuna estrazione nuova ne' spostata (rinvio, quote e intervalli non chiamano `_draw`). Con VA acceso un
  tiro tolto, rimandato o reso possibile dal rinvio cambia le estrazioni **successive** di danno: e' l'effetto atteso.
- **VA spento = codice di prima**: `_altitudes_at` None -> `_call_fire_control` identico; `_band_of` None -> chiavi e
  chiamate di `_range_entry` identiche; `_altitude_deferral` restituisce `(None, None)` -> ramo `exhausted` identico;
  la fire control senza `altitudes` legge `_z` come oggi. Lo verificano i test 13-14 di §4.1.6.
- **Una sola disuguaglianza**: la fascia e il tetto della `ShotSpec` vengono dagli stessi campi di registro che
  `in_altitude_envelope` usa; nessuna costante di quota nuova. Il caso "bordo della fascia" (istante calcolato dal
  risolutore, quota interpolata appena fuori per arrotondamento) e' chiuso dal ramo `(None, (spec, colpi))` del rinvio,
  senza tolleranze di quota.
- **Determinismo**: nessun `set` o dizionario iterato in ordine non deterministico nelle funzioni nuove; il minimo degli
  ingressi a pari istante sceglie l'ordine di preferenza.
- **Core indifferente al simulatore**: nessun import dall'adapter DCS.

#### 4.1.6 Test del blocco 1 (23)

`Test/Test_Contact_Scheduler.py`, classe nuova `TestAltitudeIntervals` (logger mockato come nel file):
1. bersaglio che sale linearmente da 0 a 2000 m in 100 s contro tiratore fermo a z 0, fascia (500, 1500) ->
   `[(25.0, 75.0)]` (`assertAlmostEqual` sugli estremi);
2. quota relativa costante 1000 m: fascia (500, 1500) -> l'intero tempo comune; (1200, 1500) -> `[]`;
3. limiti None: (None, 1500) sul caso 1 -> `[(0.0, 75.0)]`; (500, None) -> `[(25.0, 100.0)]`;
4. rotta che sale e poi scende (due tratti) attraverso la fascia -> due intervalli; `z_min > z_max` -> `ValueError`;
5. tiratore che sale con il bersaglio (quota relativa costante): stesso risultato del caso 2; con `relative=False`
   conta la sola quota assoluta del bersaglio (tetto 1500 sul caso 1 -> `[(0.0, 75.0)]` anche col tiratore in salita).

`Test/Test_Contact_Scheduler.py`, classe nuova `TestIntersectIntervals`:
6. `[(0, 10), (20, 30)]` ∩ `[(5, 25)]` -> `[(5, 10), (20, 25)]`; liste vuote -> `[]`; contatto in 10 -> `[(10, 10)]`;
7. intersezione con una lista che copre tutto -> l'altra lista invariata.

`Test/Test_Engagement_Resolver.py`, classe nuova `TestEngagementAltitude` (fixture della classe del controllo di
portata, `:1960-2030`; interruttore con `patch.object(sys.modules[ER.__name__], 'VA_ENGAGEMENT_ALTITUDE_BAND', True)`
attorno alla chiamata, come S32 per `D5_DWELL_TIME`):
8. `ShotSpec`: `min_altitude=5.0, max_altitude=1.0` -> `ValueError`; `max_target_z=True` -> `ValueError`; default
   None accettati;
9. `engagement_intervals(legs_s, legs_t, R)` == `engagement_intervals(..., band=None)` == valore di oggi
   (`[(70.0, 100.0)]` su `self.LEGS['b1']`, `self.LEGS['r1']`); con una fascia relativa e con un tetto assoluto =
   intersezioni calcolate a mano;
10. `accepts_keyword`: una funzione con `altitudes` -> True per `altitudes`, False per `target_grounded`; con
    `**kwargs` -> True per entrambe; `accepts_target_grounded` invariata sui casi del test esistente;
11. **acceso, fascia relativa, bersaglio sempre sopra la fascia dentro la sfera** -> nessuna salva, candidato esaurito;
12. **acceso, bersaglio che entra nella fascia piu' tardi** (fire control che restituisce l'arma all'istante) ->
    `t_launch` = istante d'ingresso in sfera ∩ fascia;
13. **spento**: con una `ShotSpec` dotata di fascia mai rispettata la salva parte come oggi; la funzione sostituita di
    `engagement_intervals` riceve **3 argomenti** (spia come `test_geometry_is_isolated_and_replaceable`); una fire
    control che dichiara `altitudes` **non** la riceve;
14. **acceso con una fire control che NON dichiara `altitudes`** (firma `(shooter, target)`): chiamata a 2 argomenti,
    nessun rinvio; con `ShotSpec` senza quote l'esito e' identico a VA spento;
15. **acceso, `altitudes` all'istante**: una fire control spia che dichiara `altitudes` riceve, alla decisione,
    le quote di `position_on_legs` dei due tratti a `t_fire` (`assertAlmostEqual`), non quelle delle posizioni degli
    asset;
16. **acceso, tetto assoluto** (`max_target_z`): bersaglio che sale oltre il tetto prima di entrare nella sfera ->
    nessuna salva; sotto il tetto -> salva all'ingresso nella sfera;
17. **acceso, senza tratti**: ripiego di oggi, quote e fascia ignorate;
18. **acceso, `_in_range_at`**: un bersaglio fuori fascia a `t_fire` ma in fascia dopo -> `False` (rinvio non e' "a
    portata adesso") e il candidato non e' modificato;
19. **acceso, armi diverse**: la fire control all'istante scarta l'arma preferita fuori fascia e restituisce la
    seconda in fascia -> la salva usa la seconda (`salvo.spec.weapon`);
20. **rinvio (VA-2.1)**: fire control che all'istante restituisce None (quote dichiarate fuori fascia) e con
    `altitudes=(None, None)` un'arma; il bersaglio entra in sfera ∩ fascia a t = 120 s -> la salva parte a 120 s (non
    prima); la fire control e' stata richiamata a 120 s con le quote di quell'istante;
21. **rinvio impossibile**: con `altitudes=(None, None)` un'arma che non entra mai in sfera ∩ fascia nella finestra
    d'ingaggio -> candidato esaurito come oggi.

`Test/Test_Fire_Control.py`:
22. `shot_spec_for` contro un aereo: SAM terrestre (`9M33-SAM`) -> `min_altitude`/`max_altitude` dal registro
    (`GWD.GROUND_WEAPONS['MISSILES']['9M33-SAM']`, non scritti a mano), `max_target_z` None; SAM navale -> fascia dal
    registro navale; AAM (`AIM-9M`, `max_height` 18 km nel registro) -> `max_target_z == 18000.0` e fascia None; arma
    terrestre contro un bersaglio di superficie -> tre None;
23. `make_registry_fire_control` con `altitudes`: (i) `altitudes=None` -> stesso risultato e stessa chiave di cache di
    oggi (posizioni degli asset); (ii) `altitudes=(0.0, 6000.0)` contro l'Osa -> nessun `9M33-SAM`, `(0.0, 3000.0)` ->
    `9M33-SAM`; (iii) `altitudes=(None, None)` -> nessun filtro di quota; (iv) `restrict_by_policy` di una base che
    dichiara entrambe le keyword le dichiara e le inoltra, di una base che non le dichiara non le dichiara (le quattro
    varianti).

#### 4.1.7 Esito atteso del blocco 1

- Suite: `Ran B + 23`, `OK` (stessi `skipped` della base).
- Confronto: **1009 identiche**, 0 cambiate, nuove solo quelle gia' note (20 S32-DWELL, 32 S35-ADTGT).
- Fotografia mai reinstallata.

### 4.2 Blocco 2 — scenario S34-BAND

#### 4.2.1 `Test/Test_Session_Scenarios_S34.py` (nuovo, 9 test)

Struttura di `Test/Test_Session_Scenarios_S32.py` (setUpClass con ciclo esterno sui semi e interno sulle varianti,
spia su `ER.resolve_engagement`, `F.LoggerSilencer`). Geometria: una funzione `build(z0)` locale, copia di
`Test_Session_Scenarios_S19_Air_Defence.build` (`:71-78`) con il modello `'9A33-Osa'` in `(1_000.0, -300.0)` (la
posizione di S19 e S32) e la quota di partenza degli A-10C `z0` al posto dei 3000 m fissi; da S19 si importano
`IFV_IDS`, `MAVERICK`, `DURATION`, `VISUAL`. Linea Red di 3 BMP-2 e un `9A33-Osa`; 4 A-10C `Maverick/Gun CAS` da
`(-40_000.0, 0.0, z0)`, passo `(0.0, 500.0)`; missione CAS sui BMP-2 come S32 (`F.missions_for`, ROE
`only_designated`, `BOTH_HOLD`), fire control `make_registry_fire_control()`. Rotte (punti 3D, `route_for` accetta la
terza coordinata, `Test/Scenario_Fixtures.py:584`):

```python
SEEDS = [f'S34-BAND-{index}' for index in range(4)]
OSA = 'Red-Line/ad0'
# profilo -> (quota di partenza z0 [m], punti della rotta (x, y, z)). Geometria di TEST, non dati.
PROFILES = {
    'level':        (3_000.0, [(20_000.0, 0.0, 3_000.0)]),
    'climb':        (3_000.0, [(-20_000.0, 0.0, 6_000.0), (20_000.0, 0.0, 6_000.0)]),
    'descend':      (6_000.0, [(-20_000.0, 0.0, 3_000.0), (20_000.0, 0.0, 3_000.0)]),
    'late_descend': (6_000.0, [(-12_000.0, 0.0, 6_000.0), (-6_000.0, 0.0, 3_000.0), (20_000.0, 0.0, 3_000.0)]),
}
# variante -> (profilo, VA_ENGAGEMENT_ALTITUDE_BAND)
VARIANT_SPEC = {
    'level_off': ('level', False), 'level_on': ('level', True),
    'climb_off': ('climb', False), 'climb_on': ('climb', True),
    'descend_off': ('descend', False), 'descend_on': ('descend', True),
    'late_descend_off': ('late_descend', False), 'late_descend_on': ('late_descend', True),
}
```

Geometria [V sul registro, calcolo; da confermare con la sonda di geometria dell'esecutore]: 9M33 portata 10 km,
fascia 25-5000 m; radar dell'Osa 30 km (`Asset/Vehicle_Data.py:4144`).
- `climb`: a 6000 m la sfera e' attraversata fino a 8,0 km orizzontali, sempre sopra la fascia; la salita finisce a
  x = -20 km (oltre 21 km dal sito). Spento: filtro statico sulla partenza (3000 m) superato, salve a 6000 m. Acceso:
  all'istante della decisione la quota e' quella dei tratti; comunque entri il candidato, sfera ∩ fascia e' vuota ->
  **nessuna salva**.
- `descend`: la quota scende sotto i 5000 m a x = -33,3 km, cioe' a ~34 km dal sito, **prima** del rilevamento
  possibile (30 km): alla decisione l'A-10C e' gia' in fascia. Spento: filtro statico sulla partenza (6000 m) ->
  nessuna arma, **nessuna salva** (caso 3 di §1.2). Acceso: la fire control all'istante sceglie il 9M33, il tiro
  parte all'ingresso nella sfera a 3000 m (9,5 km orizzontali) -> **salve dell'Osa**; nessun rinvio necessario.
- `late_descend`: 6000 m fino a x = -12 km, discesa a 3000 m entro x = -6 km. La quota scende sotto i 5000 m a
  x = -10 km (11 km orizzontali dal sito, fuori dalla sfera); l'ingresso in sfera ∩ fascia e' a circa x = -8,3 km
  (quota ~4100 m, distanza 3D 10 km). La decisione dell'Osa (rilevamento + 26 s di reazione,
  `Context/Reaction_Profile.py:168`; A-10C a ~190 m/s [I sulla velocita' esatta]) cade sopra i 5000 m se il
  rilevamento avviene oltre ~16 km, cioe' per estrazioni `u <= ~0,96` (raggio estratto `30 x ((1-u)/0,5)^(1/4)` km).
  Spento: nessuna salva (filtro statico alla partenza, 6000 m). Acceso con il rinvio VA-2.1 (i): la fire control
  all'istante non ha armi, il rinvio porta la decisione all'ingresso in sfera ∩ fascia -> **salve dell'Osa** dopo il
  rinvio. Con VA-2.1 (ii) il candidato si esaurirebbe: nessuna salva.
- `level`: sempre in fascia: spento e acceso identici.

**Se la sonda di geometria dell'esecutore (prima del test 1) non da' salve dell'Osa in `climb_off` per almeno 3 semi
su 4, o da' un rilevamento dell'Osa in `descend` mentre l'A-10C e' sopra i 5000 m, o non da' in `late_descend_on`
almeno un rinvio (decisione dell'Osa con l'A-10C sopra i 5000 m) per almeno 3 semi su 4, fermarsi e riferire.**

Test:
1. `climb_off`: almeno una salva dell'Osa in almeno 3 semi su 4, e **ogni** salva dell'Osa ha il bersaglio a quota
   relativa > 5000 m all'istante di lancio (`Contact_Scheduler.position_on_legs` sui tratti, o quota della rotta);
2. `climb_on`: **nessuna** salva dell'Osa in nessun seme;
3. `level_off` e `level_on`: eventi di munizioni e di danno identici per seme;
4. `descend_off`: nessuna salva dell'Osa (filtro statico alla quota di partenza);
5. `descend_on`: almeno una salva dell'Osa in almeno 3 semi su 4, ogni salva con il bersaglio in fascia (25-5000 m
   relativi) ed entro 10 km;
6. `late_descend_off`: nessuna salva dell'Osa;
7. `late_descend_on`: almeno una salva dell'Osa in almeno 3 semi su 4; ogni salva dell'Osa parte con il bersaglio
   sotto i 5000 m relativi ed entro 10 km (cioe' dopo il rinvio, non al `t_ready` in quota);
8. determinismo: rieseguire `late_descend_on` del primo seme da' gli stessi eventi;
9. lo stream dell'ingaggio non cambia con l'interruttore in `level` (stesse `Detection`: `observer_id`, `draw`,
   `detected`).

#### 4.2.2 `Test/Scenario_Baseline.py`

- In `UNITS`, in coda (dopo S35-ADTGT della BI), nomi stabili:

```python
    # ── S34 (VA: quota nel volume d'ingaggio, Proposta_Allineamento_Volumi_DES_Pianificatore.md) — in coda ──
    ('S34-BAND', 'Test_Session_Scenarios_S34', 'TestS34AltitudeBand', None,
     _by_occurrence('level_off', 'level_on', 'climb_off', 'climb_on', 'descend_off', 'descend_on',
                    'late_descend_off', 'late_descend_on')),
```

- Docstring del modulo, dopo la sezione della BI:

```
## Quota nel volume d'ingaggio (VA)

La quota nel volume d'ingaggio (`Engagement_Resolver.VA_ENGAGEMENT_ALTITUDE_BAND`, SPENTO;
`Proposta_Allineamento_Volumi_DES_Pianificatore.md`) non cambia le esecuzioni esistenti (interruttore spento).
Aggiunge in coda l'unita' S34-BAND (8 varianti, 4 seed): 32 esecuzioni nuove; nessuna voce nuova nel riassunto.
```

#### 4.2.3 Vincoli del blocco 2

- L'ordine delle varianti in `VARIANT_SPEC` e in `_by_occurrence` coincide (la fotografia numera per occorrenza del
  `session_id`).
- L'interruttore e' sostituito con `patch.object(sys.modules[ER.__name__], 'VA_ENGAGEMENT_ALTITUDE_BAND', ...)` attorno
  all'intera esecuzione della variante (stesso schema di S32, `ER_MODULE`).
- Nessuna costante calibrata: quote e posizioni sono geometria di test, dichiarate tali nel docstring del modulo.

#### 4.2.4 Esito atteso del blocco 2

- Suite: `Ran B + 32`, `OK`.
- Confronto: **1009 identiche**, 0 cambiate, nuove: quelle note piu' **32 `S34-BAND/...`**.

### 4.3 Dopo i blocchi (sessione principale, non l'esecutore)

1. Sonda di accensione V-3 (da scrivere sul modello di `Rapporti/Sonde_Finestre_Passaggio/probe_switch_on.py`):
   accende in memoria `VA_ENGAGEMENT_ALTITUDE_BAND` e riesegue il confronto. **Atteso** (V-2, §1.7): **1009 identiche**. V-2
   non trova nessuna decisione della fire control che cambi con le quote all'istante (0 su 3091), nessun istante di
   tiro che cambi con sfera ∩ fascia o tetto (0 su 978 + 90), nessun bombardiere con quota di sgancio diversa, e i 48
   rinvii che il risolutore tenterebbe (14 esecuzioni: S19 `run`/`replay` 4, S21R 6, S31 `vads_high` 4) non trovano
   nessun ingresso in sfera ∩ fascia fino alla fine dei tratti (calcolo esatto, V-2b): stesso esito di oggi (candidato
   esaurito). Una riga CHANGED in V-3 e' fuori dall'atteso: fermarsi e riferire. S34 come da test.
2. Decisione dell'utente sull'accensione (non in questo piano) e, solo con sua decisione, nuova fotografia.

### 4.4 Tempi di verifica (ProArt, `tools/ai/verifica.sh`, mai in parallelo)

Suite ~10 minuti, confronto ~10 minuti per blocco; S34 aggiunge circa un minuto [I].

### 4.5 Scelte minori lasciate all'esecutore (da elencare nel rapporto)

Nomi locali e struttura interna dei test; il modo di ricavare la quota all'istante di lancio nei test di S34 (tratti
della sessione o quota della rotta); messaggi di log.

### 4.6 Dimensione [S]

Blocco 1: ~215 righe di codice (`Contact_Scheduler` ~60, risolutore ~110, fire control ~45, docstring a parte) e ~420
di test (23 test). Blocco 2: ~260 righe di test (9 test) e 8 righe in `Scenario_Baseline.py`. Totale ~215 + ~680.
Rispetto al piano con VA-2 (a) e VA-3 (a) (~110 + ~400, 21 test): circa il doppio del codice, per il protocollo
`altitudes`, le quattro varianti di `restrict_by_policy`, il rinvio e il tetto assoluto.

---

## 5. Rischi e limiti

### 5.1 Rischi che (d) e (b) aggiungono rispetto alle (a) raccomandate in prima stesura

- **Due punti per la stessa regola.** La disuguaglianza di quota e' valutata dalla fire control all'istante della
  decisione e dal risolutore nel tempo. Il piano li tiene coerenti (stessi dati, nessuna costante nuova, bordo chiuso
  dal rinvio), ma un cambio futuro a `in_altitude_envelope` (es. una quota minima per le armi d'aereo) va riportato in
  `shot_spec_for`/`_band_of`, altrimenti i due punti divergono. Mitigazione: test 22-23 e un commento incrociato nei due
  punti.
- **Protocollo della fire control allargato.** Una seconda keyword per introspezione (`altitudes`) e quattro varianti
  di `restrict_by_policy`: piu' casi da testare; una fire control futura che dichiari `**kwargs` ricevera' `altitudes`
  e deve gestirla.
- **Rinvio = un percorso nuovo nella schedulazione.** `_altitude_deferral` aggiunge chiamate alla fire control (una con
  quote ignote) e calcoli di intervalli per opzione; puo' rendere possibili tiri che oggi non esistono (caso 3), quindi
  con VA acceso cambia **piu'** esecuzioni della (a) (che poteva solo togliere o ritardare). Rischio di cicli: escluso
  per costruzione (il rinvio va a un istante > `t_fire` oppure sceglie subito un'arma), ma da verificare nei test 20-21.
- **Costo della memoizzazione.** Con le quote all'istante la chiave cambia per ogni decisione su un aereo che sale o
  scende: piu' calcoli di `rank_weapons` e `shot_spec_for` (balistica delle bombe per i bombardieri in salita/discesa)
  e una cache che cresce per sessione. V-2 misura il numero di chiavi distinte sulla fotografia (§1.7); il costo in una
  campagna con molte rotte a quota variabile **non e' misurato**.
- **Bombardieri**: con `altitudes` anche la quota di sgancio delle bombe (B6) diventa quella dell'istante; e' coerente
  (la fire control non mescola due quote per lo stesso colpo) ma estende l'effetto oltre la difesa aerea: un'esecuzione
  con un bombardiere che cambia quota puo' cambiare anche senza nessuna arma contraerea (V-2: `fc_bomb_alt_differs`).
- **Armi d'aereo** (VA-3 (b)): il tetto assoluto `max_height` del registro e' un dato per modello (18-30 km, §2.6) di
  qualita' non verificata qui; nessuna quota minima. Il controllo nel tempo cambia l'esito solo per bersagli che salgono
  sopra 18 km durante la finestra d'ingaggio, caso raro (V-2: `entry_differs_air`).
- **Limite residuo**: il rinvio considera l'ingresso piu' vicino fra le opzioni non filtrate, ma al momento del tiro
  vale ancora "prima arma con scorta" (`_first_with_stock`): se all'istante del rinvio la fire control restituisce piu'
  armi, spara la preferita, non quella che ha motivato il rinvio (coerente con la fire control, non un errore).

### 5.2 Limiti di modello (da dichiarare nel manuale)

- **Prima arma con scorta, senza ripiego per la portata**: fuori dal rinvio di quota, se l'arma preferita non entra
  mai nella propria sfera il candidato si esaurisce anche se un'altra arma potrebbe ingaggiare (limite di oggi,
  `_first_with_stock` `:2992-3009`).
- **Profilo d'inviluppo**: sfera ∩ fascia e' una prima approssimazione; gli inviluppi reali hanno portata ridotta a
  bassa quota e vicino al tetto e una zona morta interna [I]. Nessun dato nel registro.
- **Portata minima e cono di silenzio** non modellati (nessun dato): forme non convesse, da trattare con la Attivita' D
  (due intervalli per tratto).
- **Riferimento verticale**: quota relativa al tiratore (armi di superficie) o assoluta (armi d'aereo), senza
  terreno; `altitude_reference='AGL'` dei punti di missione non e' letto.
- **Pianificatore conservativo** (VA-4 (a)): negli angoli del cilindro vede pericolo dove il DES non spara.
- **Rilevamento** (VA-5): resta sferico nel DES e cilindrico nel pianificatore; la permanenza D-5 continua a divergere
  (§1.6).
- **Fire control di test non allineata**: le `ShotSpec` di `Scenario_Fixtures.SHOTS` non hanno portata ne' fascia e
  non dichiarano `altitudes`; nella fotografia producono 523 salve sopra il tetto del cilindro del pianificatore e
  1 238 oltre il raggio (V-0). La regola VA non le tocca; dar loro portata e fascia cambierebbe la fotografia
  (attivita' separata, decisione dell'utente).
- **Fascia/tetto senza portata, controllo solo all'istante**: una `ShotSpec` con fascia (`min_altitude`/`max_altitude`)
  o tetto (`max_target_z`) ma `max_range = None` non riceve alcun controllo nel tempo (il rinvio salta le opzioni senza
  `max_range`, §4.1.2 punto 12): la regola "una disuguaglianza, due istanti" vale solo all'istante della fire control.
  Non e' una regressione (meglio del filtro statico, che nel tempo non vede alcuna quota). Frequenza: il principale ha
  verificato che nei registri terrestri e navali (31 armi con fascia di quota) nessuna manca di portata; le armi
  aria-aria non sono state controllate [I].

### 5.3 Cosa non e' stato verificato

- Il comportamento effettivo del rinvio e dei tre profili di S34 **in sessione**: le attese di §4.2.1 vengono da calcolo
  geometrico e dalla lettura del codice, non da un'esecuzione (la sonda di geometria e' compito dell'esecutore).
- Il costo in tempo della memoizzazione con le quote all'istante (V-2 conta le chiavi, non misura il tempo).
- La qualita' dei `max_height` delle armi d'aereo rispetto a fonti esterne.
- La previsione di V-2 per il rinvio usa un campionamento di 40 istanti per candidato (`cand_static_excluded_dyn_ok`),
  non il calcolo esatto: un ingresso in fascia piu' breve del passo di campionamento sfuggirebbe.

---

## 6. Documenti da aggiornare dopo (non scritti qui)

- **Manuale DES** (`des-manual-writer`): cap. 4 §4.17 (controllo di portata: sfera ∩ fascia/tetto nel tempo,
  interruttore, ripiego senza tratti, rinvio), la sezione della fire control (quota all'istante con `altitudes`, campi
  della `ShotSpec`, `restrict_by_policy`), cap. 3 (primitive `altitude_intervals`, `intersect_intervals`), cap. 8
  (S34-BAND), cap. 9 (`10_Limiti_Estensioni_Divergenze.md`: i limiti di §5.2; la divergenza sfera/cilindro passa da
  "aperta" a "involucro conservativo" con l'interruttore acceso); atlante `11a_Atlante_Risolutore.md` (costante,
  `accepts_keyword`/`accepts_altitudes`, `_altitudes_at`, `_band_of`, `_altitude_deferral`, firme di
  `_range_entry`/`_call_fire_control`/`_fire_control`, campi di `ShotSpec`).
- **`F4_Differenze_Scenari.md`**: sezione "VA — quota nel volume d'ingaggio": 1009 identiche, 32 nuove di S34, esiti di
  V-0, V-1, V-2 e V-3.
- **`Piano_Implementazione_Missione.md`**: riga in §5 fuori numerazione F, come D-4b/D-4c e D-5, con lo stato
  dell'interruttore.
- **`Proposta_Volumi_Rilevamento_Intercettazione.md`** §5: nota di stato "lato DES dell'ingaggio: v. VA".
- **`Piano_Lavori_2026_09_24.md`** Attivita' D: stato (primitive fascia e intersezione fatte; volume di rilevamento da
  fare).
- **Memoria** (solo la sessione principale): decisioni VA, interruttore, esiti delle sonde.
