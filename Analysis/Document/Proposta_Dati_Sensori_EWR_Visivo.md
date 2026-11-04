# Proposta: dati dei sensori — radar EWR (D-4b) e sensore visivo di ripiego per ZSU-57-2 e M163 (D-4c)

**Stato**: DECISIONI PRESE dall'utente il 2026-11-04 (§3.1): 16 su 17 come raccomandato, la **12 diversa**
(`reliability` generica 45/4 invece di omessa). Il piano di §4 e' aggiornato di conseguenza (blocco B).
Analisi e proposta del 2026-11-04. Nessun file di codice
o di test modificato. Le sonde di §1.6 sono script di sola lettura nella scratchpad di sessione: modificano i
record del registro **in memoria** e rieseguono codice e test esistenti, senza toccare il repository.
**Origine**: `Proposta_Volumi_Rilevamento_Intercettazione.md` (D-1..D-7 implementate, commit `815dc35f`),
decisione D-4 punti (b) e (c). **Fonti**: `Ricerca_EWR_2026_10_29.md` e
`Ricerca_Sensore_Visivo_ZSU57_M163_2026_10_29.md` (commit `2b6a2c3a`), lette per intero.
**Fuori scope** (deciso, non si riapre): D-5 opzione 2 (`dwell_time_s`, cambia la legge del motore), D-7 seconda
parte (reti EWR→SAM, cueing), D-8.
**Vincolo di modello ribadito**: evitare il rilevamento NON equivale a evitare l'intercettazione. Il
sensore visivo e i radar EWR aggiungono volumi di RILEVAMENTO, non estendono nessun volume d'intercettazione
(§4.A.6, variante `vads_high`).
**Convenzioni**: **[V]** = verificato leggendo il codice (`file:riga`) o eseguendolo; **[S]** = stima o scelta
di progetto, mai dato tarato; **F/D/S** nelle tabelle dei valori = Fonte / Dedotto / Stima, come nelle due
ricerche. Percorsi di codice relativi a `Code/Dynamic_War_Manager/Source/`.

---

## 0. Sintesi

| Tema | Raccomandazione | Costo | Fotografia |
|---|---|---|---|
| D-4c, dove sta il sensore visivo | Campo nuovo `visual` nel registro, letto da `Mobile.detection_range` come terzo sensore, dietro l'interruttore `Mobile.D4C_VISUAL_SENSOR` | ~4 funzioni in 3 moduli + 2 record + scenario S31 | 989 identiche + 20 nuove (S31-VISUAL) |
| D-4c, valore | `acquisition_range` aria 6 km [S, confidenza bassa]; solo modo `air` | dati | — |
| D-4b, quali EWR | Nucleo di 8 radar mobili o semimobili (SCR-270, Freya, P-12, P-18, P-37, 1L13, 55Zh6, AN/TPS-43); i siti fissi restano rimandati | 8 record + 1 funzione d'appoggio | tutte identiche, nessuna nuova |
| D-4b, normalizzazione del combat score | Escludere la categoria EWR dalla popolazione **globale** del solo combat score (`get_normalized_combat_score`) | 1 metodo | nessun effetto (garantisce che non cambi nulla) |
| D-4b, curva portata-quota | Scalare alla quota di ~10 km (opzione (a) della ricerca); curva di fonte conservata come dato NON letto (`acquisition_profile`) | dati | — |

Due blocchi in sequenza: **A (D-4c)** cambia il codice di percezione ed entra nella fotografia; **B (D-4b)** è
quasi solo dati. Il blocco C (siti fissi) non è eseguibile da questo documento e richiede la decisione 14.

---

## 1. Problema e comportamento attuale

### 1.1 Dove si legge il sensore [V]

- **Schema del registro** (`Asset/Mobile.py:59-86`):
  `record.<sensore>['capabilities'][mode] = (bool, {'tracking_range', 'acquisition_range', 'engagement_range', 'multi_target_capacity'})`,
  portate in km. I sensori riconosciuti sono `DETECTION_SENSORS = ("radar", "TVD")` (`Asset/Mobile.py:80`).
- **Il punto unico di lettura** è `Mobile.detection_range(mode, sensor=None, range_type='acquisition_range') -> Optional[float]`
  (`Asset/Mobile.py:1559-1635`). Valida `sensor` contro `DETECTION_SENSORS` (`:1601-1602`). Compone i sensori col
  massimo (`:1623-1635`) e restituisce metri. `_sensor_range_km(data_record, sensor, mode, range_type)`
  (`:1521-1557`) legge un sensore con `getattr(record, sensor, None)` e restituisce None per ogni forma assente o
  nulla. Un record senza l'attributo (Ship_Data senza `TVD`) è già un caso normale.
- **Consumatori di `detection_range`** (ricerca di tutti gli usi):
  - DES: `Contact_Scheduler.mutual_detection_ranges` (`Logic/Contact_Scheduler.py:972-1020`, chiamata a `:1012`)
    produce le portate delle finestre di contatto; `Engagement_Resolver._air_detection_range`
    (`Logic/Engagement_Resolver.py:3052-3067`) serve alla geometria delle intercettazioni;
  - blocco: `Military.detection_range` (`Block/Military.py:773-803`), usato dalla potatura `block_reach`;
  - pianificatore: `build_detection_threat` (`Logic/Air_Route_Manager.py:726-779`), che scorre
    `('radar', 'TVD')` (`:754`). Per ogni sensore calcola `min(acquisition_range, orizzonte)`, con
    `EFFECTIVE_EARTH_RADIUS_FACTOR = {'radar': 4/3, 'TVD': 1.0}` (`:645`). Tiene il raggio effettivo maggiore con
    confronto stretto (`:764`): a parità vince il primo sensore del ciclo.
- **Il sensore `'visual'`** compare solo nel docstring di `DetectionThreat` (`Logic/Air_Route_Manager.py:295-296`):
  "previsto per i sensori visivi di ripiego, non ancora nei dati: decisione D-4(c)".

### 1.2 ZSU-57-2 e M163-VADS oggi [V]

- `ZSU_57_2_data` (`Asset/Vehicle_Data.py:3677-3724`) e `M163_VADS_data` (`:3785-3832`) hanno `'radar': False`,
  `'TVD': False` (`:3697-3698`, `:3805-3806`). Le armi ci sono: `S-68-57mm` (`range.direct` 4000 m, quota
  50-4000 m) e `M61-Vulcan-20mm` (1200 m, quota 0-1000 m) (`Asset/Ground_Weapon_Data.py:2254-2300`).
- **Pianificatore**: `build_detection_threat` restituisce None, cioè nessun volume di rilevamento. Lo fissa il test
  `Test/Test_Threat_AA_Factory.py:436-441` (`test_systems_without_sensor_data_give_none`).
- **DES: oggi questi due mezzi non sparano mai a un aereo.** `_detect_direction` esce **prima** di estrarre se
  `own_range` è None (`Logic/Engagement_Resolver.py:1988-1989`). Il candidato al tiro nasce solo per l'osservatore
  che ha rilevato (`:2021-2026`), quindi senza sensore proprio non c'è tiro. Lo conferma la sonda E-3 (§1.6):
  0 colpi in ogni seme.
- Nessuno scenario dei test né della fotografia usa ZSU-57-2 o M163-VADS. Gli unici riferimenti nei test sono il
  test del pianificatore sopra e `Test/Test_Air_Defense_Efficacy.py:234-238` (non emettono radar). Gli inventari di
  campagna li elencano (`Context/Initial_Context.py:464-466`, `Context/Actual_Context.py:386-388`), ma nessuno
  scenario li istanzia.

### 1.3 EWR oggi [V]

- La categoria esiste: `Ground_Vehicle_Asset_Type.EWR` (`Context/Context.py:751`), pesi EWR in `_combat_eval`
  (`Asset/Vehicle_Data.py:578-662`), `Vehicle.isEWR` (`Asset/Vehicle.py:298-299`), altezza d'antenna
  `SENSOR_HEIGHT_EWR_M = 20.0` [S] (`Logic/Air_Route_Manager.py:654-656`, `:717-721`).
- **Nessun record EWR** fra i 64 del registro: 18 Tank, 19 Armored, 12 Artillery_Semovent, 4 AAA, 8 SAM_Small,
  2 SAM_Medium, 1 SAM_Big (conteggio della sonda E-1). L'inventario di campagna EWR è vuoto
  (`Context/Initial_Context.py:469-470`).
- La catena per un sensore puro funziona già: la sonda E-4 ha registrato in memoria un P-18 come `Vehicle` reale in
  un `Military`. Risultati:
  - `isEWR` True;
  - `build_threat_aa` None, `air_defense_threats()` vuota;
  - `air_detection_threats(5000)` restituisce un volume;
  - raggio 59,7 / 110,6 / 180 km a 100 / 500 / 10 000 m;
  - `emits_radar` True, `sam_category` None, `air_defense_profile` None;
  - una sessione DES con un A-10C gira senza errori.

### 1.4 Effetti collaterali sugli score del registro [V, sonde E-1/E-5]

