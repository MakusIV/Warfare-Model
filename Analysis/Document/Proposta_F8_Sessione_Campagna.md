# Proposta F8: sessione e campagna (validatore di sessione, prontezza, posizione persistente, esito d'Operazione)

**Stato**: PROPOSTA (2026-10-21), da approvare. Nessun codice modificato.
**Base**: HEAD `dcedc541` del branch `analysis/dce-dcs-persistence` (F0-F7b fatte; suite 4555 OK; fotografia 982 esecuzioni).
**Fonti**: `Piano_Implementazione_Missione.md` (Fase 8 a :213-233, tabella §5 a :304, limite a :421-422);
`Proposta_Struttura_Missione_Decisioni.md` (D1.d :417-420, D2.d-e :362-374, D4 :429-468, D6 :472-505);
`Proposta_G4_Ri_scheduling.md`; deviazioni 15-22 del Piano (bingo G0-G5); memoria `project_mission_structure_decisions`,
`project_session_2026_10_13_summary` (F6-B3).
**Convenzioni**: [V] verificato sul codice (con `file:riga`); [S] misurato con una sonda in sola lettura (script fuori dal
repository, §1.7); STIMA = valore non tarato, da dichiarare come tale nel codice.
**Numerazione delle decisioni**: continua quella della `Proposta_F7_Bersagli_Filtro_Armi.md`, che arriva alla 16
(la 15 e' la F7b, la 16 la scorta): qui si parte dalla **17**.

---

## 0. Sintesi

La Fase 8 del Piano chiede quattro cose: un **validatore di sessione** (durata, missioni fuori finestra, un asset in
una sola missione, sessioni disgiunte), la **prontezza** degli asset ("pronto da t", turnaround per classe, riparazione
funzione del danno, anche terra e mare), la **posizione persistente** fra sessioni e, dal Piano §5, l'esito
dell'Operazione con lo stato "in corso" che manca. Il compito aggiunge la decisione aperta **F6-B3** (S24-GLIDE con il
bingo di default).

Oggi [V]:
- nessun validatore di sessione: `run_session` accetta qualunque durata (sessione aperta compresa, con `horizon`),
  taglia in silenzio le missioni oltre la fine (E4) e non chiama i validatori di pianificazione `check_mission_fuel` e
  `check_mission_bingo`, che esistono ma non hanno chiamanti di produzione;
- nessuna nozione di prontezza: nessun campo, nessun tempo di turnaround; `Asset.repair_time` esiste ma vale per tutti
  il segnaposto `(1, 7)` di unita' ignota;
- la posizione a fine sessione non e' calcolata ne' applicata: la sessione successiva riparte dalle posizioni iniziali
  (limite dichiarato in S11 e nella mini-campagna di validazione); `Campaign_State` la salva ma non la ripristina;
- `MissionStatus` non ha "in corso" (una missione non finita alla fine della sessione e' FAILED); l'esito
  dell'Operazione (`Operation.outcome_rule`) e' dichiarato ma nessuno lo calcola.

**Raccomandazione in breve**: il validatore e il ciclo di campagna stanno FUORI da `run_session` (l'esecutore,
sintetico o DCS, esegue; il pianificatore valida: la stessa scelta gia' fatta per il bingo a priori, deviazione 15),
in tre moduli nuovi del core (`Command/Campaign_Types`, `Logic/Session_Validator`, `Logic/Readiness`) piu' un
conduttore minimo (`Logic/Session_Campaign.run_campaign_session`: processi fra sessioni, validazione, sessione,
posizioni, prontezza). La sessione aggiunge all'esito solo dati (posizioni finali, fine del movimento, esito delle
Operazioni) e uno stato di missione `IN_PROGRESS` dietro l'interruttore `F8_IN_PROGRESS`. **Fotografia: 982 esecuzioni
identiche, 4 nuove (scenario S30-CAMPAIGN)**. F6-B3: chiudere lasciando S24-GLIDE com'e' (costo zero).

---

## 1. Problema e comportamento attuale

### 1.1 Durata e finestra della sessione [V]

- `SessionOrder.t_end` puo' essere None (sessione aperta); allora `run_session` richiede `horizon` e lo usa
  (`Session_Simulator.py:1005-1024`, docstring "Sessione aperta" a `:700-704`). Nessun default di 2 h, nessun massimo
  di 4 h (D4.b), nessun controllo di sovrapposizione con la sessione precedente (D4.a).
- `Session_Types.py:28-31` dichiara esplicitamente che le "finestre di sessione di campagna (F8)" non esistono ancora.
- Una missione piu' lunga della sessione e' **tagliata in silenzio** (E4): i tratti sono ritagliati a `[t0, session_end]`
  (`Mission_Adapter.movement_legs`, `Mission_Adapter.py:1000-1025`) e l'esito per asset e' `SESSION_END`
  (`Session_Simulator.py:2084-2085`). Una partenza derivata (TOT, ETA bloccata) anteriore a `t0` e' gia' un errore
  (`Mission_Adapter.mission_start`, `:721-723`), e il docstring rimanda il rifiuto delle missioni fuori finestra "al
  validatore di sessione della F8" (`Mission_Adapter.py:71-73`).
- Un asset in al piu' una missione per sessione: **gia' verificato** dalla porta (`Session_Types.py:251-257`), insieme
  agli id di missione unici e ai blocchi in `force_ids`. L'appartenenza degli asset al blocco, la regola A della
  velocita' e la coerenza del loadout sono verificate da `run_session` (`_check_missions`, `Session_Simulator.py:1898-1924`).

### 1.2 Validatori di pianificazione esistenti [V]

| Funzione | Regola | Chiamanti |
|---|---|---|
| `Mission_Adapter.check_mission_speed` (`:1136`) | regola A (velocita' del piu' lento) | `run_session` (`_check_missions`) |
| `Mission_Adapter.check_mission_fuel` (`:1422`) | G1: carburante > rotta intera + riserva di disimpegno | solo test |
| `Mission_Adapter.check_mission_bingo` (`:1280`) | G2 (default): parte sotto la soglia di bingo; F6-B2/B2bis con i parametri | solo test |
| `Mission_Types.check_mission_assets` (`:1150`) | asset del blocco della missione | `run_session` |

`check_mission_fuel` e `check_mission_bingo` rifiutano con `ValueError` al primo asset, restituiscono None per le
missioni non aeree o con `EndCriteria.bingo` False (`Mission_Adapter.py:1324-1325`, `:1452-1453`). Il Piano li assegna
al "pianificatore (F8, validatore di sessione, da confermare)" (`Piano_Implementazione_Missione.md:421-422`). La
deviazione 15 ha gia' deciso che l'esecutore NON rifiuta (fa tornare l'aereo al bingo) e che validatore ed esecutore
usano lo stesso criterio.

### 1.3 Prontezza degli asset [V]

- Nessun campo "pronto da", nessun tempo di turnaround in `Context`, nessun processo fra sessioni. Il pianificatore
  aereo che dovrebbe "vedere solo gli asset pronti" non esiste: `Air_Resources_Assigner.get_aircraft_availability_list`
  e' uno stub (`Air_Resources_Assigner.py:1205-1240`, corpo `pass`).
- `Asset.repair_time` (`Asset.py:264-270`) e' popolato dal campo `t2r` delle tabelle di `Context` (`Context.py:1002-1010`
  e seguenti): **lo stesso segnaposto `(1, 7)` per tutte le classi**, una tupla di unita' ignota (mentre il setter
  valida un `int`). Non e' utilizzabile come dato.
- Riarmo e rifornimento: per un aereo assegnare il loadout RIARMA e fa il PIENO di quel loadout
  (`Aircraft.assigned_loadout`, `Aircraft.py:176-213`); per veicoli e navi `Mobile.load_stores_from_registry` (`:931`) e
  `Mobile.load_fuel_from_registry` (`:1369`). Il setter `Mobile.fuel` dichiara che "il rifornimento e' fuori scope
  (materia del ciclo di campagna)" (`Mobile.py:1187-1196`).
- Salute: `Asset.health` (setter, `Asset.py:207-209`) aggiorna lo stato (`DataType/State.py`: Damaged <= 80, Critical
  <= 50, Destroyed <= 15). La "mission kill" della F6-B1 e' una soglia di missione, non uno stato.

### 1.4 Posizione fra sessioni e postura di fine missione [V]

- `run_session` non aggiorna `asset.position` (docstring di S11, `Test_Session_Scenarios_S10_S18.py:347-350`; mini-campagna
  di validazione, `Test_Session_Validation.py:281-284`): la sessione successiva riparte dalle posizioni iniziali.
- La posizione a fine sessione e' gia' calcolabile: i tratti definitivi di ogni asset (dopo bingo, esaurimento e
  ri-pianificazione G4b) sono in `all_legs` (`Session_Simulator.py:2349-2361`, aggiornati in `replan` a `:2645-2650`) e
  `Contact_Scheduler.position_on_legs` (`:508`) satura agli estremi. Non e' pero' nell'esito.
- `SessionOutcome.postures` (`Session_Types.py:337-342`) da' la postura a fine sessione: `parking_cold` (aereo a terra),
  `off_scene` (uscito di scena), `Defense` (terra/mare), il tipo di missione (ancora in movimento), `destroyed`.
- `Campaign_State._serialize_asset` salva gia' la posizione (`Campaign_State.py:453-489`), `_restore_asset` non la
  ripristina (`:620-632`). `CampaignState` non ha chiamanti di produzione (solo `Test_Campaign_State`).

### 1.5 Stato "in corso" ed esito dell'Operazione [V]

- `MissionStatus` = COMPLETED, ABORTED, FAILED, DESTROYED (`Mission_Types.py:161-166`). Regola unica della F6-B1
  (`Session_Simulator.py:2096-2109`): DESTROYED > COMPLETED > ABORTED > FAILED; FAILED comprende "ancora in corso a fine
  sessione" (docstring `:166-169`, punto aperto del Piano `:501`). `AssetEndReason.SESSION_END` (`Mission_Types.py:214`)
  esiste gia' per l'asset.
- `Operation` ha `outcome_rule` (ALL, ANY, MAIN_MISSION) e `main_mission_id` (`Mission_Types.py:154-158`, `:1182-1223`),
  validati, ma nessun codice calcola l'esito: `OutcomeRule` e' usato solo in `Test_Mission_Types`.