`Vehicle_Data` normalizza ogni score su **tutto il registro** (`_normalize`, `Asset/Vehicle_Data.py:1020-1036`;
tabella `VEHICLE`, `:4632-4652`). Fra gli score normalizzati **uno solo è consumato** fuori dai moduli dati: il
`'combat score'['global_score']`. Lo legge `Vehicle.set_combat_power` (`Asset/Vehicle.py:355`), quindi
`Military.combat_power`, `Tactical_Evaluation`, `Region` e `Combat_Power_Estimation._bucket_scores`
(`Context/Combat_Power_Estimation.py:61-117`). Per gli altri score (radar, weapon, TVD, mtbf/mttr, availability)
la ricerca di tutti gli usi non trova consumatori, né nel motore né in Block, Logic o Context.

Il **DES non legge la combat power**: nessun riferimento in `Session_Simulator`, `Engagement_Resolver`,
`Fire_Control`, `Damage_Model`, `Contact_Scheduler`, `Mission_Adapter`, `Session_Campaign`. Lo stesso vale per la
fotografia, che non la registra.

- **Il minimo globale del combat score è la ZSU-57-2** (0,2714; massimo T-90M 5,6567). Mettere il sensore nel
  `TVD` (che `_TVD_eval` legge, con peso 7 per AAA) alza il suo combat score e **sposta la normalizzazione
  globale di 63 modelli**. Lo stesso farebbe la `reliability` nel `TVD`, che entra in `_reliability_eval`.
- **Gli EWR del nucleo, con campi non-sensore stimati, scendono sotto quel minimo** in 6 casi su 8 (sonda E-5:
  Freya 0,15, P-37 0,20, 55Zh6 0,24, SCR-270 0,23, P-12 0,24, 1L13 0,26). Aggiunti così, diventerebbero il nuovo
  minimo e **cambierebbero la combat power di tutti i Vehicle**. Il motivo è che un EWR non ha armi né corazza:
  il suo combat score è basso per costruzione.

### 1.5 La curva portata-quota (punto aperto della ricerca, `Ricerca_EWR_2026_10_29.md:438-452`) [V]

`acquisition_range` è insieme la R della legge di Pd del DES e il raggio nominale del cilindro del pianificatore,
poi tagliato dall'orizzonte. La legge del DES è `Pd = f·(1 − 0,5·(d/R)⁴)`
(`Logic/Engagement_Resolver.py:454`, `:1041`).

**Il DES non ha orizzonte radar.** La ricerca di `horizon`/`orizzonte` in `Contact_Scheduler`,
`Engagement_Resolver` e `Session_Simulator` non trova nulla. L'orizzonte è solo nel pianificatore. Un R unico
alla quota di crociera **sovrastima** quindi la portata a bassa quota:
- nel pianificatore di circa 1,8 volte: P-18 a 500 m 110,6 km di orizzonte contro i 60 km della fonte;
- nel DES di più, perché lì non c'è alcun taglio.

È un limite da dichiarare (§5), non da risolvere qui.

### 1.6 Sonde eseguite (sola lettura, scratchpad di sessione)

| # | Cosa | Risultato |
|---|---|---|
| E-1 | Score del registro: min/max di `_combat_eval`, `_TVD_eval`, `_radar_eval`, mtbf, mttr | combat min ZSU-57-2 0,2714 / max T-90M 5,6567; radar max S-300PS 1,4175; mtbf 18,5-81,7; mttr 1,03-5,33 |
| E-2 | Suite completa (4710 test) con ZSU/M163 dotati di un `TVD` visivo e 2 EWR di prova, in memoria | `Ran 4710`, 1 solo fallimento: `test_systems_without_sensor_data_give_none` (atteso); skipped 7 |
| E-3 | Scenario S19AD con ZSU-57-2 e M163 al posto della difesa, sensore emulato in memoria, 4 semi | ZSU senza sensore 0 colpi, con sensore 550 colpi e 1 perdita Blue; M163 a 3000 m: 0 colpi con e senza sensore (sopra i 1000 m dell'arma); M163 con A-10C a 500 m: 0 senza, 2650 colpi e 2 perdite con sensore |
| E-4 | EWR di prova come `Vehicle` reale (pianificatore, ADE, sessione DES) | v. §1.3 |
| E-5 | `_combat_eval` degli 8 EWR del nucleo con il modello di campi di §4.B.2 | 6 su 8 sotto il minimo del registro (v. §1.4) |

---

## 2. Alternative e raccomandazione

### 2.1 D-4c: dove mettere il sensore visivo

| | V1: dati nel `TVD` esistente | **V2: nuovo campo `visual`** (raccomandata) | V3: AN/VPS-2 come `radar` |
|---|---|---|---|
| Codice | nessuno | `Vehicle_Data.__init__` (+1 argomento), `Mobile` (+1 sensore, interruttore), `Air_Route_Manager` (+1 sensore nel ciclo e nel fattore k) | nessuno |
| Semantica | il `TVD` è un dispositivo ottico/termico; l'occhio dell'equipaggio no | onesta: scoperta a occhio nudo | **sbagliata**: il VPS-2 misura solo la distanza, non scopre (ricerca §2.3) |
| Score del registro | **spostati per 63 modelli**: la ZSU è il minimo globale del combat score (§1.4) | invariati: `_TVD_eval`/`_radar_eval`/`_reliability_eval` non leggono `visual` | invariati per lo score, ma l'M163 diventerebbe un emettitore (`_has_air_radar`) |
| RWR / ADE | invariati | invariati | l'M163 entra nel catalogo RWR VSHORAD (`default_rwr_catalogue`, `Context/Air_Defense_Efficacy.py:683-703`): **cambiano i pesi di classe** e i test `Test_Air_Defense_Efficacy.py:234-238`, `:286-296` |
| Interruttore | impossibile (dato puro) | `D4C_VISUAL_SENSOR`, spento = comportamento precedente | impossibile |
| Degradazioni future per sensore (notte, meteo) | il visivo resta confuso con il TVD | il sensore è separabile (`sensor='visual'`) | — |
| Pianificatore | k = 1 come il TVD | k = 1 dichiarato per `visual` | k = 4/3, sbagliato per un sensore visivo |

**Raccomandazione: V2.**
- V1 cambia senza dirlo la combat power di tutti i Vehicle e non si può spegnere.
- V3 descrive male il mezzo e sposta la fotografia (pesi di classe RWR).
- V2 costa poco codice, isola l'effetto ai due record e lascia il sensore separabile per la futura
  degradazione notturna.

### 2.2 D-4c: valore della portata visiva

| Opzione | Valore | Base | Note |
|---|---|---|---|
| **a** (raccomandata) | 6 km | ricerca §3: Howell (DC-3, osservatore vigile 17-23 km, piloti 5,5-8,7 km) riportato in scala alle dimensioni di un caccia, fattore ~0,3 | [S] confidenza bassa; intervallo plausibile 3-8 km |
| b | 8 km | coerenza con `Optical sight` dello Strela-1 (`Asset/Vehicle_Data.py:3975-3983`) | quel valore non ha fonte nota |
| c | 4 km | scelta prudente (scala dei piloti) | sotto la portata dell'arma della ZSU (4 km): la ZSU vedrebbe solo quando è già a tiro |

### 2.3 D-4b: normalizzazione globale del combat score

| | G1: accettare lo spostamento | **G2: EWR fuori dalla popolazione globale del combat score** (raccomandata) | G3: ritoccare i campi stimati finché rientrano |
|---|---|---|---|
| Effetto | la combat power di tutti i Vehicle si riscala (~2 %), senza effetti su DES e fotografia | nessun numero esistente cambia, per costruzione | nessun numero cambia |
| Codice | nessuno | `get_normalized_combat_score`, ~6 righe | nessuno |
| Difetto | effetto silenzioso su Tactical/Region/Combat_Power_Estimation | asimmetria: SAM e AAA restano nella popolazione | **adattare valori inventati a un invariante è peggio che inventarli** |

**Raccomandazione: G2.**
- La combat power degli EWR è 0 per definizione (`Context/Context.py:775-777`): non sono popolazione di
  combattimento. Lo stesso criterio lo usa già `Combat_Power_Estimation`, che esclude le classi senza efficacia
  dalla mediana globale.
- Senza record EWR la modifica non cambia nulla, quindi riproduce esattamente il comportamento precedente.
- Interruttore non necessario, ma disponibile su richiesta (decisione 9).

### 2.4 D-4b: mappatura della portata (ricerca §5.2.1)

| Opzione | Contenuto | Pro | Contro |
|---|---|---|---|
| **(a)** (raccomandata) | un R alla quota di ~10 km contro un caccia, quando la fonte lo dà; altrimenti il massimo non qualificato, marcato | semplice, coerente con l'orizzonte del pianificatore | sovrastima a bassa quota (§1.5) |
| (b) | media fra le quote | meno sovrastima in basso | sottostima in quota; nessuna fonte la usa |
| (c) | curva portata-quota nello schema, letta da DES e pianificatore | fisica corretta | cambia la legge del motore: **Proposta a parte** |

In aggiunta ad (a), si raccomanda di conservare la curva di fonte come dato NON letto (`acquisition_profile`,
decisione 8). Così (c) partirà dai numeri già in registro.

### 2.5 D-4b: quali radar

| Opzione | Contenuto |
|---|---|
| **N** (raccomandata) | Nucleo di 8 radar mobili o semimobili, uno o più per blocco ed epoca: SCR-270 (USA, 1940), FuMG 80 Freya (Germania, 1938), P-12 (URSS, 1956), P-18 (URSS, 1970), P-37 (URSS, 1961), 1L13 (URSS, 1984; unità DCS "1L13 EWR"), 55Zh6 (URSS, 1986; unità DCS "55G6 EWR"), AN/TPS-43 (USA, 1968) |
| N+C | Nucleo più i siti fissi (Chain Home, AMES Type 7, AMES Type 80, AN/FPS-20, AN/FPS-117, P-14, Wassermann, Mammut): serve prima decidere come si modella un'installazione fissa (decisione 14) |
| DCS | Solo 1L13 e 55Zh6 |

Esclusi in ogni caso, con il motivo della ricerca:
- Chain Home Low: portata non trovata;
- Würzburg: radar GCI/di tiro;
- P-15/P-19: fonti deboli o da gioco; il P-19 è il radar di scoperta dell'S-125, assente dal registro;
- Nebo-SVU/Nebo-M: fuori periodo.

---

## 3. Decisioni da prendere (per l'utente)

Ogni decisione ha una raccomandazione. Il piano di §4 è scritto per le opzioni raccomandate. Dove un'opzione
diversa cambia il piano, la differenza è indicata.

**Blocco A (D-4c)**
1. **Sede del sensore visivo**: V2 campo `visual` (racc.) / V1 `TVD` / V3 `radar`. Con V1 il blocco A si
   riduce ai soli dati e allo scenario, senza interruttore e senza le varianti `_off`, e la combat power di 63
   modelli cambia.
2. **Portata visiva**: 6 km (racc.) / 8 km / 4 km. Stesso valore per ZSU-57-2 e M163.
3. **Modi**: solo `air` (racc.) / anche `ground`. Il valore a terra non è stato trovato: sarebbe una STIMA di
   5 km per entrambi, e creerebbe un comportamento nuovo nel DES (AAA che scopre e ingaggia mezzi terrestri),
   non richiesto.
4. **Default dell'interruttore `D4C_VISUAL_SENSOR`**:
   - True (racc.): è la prassi degli interruttori F6-F8 (`Logic/Session_Simulator.py:807-908`), "ATTIVO, spento
     = come prima". Riproduce il comportamento precedente su **tutte** le esecuzioni esistenti, perché nessuna
     usa i due modelli;
   - False: lettera di `AGENTS.md` ("il cui default riproduce il comportamento precedente"). Il dato resta
     dormiente finché non si accende, e S31 lo accende esplicitamente.
5. **Scenario S31-VISUAL nella fotografia**: sì, 20 esecuzioni nuove (racc.) / solo test fuori dalla fotografia.

**Blocco B (D-4b)**
6. **Insieme dei radar**: nucleo N (racc.) / N+C / solo DCS.
7. **Mappatura di `acquisition_range`**: (a) (racc.) / (b) / (c) in Proposta separata.
8. **Curva di fonte come dato non letto** `acquisition_profile`: sì (racc.) / solo commento.
9. **Normalizzazione del combat score**: G2 (racc.) / G1 / G2 con interruttore.
10. **`tracking_range` degli EWR**:
    - 0 (racc.): nessuna traccia di tiro, nessuno lo legge;
    - uguale ad `acquisition_range`: il precedente dell'AWACS E-3A (400/400, `Asset/Aircraft_Data.py:2144`). Da
      rivedere con D-7.
11. **`multi_target_capacity`**:
    - 0 = "non trovato" (racc.), salvo P-18 = 10 [F]. 0 è la forma che il codice già tratta come assente:
      `_sensor_range_km` restituisce None per valori ≤ 0;
    - in alternativa 1 come segnaposto.
12. **`reliability` del radar**:
    - omessa quando mtbf e mttr non sono **entrambi** di fonte (racc.: nel nucleo nessun record li ha entrambi;
      P-18 140 h e 55Zh6 >250 h restano in commento);
    - in alternativa un valore generico del registro (45/4), che sarebbe una stima.
13. **Campi non-sensore stimati** (dimensioni, costo, autonomia, velocità, comunicazioni): modello per classe di
    mobilità, tutto [S] e dichiarato in un solo punto (racc., §4.B.2) / valori forniti dall'utente.
14. **Siti fissi (blocco C)**:
    - rimandati (racc.). Un sito fisso come `Vehicle` richiede `range` > 0, imposto dal test
      `Test/Test_Vehicle_Data.py:318-322`, e velocità 0: serve una scelta di modello (Vehicle immobile oppure
      Structure con sensore);
    - in alternativa inclusi ora come Vehicle a velocità 0 con autonomia segnaposto.
15. **55Zh6**:
    - incluso con 400 km a 20 km di quota (racc., confidenza media-bassa, possibile confusione 55Zh6/Nebo-U nella
      fonte);
    - in alternativa escluso.
16. **Altezza d'antenna da fonte**: solo SCR-270, 16,8 m [D, 55 ft] (racc.); gli altri usano il default EWR di
    20 m [S] / tutti a 20 m.
17. **Inventari di campagna** (`Initial_Context`/`Actual_Context`, `ag.EWR.value: {}`): restano vuoti (racc.:
    il bilanciamento di campagna è un'altra decisione) / popolati.

### 3.1 Decisioni dell'utente (2026-11-04)

Prese una per una. Tutte come raccomandato **tranne la 12**.

| N. | Scelta |
|---|---|
| 1 | V2: campo `visual` |
| 2 | 6 km (stima, confidenza bassa) |
| 3 | solo modo `air` |
| 4 | `D4C_VISUAL_SENSOR` default **True** (prassi F6-F8) |
| 5 | S31-VISUAL nella fotografia (20 esecuzioni nuove) |
| 6 | nucleo N, 8 radar |
| 7 | (a) R alla quota di ~10 km |
| 8 | `acquisition_profile` conservato come dato non letto |
| 9 | G2: categoria EWR fuori dalla popolazione globale del combat score, senza interruttore |
| 10 | `tracking_range` = 0 |
| 11 | `multi_target_capacity` = 0 (P-18 = 10) |
| **12** | **DIVERSA dalla raccomandazione: `reliability` generica del registro, mtbf 45 / mttr 4, per tutti gli 8 radar, dichiarata [S]** |
| 13 | campi non-sensore per classe di mobilita', tutti [S], in `_ewr_support_fields` |
| 14 | siti fissi (blocco C) rimandati |
| 15 | 55Zh6 incluso |
| 16 | `antenna_height` da fonte solo per SCR-270 (16,8 m) |
| 17 | inventari di campagna EWR vuoti |

**Conseguenze della decisione 12 sul piano** (sostituiscono dove il testo di §4.B dice "reliability omessa"):
- ogni record radar ha `'reliability': {'mtbf': 45, 'mttr': 4}` con commento obbligatorio "STIMA [S]: valore generico del
  registro, non dato di fonte; nessun dato di fonte per questo modello";
- i valori di fonte (P-18 MTBF 140 h, 55Zh6 MTBCF >250 h) restano **solo nel commento**, non nel campo: non si
  mescolano un MTBF di fonte e un MTTR stimato nello stesso record;
- il test 6 diventa `test_reliability_is_the_declared_generic_estimate`: `radar['reliability'] == {'mtbf': 45, 'mttr': 4}`
  per tutti e 8;
- il record `communication` degli EWR puo' restare com'e' (la sua `reliability` 45/3 non serve piu' a evitare la lista
  vuota di `_reliability_eval`): l'esecutore sistema la nota di §4.B.1 di conseguenza;
- l'esecutore verifica, con il confronto, che la `reliability` del radar non abbia consumatori sugli asset
  (atteso: confronto con tutte le esecuzioni identiche, nessuna nuova). Se il confronto cambia, si ferma e riferisce;
- la voce "reliability" degli score globali (§5.2 punto 8) si sposta comunque: e' gia' prevista.

---

## 4. Piano di intervento

### Blocco A — D-4c, sensore visivo (opzioni raccomandate 1-5)

**Esecutore suggerito**: `des-developer`, Sonnet, sforzo alto. Il blocco tocca tre moduli del core e aggiunge
un'unità alla fotografia. Alternativa: `oc-developer` (DeepSeek V4 Pro high).
**Dimensione stimata**: ~60-90 righe di codice e dati, ~250-300 righe di test (modulo nuovo S31 compreso).

#### A.1 `Asset/Vehicle_Data.py`
- `Vehicle_Data.__init__` (`:65`): aggiungere l'ultimo argomento keyword `visual: Optional[Dict] = None` e
  `self.visual = visual` accanto a `self.TVD` (`:93`). Docstring o commento: "sensore visivo dell'equipaggio
  (D-4c): stessa forma di `radar`/`TVD`, nessuna `reliability`; NON entra negli score (`_TVD_eval`,
  `_radar_eval`, `_reliability_eval`, `_combat_eval`)".
- Nessuna modifica a `_TVD_eval`, `_radar_eval`, `_reliability_eval`, `_maintenance_eval`, `_combat_eval`.
- `ZSU_57_2_data`: lasciare `'radar': False` e `'TVD': False`; aggiungere dopo `'TVD'`:
  ```python
  # D-4c (Proposta_Dati_Sensori_EWR_Visivo.md, Ricerca_Sensore_Visivo_ZSU57_M163_2026_10_29.md): nessun radar ne'
  # mirino strumentale di scoperta [FONTE, conf. alta]; scoperta SOLO a vista dell'equipaggio (torretta aperta).
  #   acquisition_range 6: STIMA (conf. bassa) -- Howell (DC-3) in scala alle dimensioni di un caccia, intervallo 3-8 km;
  #   tracking_range 5.5: FONTE (Wikipedia, portata obliqua massima del mirino automatico; pagina con tag di accuratezza), conf. media;
  #   engagement_range 4: FONTE (museo finlandese, valka.cz), conf. media; multi_target_capacity 1: un solo mirino (dedotto).
  # Solo cielo sereno e giorno nelle fonti: notte/meteo NON modellati per sensore (limite noto).
  'visual': {
      'model': 'Crew visual observation + analog reflex sight',
      'capabilities': {
          'air': (True, {'tracking_range': 5.5, 'acquisition_range': 6, 'engagement_range': 4, 'multi_target_capacity': 1}),
          'ground': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
          'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
      },
  },
  ```
- `M163_VADS_data`: lasciare `'radar': False` (l'AN/VPS-2 misura solo la distanza, non scopre) e `'TVD': False`;
  aggiungere:
  ```python
  # D-4c: l'AN/VPS-2 e' un radar di sola distanza (range-only) [FONTE, conf. alta]: non scopre, quindi NON e' `radar`.
  # Scoperta a vista del puntatore (torretta aperta).
  #   acquisition_range 6: STIMA (conf. bassa), come la ZSU-57-2;
  #   tracking_range 5: FONTE (portata del VPS-2 contro 1 m2, AFV Database + weaponsystems.net), conf. media -- 7 km di
  #   War Thunder scartato; engagement_range 1.2: FONTE (HEI-T-SD M246, Wikipedia), conf. media; multi_target_capacity 1.
  'visual': {
      'model': 'Crew visual observation + M61 lead-computing sight (AN/VPS-2 range-only radar for ranging)',
      'capabilities': {
          'air': (True, {'tracking_range': 5, 'acquisition_range': 6, 'engagement_range': 1.2, 'multi_target_capacity': 1}),
          'ground': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
          'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
      },
  },
  ```
  Nel nome del modello non scrivere "gyro": la denominazione è contraddittoria fra le fonti.

#### A.2 `Asset/Mobile.py`
- Commento di schema (`:59-86`): aggiungere `visual` fra i sensori, con la nota "solo Vehicle_Data; assente negli
  altri registri (caso normale)".
- `VISUAL_SENSOR = "visual"`; `DETECTION_SENSORS = ("radar", "TVD", VISUAL_SENSOR)`. L'**ordine** va mantenuto:
  radar e TVD restano primi, quindi a parità di raggio il risultato dei record esistenti non cambia.
- Interruttore, subito sotto, nello stile di `Logic/Session_Simulator.py:897-902`:
  ```python
  # D-4c, sensore visivo di ripiego (Proposta_Dati_Sensori_EWR_Visivo.md), interruttore dedicato:
  #   * `D4C_VISUAL_SENSOR` (ATTIVO): il sensore `visual` dei registri (scoperta a occhio dell'equipaggio, per i mezzi
  #     senza radar ne' TVD di scoperta: ZSU-57-2, M163-VADS) entra in detection_range come terzo sensore, composto col
  #     massimo come radar e TVD; lo leggono quindi DES (finestre di contatto) e pianificatore (DetectionThreat).
  #     Spento: detection_range ignora `visual` (None se chiesto esplicitamente), come prima della D-4c. Nessuno
  #     scenario precedente usa i due modelli, quindi con l'interruttore acceso nessuna sessione precedente cambia.
  D4C_VISUAL_SENSOR = True
  ```
  Il default è `True` se la decisione 4 resta come raccomandata, altrimenti `False`.
- `detection_range` (`:1559-1635`):
  - la validazione `sensor not in DETECTION_SENSORS` (`:1601`) resta, e ora accetta `'visual'`;
  - dopo `sensors = (sensor,) if sensor is not None else DETECTION_SENSORS` (`:1623`):
    ```python
    if not D4C_VISUAL_SENSOR:
        sensors = tuple(s for s in sensors if s != VISUAL_SENSOR)
    ```
    La variabile va letta a ogni chiamata come globale di modulo: i test la sostituiscono con `patch.object`. Una
    tupla vuota porta al ramo "nessun raggio", che già restituisce None con un log di debug (`:1629-1633`);
  - docstring: `sensor` accetta `'radar'/'TVD'/'visual'`; composizione "massimo dei tre"; riferimento
    all'interruttore.
- `engagement_channels` (`:1637-1679`): **nessuna modifica**. Legge solo il `radar`.

#### A.3 `Logic/Air_Route_Manager.py`
- `EFFECTIVE_EARTH_RADIUS_FACTOR = {'radar': 4.0 / 3.0, 'TVD': 1.0, 'visual': 1.0}` (`:645`). Nel commento sopra
  (`:638-640`): "visual: linea di vista geometrica come il TVD, STIMA DICHIARATA; con 6 km l'orizzonte non limita
  mai (antenna di default 5 m, bersaglio a 30 m: 27,5 km)".
- `build_detection_threat`, ciclo (`:754`): `for sensor in ('radar', 'TVD', 'visual'):`. Tupla letterale, nello
  stesso ordine di `Mobile.DETECTION_SENSORS`, **senza importare Mobile a livello di modulo**: è il ciclo d'import
  noto, e la coerenza la verifica un test.
- `sensor_antenna_height(asset, sensor)` (`:699-723`): **nessuna modifica**. Legge `getattr(record, 'visual')`;
  senza `antenna_height` vale il default del veicolo, 5 m [S].
- Docstring:
  - `DetectionThreat` (`:295-296`): `sensor: 'radar' | 'TVD' | 'visual'` (visivo di ripiego, D-4c);
  - `build_detection_threat` (`:738-742`): togliere l'esempio "ZSU-57-2 e M163-VADS, senza sensori" e scrivere
    "nessun `acquisition_range` aria utilizzabile (es. un carro senza sensori aria, o i mezzi a vista con
    `Mobile.D4C_VISUAL_SENSOR` spento)".
- `build_air_defense_threats`, `ThreatAA`, `calcRoute`: nessuna modifica.

#### A.4 Effetti sugli altri moduli e sui chiamanti (tutti gli usi di `detection_range`, `DETECTION_SENSORS`, `sensor`)
| Chiamante | Effetto |
|---|---|
| `Contact_Scheduler.mutual_detection_ranges` (`:1012`) | ZSU/M163 come osservatori: portata 6000 m contro aerei (prima None); contro terra e mare resta None |
| `Engagement_Resolver._detect_direction` (`:1986-2031`) | per ZSU/M163 nasce un'estrazione RNG in più per finestra con aereo, perché prima usciva a `:1988-1989` prima dell'estrazione a `:2001`. Lo stream cambia **solo nelle sessioni con questi modelli** |
| `Engagement_Resolver._air_detection_range` (`:3052-3067`) | portata 6000 m; serve solo agli intercettori (task `Anti_Missile`), che ZSU e M163 non sono |
| `Military.detection_range` (`Block/Military.py:773-803`) | la stessa composizione; `block_reach` dei blocchi con questi mezzi cresce a 6 km |
| `build_detection_threat` | `DetectionThreat(sensor='visual')`, raggio 6000 m a ogni quota ≥ 0 |
| `Air_Defense_Efficacy` (`emits_radar`, `_director`, catalogo RWR) | nessuno: leggono il solo `radar` |
| `Vehicle_Data` score, tabella `VEHICLE`, `Combat_Power_Estimation` | nessuno (sonda E-1: `_TVD_eval` e `_radar_eval` non leggono `visual`) |
| `Test/Scenario_Fixtures.declare_sensor` (`:271-303`) | invariato: delega al registro con `sensor=sensor`; nessun mezzo degli scenari esistenti ha `visual` |
| `Ship_Data`, `Aircraft_Data` | nessuno: niente attributo `visual`, `getattr` restituisce None |
| `Test/Test_Mobile.py` `_SensorRecord` (`:1131-1135`) | nessun attributo `visual`, quindi None: i test esistenti restano validi |

Vincoli:
- **determinismo**: nessuna estrazione nuova fuori dalle sessioni con ZSU-57-2/M163; nessun uso del modulo
  `random`;
- **core indifferente al simulatore**: nessun riferimento a DCS;
- nomi delle chiavi del registro invariati (`'ZSU-57-2'`, `'M163-VADS'`).

#### A.5 Test (blocco A)
Stile: classi `unittest.TestCase` per i test; classi base condivise NON TestCase. Logger mockati come nei file di
destinazione (`patch(_MOBILE_LOGGER, MagicMock())` in `Test_Mobile.py`; `F.LoggerSilencer` negli scenari).

`Test/Test_Mobile.py`: estendere `_SensorRecord.__init__(self, radar=False, TVD=False, visual=None)`, che
assegna `self.visual = visual`. Nuova classe `TestDetectionRangeVisualSensor`, con setUp e tearDown come
`TestDetectionRangeArgumentDomain`:
1. `test_visual_is_the_third_detection_sensor`: `DETECTION_SENSORS == ('radar', 'TVD', 'visual')`.
2. `test_visual_only_asset`: visual air 6 → `detection_range('air') == 6000.0`; `'ground'` → None.
3. `test_visual_composed_with_max`:
   - radar 5 con visual 6 → 6000.0;
   - radar 20 con visual 6 → 20000.0.
4. `test_visual_isolated_by_sensor`: `sensor='visual'` → 6000.0; `sensor='TVD'` → None.
5. `test_switch_off_ignores_visual`: con `patch.object(Mobile_module, 'D4C_VISUAL_SENSOR', False)`:
   - visual-only → None;
   - `sensor='visual'` → None;
   - radar 5 con visual 6 → 5000.0.

`Test/Test_Vehicle_Data.py`, nuova classe `TestVisualSensorRecords`:
6. `test_zsu_and_vads_have_the_visual_sensor`: valori aria di A.1 (6/5.5/4/1 e 6/5/1.2/1); `ground` e `sea`
   `(False, ...)`; `radar is False`, `TVD is False`.
7. `test_other_records_have_no_visual_sensor`: tutti gli altri record hanno `visual is None`.
8. `test_visual_does_not_enter_the_scores`: per entrambi, `_TVD_eval() == 0.0` e `_radar_eval() == 0.0`.
9. `test_constructor_defaults_visual_to_none`:
   - copia di un dict di registro (es. `MTLB_data`) con `model='test-visual-default'` e senza `visual`;
   - si costruisce e si verifica `.visual is None`;
   - si rimuove dal registro in `finally`.

`Test/Test_Threat_AA_Factory.py`:
10. Sostituire `test_systems_without_sensor_data_give_none` (`:436-441`) con
    `test_visual_fallback_systems_detect_by_sight`. Per ZSU-57-2 e M163-VADS a 1000 m e a 30 m:
    - `threat.sensor == 'visual'`;
    - raggio 6000.0;
    - `acquisition_range == 6000.0`;
    - `build_threat_aa(asset)` non None.
11. `test_visual_fallback_switch_off_gives_none`: con l'interruttore spento → None, il comportamento precedente.
    L'intercettazione resta.
12. `test_sensor_tables_are_consistent`:
    - `set(EFFECTIVE_EARTH_RADIUS_FACTOR) == set(Mobile.DETECTION_SENSORS)`;
    - `EFFECTIVE_EARTH_RADIUS_FACTOR['visual'] == 1.0`.

`Test/Test_Air_Defense_Efficacy.py`: nessuna modifica. `test_only_radar_emitters_are_visible` (`:234-238`) deve
restare verde: ZSU e M163 non emettono.

Nuovo `Test/Test_Session_Scenarios_S31.py`, con docstring di modulo nello stile di S19AD. Riusa `build`, la
geometria e `run_variant` di `Test_Session_Scenarios_S19_Air_Defence` (`:69-97`), con un `build` locale che
accetta la quota degli A-10C:
- `SEEDS = [f'S31-VISUAL-{i}' for i in range(4)]`;
- `VARIANTS = ('zsu', 'zsu_off', 'vads_low', 'vads_low_off', 'vads_high')`. Ciclo esterno sui semi, interno sulle
  varianti, **stesso `session_id` per le 5 varianti di un seme**;
- una variante = difesa in `(1000, -300)`, 3 BMP-2 come in S19AD (sensore dichiarato `VISUAL` a terra), 4
  A-10C `Maverick/Gun CAS` da `(-40 000, 0, quota)`, rotta `OVERFLIGHT`, bersaglio ristretto ai BMP-2 con ROE
  `only_designated` (come `targets_ifv_only=True`), `BOTH_HOLD`, `DURATION` 1800 s;
- parametri per variante:

  | Variante | Difesa | Quota A-10C | Interruttore |
  |---|---|---|---|
  | `zsu` | ZSU-57-2 | 3000 m | acceso |
  | `zsu_off` | ZSU-57-2 | 3000 m | spento |
  | `vads_low` | M163-VADS | 500 m | acceso |
  | `vads_low_off` | M163-VADS | 500 m | spento |
  | `vads_high` | M163-VADS | 3000 m | acceso |

- interruttore: `with patch.object(Mobile_module, 'D4C_VISUAL_SENSOR', not variant.endswith('_off')):` attorno
  all'intera esecuzione.

Classe `TestS31VisualSensorRanges(F.LoggerSilencer, unittest.TestCase)`, unitaria, **non** nella fotografia:
13. `test_mutual_detection_ranges_with_the_visual_sensor`:
    - ZSU-57-2 reale (`F.make_vehicle`) e A-10C reale (`F.make_aircraft`, 3000 m): la portata della ZSU verso
      l'aereo è 6000.0;
    - con l'interruttore spento è None.

Classe `TestS31VisualSensor(F.LoggerSilencer, unittest.TestCase)`, in fotografia:
14. `test_mavericks_are_launched`: premessa non vacua, in ogni variante e seme si lanciano Maverick (> 0).
15. `test_without_the_visual_sensor_the_aaa_never_fires`: `zsu_off` e `vads_low_off` hanno 0 colpi della difesa
    in ogni seme (comportamento precedente).
16. `test_zsu_with_the_visual_sensor_fires`: in `zsu` i colpi della difesa, sommati sui semi, sono > 0; ogni suo
    `AmmunitionEvent` ha arma `'S-68-57mm'`.
17. `test_vads_with_the_visual_sensor_fires_at_low_altitude`: in `vads_low` la somma è > 0; arma
    `'M61-Vulcan-20mm'`.
18. `test_vads_sees_but_cannot_reach_aircraft_at_3000_m`: `vads_high` ha 0 colpi della difesa in ogni seme. Il
    sensore vede a 6 km, l'arma arriva a 1000 m di quota: rilevamento ≠ intercettazione.

Valori della sonda E-3 (orientativi, non da asserire): `zsu` 550 colpi e 1 perdita Blue su 4 semi;
`vads_low` 2650 colpi e 2 perdite. Se un'asserzione 14-18 fallisce, **fermarsi e riferire**: niente ritocchi a
geometria o valori.

`Test/Scenario_Baseline.py`:
- in coda a `UNITS` (`:379`):
  ```python
  # ── S31 (D-4c: sensore visivo di ripiego di ZSU-57-2 e M163-VADS) — in coda, nomi stabili ──
  ('S31-VISUAL', 'Test_Session_Scenarios_S31', 'TestS31VisualSensor', None,
   _by_occurrence('zsu', 'zsu_off', 'vads_low', 'vads_low_off', 'vads_high')),
  ```
- nel docstring del modulo, dopo "Fuoco su posizione dopo la F7b", il paragrafo `## Sensore visivo dopo la
  D-4c`: "non cambia le esecuzioni esistenti (nessuno scenario usa ZSU-57-2 o M163-VADS); aggiunge in coda l'unità
  S31-VISUAL (5 varianti, 4 semi): 20 esecuzioni nuove; nessuna voce nuova nel riassunto".

#### A.6 Esito atteso (blocco A)
- **Suite**: `Ran 4727` (4710 + 17 test nuovi: 1-9, 11-18; il 10 sostituisce un test esistente), `OK`,
  `skipped=7`. Se il conteggio differisce, riferire l'elenco.
- **Confronto con la fotografia**:
  - **989 esecuzioni IDENTICHE**: nessuno scenario esistente contiene ZSU-57-2 o M163-VADS. Le portate di tutti
    gli altri modelli sono invariate, perché `visual` sta solo in quei due record e radar e TVD restano primi nel
    ciclo. Lo stream RNG è invariato fuori dalle sessioni con i due modelli;
  - **20 NUOVE**: `S31-VISUAL/S31-VISUAL-<0..3>/<zsu|zsu_off|vads_low|vads_low_off|vads_high>`;
  - **0 CAMBIATE**. Una sola esecuzione cambiata è un'anomalia: fermarsi e riferire.
- **Non installare** la fotografia nuova: lo fa la sessione principale dopo la verifica.

---

### Blocco B — D-4b, radar EWR, nucleo (opzioni raccomandate 6-17)

**Esecutore suggerito**: `oc-developer` (DeepSeek V4 Pro high). Sono dati da inserire secondo tabelle complete,
più una modifica di ~6 righe. Alternativa: `des-developer` Sonnet, sforzo medio.
**Dimensione stimata**: ~450-550 righe di dati, ~15 righe di codice, ~200-250 righe di test. **Prerequisito**:
nessuno; è indipendente dal blocco A. Se segue A, il costruttore ha già `visual`, che negli EWR resta None.

#### B.1 `Asset/Vehicle_Data.py`: codice
- Costante, accanto a `AA_CANNONS_ALLOWED_CATEGORIES` (`:53-58`):
  ```python
  # Categorie escluse dalla popolazione GLOBALE del combat score (Proposta_Dati_Sensori_EWR_Visivo.md, decisione 9, G2):
  # un EWR non combatte (combat power 0 per definizione, Context.py ASSENZA INTENZIONALE DI SAM/AAA/EWR) e il suo
  # combat score, senza armi ne' corazza, e' il piu' basso del registro: incluso, abbasserebbe il minimo e
  # riscalerebbe la combat power di ogni Vehicle. Senza record EWR la popolazione e' quella di prima.
  GLOBAL_COMBAT_SCORE_EXCLUDED_CATEGORIES = frozenset({Ground_Vehicle_Asset_Type.EWR.value})
  ```
- `get_normalized_combat_score` (`:950-964`): solo nel caso globale (`category` non passato), la popolazione
  esclude quelle categorie e il risultato si satura in [0, 1]. Così un EWR, normalizzato su una popolazione che
  non lo contiene, resta nell'intervallo richiesto dal test `test_vehicle_score_values_are_floats_in_range`:
  ```python
  global_scope = not category
  if global_scope:
      category = CATEGORY
  elif ...  # validazione invariata
  vehicles = [ac for ac in Vehicle_Data._registry.values() if ac.category in category
              and not (global_scope and ac.category in GLOBAL_COMBAT_SCORE_EXCLUDED_CATEGORIES)]
  scores = [ac._combat_eval() for ac in vehicles]
  value = self._normalize(self._combat_eval(), scores)
  return min(1.0, max(0.0, value)) if global_scope else value
  ```
  Per i record esistenti il valore è dentro [min, max] della popolazione, quindi la saturazione non cambia nulla.
  Gli altri `get_normalized_*` **non** cambiano (decisione G2 ristretta): i loro score globali si spostano con gli
  EWR, ma non hanno consumatori (§1.4).
- Funzione d'appoggio, prima dei record EWR:
  ```python
  def _ewr_support_fields(mobility: str) -> Dict:
      """Campi NON sensore dei record EWR (D-4b): TUTTI STIME DI SCHEMA DICHIARATE, nessuna fonte.

      Servono a soddisfare lo schema di Vehicle_Data (dimensioni intere positive, costo e autonomia > 0, velocita').
      `mobility`: 'mobile' (radar su autocarro) | 'semi_mobile' (rimorchi, messa in opera di ore).
      Restituisce dizionari NUOVI a ogni chiamata (nessuna struttura condivisa fra record).
      """
  ```
  Contenuto, identico per i due valori di `mobility` salvo dove indicato:

  | Chiave | `mobile` | `semi_mobile` | Statuto |
  |---|---|---|---|
  | `physical_characteristics` | `{'length': 9, 'width': 3, 'height': 4, 'weight': 14}` | `{'length': 12, 'width': 3, 'height': 6, 'weight': 25}` | [S] ordine di grandezza di un autocarro 6x6 / rimorchio d'antenna; l'asset è il mezzo dell'antenna, non l'intero sito |
  | `cost` | 2.0 | 4.0 | [S] M$, non consumato dal motore (il costo dell'asset viene dal Context) |
  | `range` | 500 | 300 | [S] km di autonomia |
  | `engine` | `None` | `None` | il motore non è il soggetto del record; l'autonomia si legge da `range` (`Asset/Mobile.py:1291-1300`) |
  | `weapons` | `{}` | `{}` | nessun armamento |
  | `TVD` | `False` | `False` | — |
  | `communication` | `{'model': 'generic comm model', 'capabilities': {'navigation_accuracy': 0.3, 'communication_range': 100}, 'reliability': {'mtbf': 45, 'mttr': 3}}` | uguale | [S] come i "generic comm model" del registro; è il solo componente con `reliability`, necessario perché `_reliability_eval` non riceva una lista vuota (`:230-232`) |
  | `protections` | `{'active': None, 'armor': {}, 'reactive': {}}` | uguale | nessuna corazza (mezzo non protetto) |
  | `hydraulic` | `False` | `False` | non modellato |
  | `speed_data` | sustained 50 / max 70 / off_road 30 km/h, consume 0.4 / 0.55 / 0.7 | 30 / 40 / 15, stessi consumi | [S] |

  La sonda E-5 ha costruito gli 8 record con questi campi senza errori.

#### B.2 `Asset/Vehicle_Data.py`: record (chiavi stabili)
Forma del radar, uguale per tutti:
```python
'radar': {
    'model': <nome radar>,
    'capabilities': {
        'air': (True, {'tracking_range': 0, 'acquisition_range': <km>, 'engagement_range': 0, 'multi_target_capacity': <n>}),
        'ground': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
        'sea': (False, {'tracking_range': 0, 'acquisition_range': 0, 'engagement_range': 0, 'multi_target_capacity': 0}),
    },
    'reliability': {'mtbf': 45, 'mttr': 4},  # STIMA [S] generica del registro (decisione 12, scelta dell'utente), non dato di fonte
    # 'antenna_height' solo dove di fonte (decisione 16).
    # 'acquisition_profile': ((quota bersaglio [m], portata [km]), ...) -- dato di FONTE NON LETTO DAL CODICE (decisione 8).
},
```
Ogni record: `**_ewr_support_fields(<mobility>)` più i campi seguenti, con `'category': 'EWR'`,
`'roles': ['EWR']`. `roles` non deve contenere `AAA`/`SHORAD`/`MERAD`/`LORAD`: lo legge `sam_category`
(`Context/Air_Defense_Efficacy.py:545-552`). `'constructor': 'non trovato'` per tutti: nessuna ricerca lo
riporta.

| Variabile | `model` (chiave) | `made` | Mobilità | Servizio | `users` | `radar['model']` |
|---|---|---|---|---|---|---|
| `SCR270_data` | `'SCR-270'` | USA | mobile | 1940-1945 | `['USA']` | `'SCR-270'` |
| `FuMG80_Freya_data` | `'FuMG-80-Freya'` | Germany | semi_mobile | 1938-1945 | `['Germany', 'Romania']` | `'FuMG 80 Freya'` |
| `P12_Yenisei_data` | `'P-12-Yenisei'` | USSR | mobile | 1956-None | `['USSR', 'Egypt', 'Vietnam', 'Iraq', 'Syria', 'East Germany', 'Czechoslovakia', 'Serbia']` | `'P-12 Yenisei (Spoon Rest A)'` |
| `P18_Terek_data` | `'P-18-Terek'` | USSR | mobile | 1970-None | `['USSR', 'East Germany', 'Poland', 'Syria', 'India', 'Vietnam', 'Finland']` | `'P-18 Terek (Spoon Rest D)'` |
| `P37_Mech_data` | `'P-37-Mech'` | USSR | semi_mobile | 1961-None | `['USSR', 'Czechoslovakia']` | `'P-37 Mech (Bar Lock)'` |
| `Nebo_SV_1L13_data` | `'1L13-Nebo-SV'` | USSR | mobile | 1984-None | `['USSR', 'Russia']` | `'1L13 Nebo-SV (Box Spring)'` |
| `Nebo_55Zh6_data` | `'55Zh6-Nebo'` | USSR | semi_mobile | 1986-None | `['USSR', 'Russia']` | `'55Zh6 Nebo (Tall Rack)'` |
| `AN_TPS43_data` | `'AN-TPS-43'` | USA | mobile | 1968-None | `['USA', 'Argentina', 'Bangladesh', 'Spain']` | `'AN/TPS-43'` |

`end_service` None = "in servizio o fine non trovata". Nella chiave `'AN-TPS-43'` si usa il trattino al posto della
barra, come gli altri modelli veicolo.

| Modello | `acquisition_range` | `multi_target_capacity` | `antenna_height` | `acquisition_profile` | Commento obbligatorio nel codice |
|---|---|---|---|---|---|
| SCR-270 | 160 | 0 | 16.8 | `((305, 32), (1524, 80), (6096, 160), (7620, 180))` | "160: FONTE (tabella SCR-270-D, Wikipedia), singolo bombardiere a 20 000 ft (6 100 m), conf. media-alta; bersaglio piu' grande di un caccia: sovrastima contro un caccia. antenna_height 16.8: DEDOTTO (antenna alzata a 55 ft). Profilo: quote convertite da ft (D)" |
| FuMG-80-Freya | 120 | 0 | — | — | "120: FONTE (infobox Wikipedia), bombardieri, quota non qualificata, conf. media; CONTRADDIZIONE 120/160/200 km fra le fonti" |
| P-12-Yenisei | 200 | 0 | — | — | "200: FONTE (Wikipedia en/ru), quota max 25 km, bersaglio non qualificato, conf. media; altre fonti 250-360 km (360 = portata strumentale)" |
| P-18-Terek | 180 | 10 | — | `((500, 60), (10000, 180), (20000, 260))` | "180: FONTE (Wikipedia ru) contro MiG-21 a 10 000 m, conf. media-alta. multi_target 10: FONTE, conf. media. MTBF 140 h di fonte (conf. media-bassa, contraddizione 140/800 h), MTTR non trovato: nel campo `reliability` va la STIMA generica 45/4 (decisione 12), il 140 h resta solo nel commento" |
| P-37-Mech | 280 | 0 | — | — | "280: FONTE (Wikipedia ru) contro caccia, quota non indicata, conf. media (bombardiere 350, missile da crociera 235)" |
| 1L13-Nebo-SV | 250 | 0 | — | `((500, 50), (10000, 250), (27000, 330))` | "250: FONTE (APA, 'non inferiore a') contro caccia a 10 000 m, conf. media; CONTRADDIZIONE con la stampa (60 km a 500 m, 350 km a 27 km). Servizio 1984: Wikipedia en (P-18 sostituito nel 1984); radartutorial ~1990" |
| 55Zh6-Nebo | 400 | 0 | — | `((500, 65), (20000, 400))` | "400: FONTE di seconda mano (Defense Express via armedconflicts) contro caccia di 4a gen. a 20 000 m (non 10 000), conf. media-bassa; possibile attribuzione al Nebo-U. MTBCF >250 h (radartutorial, conf. media-bassa) solo nel commento; nel campo `reliability` la STIMA generica 45/4 (decisione 12)" |
| AN-TPS-43 | 440 | 0 | — | — | "440: FONTE (Wikipedia, massimo 240 nmi), bersaglio non qualificato, conf. bassa-media; i profili per quota CMANO (gioco) NON sono usati" |

Ordine della disuguaglianza `acquisition ≥ tracking ≥ engagement` rispettato (x ≥ 0 ≥ 0).

Registrazione in coda, dopo `Vehicle_Data(**S300PS_data)` (`:4614`), con l'intestazione `# Nuovi EWR (D-4b)`, nello
stesso ordine della tabella. Le altre registrazioni non si spostano.

#### B.3 Effetti sugli altri moduli e sui chiamanti [V salvo dove indicato]
| Modulo | Effetto |
|---|---|
| `Vehicle_Data` tabella `VEHICLE` | 8 voci nuove. Gli score globali `radar`, `weapon`, `reliability`, `availability` dei 64 record esistenti si spostano (es. P-18 nuovo massimo radar 1,453 > S-300PS 1,4175; weapon minimo 0): nessun consumatore. Il **combat score** globale resta identico (G2) |
| `Vehicle.set_combat_power` | per gli EWR 0 in ogni azione (EWR assente da `GROUND_COMBAT_EFFICACY`); per gli altri invariato |
| `Combat_Power_Estimation._bucket_scores` | bucket `('EWR', dimensione)` nuovo, mai usato: EWR senza efficacia, esclusa anche dalla mediana globale (`:146-150`) |
| `Air_Defense_Efficacy` | `emits_radar` True, `sam_category` None, `air_defense_profile` None (sonda E-4): **fuori dal catalogo RWR**, pesi di classe invariati. L'RWR non "vede" gli EWR (il flag `ewr` di `Aircraft_Rwr_Data` resta inutilizzato: limite) |
| `Air_Route_Manager` | `build_detection_threat` produce il volume EWR con antenna di 20 m [S], o 16,8 m per lo SCR-270; `build_threat_aa` None (log `air_defense_volume: no AD weapons`) |
| `Military` | `air_detection_threats` include gli EWR; `air_defense_threats`/`air_defense_power`/`salvo_interceptors` no |
| DES | un EWR in una sessione rileva, quindi percezione condivisa del dominio (`_perceive`, `Logic/Engagement_Resolver.py:2033-2037`), candidati senza armi, nessun tiro; è un bersaglio di classe `air_defence` (`Logic/Fire_Control.py:596-608`). **Nessun cueing** verso i SAM (D-7 fuori scope) |
| Inventari di campagna, adapter DCS | nessuno (decisione 17; il core non mappa i tipi DCS) |

Vincoli: nessuna estrazione RNG nuova nelle sessioni esistenti, perché nessuna contiene EWR; nessun riferimento a
DCS nel core. I nomi DCS ("1L13 EWR", "55G6 EWR") restano commenti informativi nei record e non diventano chiavi.

#### B.4 Test (blocco B)
Nuovo `Test/Test_EWR_Data.py`, con logger mockati (`patch(...Vehicle_Data.logger, MagicMock())` e
`F.LoggerSilencer` per le classi con asset reali):

`TestEWRRecords`:
1. `test_ewr_models_are_registered`: le 8 chiavi presenti, `category == 'EWR'`, `roles == ['EWR']`.
2. `test_ewr_radar_is_an_air_only_search_sensor`: `air[0]` True; `ground[0]`/`sea[0]` False;
   `tracking_range == 0`, `engagement_range == 0`.
3. `test_acquisition_ranges_match_the_plan`: dizionario `{modello: km}` della tabella di B.2.
4. `test_multi_target_capacity`: P-18 = 10, gli altri 0.
5. `test_ewr_have_no_weapons_and_no_other_sensor`: `weapons == {}`, `TVD is False`; `visual` None (con
   `getattr(..., 'visual', None)`, così il test vale anche prima del blocco A).
6. `test_reliability_is_the_declared_generic_estimate` (decisione 12): `radar['reliability'] == {'mtbf': 45, 'mttr': 4}`
   per tutti e 8.
7. `test_acquisition_profiles_are_consistent`:
   - quote e portate strettamente crescenti;
   - la portata alla quota di riferimento è uguale ad `acquisition_range`: P-18 (10000 → 180), 1L13 (10000 →
     250), SCR-270 (6096 → 160), 55Zh6 (20000 → 400).
8. `test_scr270_antenna_height`: 16.8; gli altri senza la chiave.

`TestEWRDoNotShiftTheCombatScores`:
9. `test_global_combat_population_excludes_ewr`:
   - si legge `T-90M`.`get_normalized_combat_score()`;
   - si registra un record EWR di prova `'test-ewr-extreme'` (copia di `P18_Terek_data` con
     `acquisition_range` 10000 e `multi_target_capacity` 100, combat score fuori scala);
   - il valore di T-90M non cambia;
   - si rimuove il record in `finally`.
10. `test_ewr_global_combat_scores_in_unit_interval`: per gli 8 record, `0.0 <= get_normalized_combat_score() <= 1.0`.
11. `test_global_combat_scores_of_existing_models_ignore_ewr`: per ogni record non EWR, il valore globale è uguale
    a `_normalize(_combat_eval(), [score dei soli non-EWR])`.

`TestEWRAsAssets` (asset reali, `F.build_force`/`F.make_vehicle` in un `Military`):
12. `test_ewr_vehicle_has_zero_ground_combat_power`: `isEWR` True; tutti i valori di
    `combat_power(force='ground')` sono 0.
13. `test_ewr_gives_detection_without_interception`:
    - `air_defense_threats() == []`;
    - con P-18, `air_detection_threats(10000.0)` dà un volume di raggio 180 000 m, `sensor == 'radar'`;
    - a 500 m il raggio è `radar_horizon_range(SENSOR_HEIGHT_EWR_M, 500.0)` (~110,6 km), sotto i 180 km;
    - lo SCR-270 a 500 m usa l'antenna di 16,8 m.
14. `test_ewr_is_an_emitter_outside_the_rwr_catalogue`:
    - `emits_radar` True, `sam_category` None, `air_defense_profile` None;
    - nessun modello EWR in `default_rwr_catalogue()`.
15. `test_ewr_in_a_session_detects_and_never_fires`:
    - una sessione con `F.run`: 1 P-18 Red e 1 A-10C Blue da `(-100 000, 0, 3000)`, rotta fino a `(20 000, 0)`,
      bersaglio il gruppo EWR, come la sonda E-4;
    - la sessione termina;
    - nessun `AmmunitionEvent` con `asset_id` dell'EWR.

Nessuna unità nuova nella fotografia per il blocco B. Lo scenario EWR con SAM e cueing appartiene a D-7.

#### B.5 Esito atteso (blocco B)
- **Suite**: `Ran` = base + 15. Base 4710, oppure 4727 dopo il blocco A: 4725 / 4742. `OK`, `skipped=7`. La sonda
  E-2 (suite completa con 2 EWR di prova in memoria) non ha rotto nessun test esistente.
- **Confronto**: **tutte identiche** (989, oppure 1009 dopo A), **0 nuove, 0 cambiate**. Motivi:
  - nessuno scenario istanzia un EWR;
  - il combat score globale dei record esistenti non cambia (G2);
  - catalogo RWR e pesi di classe invariati;
  - il DES non legge gli score del registro.

  Con G1 al posto di G2, il confronto dovrebbe restare identico (la fotografia non registra la combat power), ma la
  suite va verificata: la sonda E-2 ha già mostrato che uno spostamento del minimo non rompe test.

---

### Blocco C — siti fissi (solo se la decisione 14 li include)

Non eseguibile da questo documento.
- Candidati, con le portate proposte dalla ricerca (§4 della ricerca), da rileggere per confidenza:
  Chain Home 160, AMES Type 7 140, AMES Type 80 390, AN/FPS-20 322 o 407 (contraddizione, bassa), AN/FPS-117 330
  (Lockheed, Pd 80 % su 1 m², media-alta; unico con MTBF >2000 h e MTTR <45 min entrambi di fonte),
  P-14 400 (bassa-media), Wassermann 190 a 6000 m, Mammut 300 (media-bassa).
- Prima serve decidere il modello dell'installazione fissa:
  - `Vehicle` a velocità 0, con il test `range > 0` da conciliare;
  - oppure `Structure` dotata di sensore, che oggi non ha `detection_range`.
- Una volta decisa, la Proposta verrà aggiornata con le schede complete.

---

### Documenti da aggiornare dopo (non scritti qui)

- `Analysis/Document/Manuale_Motore_DES/`:
  - `04_Strato1_Scheduler_Contatti.md`: composizione dei sensori in `detection_range` con `visual`, interruttore;
  - `08_Supporto_Trasversale.md`: `:501-502` (ZSU-57-2/M163 non più senza sensore), `:557` (D-4b/c fatte), voce
    degli EWR fra i sensori puri;
  - `09_Validazione.md`: scenario S31-VISUAL;
  - `10_Limiti_Estensioni_Divergenze.md`:
    - `:570-573` e `:634`: da "sospesa" a "fatta", con i limiti di §5;
    - `:751`: riepilogo;
    - limite nuovo: orizzonte assente nel DES;
    - limite nuovo: fattore notte unico anche per il visivo.
- `Analysis/Document/F4_Differenze_Scenari.md`: sezione "D-4c" (20 esecuzioni nuove S31-VISUAL, esistenti
  identiche) e nota sul blocco B (nessuna differenza).
- `Analysis/Document/Piano_Implementazione_Missione.md`: nota di stato accanto ai riferimenti EWR (`:318`,
  `:458`): EWR presenti nei registri, cueing sempre fuori perimetro.
- `Analysis/Document/Proposta_Volumi_Rilevamento_Intercettazione.md` §9 (D-4): nota di stato a cura del
  pianificatore.
- `Ricerca_EWR_2026_10_29.md` §1: annotare il controllo locale di §5.3 (unità DCS "FPS-117").
- Memoria `project_detection_interception_volumes` (solo la sessione principale): D-4b nucleo e D-4c fatte, con
  il commit; blocco C e curva portata-quota (opzione (c)) aperti.

---

## 5. Rischi e limiti

### 5.1 Valori deboli che entrano nel codice
Ogni riga va dichiarata con il suo commento (testi in A.1 e B.2) e riportata nel rapporto dell'esecutore.

| Valore | Tipo | Confidenza | Nota |
|---|---|---|---|
| visivo `acquisition_range` 6 km (ZSU, M163) | S | **bassa** | nessuna fonte dà la portata di scoperta dei due mezzi; scala da Howell (DC-3) |
| ZSU `tracking_range` 5,5 | F | media | pagina Wikipedia con tag di accuratezza contestata |
| ZSU `engagement_range` 4 | F | media | concorda con `range.direct` dell'arma (`Ground_Weapon_Data.py:2262`) |
| M163 `tracking_range` 5 | F | media | portata del VPS-2 (misura di distanza, non scoperta) |
| M163 `engagement_range` 1,2 | F | media | HEI-T-SD; 2,0-2,6 km sono versioni successive (PIVADS 1984), non usate |
| SCR-270 160 | F | media-alta | bombardiere, non caccia: sovrastima contro un caccia |
| Freya 120 | F | media | contraddizione 120/160/200 |
| P-12 200 | F | media | non qualificato |
| P-18 180, multi 10 | F | media-alta / media | il dato migliore del nucleo |
| P-37 280 | F | media | quota non indicata |
| 1L13 250 | F | media | "non inferiore a"; contraddizione con la stampa; anno 1984 contro ~1990 |
| 55Zh6 400 | F | **media-bassa** | seconda mano, quota 20 km, possibile confusione con il Nebo-U |
| AN/TPS-43 440 | F | **bassa-media** | massimo non qualificato |
| SCR-270 antenna 16,8 m | D | media | 55 ft |
| Altezza antenna EWR 20 m (gli altri 7) | S | — | costante già esistente `SENSOR_HEIGHT_EWR_M` |
| Campi non-sensore degli EWR (dimensioni, costo, autonomia, velocità, comunicazioni) | S | — | un solo punto, `_ewr_support_fields`; non consumati dal DES salvo velocità/autonomia (gli EWR negli scenari non si muovono) |
| `multi_target_capacity` 0 | — | — | significa "non trovato", non "nessun bersaglio" |

### 5.2 Limiti di modello (da dichiarare nel manuale)
1. **Il DES non ha orizzonte radar** (§1.5). Un EWR con R alla quota di crociera vede nel DES un aereo radente a
   tutta portata. Nel pianificatore la sovrastima a 500 m è di ~1,8 volte (P-18). La curva di fonte è conservata
   (`acquisition_profile`) per una Proposta futura (opzione (c)).
2. **Notte e meteo non distinguono il sensore**: `weather_detection_factor` è unico
   (`Logic/Engagement_Resolver.py:1117-1122`, notte 0,7). Il visivo di notte resta al 70 %, mentre le fonti dicono
   "tiro notturno impraticabile" (ZSU) e "solo tempo sereno" (entrambi). V2 rende possibile la correzione per
   sensore, che resta da proporre.
3. **ZSU-57-2 "tiro efficace solo a veicolo fermo"** [fonte bassa-media]: non modellato.
4. **Combat score**: con V2 il combat score di ZSU/M163 non riflette la capacità di vedere, perché `visual` non
   entra in `_combat_eval`. È una scelta deliberata, per non spostare la normalizzazione globale.
5. **Rilevamento ≠ intercettazione**: il sensore visivo e gli EWR non creano volumi d'intercettazione. La variante
   `vads_high` lo verifica nel DES. Un EWR non abilita nessun tiratore: il cueing è D-7.
6. **Radar WWII a lettura manuale**: nessuna latenza di plotting (CH, Freya, SCR-270); l'EWR è "istantaneo" come
   gli altri sensori.
7. **RWR ed EWR**: gli RWR non identificano gli EWR (`sam_category` None). Il flag `ewr` di `Aircraft_Rwr_Data`
   resta senza effetto.
8. **Score globali non consumati**: con il blocco B si spostano radar, weapon, reliability e availability globali
   dei record esistenti. Oggi non hanno consumatori (ricerca di tutti gli usi). Un consumatore futuro dovrà
   tenerne conto o estendere G2.

### 5.3 Controllo locale delle fonti (fatto)
- `Analysis/Document/documentazione_dcs/1975 Georgian War/DCE/ScriptsMod.NG/ATO_ThreatEvaluation.lua:1182-1276`
  (script della campagna DCE, comunità, **confidenza bassa come dato**) riconosce i tipi di unità DCS:
  - "1L13 EWR", 330 km;
  - "55G6 EWR", 340 km;
  - **"FPS-117"**, 461 km;
  - "p-19 s-125 sr", 160 km;
  - "Dog Ear radar", 35 km.

  Questo **contraddice** l'affermazione della ricerca (snippet di forum) sull'assenza di EWR occidentali in DCS:
  l'FPS-117 risulta un tipo DCS. Va verificato nell'editor DCS e conta per il blocco C.
- I 330 km del 1L13 nello script coincidono con il valore "≥330 km a 27 000 m" (APA), cioè il massimo, non la
  quota di 10 km. Le portate dello script **non** vanno usate come dati.
- `DCS_-_Overview_Vehicles/DCS-Unit_overview.ods`: già cercato dalla ricerca, nessun EWR. Non ricontrollato.

### 5.4 Resta da verificare (fonti primarie non accessibili)
- Portata di scoperta visiva specifica di ZSU-57-2 e M163; capacità notturna del M163.
- 55Zh6 contro Nebo-U: a quale variante appartengono i 400/65 km e l'MTBCF >250 h.
- MTTR di P-18 e 55Zh6; contraddizione 140/800 h del P-18.
- Anni di servizio dell'1L13 (1984 contro ~1990).
- Portate per quota di Freya, P-12, P-37, TPS-43 (oggi massimi non qualificati).

### 5.5 Rischi di esecuzione
- **Ciclo d'import**: `Air_Route_Manager` non deve importare `Mobile` a livello di modulo (A.3). La coerenza la
  verifica il test 12 di A.5.
- **Interruttore letto una volta sola**: se l'esecutore copiasse `D4C_VISUAL_SENSOR` in una variabile locale al
  caricamento del modulo, le varianti `_off` non funzionerebbero. Il test 5 di A.5 lo rileva.
- **Scenario S31 sensibile alla geometria**: le asserzioni sono qualitative e la sonda E-3 le soddisfa con
  margine. Se falliscono, fermarsi e riferire.
- **Ordine dei sensori**: cambiare l'ordine in `DETECTION_SENSORS` o nel ciclo del pianificatore potrebbe
  cambiare il sensore riportato a parità di raggio. Va tenuto `radar, TVD, visual`.

### Scelte minori lasciate all'esecutore (da elencare nel rapporto)
Nomi delle funzioni d'appoggio nei test; struttura interna di `Test_Session_Scenarios_S31.py`, purché le
varianti, i semi e il `session_id` siano quelli di A.5; testo dei docstring nello stile del file.