- La fotografia NON registra lo stato di missione ne' i motivi per asset (`Scenario_Baseline.py`, sezione "Fine di
  attivita'"; `summarize_run` a `:474-573` registra `actual_etas` e `postures`, non `status`).

### 1.6 F6-B3: S24-GLIDE [V][S]

S24-GLIDE (scenario dell'esaurimento in volo della F6-A, `Test_Session_Scenarios_S24.py:357`) dichiara
`EndCriteria(bingo=False)` dalla F6-B2 per non cambiare la fotografia. Misura di oggi (§1.7, sonda 3) con il modello di
bingo finale (G1-G5) e la missione col bingo di default: **cambiano 24 esecuzioni su 32** (`glide`, `no_base`, `off` per
8 seed; `enemy_base` identica perche' il lato Blue non ha basi), con le stesse grandezze documentate il 2026-10-13 in
`F4_Differenze_Scenari.md:1475-1491`: `glide` l'aereo torna verso la base, si esaurisce a 187,5 s sul rientro ed e'
perso (lo strike Red non lo trova piu' a terra: 64 -> 0 lanci); `no_base` esaurimento a 187,5 s invece di 200 s; `off`
fine del movimento 800 -> 202,8 s, l'aereo e' a terra e lo strike Red lo colpisce (0 -> 64 lanci). Con il bingo di
default la variante `glide` non plana piu': lo scenario perderebbe il suo scopo (provare la planata della F6-A).

### 1.7 Misure (sonde in sola lettura) [S]

Tre script nello scratchpad della sessione (non nel repository) intercettano `Session_Simulator.run_session` con la
stessa tecnica di `Scenario_Baseline` (patch dell'attributo di modulo) sulle 52 unita' della fotografia.

**Sonda 1, cosa rifiuterebbe un validatore di sessione** (983 chiamate: le 982 della fotografia piu' la chiamata di
`ORC-interval` che verifica l'errore della sessione aperta senza `horizon`):

| Controllo | Chiamate rifiutate | Dove |
|---|---|---|
| sessione aperta (`t_end` None) | 2 | `ORC-interval/S-open` (una con `horizon` 600, una senza: e' il test dell'errore) |
| durata > 4 h | 0 | durate: 600 s (1), 1200 s (12), 1800 s (190), 3600 s (679), 7200 s (100) |
| missione oltre la fine (fine pianificata > `t_end`) | 8 | `S22-E3/*/not_departed`: partenza a 4200 s in una sessione di 3600 s (variante voluta: il carro non ancora partito) |
| G1 `check_mission_fuel` | 48 | `S24-ORBIT` (16: la CAP Red a secco), `S26-BINGO` (32: le varianti sotto la soglia) |
| bingo a priori `check_mission_bingo` (G2) | 48 | le stesse 48 (G1 e G2 coincidono, come dichiarato nella deviazione 18) |
| **totale delle chiamate con almeno un rifiuto** | **58** | **57 delle 982 esecuzioni della fotografia** (la 58a e' la chiamata d'errore di `ORC-interval`, che non e' nella fotografia) |

Nessuna missione senza rotta negli scenari; nessuna missione finisce entro 60 s dalla fine della sessione (nessun caso
limite di tolleranza). S24-GLIDE non e' rifiutato perche' dichiara `bingo=False` (i due validatori non lo controllano).

**Sonda 2, esiti di missione** (stessa tecnica, dopo l'esecuzione, 982 chiamate): v. §1.8.

**Sonda 3, F6-B3**: `Scenario_Baseline.capture('S24-GLIDE')` con `run_session` avvolto da un involucro che sostituisce in
memoria `EndCriteria.bingo` con True (`dataclasses.replace`), confrontato con la fotografia: 24 cambiate, 8 identiche
(§1.6).

### 1.8 Esiti "in corso" negli scenari esistenti [S]

Sonda 2 sulle 982 esecuzioni della fotografia (esiti di missione dopo `run_session`):
- stati di missione: COMPLETED 987, ABORTED 238, DESTROYED 193, **FAILED 2**;
- le 2 FAILED sono `S22-E3/S22-E3-3/not_departed` e `S22-E3/S22-E3-4/not_departed` (missione che parte dopo la fine
  della sessione, carro superstite con `SESSION_END`; negli altri 6 seed il carro e' distrutto): con `F8_IN_PROGRESS`
  attivo diventano **IN_PROGRESS**; nessun'altra missione cambia stato;
- nessuna missione FAILED con la rotta completata negli scenari della fotografia (i due test che verificano FAILED in
  quel caso, `Test_Session_Simulator.py:1355` e `Test_Session_Scenarios_S25.py:507`, costruiscono il caso a parte o non
  lo incontrano);
- posture a fine sessione: `Defense` 4202, `destroyed` 1848, `off_scene` 1790, `parking_cold` 130; **nessun aereo in
  volo e nessuna unita' ancora in movimento a fine sessione** (nessuna postura uguale a un tipo di missione);
- Operazioni: solo `S23-TOT` (24 esecuzioni) ne dichiara; il loro esito sarebbe calcolato ma non e' nella fotografia.

Quindi nella fotografia l'unico effetto di IN_PROGRESS e' su 2 esiti di missione non registrati, e l'aereo `off_scene`
(1790 posture) e' il caso particolare piu' frequente della posizione persistente (§2.F).

---

## 2. Alternative

### A. Dove si chiama il validatore di sessione

- **A1 (R)**: funzione del core **fuori** da `run_session` (`Logic/Session_Validator.check_session`), chiamata dal
  pianificatore e dal conduttore di campagna (`Logic/Session_Campaign.run_campaign_session`). `run_session` emette solo
  un **warning** per ogni missione la cui fine pianificata supera la fine della sessione (E4 non piu' silenzioso,
  nessun cambio di comportamento).
  - Pro: coerente con la deviazione 15 (l'esecutore, sintetico o DCS, non rifiuta; il pianificatore valida); il
    validatore vale per qualunque esecutore, anche l'adapter DCS; nessuno scenario esistente cambia (i 57 casi della
    §1.7 sono scenari voluti: partenza dopo la fine, carburante insufficiente per provare esaurimento e bingo).
  - Contro: un chiamante che salta il validatore puo' ancora far girare un ordine non valido (accettato: e' quello che
    fanno, di proposito, i test dell'esecutore).
- **A2**: dentro `run_session`, dietro un interruttore `F8_SESSION_VALIDATION` (default False).
  - Pro: un solo punto d'ingresso. Contro: acceso, 57 delle 982 esecuzioni della fotografia diventerebbero errori
    (bisognerebbe spegnerlo in quei test); mescola esecutore e pianificatore, contro la deviazione 15.
- **A3**: entrambi. Contro: due strade per la stessa regola.

### B. Contenuto del validatore

Controlli proposti (codici in §4.1), tutti raccolti in una lista invece di fermarsi al primo:
1. finestra: `t_end` obbligatorio (D4.b: la durata e' un parametro di campagna, niente sessioni aperte), durata
   <= massimo (4 h); il default di 2 h lo applica `SessionRules.window` a chi costruisce l'ordine;
2. sessioni disgiunte: `t_start` >= fine EFFETTIVA della sessione precedente (`SessionOutcome.t_end`, che comprende le
   salve in volo, `Session_Simulator.py:706-711`);
3. per missione: asset del blocco (`check_mission_assets`), asset non distrutti, asset pronti (prontezza), partenza
   valida (`mission_start`), **fine pianificata** (arrivo all'ultimo punto, attese comprese) entro `t_end`, regola A;
4. carburante (solo aria): **B1 (R)** G1 (`check_mission_fuel`) **e** bingo a priori (`check_mission_bingo` con gli
   interruttori dell'esecutore `F6_BINGO_REVERSE_ROUTE` / `F6_BINGO_DISENGAGE_RESERVE`, solo se `F6_BINGO` e' acceso):
   con il modello di bingo attuale coincidono (sonda: 48 e 48), ma se si spegne il G2 il bingo a priori segue la regola
   dell'esecutore (F6-B2 / F6-B2bis) e il G1 resta il minimo di carico deciso dall'utente. **B2**: solo G1 (un solo
   messaggio, ma il validatore non segue piu' l'esecutore a interruttori spenti).
5. Missione senza rotta (sul posto, terra e mare): ammessa; la sua fine e' la partenza + `max_duration_s` se dichiarata,
   altrimenti dura fino alla fine della sessione (attivita' lunga come sequenza di missioni, D4.e) ed esce "in corso".

### C. Prontezza: dove sta lo stato, quando parte, quanto dura

Dove sta lo stato:
- **C1 (R)**: un registro di campagna immutabile `Command/Campaign_Types.CampaignLedger` (sessioni passate +
  `{asset_id: ReadyRecord}`), prodotto e consumato da funzioni pure di `Logic/Readiness`; salvato in `CampaignState`
  come dizionario. Pro: nessuno stato nuovo negli asset (la stessa scelta della F4c per gli aerei a terra), nessun
  cambio alle 6 classi d'asset e ai loro test; determinismo per costruzione. Contro: chi guarda un asset non vede la
  sua prontezza senza il registro.
- **C2**: attributo `ready_at` sull'`Asset`, serializzato in `_serialize_asset`. Pro: semplice da leggere. Contro: tocca
  `Asset` (validazioni, costruttori, test), e lo stato di campagna finirebbe sparso negli oggetti.

Quando si controlla (D6.a: "il pianificatore vede solo gli asset pronti all'inizio della sessione"):
- **(R) all'inizio della sessione** (`ready_at <= t_start`), come deciso in D6.a. Alternativa: alla partenza della
  missione (`ready_at <= partenza`), piu' permissiva; si cambia con una riga, ma contraddice D6.a.

Da quando parte il turnaround:
- **(R) dal rientro**: fine del movimento dell'asset nella sessione (atterraggio, arrivo, uscita di scena, fermo per
  carburante), riportata nell'esito come `SessionOutcome.movement_ends`. D6.a: "al rientro da una missione". Il
  processo corre anche dentro la sessione: l'aereo atterrato e' a terra (bersaglio) mentre si riarma.
- alternativa: dalla fine della sessione (tutti i processi fra sessioni, D4.d). Piu' semplice, ma con sessioni di 2 h e
  turnaround di 1-2 h un caccia salterebbe sempre la sessione successiva anche se atterrato al decimo minuto.

Chi ha un turnaround: **(R)** ogni asset di una missione della sessione e ogni asset che ha consumato munizioni,
intercettori o carburante (`SessionOutcome.ammunition_consumed()`, `interceptions_consumed()`, `fuel_consumed()`):
riarmo e rifornimento servono a chi ha consumato. Per gli asset senza missione l'inizio e' la fine nominale della
sessione.

Quanto dura (D6.b: tempo per classe di velivolo da ricerca dedicata; D6.d: un tempo per dominio a terra e in mare):
- **(R) stime di progetto ora** (tabella §4.4, dichiarate STIMA nel codice) e **ricerca dedicata F8-R in parallelo**
  (agente di ricerca con schema e tabella da compilare, come per le RWR), che le sostituisce con un commit di soli dati;
  i test calcolano gli attesi dalle costanti, quindi il commit dei dati cambia solo le 4 esecuzioni di S30.
- alternativa: ricerca prima del codice (F8c attende F8-R). Nessun valore inventato, ma blocca il passo.

### D. Riparazione (D6.c)

- **D1 (R)**: tempo di riparazione **lineare nel danno**: `REPAIR_TIME_FULL_S[dominio] x (100 - salute) / 100` (STIMA),
  a **gradino** (salute riportata a 100 quando la riparazione finisce, prima l'asset resta danneggiato e non pronto);
  durata totale = turnaround + riparazione ("piu'" di D6.a), dall'istante piu' tardo fra rientro e ultimo danno subito;
  asset distrutto (salute <= 15, `State`) mai riparato; **risorse della base non modellate** (D6.c "se la base ha le
  risorse": limite dichiarato, logistica fuori dalla F8).
- **D2**: riparazione progressiva (salute che risale nel tempo). Piu' realistica per l'impiego parziale, ma serve una
  regola di impiego di un asset parzialmente riparato che nessun documento da'.
- `Asset.repair_time` / `t2r`: **non usato** (segnaposto uguale per tutti, unita' ignota); da rivedere con la ricerca.

### E. Riarmo e rifornimento a fine turnaround

- **E1 (R)**: si', dai registri: aereo con loadout = riassegnazione dello stesso loadout (`Aircraft.assigned_loadout`:
  scorta per arma e pieno di quel loadout); veicoli e navi = `load_stores_from_registry()` e `load_fuel_from_registry()`.
  Senza consumo delle scorte del blocco (`Resource_Manager`): logistica fuori F8, dichiarato. Senza questo passo la
  seconda sessione partirebbe con i serbatoi della prima e il validatore G1 la rifiuterebbe.
- **E2**: no; la prontezza e' solo un tempo, il riarmo lo fa chi assegna i loadout. Contro: per terra e mare nessuno lo fa.

### F. Posizione persistente (D1.d)

Dove si applica:
- **F1 (R)**: `run_session` calcola le posizioni a fine sessione e le mette nell'esito (`SessionOutcome.final_positions`);
  le APPLICA agli asset una funzione separata (`Session_Campaign.apply_final_positions`), chiamata dal conduttore di
  campagna. Pro: `run_session` non muta piu' di prima (S11 e la mini-campagna `VAL-agn`, che rieseguono sessioni sulle
  stesse istanze, restano identiche); e' la regola di `Session_Types` ("applicare l'esito in un'unica passata e' del
  livello di campagna", `Session_Types.py:32-35`). Contro: chi chiama `run_session` direttamente non ha la persistenza.
- **F2**: `run_session` applica le posizioni dietro un interruttore `F8_PERSIST_POSITION`. Acceso cambierebbe S11 e
  `VAL-agn` (sessioni successive su posizioni nuove).

Casi particolari (tutti in `apply_final_positions`):
- **aereo `off_scene`** (uscito di scena senza atterrare su una base vera): **(R) posizione invariata** (rientrato a una
  base fuori scena: la posizione di partenza e' la sua base); alternativa: il punto d'uscita (l'aereo comparirebbe
  parcheggiato in aria al bordo della scena);
- **aereo in volo a fine sessione** (postura = tipo di missione; possibile solo senza validatore): posizione a fine
  sessione con un **warning** (nessun movimento fuori sessione, D4.d);
- **asset distrutto**: posizione aggiornata (il relitto dove e' caduto; non ha effetti);
- **asset senza tratti** (aereo perso alla partenza per carburante, tratti vuoti): nessuna voce, posizione invariata.

Persistenza su disco: `CampaignState.restore(..., restore_position=False)`: con True ripristina anche la posizione
(default False = comportamento di oggi); il registro di campagna si salva come dizionario nell'istantanea.

### G. Stato "in corso" (D4.e, punto aperto del Piano `:501`)

- **G1 (R)**: nuovo `MissionStatus.IN_PROGRESS`; regola: DESTROYED > COMPLETED > ABORTED > **IN_PROGRESS** (almeno un
  asset superstite con motivo `SESSION_END`, cioe' ancora sulla rotta o sul posto alla fine della sessione) > FAILED.
  Interruttore `F8_IN_PROGRESS`; spento, FAILED come oggi.
- **G2**: nessuno stato nuovo; il "in corso" si ricava dagli esiti per asset. Contro: l'esito di missione (D2.d) e
  quello d'Operazione restano ambigui.

### H. Esito dell'Operazione (D2.e)

- **H1 (R)**: `OperationOutcome` (`SUCCEEDED`, `FAILED`, `IN_PROGRESS`) calcolato dalla regola dichiarata
  dell'Operazione sugli esiti delle sue missioni, nell'esito di sessione (`SessionOutcome.operation_outcomes`). Regole:

  | Regola | SUCCEEDED | IN_PROGRESS | FAILED |
  |---|---|---|---|
  | ALL | tutte COMPLETED | nessuna ABORTED/FAILED/DESTROYED e almeno una IN_PROGRESS | almeno una ABORTED, FAILED o DESTROYED |
  | ANY | almeno una COMPLETED | nessuna COMPLETED e almeno una IN_PROGRESS | nessuna COMPLETED ne' IN_PROGRESS |
  | MAIN_MISSION | principale COMPLETED | principale IN_PROGRESS | principale ABORTED, FAILED o DESTROYED |

  Funzione pura di aggregazione, nessuna regola del motore; un'Operazione e' per sessione (le Operazioni su piu'
  sessioni, "ordine permanente" di D4.e, sono del C2, fuori piano).
- **H2**: rimandare al C2 (D2.e opzione B, non scelta).

### I. F6-B3: S24-GLIDE e il bingo di default

- **I1 (R)**: **chiudere F6-B3 senza cambi**: S24-GLIDE resta lo scenario dell'esaurimento in volo e dichiara
  `bingo=False` (una missione che dichiara di non rientrare al bingo: il volo di sola andata); il bingo alla partenza e'
  coperto da S26 ('bingo', 'no_base', 'transfer_*'). Aggiungere solo una riga al docstring di S24-GLIDE che lo dice e
  che il validatore F8 non lo controlla (bingo False). Costo: nessuno, fotografia identica.
- **I2**: bingo di default in S24-GLIDE: 24 esecuzioni cambiate da accettare (§1.6), test di S24-GLIDE da riscrivere, e
  la planata della F6-A non sarebbe piu' provata da nessuno scenario (bisognerebbe aggiungere varianti `bingo=False`,
  cioe' tornare a I1 con nomi nuovi). Costo: circa mezza giornata di un esecutore piu' l'accettazione.
- **I3**: varianti nuove con il bingo di default accanto alle esistenti (`glide_bingo`, `no_base_bingo`, `off_bingo`):
  0 cambiate, 24 nuove, 2-3 test. Costo piccolo, valore modesto (S26 copre gia' il caso).

---

## 3. Decisioni aperte per l'utente

17. **Dove si chiama il validatore** (§2.A): (R) A1, funzione fuori da `run_session`, chiamata dal conduttore di
    campagna e dal futuro pianificatore; `run_session` solo un warning per le missioni oltre la fine. Alternative A2, A3.
18. **Contenuto del validatore** (§2.B): (R) i controlli 1-5 come elencati, sessione aperta rifiutata, fine di missione
    = arrivo all'ultimo punto pianificato con le attese, missioni sul posto ammesse; carburante B1 (G1 **e** bingo a
    priori con gli interruttori dell'esecutore). Alternativa B2 (solo G1).
19. **Prontezza** (§2.C): (R) registro di campagna C1; controllo all'inizio della sessione (D6.a); turnaround dal
    rientro (`movement_ends`); turnaround per gli asset di missione e per chi ha consumato; stime ora (tabella §4.4)
    e ricerca F8-R in parallelo. Da confermare anche **i valori della tabella §4.4** come stime provvisorie.
20. **Riparazione** (§2.D): (R) D1, lineare nel danno, a gradino, sommata al turnaround, risorse della base non
    modellate, `repair_time`/`t2r` non usato.
21. **Riarmo e rifornimento** (§2.E): (R) E1, dai registri alla fine del turnaround, senza logistica.
22. **Posizione persistente** (§2.F): (R) F1 (esito + funzione separata), aereo `off_scene` invariato, aereo in volo
    con warning, `CampaignState.restore(restore_position=False)` di default.
23. **Stato "in corso"** (§2.G): (R) G1 con `F8_IN_PROGRESS`. Sotto-decisione sul **default**: (R) **True** (attivo,
    come gli interruttori F5-F7 accettati), perche' la fotografia non registra lo stato di missione (982 identiche) e
    cambia solo l'esito di missione delle missioni non finite (§1.8) e un test (`test_route_cut_by_the_session_end_fails`);
    oppure False (regola letterale di AGENTS.md: il default riproduce il comportamento precedente): lo stato esiste ma
    resta spento finche' l'utente non lo accende, e il test della rotta tagliata non cambia.
24. **Esito dell'Operazione** (§2.H): (R) H1 con la tabella delle regole.
25. **Sessioni disgiunte** (§2.B punto 2): (R) la sessione successiva parte non prima della fine EFFETTIVA della
    precedente (`SessionOutcome.t_end`, salve in volo comprese); alternativa: fine nominale (`order.t_end`), che
    permetterebbe a una salva della sessione precedente di arrivare dentro la successiva.
26. **F6-B3** (§2.I): (R) I1, chiudere senza cambi (costo zero); alternative I2 (24 cambiate + test riscritti + planata
    non piu' provata) e I3 (24 nuove).
27. **Posizioni nella fotografia**: (R) NON registrare `final_positions`/`movement_ends`/`operation_outcomes` in
    `Scenario_Baseline` in questa fase (una voce nuova cambierebbe la forma di tutte le 982 esecuzioni e chiederebbe
    una fotografia nuova); le verificano i test. Alternativa: registrarle, con una rigenerazione della fotografia
    accettata dall'utente (982 cambiate nella sola forma).

---

## 4. Piano di intervento (opzioni raccomandate)

### 4.0 Passi, esecutori e ordine

| Passo | Contenuto | Motore | Fotografia attesa | Esecutore consigliato |
|---|---|---|---|---|
| **F8a** | tipi di campagna (`SessionRules`, violazioni) e validatore di sessione; `Mission_Adapter.mission_planned_end`; `Session_Simulator.session_blocks` e warning E4 | nessun cambio di comportamento | 982 IDENTICHE | **oc-developer** (meccanico, tutto specificato, nessun cambio del motore) o des-developer |
| **F8b** | esito: `final_positions`, `movement_ends`, `IN_PROGRESS` (`F8_IN_PROGRESS`), `OperationOutcome` | cambia l'esito di missione (non registrato) | 982 IDENTICHE | **des-developer** (tocca `run_session`, `Mission_Types`, `Session_Types`) |
| **F8-R** | ricerca dei tempi di turnaround e riparazione | nessuno | — | agente di ricerca (Sonnet, come per le RWR); in parallelo a F8a/F8b |
| **F8c** | prontezza, ciclo di campagna, posizione persistente, `CampaignState`, scenario S30 | nuovi moduli di campagna, nessun cambio di `run_session` | 982 IDENTICHE, **4 NUOVE** (S30) | **des-developer** (integrazione di piu' moduli e scenario nuovo) |
| **F6-B3** | secondo la decisione 26 | — | I1: identica | sessione principale (una riga di docstring) |

Ordine: F8a -> F8b -> F8c (F8c usa i tipi di F8a e i campi di F8b). F8-R in parallelo; il suo esito entra con un
commit di soli dati dopo F8c (cambiano solo le 4 esecuzioni di S30, v. §4.7). Ogni passo: suite e confronto con
`tools/ai/verifica.sh`, rapporto in `Analysis/Document/Rapporti/`.

### 4.1 F8a: tipi di campagna e validatore di sessione

#### File nuovo `Command/Campaign_Types.py`

Stile di `Command/Session_Types.py`: dataclass immutabili, validazione in `__post_init__`, mapping resi immutabili con
`MappingProxyType`. **Solo libreria standard** (nessun import da `Logic`, `Context`, `Asset`): `Context/Campaign_State`
non lo importa (riceve dizionari), quindi nessun ciclo. Tolleranza locale `_TIME_EPS = 1e-9` (come `Mission_Types.py:86`).

```python
# D4.b, decisione dell'utente (valori deliberati, NON stime): durata di default e massima di una sessione [s].
DEFAULT_SESSION_DURATION_S = 7_200.0
MAX_SESSION_DURATION_S = 14_400.0

@dataclass(frozen=True)
class SessionRules:
    default_duration_s: float = DEFAULT_SESSION_DURATION_S
    max_duration_s: float = MAX_SESSION_DURATION_S
    # __post_init__: numeri (bool escluso) > 0, default <= max, altrimenti TypeError/ValueError; salvati come float.
    def window(self, t_start: float, duration_s: Optional[float] = None) -> Tuple[float, float]:
        """(t_start, t_start + durata): durata None = default; <= 0 o > max -> ValueError."""

class ViolationCode(Enum):
    SESSION_OPEN = 'session_open'                  # t_end None
    SESSION_TOO_LONG = 'session_too_long'          # t_end - t_start > max
    SESSION_OVERLAP = 'session_overlap'            # t_start < fine effettiva della sessione precedente
    MISSION_ASSETS = 'mission_assets'              # blocco non passato o asset non del blocco
    ASSET_DESTROYED = 'asset_destroyed'
    ASSET_NOT_READY = 'asset_not_ready'
    MISSION_START_INVALID = 'mission_start_invalid'  # mission_movements/mission_start in errore (es. partenza prima di t_start)
    MISSION_BEYOND_SESSION = 'mission_beyond_session'
    MISSION_SPEED = 'mission_speed'                # regola A
    FUEL_MINIMUM = 'fuel_minimum'                  # G1, check_mission_fuel
    BINGO_AT_START = 'bingo_at_start'              # check_mission_bingo

@dataclass(frozen=True)
class SessionViolation:
    code: ViolationCode
    message: str                                   # non vuoto
    mission_id: Optional[str] = None
    asset_id: Optional[str] = None

class SessionValidationError(ValueError):
    """Ordine di sessione rifiutato. `session_id`, `violations` (tupla); messaggio = una riga per violazione."""
    def __init__(self, session_id: str, violations: Tuple[SessionViolation, ...]): ...
```

Nello stesso file, gia' nella F8a (il validatore riceve il registro come parametro facoltativo), i tipi del registro
di campagna, completi e con i loro test; le funzioni che li producono (`Logic/Readiness`) arrivano con la F8c:

```python
@dataclass(frozen=True)
class SessionRecord:
    session_id: str          # id di dominio non vuoto
    t_start: float
    t_end: float             # fine EFFETTIVA (SessionOutcome.t_end), >= t_start

@dataclass(frozen=True)
class ReadyRecord:
    asset_id: str
    ready_at: float          # istante di campagna [s] dal quale l'asset e' pronto
    since: float             # inizio del processo (rientro o ultimo danno)
    turnaround_s: float = 0.0  # >= 0: riarmo e rifornimento alla fine (ReadyRecord.rearm)
    repair_s: float = 0.0      # >= 0: salute a 100 alla fine (ReadyRecord.repair)
    # __post_init__: turnaround_s + repair_s > 0; ready_at >= since + turnaround_s + repair_s - _TIME_EPS
    #   (puo' essere maggiore: un processo precedente piu' lungo, v. Readiness)
    @property
    def rearm(self) -> bool: return self.turnaround_s > 0.0
    @property
    def repair(self) -> bool: return self.repair_s > 0.0

@dataclass(frozen=True)
class CampaignLedger:
    rules: SessionRules = SessionRules()
    sessions: Tuple[SessionRecord, ...] = ()           # in ordine; ciascuna t_start >= t_end della precedente - eps
    readiness: Mapping[str, ReadyRecord] = field(default_factory=dict, hash=False)  # chiave == record.asset_id;
                                                       # reso immutabile (MappingProxyType) e ordinato per id
    @property
    def last_end(self) -> Optional[float]: ...         # t_end dell'ultima sessione, None se nessuna
    def ready_at(self, asset_id: str) -> Optional[float]: ...   # None = nessun processo in corso
    def is_ready(self, asset_id: str, t: float) -> bool: ...    # nessun record o ready_at <= t + eps
    def with_session(self, record: SessionRecord) -> 'CampaignLedger': ...   # ValueError se si sovrappone
    def with_readiness(self, readiness: Mapping[str, ReadyRecord]) -> 'CampaignLedger': ...  # SOSTITUISCE la mappa
    def to_dict(self) -> Dict: ...                     # solo tipi JSON, chiavi ordinate
    @classmethod
    def from_dict(cls, data: Mapping) -> 'CampaignLedger': ...   # inversa esatta di to_dict
```

#### `Logic/Mission_Adapter.py`: nuova funzione

```python
def mission_planned_end(mission: Mission, movements: Sequence[AssetMovement]) -> Optional[float]:
    """Istante assoluto [s] della fine PIANIFICATA della missione (F8, D4.c): il piu' tardo fra gli arrivi all'ultimo
    punto degli asset (`waypoint_times(movement)[-1]`, attese comprese); missione senza rotta: partenza
    (`movements[0].start`) + `EndCriteria.max_duration_s` se dichiarata, altrimenti None (dura fino alla fine della
    sessione, D4.e). Funzione pura."""
```
Da mettere dopo `waypoint_times` (`:1107`). Docstring del modulo: aggiornare `:71-73` ("le missioni fuori finestra
sono rifiutate dal validatore di sessione, `Logic/Session_Validator`").

#### `Logic/Session_Simulator.py`: due ritocchi senza cambio di comportamento

1. Nuova funzione pubblica, accanto a `_collect_forces` (`:1027`):
   ```python
   def session_blocks(order: SessionOrder, forces_a: Iterable, forces_b: Iterable) -> Dict[str, object]:
       """I blocchi della sessione per id di dominio, con le stesse verifiche di `run_session` (F8: li usa il
       validatore di sessione). `_collect_forces(order, forces_a, forces_b)[2]`."""
   ```
2. In `run_session`, subito dopo il calcolo di `mission_movements` (`:2208-2210`), per ogni missione nell'ordine
   dell'ordine: `end = MA.mission_planned_end(mission, mission_movements[mission.mission_id])`; se `end is not None and
   end > session_end + CS.TIME_EPS`: `logger.warning(f"run_session: mission {id!r} is planned to end at t={end:.1f}, after
   the session end t={session_end:.1f}: its route is cut (E4); the session validator (Logic/Session_Validator) rejects
   it")`. Nessun altro effetto. Aggiornare il docstring (sezione nuova "Validazione di sessione (F8)": il validatore e'
   fuori, qui solo il warning).

#### File nuovo `Logic/Session_Validator.py`

```python
def validate_session(order: SessionOrder, forces_a: Iterable, forces_b: Iterable, *,
                     ledger: Optional[CampaignLedger] = None, rules: Optional[SessionRules] = None,
                     horizon: Optional[float] = None) -> Tuple[SessionViolation, ...]:
def check_session(order, forces_a, forces_b, *, ledger=None, rules=None, horizon=None) -> None:
    """validate_session; se c'e' almeno una violazione, SessionValidationError(order.session_id, violazioni)."""
```

Comportamento di `validate_session` (funzione pura: nessuna mutazione degli asset, nessuna estrazione casuale), con le
violazioni nell'ordine dei punti sotto e, dentro il punto 5, nell'ordine delle missioni dell'ordine e degli asset della
missione. Tolleranza: `TIME_EPS` = `Contact_Scheduler.TIME_EPS`.
1. `rules` = `rules` se dato, altrimenti `ledger.rules` se c'e' il registro, altrimenti `SessionRules()`.
2. **Finestra**: `order.t_end is None` -> `SESSION_OPEN`, e `session_end` = `t_start + horizon` se `horizon` e' dato,
   altrimenti None (si saltano i controlli di fine missione); altrimenti `session_end = order.t_end` e `t_end - t_start >
   rules.max_duration_s + TIME_EPS` -> `SESSION_TOO_LONG`.
3. **Disgiunzione**: `ledger is not None and ledger.last_end is not None and order.t_start < ledger.last_end - TIME_EPS`
   -> `SESSION_OVERLAP`.
4. **Blocchi**: `blocks = SS.session_blocks(order, forces_a, forces_b)` (gli errori strutturali delle forze, forze
   duplicate o fuori `force_ids`, restano `ValueError` propagati: sono errori di programma, non di pianificazione);
   `assets = {id di dominio: asset}` di tutti i blocchi (come `assets_by_id` di `run_session`).
5. **Per missione** (`order.missions` in ordine):
   a. blocco assente -> `MISSION_ASSETS` (messaggio di `_check_missions`); altrimenti `check_mission_assets(mission,
      block)` in `try`: `ValueError` -> `MISSION_ASSETS`. In entrambi i casi si passa alla missione successiva.
   b. per ogni `asset_id` di `mission.asset_ids`: asset distrutto (`getattr(asset, 'is_destroyed', lambda: False)()`) -> `ASSET_DESTROYED`;
      altrimenti, con il registro, `not ledger.is_ready(asset_id, order.t_start)` -> `ASSET_NOT_READY` (messaggio con
      `ready_at` e il tipo di processo: turnaround, riparazione o entrambi).
   c. `bases = MA.air_base_points(blocks.values(), side)` per le missioni aeree (`side` del blocco), `()` altrimenti;
      `movements = MA.mission_movements(mission, order.t_start, bases)` in `try`: `ValueError` ->
      `MISSION_START_INVALID` e si saltano d-f.
   d. `end = MA.mission_planned_end(mission, movements)`; con `session_end` non None: `end is not None and end >
      session_end + TIME_EPS` -> `MISSION_BEYOND_SESSION` (messaggio: fine pianificata, fine della sessione, eccedenza).
   e. `MA.check_mission_speed(mission, assets, order.t_start)` in `try`: `ValueError` -> `MISSION_SPEED`.
   f. solo missioni aeree: `MA.check_mission_fuel(mission, assets, order.t_start, bases)` -> `FUEL_MINIMUM`; se
      `SS.F6_BINGO`: `MA.check_mission_bingo(mission, assets, bases, order.t_start,
      reverse_route=SS.F6_BINGO_REVERSE_ROUTE, disengage_reserve=SS.F6_BINGO_DISENGAGE_RESERVE)` -> `BINGO_AT_START`.
      Gli interruttori si leggono al momento della chiamata come attributi del modulo `SS` (cosi' un test che li
      spegne con `patch.object` li vede). Il messaggio e' quello del `ValueError` (nomina gia' l'asset);
      `asset_id` della violazione None.
6. Log: `logger.debug` per ogni violazione, `logger.info` del numero totale.

Il validatore NON ripete i controlli della porta (`SessionOrder` gia' rifiuta un asset in due missioni e i blocchi fuori
`force_ids`) ne' quello del loadout della F7a (resta in `run_session`).

#### Test della F8a

- `Test/Test_Campaign_Types.py` (nuovo): `SessionRules` (default 7200/14400; `window(0)` = (0, 7200); `window(0, 3600)`;
  durata 0, negativa, > max, bool -> errore; default > max -> `ValueError`); `SessionViolation`/`ViolationCode`
  (messaggio vuoto -> errore); `SessionValidationError` (e' un `ValueError`, porta `violations`, una riga per
  violazione); `SessionRecord` (t_end < t_start -> errore); `ReadyRecord` (entrambi i tempi nulli -> errore, `ready_at`
  troppo presto -> errore, `rearm`/`repair`); `CampaignLedger` (immutabile; `last_end`; `is_ready` senza record,
  prima/dopo `ready_at`; `with_session` che si sovrappone -> `ValueError`, contigua ammessa; `with_readiness` sostituisce;
  `to_dict`/`from_dict` andata e ritorno identici e serializzabili con `json.dumps`).
- `Test/Test_Session_Validator.py` (nuovo), con forze minime costruite con `Scenario_Fixtures` (come
  `Test_Session_Simulator`): un ordine valido -> tupla vuota e `check_session` non solleva; un caso per ogni codice
  (sessione aperta, 4 h + 1 s, sovrapposta al registro, blocco assente, asset distrutto (`asset.health = 0`), asset non
  pronto (registro con `ReadyRecord`), TOT che porta la partenza prima di `t_start`, missione che arriva dopo `t_end`
  (fine 5000 s in una sessione di 3600 s, come `S22-E3 not_departed`), regola A violata, carburante sotto il minimo (il
  caso `DRY_FUEL` di S26) che produce `FUEL_MINIMUM` **e** `BINGO_AT_START`, lo stesso con `patch.object(SS, 'F6_BINGO',
  False)` che produce solo `FUEL_MINIMUM`); piu' violazioni nello stesso ordine raccolte tutte e nell'ordine dichiarato;
  missione con `EndCriteria(bingo=False)` non controllata per il carburante; missione sul posto (terra, senza rotta)
  ammessa; il validatore non muta gli asset (carburante, salute e posizione uguali prima e dopo).
- `Test/Test_Mission_Adapter.py` (esistente): `mission_planned_end` con e senza attese (WAIT), missione sul posto con e
  senza `max_duration_s`.
- `Test/Test_Session_Simulator.py`: `session_blocks` restituisce i blocchi per id; una missione oltre la fine produce il
  warning (`assertLogs` sul logger del modulo, o il logger mockato come negli altri test) e lo stesso esito di prima.

#### Esito atteso della F8a

Suite verde con i test nuovi; confronto: **982 IDENTICHE, 0 cambiate, 0 nuove** (il warning non cambia nulla).

### 4.2 F8b: l'esito porta posizioni, fine del movimento, "in corso" ed esito d'Operazione

#### `Command/Mission_Types.py`

- `MissionStatus.IN_PROGRESS = 'in_progress'` (commento: "missione non finita alla fine della sessione: almeno un
  asset superstite ancora sulla rotta o sul posto (SESSION_END), F8, D4.e"). `MissionOutcome.__post_init__` non cambia
  (IN_PROGRESS non ammette `reason`, gia' cosi' per ogni stato diverso da ABORTED).
- Nuovo enum `OperationStatus`: `SUCCEEDED = 'succeeded'`, `FAILED = 'failed'`, `IN_PROGRESS = 'in_progress'`.
- Nuova dataclass, dopo `MissionOutcome`:
  ```python
  @dataclass(frozen=True)
  class OperationOutcome:
      operation_id: str
      status: OperationStatus
      mission_statuses: Mapping[str, MissionStatus] = field(default_factory=dict, hash=False)
      # __post_init__: id di dominio; status coerced; mission_statuses non vuoto, chiavi id di dominio, valori
      # MissionStatus (coerced), reso immutabile e ordinato per id.
  ```
- Docstring del modulo: la riga "Nessuna logica di calcolo (... esito di un'Operazione)" resta vera (il calcolo e' in
  `Session_Types`).

#### `Command/Session_Types.py`

- Nuova funzione pura (aggregazione, nello spirito del modulo):
  ```python
  def operation_outcome(operation: Operation, mission_outcomes: Mapping[str, MissionOutcome]) -> OperationOutcome:
      """Esito dell'Operazione dalla sua regola dichiarata (D2.e, F8): tabella §2.H della Proposta F8.
      ValueError se manca l'esito di una sua missione."""
  ```
- `SessionOutcome`, tre campi nuovi in coda (default vuoti, `hash=False`, resi immutabili e ordinati per chiave):
  - `operation_outcomes: Mapping[str, OperationOutcome]` (chiave == `operation_id` dell'esito);
  - `final_positions: Mapping[str, Tuple[float, float, float]]` (posizione [m] di ogni asset alla fine NOMINALE della
    sessione; tre float finiti, `float` di Python);
  - `movement_ends: Mapping[str, float]` (istante [s] in cui l'asset di missione ha smesso di muoversi nella sessione).
  Validazioni nuove nello stile di `_check_postures`. Docstring degli attributi aggiornato (F8).
- `assemble_session_outcome(..., operation_outcomes=None, final_positions=None, movement_ends=None)`: riportati tali e
  quali (None = vuoto), come `postures`.

#### `Logic/Session_Simulator.py`

- Interruttore nuovo, accanto a `F7_AREA_FIRE` (`:876-881`), con il commento nello stile degli altri:
  ```python
  # F8, stato "in corso" (decisione 23 dell'utente):
  #   * `F8_IN_PROGRESS` (ATTIVO): una missione non distrutta, non completata e non abortita con almeno un asset
  #     superstite ancora sulla rotta o sul posto alla fine della sessione (SESSION_END) e' IN_PROGRESS. Spento: FAILED,
  #     come prima. La fotografia non registra lo stato di missione.
  F8_IN_PROGRESS = True     # (o False, secondo la decisione 23)
  ```
- `_mission_outcome` (`:2096-2109`): fra il ramo `aborted` e `FAILED`:
  ```python
  elif F8_IN_PROGRESS and any(o.end_reason is AssetEndReason.SESSION_END for o in survivors):
      status = MissionStatus.IN_PROGRESS
  ```
  (con `F6_END_CRITERIA` spento la regola provvisoria della F6-A resta com'e', piu' questo ramo).
- Porta di uscita (`:3079-3102`), dopo le posture:
  ```python
  final_positions = {}
  for asset_id in sorted(assets_by_id):
      legs = all_legs.get(asset_id)
      point = CS.position_on_legs(legs, session_end) if legs else None
      if point is not None:
          final_positions[asset_id] = tuple(float(c) for c in point)
  movement_ends = {asset_id: float(legs[-1].t_end) for asset_id, legs in sorted(moving_legs.items()) if legs}
  operation_outcomes = {op.operation_id: operation_outcome(op, mission_outcomes) for op in order.operations}
  ```
  e i tre dizionari passati ad `assemble_session_outcome`. `session_end` e' la fine NOMINALE (`t0 + horizon`), non
  `latest`: le salve in volo non muovono nessuno. `all_legs` e `moving_legs` sono i dizionari definitivi (dopo bingo,
  esaurimento e ri-pianificazione G4b). Gli asset senza tratti (aereo perso alla partenza) non hanno posizione.
- Docstring: "Esito di missione" con IN_PROGRESS; sezione nuova "Esito per la campagna (F8)": posizioni finali, fine
  del movimento, esito delle Operazioni; "Cosa NON fa" (`:713-719`): non applica le posizioni agli asset (lo fa
  `Session_Campaign.apply_final_positions`), non scrive `Campaign_State`.

#### Effetti sui chiamanti (F8b)

- `SessionOutcome` e' costruito solo da `assemble_session_outcome` in produzione; i test che costruiscono
  `SessionOutcome` a mano non passano i campi nuovi (default vuoti): nessun cambio.
- `Test_Session_Validation.test_every_id_in_the_outcome_is_a_domain_id` e `test_every_time_is_seconds_within_the_session`
  visitano tutte le foglie dell'esito (`_OutcomeWalker`, `Test_Session_Validation.py:242-259`): i valori nuovi devono
  essere `float`/`str`/enum (nessun `Point3D` sympy, nessun numpy) e nessun campo nuovo si chiama `time` o come un
  campo id (`target_id`, `source_id`, `asset_id`, `force_id`, `block_id`). `OperationOutcome` usa `operation_id` e
  `mission_statuses`: va bene.
- `Scenario_Baseline.summarize_run` non legge i campi nuovi (decisione 27): fotografia invariata.
- Test da aggiornare per `F8_IN_PROGRESS` attivo: `Test_Session_Simulator.test_route_cut_by_the_session_end_fails`
  (`:756-762`) diventa `test_route_cut_by_the_session_end_is_in_progress` (IN_PROGRESS) con la controprova
  `patch.object(SS, 'F8_IN_PROGRESS', False)` -> FAILED. Gli altri due test che verificano FAILED
  (`Test_Session_Simulator.py:1355`, `Test_Session_Scenarios_S25.py:507`) hanno la rotta completata (nessun
  `SESSION_END`): restano FAILED; l'esecutore lo verifica eseguendoli (v. anche §1.8).

#### Test della F8b

- `Test_Mission_Types.py`: `IN_PROGRESS` esiste e un `MissionOutcome` IN_PROGRESS con `reason` -> `ValueError`;
  `OperationOutcome` (validazioni, immutabilita', ordine).
- `Test_Session_Types.py`: `operation_outcome` per le 3 regole x i casi della tabella §2.H (almeno 9 casi, con
  IN_PROGRESS), missione mancante -> `ValueError`; `SessionOutcome` con i campi nuovi (validazione: chiave diversa
  dall'id, posizione non a 3 componenti o non finita, tempo non numerico -> errore; ordinamento per chiave);
  `assemble_session_outcome` li riporta.
- `Test_Session_Simulator.py`: (1) `final_positions`: un'unita' di terra arrivata a destinazione ha la posizione
  dell'ultimo punto; un asset senza missione la sua posizione iniziale; un aereo atterrato su una base vera il punto
  d'atterraggio; un aereo `off_scene` il punto d'uscita (la decisione di non applicarla e' della F8c); (2)
  `movement_ends` = istante d'arrivo (rotta completata), istante d'esaurimento (fermo per carburante), assente per gli
  asset senza missione; (3) IN_PROGRESS come sopra; (4) `operation_outcomes`: un'Operazione ALL con una missione
  completata e una tagliata dalla fine della sessione -> IN_PROGRESS; con `F8_IN_PROGRESS` spento -> FAILED.

#### Esito atteso della F8b

Suite verde; confronto: **982 IDENTICHE** (stato di missione, posizioni ed esiti d'Operazione non sono nella
fotografia; nessuna estrazione RNG nuova, nessun tratto cambiato).

### 4.3 F8-R: ricerca dei tempi (in parallelo)

Compito per un agente di ricerca (nessun codice): compilare `Analysis/Document/Ricerca_Turnaround_Riparazione.md` con
una tabella per **classe** `Air_Asset_Type` (Fighter, Fighter_Bomber, Attacker, Bomber, Heavy_Bomber, Awacs, Recon,
Transport, Helicopter): tempo di turnaround fra due sortite in operazioni sostenute (riarmo, rifornimento, controlli),
valore proposto, intervallo, fonti; una riga per terra (riorganizzazione e rifornimento di un reparto meccanizzato) e una
per mare (rifornimento e riarmo in porto); per dominio, il tempo di riparazione di un danno grave riparabile. Ogni valore
con fonte e livello di confidenza; dove non ci sono fonti, dichiararlo. L'utente approva i valori; un commit di soli dati
aggiorna `Context` (§4.4) e i commenti passano da "STIMA DI PROGETTO" a "ricerca F8-R (data, fonti in ...)".

### 4.4 F8c: prontezza, ciclo di campagna, posizione persistente

#### `Context/Context.py`: tabelle (D6.b: "un tempo per classe in `Context`")

Dopo `AIR_MILITARY_CRAFT_ASSET` (`:1001`), con un commento che dichiara: "F8 (D6.b-d): tempi [s]. STIME DI PROGETTO
(ordini di grandezza), NON dati tarati: da sostituire con la ricerca F8-R."

| Costante | Chiave | Valore (STIMA) |
|---|---|---|
| `AIR_TURNAROUND_S` (dict) | `Air_Asset_Type.FIGHTER.value` | 7 200 (2 h) |
| | `FIGHTER_BOMBER` | 9 000 (2,5 h) |
| | `ATTACKER` | 9 000 (2,5 h) |
| | `BOMBER` | 14 400 (4 h) |
| | `HEAVY_BOMBER` | 28 800 (8 h) |
| | `AWACS` | 14 400 (4 h) |
| | `RECON` | 7 200 (2 h) |
| | `TRANSPORT` | 10 800 (3 h) |
| | `HELICOPTER` | 5 400 (1,5 h) |
| `AIR_TURNAROUND_DEFAULT_S` | classe ignota | 9 000 (2,5 h) |
| `GROUND_TURNAROUND_S` | reparto terrestre | 21 600 (6 h) |
| `SEA_TURNAROUND_S` | nave | 43 200 (12 h) |
| `REPAIR_TIME_FULL_S` (dict) | `'air'` / `'ground'` / `'sea'` | 86 400 / 86 400 / 259 200 (24 h / 24 h / 72 h) per un danno da 100 a 0 |

Nessun valore ha una fonte nel repository: sono scelti solo perche' abbiano l'ordine di grandezza giusto rispetto a
sessioni di 2 h (un caccia atterrato a meta' sessione salta la sessione successiva, un bombardiere pesante ne salta
quattro, un reparto terrestre tre). Vanno dichiarati cosi' nel codice e nel rapporto.

#### File nuovo `Logic/Readiness.py`

Funzioni pure salvo `apply_campaign_processes` (che muta gli asset, come `apply_engagement_result`); nessun RNG;
iterazioni sempre in ordine di id.

```python
def asset_domain(asset) -> str:
    """'air' (`validate_class(asset, 'Aircraft')`), 'sea' ('Ship'), altrimenti 'ground' (veicoli, strutture): la stessa
    partizione di `Mission_Adapter.continuous_posture`."""

def turnaround_class(asset) -> Optional[str]:
    """Classe aerea per il turnaround: `asset.asset_type` (valore di `Air_Asset_Type`, o il membro dell'enum: si usa
    `.value`) se e' una chiave di `AIR_TURNAROUND_S`; altrimenti la prima classe di `Aircraft_Data` per `asset.model`
    (`category[0]`); altrimenti None. None per gli asset non aerei."""

def turnaround_s(asset) -> Tuple[float, str]:
    """(secondi, provenienza): aereo = `AIR_TURNAROUND_S[classe]` ('class:<classe>') o `AIR_TURNAROUND_DEFAULT_S`
    ('default', con un warning); terra = `GROUND_TURNAROUND_S` ('ground'); mare = `SEA_TURNAROUND_S` ('sea')."""

def repair_s(asset) -> Optional[float]:
    """Tempo di riparazione [s] dal danno attuale: None se distrutto (`is_destroyed()`) o salute non leggibile; 0.0 se
    salute >= 100; altrimenti `REPAIR_TIME_FULL_S[asset_domain(asset)] * (100 - salute) / 100` (lineare, STIMA)."""

def readiness_after_session(ledger: CampaignLedger, order: SessionOrder, outcome: SessionOutcome,
                            assets: Mapping[str, object]) -> Dict[str, ReadyRecord]:
    """La nuova mappa di prontezza dopo la sessione (regola sotto)."""

def record_session(ledger: CampaignLedger, order: SessionOrder, outcome: SessionOutcome,
                   assets: Mapping[str, object]) -> CampaignLedger:
    """`ledger.with_session(SessionRecord(order.session_id, order.t_start, outcome.t_end))` (se `outcome.t_end` e'
    None: `order.t_end`) `.with_readiness(readiness_after_session(...))`."""

def apply_campaign_processes(ledger: CampaignLedger, assets: Mapping[str, object], t: float) -> CampaignLedger:
    """Processi di campagna fra sessioni (D4.d) conclusi entro `t`: per ogni record con `ready_at <= t + eps`, in ordine
    di id: asset assente -> record tolto con un warning; asset distrutto -> record tolto; `record.repair` ->
    `asset.health = 100`; `record.rearm` -> riarmo e rifornimento (`_rearm_and_refuel`); record tolto. Restituisce il
    registro con i soli record non conclusi. IDEMPOTENTE (riapplicarlo con lo stesso registro e lo stesso `t` lascia
    gli asset nello stesso stato)."""

def _rearm_and_refuel(asset) -> None:
    """Aereo con `assigned_loadout` non None: `asset.assigned_loadout = asset.assigned_loadout` (scorta e pieno del
    loadout, `Aircraft.py:176-213`); aereo senza loadout: niente (non modellato). Veicolo/nave:
    `load_stores_from_registry()` e `load_fuel_from_registry()` se esistono. Nessun consumo delle scorte del blocco
    (logistica fuori F8, dichiarato)."""

def ready_assets(ledger: CampaignLedger, assets: Mapping[str, object], t: float) -> Tuple[str, ...]:
    """Id (ordinati) degli asset non distrutti e pronti a `t`: cio' che il pianificatore puo' impiegare (D6.a)."""
```

**Regola di `readiness_after_session`** (decisioni 19-21), per ogni `asset_id` in `sorted(assets)`:
Definizioni: `end_nominal` = `order.t_end` (o `outcome.t_end` per un ordine aperto); `previous` =
`ledger.readiness.get(asset_id)`; `in_mission` = l'asset e' in una missione dell'ordine; `consumed` = l'asset compare con
valore > 0 in `outcome.ammunition_consumed()`, `outcome.interceptions_consumed()` o `outcome.fuel_consumed()`;
`last_damage` = l'istante massimo dei `DamageEvent` dell'esito con `target_id == asset_id` (None se nessuno).
1. asset distrutto (`getattr(asset, 'is_destroyed', lambda: False)()`, come in `Session_Simulator`) -> nessun record
   (mai pronto; il validatore lo rifiuta con `ASSET_DESTROYED`).
2. **Nulla di nuovo nella sessione** (`not in_mission and not consumed and last_damage is None`): se `previous` c'e'
   resta COM'E' (un processo in corso non riparte); se non c'e' e `repair_s(asset) > 0` (danno anteriore al registro)
   -> record di sola riparazione con `since = end_nominal`, `ready_at = end_nominal + repair`; altrimenti nessun record.
3. Altrimenti: `turnaround` = `turnaround_s(asset)[0]` se `in_mission or consumed`, altrimenti 0; `repair` =
   `repair_s(asset)` (0 se intatto). Se entrambi sono 0, `previous` resta com'e' (o nessun record).
4. Inizio `base`: per un asset di missione `outcome.movement_ends.get(asset_id)`, altrimenti l'`end_time` del suo
   `AssetMissionOutcome`, altrimenti `end_nominal`; per un asset senza missione `end_nominal`.
5. `since = max(base, last_damage)` (sui valori non None); `ready_at = since + turnaround + repair`; se `previous` c'e',
   `ready_at = max(ready_at, previous.ready_at)`.
6. Record `ReadyRecord(asset_id, ready_at, since, turnaround, repair)`.
I record degli asset non presenti in `assets` restano (forze non passate a questa sessione).

#### File nuovo `Logic/Session_Campaign.py` (il conduttore minimo, non il `Theater_Session_Manager`)

```python
def apply_final_positions(outcome: SessionOutcome, forces_a: Iterable, forces_b: Iterable) -> Dict[str, Tuple[float, float, float]]:
    """Applica `outcome.final_positions` agli asset delle forze (D1.d). Per ogni asset (ordine di id) con una posizione:
    postura `Mission_Adapter.OFF_SCENE_POSTURE` -> NON applicata (rientrato fuori scena, la posizione resta quella di
    partenza, decisione 22); aereo con postura diversa da `PARKED_POSTURE` e `DESTROYED_POSTURE` -> applicata con un
    warning ("in volo a fine sessione"); altrimenti applicata. `asset.position = Point3D(x, y, z)` con le coordinate
    arrotondate a `Mission_Adapter.OFFSET_DECIMALS` (rumore della rotazione). Restituisce `{asset_id: posizione}` delle
    sole posizioni applicate."""

def run_campaign_session(ledger: CampaignLedger, order: SessionOrder, forces_a: Iterable, forces_b: Iterable,
                         fire_control: Callable, *, apply_positions: bool = True,
                         **run_kwargs) -> Tuple[SessionOutcome, CampaignLedger]:
    """Una sessione nel ciclo di campagna (F8): (1) `apply_campaign_processes(ledger, assets, order.t_start)`;
    (2) `check_session(order, forces_a, forces_b, ledger=ledger, horizon=run_kwargs.get('horizon'))` (solleva
    `SessionValidationError`: i processi del punto 1 sono gia' applicati agli asset, e riapplicarli e' idempotente);
    (3) `SS.run_session(order, forces_a, forces_b, fire_control, **run_kwargs)`; (4) con `apply_positions`,
    `apply_final_positions`; (5) `record_session`. Restituisce `(esito, nuovo registro)`."""
```

Vincolo: `run_session` va chiamata come **attributo del modulo** (`from Code.Dynamic_War_Manager.Source.Logic import
Session_Simulator as SS`; `SS.run_session(...)`), mai importata per nome: `Scenario_Baseline` la intercetta cosi'
(`Scenario_Baseline.py:20-26`). Il modulo e' del core e non sa nulla del simulatore: un adapter DCS sostituirebbe il
solo punto (3).

#### `Context/Campaign_State.py`

- `restore(self, mission_id, regions, restore_position: bool = False)`: inoltra a `_restore_region` ->
  `_restore_block` -> `_restore_asset(asset, asset_snap, restore_position)`; con True e `asset_snap["position"]` non
  None: `asset.position = Point3D(x, y, z)` (warning se fallisce, come gli altri campi). Default False: comportamento
  di oggi. Docstring di `restore` (elenco dei campi) aggiornato.
- `add_ledger(self, mission_id: str, ledger: Mapping) -> None`: salva il dizionario (`CampaignLedger.to_dict()`) in
  `self._state[mission_id]["ledger"]` (KeyError se la missione di campagna non e' registrata); `get_ledger(self,
  mission_id) -> Optional[Dict]`. Nessun import di `Command`: il chiamante converte con `CampaignLedger.from_dict`.
  Nota terminologica nel docstring: qui `mission_id` e' la missione di CAMPAGNA (una sessione), non la `Mission`.

#### Scenario nuovo S30-CAMPAIGN (`Test/Test_Session_Scenarios_S30.py`)

Classe `TestS30CampaignSequence(F.LoggerSilencer, unittest.TestCase)`; tutte le sessioni in `setUpClass` con
`Session_Campaign.run_campaign_session` (le chiamate a `run_session` passano dal modulo e sono registrate dalla
fotografia). **Nessun contatto** (nessuna estrazione RNG): la storia dipende solo da geometria, tempi e costanti.
Costruzione con `Scenario_Fixtures` e i modelli gia' usati (le scelte di dettaglio, posizioni esatte e helper, sono
dell'esecutore, da elencare nel rapporto):
- **Blue-Base**: base aerea Blue (Military `F.AIR_UNIT` con una struttura `'Farp'` in (0, 0), come `Blue-Base` di S26);
- **Blue-Wing**: 2 F-16C Block 52d con loadout 'Strike', parcheggiati sulla base; una missione ad anello
  DEPARTURE (base) -> NAV (100 km, 0, 5000 m) -> LAND (base), partenza dal parcheggio (come S22-AIR / S26), carburante
  del loadout (sopra il minimo G1);
- **Blue-Mech**: 2 M1A2-Abrams in (0, -20 km); `mbt0` in missione `'Movement'` (categoria POSITIONING: bersaglio
  `Target` POINT sulla destinazione) fino a (10 km, -20 km) alla velocita' nominale del registro; `mbt1` senza missione
  e **danneggiato prima della prima sessione** (`health = 60`, danno anteriore al registro);
- **Red-Depot**: un blocco Red con una struttura a (300 km, 0) (nessun sensore utile, nessun contatto).

Sequenza (istanti calcolati in `setUpClass` dalle costanti e dal registro, mai scritti a mano):
1. `S30-CAMPAIGN-1`: `SessionRules().window(0.0)` = [0, 7200]; le due missioni. Attesi: `mbt0` a (10 km, -20 km) in
   `final_positions` e in `asset.position`; F-16C a terra sulla base (`parking_cold`); registro: F-16C pronti a
   `movement_ends + turnaround_s` (classe Fighter), `mbt0` a `arrivo + GROUND_TURNAROUND_S`, `mbt1` a `7200 + repair_s`
   (riparazione in corso, salute 60).
2. Sessione 2 a `t2 = ledger.last_end` (finestra di 2 h). Precondizione verificata dal test con un messaggio esplicito:
   `ledger.ready_at('mbt0') > t2` (vera con le stime della §4.4; se la ricerca F8-R la rendesse falsa va allungata la
   rotta della sessione 1, non tolta l'asserzione). Un ordine con una missione per `mbt0` -> `SessionValidationError`
   con `ASSET_NOT_READY` per `mbt0`; `ready_assets(ledger, assets, t2)` = esattamente gli asset il cui `ready_at` nel
   registro e' <= `t2` (con le stime: nessuno dei quattro). Poi
   `S30-CAMPAIGN-2` senza missioni: `final_positions['mbt0']` = (10 km, -20 km) (**posizione ripresa**: e' fermo dove
   l'aveva lasciato la sessione 1), `mbt1` salute 60.
3. `S30-CAMPAIGN-3` a `t3 = max(ledger.last_end, ledger.ready_at('mbt0'))` (finestra di 2 h): `mbt0` rifornito
   (carburante = pieno) e pronto; una missione da (10 km, -20 km) a (20 km, -20 km), costruita con `F.missions_for`
   DOPO la sessione 2 (legge `asset.position`, quindi parte dalla posizione persistita), **accettata**; `mbt1` ancora in
   riparazione (precondizione `ledger.ready_at('mbt1') > t3`; record presente, salute 60, `ASSET_NOT_READY` se lo si
   mette in una missione).
4. `S30-CAMPAIGN-4` a `t4 = max(ledger.last_end, ledger.ready_at('mbt1'))`: `mbt1` riparato (salute 100), assente dal
   registro, impiegabile. Con le stime della §4.4 la riparazione di `mbt1` (0,4 x 24 h dalla fine della sessione 1)
   finisce a 41 760 s e non e' ripartita nelle sessioni 2 e 3 (regola 2: nulla di nuovo per `mbt1`).

`Scenario_Baseline.UNITS`: aggiungere in coda `('S30-CAMPAIGN', 'Test_Session_Scenarios_S30', 'TestS30CampaignSequence',
None, _single_or_index)`. Nomi stabili: chiavi `S30-CAMPAIGN/S30-CAMPAIGN-1` ... `-4` (un `session_id` per sessione,
nessuna variante). Test:
- `test_positions_persist` (1, 2, 3), `test_not_ready_asset_is_rejected` (2), `test_ready_assets` (2, 3),
  `test_repair_in_progress_then_done` (1-4), `test_turnaround_rearms_and_refuels` (3: carburante e scorta tornati al
  pieno del registro), `test_sessions_are_disjoint` (una sessione che parte prima della fine della precedente ->
  `SESSION_OVERLAP`), `test_ledger_round_trip` (registro in `CampaignState.add_ledger`/`get_ledger` e
  `from_dict` identico), `test_restore_position` (`CampaignState.restore(..., restore_position=True)` riporta la
  posizione della sessione 1 su forze ricostruite).

#### Altri test della F8c

- `Test/Test_Readiness.py` (nuovo): `asset_domain`; `turnaround_class` (enum, stringa, dal registro, ignota);
  `turnaround_s` per ogni classe della tabella e il default con warning, terra, mare; `repair_s` (100 -> 0, 60 -> 0,4 x
  pieno, distrutto -> None); `readiness_after_session` sui casi 1-6 della regola con un `SessionOutcome` costruito a
  mano (asset distrutto, di missione con `movement_ends`, senza missione che ha consumato, danneggiato senza danno
  nella sessione, riparazione in corso che NON riparte in una sessione senza novita' (regola 2), record precedente piu'
  lungo che prevale); `apply_campaign_processes` (salute a 100, riarmo
  dell'aereo con la riassegnazione del loadout, rifornimento del veicolo, record non concluso che resta, asset
  assente, idempotenza); `ready_assets`; nessun uso del modulo `random` (come gli altri test di determinismo, se ce
  n'e' uno: altrimenti non serve).
- `Test/Test_Session_Campaign.py` (nuovo): `apply_final_positions` (unita' di terra spostata, aereo parcheggiato, aereo
  `off_scene` non spostato, aereo in volo con warning, asset senza posizione); `run_campaign_session` con un ordine non
  valido (solleva e non chiama `run_session`: `patch.object(SS, 'run_session')` con un `MagicMock` non chiamato).
- `Test/Test_Campaign_State.py`: `restore` senza parametro non tocca la posizione (comportamento di oggi); con
  `restore_position=True` la imposta; `add_ledger`/`get_ledger` (missione non registrata -> `KeyError`).
- `Test/Test_Context.py`: ogni `Air_Asset_Type` ha una voce in `AIR_TURNAROUND_S`; tutti i valori > 0;
  `REPAIR_TIME_FULL_S` ha 'air', 'ground', 'sea'.

#### Esito atteso della F8c

Suite verde; confronto: **982 IDENTICHE, 0 cambiate, 4 NUOVE** (`S30-CAMPAIGN/S30-CAMPAIGN-1..4`). La fotografia NON va
installata dall'esecutore: la installa la sessione principale dopo l'approvazione (986 esecuzioni).

### 4.5 F6-B3 (decisione 26)

- **I1 (R)**: una frase nel docstring di `TestS24DryAircraft` (`Test_Session_Scenarios_S24.py:357`): "dichiara
  `EndCriteria(bingo=False)`: volo che non rientra al bingo (lo scenario prova la planata della F6-A); il bingo alla
  partenza e' in S26; il validatore di sessione della F8 non controlla il carburante di una missione con `bingo`
  False". Piano §5: F6-B3 chiusa. Fotografia identica.
- I2: togliere `bingo=False`, riscrivere i test di S24-GLIDE sulle grandezze della §1.6 (rientro, esaurimento a 187,5 s,
  perdita in `glide`; a terra e colpito in `off`), accettare 24 esecuzioni cambiate; aggiungere varianti `bingo=False`
  per la planata (nomi nuovi).
- I3: tre varianti nuove in coda a `VARIANTS` (`glide_bingo`, `no_base_bingo`, `off_bingo`) e una voce di nome nella
  tabella `UNITS` se serve; 24 nuove.

### 4.6 Vincoli comuni

- **RNG**: nessuna estrazione nuova in nessun passo; l'ordine delle estrazioni esistenti non cambia (validatore,
  prontezza, posizioni ed esiti d'Operazione non usano numeri casuali; S30 non ha contatti). Mai il modulo `random`.
- **Interruttori**: uno solo nuovo nel motore, `Session_Simulator.F8_IN_PROGRESS` (decisione 23). Validatore,
  prontezza e posizioni non sono regole del motore: sono funzioni nuove fuori da `run_session`, quindi gli scenari che
  chiamano `run_session` non cambiano; le funzioni di `Campaign_State` cambiate hanno un parametro con default che
  riproduce il comportamento di oggi (`restore_position=False`).
- **Core indifferente al simulatore**: nessun modulo nuovo importa l'adapter DCS o dati del simulatore; il conduttore
  chiama un esecutore attraverso `SS.run_session`; il registro e' JSON di dominio (id, secondi, metri).
- **Costanti**: `DEFAULT_SESSION_DURATION_S`/`MAX_SESSION_DURATION_S` sono decisioni dell'utente (D4.b), non stime;
  turnaround e riparazione sono STIME dichiarate (§4.4) fino a F8-R; nessun'altra costante nuova.
- **Nomi della fotografia**: nessun nome esistente cambia; S30 aggiunge 4 chiavi (sopra).
- **Import**: sempre il percorso completo `Code.Dynamic_War_Manager.Source...`; `Command/Campaign_Types` solo libreria
  standard; `Logic/Readiness` importa `Context`, `Command.Campaign_Types`, `Command.Session_Types` (tipi),
  `Utility.Utility.validate_class` e, dentro `turnaround_class`, `Asset.Aircraft_Data` (import locale se crea un ciclo,
  v. memoria `feedback_circular_import_workaround`).
- **Test**: logger mockati come negli altri `Test_*.py` (`patch("Code.Dynamic_War_Manager.Source.Logic.Readiness.logger",
  MagicMock())`); classi base condivise senza `unittest.TestCase`.

### 4.7 Esito atteso del confronto con la fotografia (riepilogo)

| Dopo | Identiche | Cambiate | Nuove | Perche' |
|---|---|---|---|---|
| F8a | 982 | 0 | 0 | il validatore non e' chiamato da `run_session`; il warning non cambia nulla |
| F8b | 982 | 0 | 0 | stato di missione, posizioni, fine del movimento ed esito d'Operazione non sono nella fotografia |
| F8c | 982 | 0 | 4 | S30-CAMPAIGN (4 sessioni) |
| commit dei dati F8-R | 982 | 4 (solo S30) | 0 | gli istanti delle sessioni 3-4 di S30 sono calcolati dalle costanti (`session.order_t_start`, `t_end`) |
| F6-B3 I1 | 986 | 0 | 0 | solo docstring |

Se compare una qualunque esecuzione cambiata fuori da quelle elencate, l'esecutore si ferma e riferisce.

### 4.8 Documenti da aggiornare (dalla sessione principale o dall'esecutore, come indicato)

- `Piano_Implementazione_Missione.md`: tabella §5, righe F8a, F8b, F8c (e F6-B3) con stato e commit; deviazione 25
  (validatore fuori da `run_session`, registro di campagna, posizioni nell'esito e applicate fuori, IN_PROGRESS,
  esito d'Operazione); "Punti aperti" (`:501`: la missione sul posto non e' piu' FAILED). Lo aggiorna la sessione
  principale dopo la verifica (AGENTS.md: lo stato del progetto non lo scrive l'esecutore).
- `F4_Differenze_Scenari.md`: sezione "F8" con il confronto di ogni passo (identiche/nuove) e S30; l'esecutore la
  scrive nel proprio rapporto, la sessione principale la riporta.
- Manuale DES (F9, non ora: un altro agente lo sta aggiornando per F7a/F7b): capitolo 03 (campi nuovi di
  `SessionOutcome`, `IN_PROGRESS`, `OperationOutcome`), 07 (warning E4, porta di uscita, "Cosa non fa"), 10 (limiti:
  logistica, risorse di riparazione, `off_scene`), un paragrafo nuovo sul ciclo di campagna (validatore, prontezza,
  posizione).
- Docstring: `Session_Types` ("Cosa NON c'e'" `:28-35`: le finestre di campagna esistono), `Mission_Adapter` (`:71-73`,
  `:236-240`, `:263`: chi chiama i validatori), S11 (`Test_Session_Scenarios_S10_S18.py:347-350`) e mini-campagna
  (`Test_Session_Validation.py:281-284`): il limite resta per chi chiama `run_session` direttamente, la persistenza e'
  del conduttore di campagna (S30). Solo testo.

---

## 5. Rischi e limiti

| Rischio / limite | Mitigazione o dichiarazione |
|---|---|
| Tempi di turnaround e riparazione inventati | dichiarati STIMA nel codice e nel rapporto; ricerca F8-R; test relativi alle costanti (non ai numeri) |
| Logistica assente: riarmo, rifornimento e riparazione senza consumo delle scorte del blocco ne' risorse della base | limite dichiarato; la logistica (`Resource_Manager`) e' un lavoro separato |
| Turnaround uguale per chi ha volato 10 minuti e chi ha volato 2 ore; per un reparto che si e' solo spostato | semplificazione dichiarata (un tempo per classe e per dominio, D6.b/d) |
| Il turnaround corre dentro la sessione: un aereo atterrato e colpito sul parcheggio somma riparazione e turnaround dall'ultimo danno | regola 5 di §4.4, dichiarata |
| Aereo `off_scene`: torna "alla base" senza sapere quale | posizione invariata (decisione 22); la base vera e' del modulo mappe/C2 |
| Aereo in volo a fine sessione (solo senza validatore) | warning e posizione a fine sessione; il validatore lo impedisce |
| Chi chiama `run_session` direttamente non ha validazione, prontezza ne' persistenza | voluto (test dell'esecutore); il ciclo di campagna passa da `run_campaign_session` |
| Il validatore duplica il messaggio del carburante (G1 e bingo a priori coincidono) | due codici distinti; decisione 18 (B2 lo evita) |
| Prontezza "all'inizio della sessione" (D6.a) esclude un asset pronto dopo pochi minuti | decisione 19; cambiabile con una riga |
| IN_PROGRESS cambia l'esito di missione degli scenari con missioni non finite | la fotografia non lo registra; §1.8 elenca i casi; interruttore |
| Operazioni su piu' sessioni (ordine permanente, D4.e) | fuori F8 (C2); l'esito d'Operazione e' per sessione |
| Le 4 esecuzioni di S30 cambiano a ogni ritaratura delle costanti | atteso e dichiarato (§4.7) |
| `CampaignState` non ha chiamanti di produzione: la persistenza su disco e' provata solo dai test | il conduttore di campagna la usera' quando esistera' il C2/TSM |
| `Asset.repair_time` / `t2r` (`(1, 7)` per tutti, tupla in un setter che valida `int`) resta incoerente | non usato dalla F8; da correggere con la ricerca (arretrato) |
