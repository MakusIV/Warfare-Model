# Piano di implementazione dell'entità Missione

**Stato**: APPROVATO (2026-10-05, Q1-Q4 sì) e IN CORSO: fatte F0, F1, F2, F3, F4a e F4b (v. §5 "Stato di avanzamento").
**Base**: le decisioni D1-D6 e N1-N3 di `Proposta_Struttura_Missione_Decisioni.md` (tutte prese;
N2.a = C, N3.f = B).
**Convenzioni**:
- **[V]** = verificato sul codice;
- **[I]** = ipotesi da confermare in quella fase.

---

## 0. Principi

1. **Prima i tipi, poi il comportamento.** Le prime fasi introducono strutture dati validate e
   testate senza cambiare il comportamento del motore. La porta di sessione cambia nella Fase 3, il comportamento del motore dalla Fase 4.
2. **Non regressione misurata.** Gli scenari di sessione (S1-S19) si fotografano nella Fase 0:
   esiti di forza, perdite, munizioni, carburante. Il confronto con la fotografia si ripete a ogni
   fase. Una differenza è ammessa solo se la fase la prevede, e va spiegata nel commit.
3. **Una fase = un commit (o pochi), suite completa verde.** Proposta per le decisioni intermedie
   prima del codice, come per le proposte precedenti.
4. **Fuori da questo piano**, per decisione:
   - rifornimento in volo simulato (D5.a);
   - condizioni sullo stato e re-scheduling (N2.d, D2.a, R4 seconda parte);
   - adapter DCS (N1);
   - secondo stadio di scelta del tipo di missione nel pianificatore (N3.f);
   - pianificatore C2 / `Theater_Session_Manager`.

   Il piano li predispone senza implementarli.

---

## 1. Fasi

### Fase 0: fotografia di riferimento degli scenari

**Cosa**: uno script di prova (fuori dal repo o in `Test/`, da decidere) che esegue S1-S19 con seed
fissi e salva, per ogni scenario:
- esito di ogni forza;
- perdite per asset;
- munizioni e carburante residui;
- numero di salve e intercettazioni.

**Perché**: dalla Fase 3 la porta di sessione cambia e servono numeri per dimostrare che a parità di
input il motore produce la stessa storia.

**Fatto quando**: la fotografia esiste ed è riproducibile, cioè identica in due esecuzioni.

### Fase 1: tipi di dominio della Missione (nessun cambio di comportamento)

**Nuovo modulo** `Command/Mission_Types.py`: dataclass immutabili con validazione, nello stile di
`Command/Attack_Types.py` e `Command/Session_Types.py`.

| Tipo | Contenuto | Decisione |
|---|---|---|
| `MissionCategory` (enum) | ATTACK, TRANSPORT, POSITIONING, SUPPORT | N3.a |
| `Target` | forma: ASSET/GROUP, POINT/AREA (centro, raggio), ZONE, NONE; **provenienza**: OBSERVED (asset_id, istante dell'ultima osservazione) oppure ESTIMATED (posizione, istante, incertezza) | N3.d, N3.e |
| `MissionAction` | genere: TASK, RULE, COMMAND, WAIT; parametri; priorità (0 = massima); condizione di avvio **pre-calcolabile** (all'arrivo, all'istante t, dopo una durata) | N2.c, N2.d |
| `MissionWaypoint` | **contiene** un `DataType.Waypoint`; ruolo del punto (enum: DEPARTURE, JOIN, NAV, IP, ATTACK, EGRESS, SPLIT, LAND, STATION, ASSEMBLY, OBJECTIVE...); ETA pianificata; velocità del tratto in arrivo; riferimento di quota (MSL/AGL); azioni ordinate | N2.a = C, N2.b |
| `MissionAsset` | asset_id, ruolo = posizione nella formazione (aria lead/element_lead/wingman, terra lead/main/rear, mare lead/main/screen), offset di formazione, **loadout e profilo d'attacco per asset** (aria) | D3.b, D3.c, nota utente 2026-10-05 |
| `EndCriteria` | criteri dichiarati: ultimo waypoint, durata o tempo sulla stazione, bingo (sì/no), winchester (per categoria d'arma), aborto per minaccia (sì/no), soglia di danno, bersaglio distrutto (sì/no) | D2.a, D2.b |
| `MissionRules` | ROE, stato di allerta, reazione alla minaccia, EMCON, formazione | D3, sintesi §3.4 |
| `Mission` | `mission_id`, `block_id`, dominio, `MissionCategory`, tipo di missione, `Target`, priorità, asset (`MissionAsset`), rotta di riferimento (`DataType.Route`) + `MissionWaypoint`, istante e modo di avvio, regole, `EndCriteria`, `operation_id` facoltativo (loadout e `AttackProfile` sono per asset) | D3 |
| `Operation` | `operation_id`, scopo, `mission_ids`, TOT comune facoltativo, regola d'esito | D3.a, D2.e |
| `MissionOutcome` | esito: COMPLETED, ABORTED (+motivo), FAILED, DESTROYED; esiti per asset con motivo di fine; ETA effettive | D2.d, N2.b |

**Validazioni** (in `__post_init__`):
- asset tutti dello stesso blocco;
- ETA crescenti;
- almeno un istante bloccato (avvio o TOT);
- rotta aerea che inizia e finisce in una base (D2.c);
- ruoli ammessi per il dominio;
- bersaglio coerente con la categoria (TRANSPORT e POSITIONING: zona o blocco amico).

**Test**: `Test/Test_Mission_Types.py`, solo costruzione e validazione.

**Fatto quando**: tipi e test esistono; nessun altro modulo li usa ancora; suite verde.

### Fase 2: tassonomia dei tipi di missione e tabella di compatibilità (N3)

**`Context/Context.py`**:
- `AIR_TASK` + **AWACS, Tanker, Transport** (in un nuovo gruppo "supporto" accanto ad A2A e A2G);
- nuovi enum `Ground_Mission_Type` (Attack, Defense, Maintain, Retreat, **Fire_Support, Movement,
  Recon, Supply**) e `Sea_Mission_Type` (Attack, Defense, Retreat, **Patrol, Escort,
  Shore_Bombardment, Transport**);
- mappa `tipo di missione → MissionCategory`;
- tabella **`MISSION_TYPE_POSTURES`**: tipo di missione → posture ammesse e postura di riferimento
  per la combat power (N3.f = B). `Ground_Action`, `Sea_Task`, combat power, tabelle di efficacia
  e controllore fuzzy restano **invariati**.

**Aria, da verificare in questa fase** [I]:
- l'effetto dei tre nuovi task su `Aircraft_Data` (punteggio per task del miglior loadout),
  `Air_Resources_Assigner` (validazione dei task) e `Aircraft.set_combat_power`;
- assegnare i task ai **14 loadout con `tasks` vuoto** in `Aircraft_Loadouts` (presumibilmente
  tanker, AWACS e trasporti).

**Test**: aggiornare gli insiemi attesi in `Test_Context`; nuovi test della tabella di
compatibilità (ogni tipo di missione ha almeno una postura ammessa; la postura di riferimento è fra
quelle ammesse).

**Fatto quando**: suite verde e fotografia della Fase 0 invariata.

### Fase 3: la Missione attraversa la porta di sessione (P1)

**`Command/Session_Types.py`**:
- `SessionOrder` acquisisce `missions` e `operations`;
- `SessionOutcome` acquisisce `mission_outcomes`.

**`Logic/Session_Simulator.py`**:
- `run_session` accetta le missioni e ne **ricava** `routes`/`starts`/`speeds` per asset: la rotta
  di riferimento più l'offset di formazione dà la rotta per asset; la partenza viene dall'avvio
  della missione;
- `mission_id` reale nell'RNG (oggi `None`) [V: lo slot c'è in `Session_Rng`];
- esito di missione nella prima forma: COMPLETED se almeno un asset raggiunge l'ultimo waypoint,
  DESTROYED se tutti persi.
- validazione dell'ordine di sessione: **un asset in una sola missione per sessione**; un blocco può
  invece avere **più missioni nella stessa sessione**. Esempio (indicazione dell'utente, 2026-10-05):
  il blocco airbase_a con fighter e fighter_bomber può impiegarli nella stessa missione (stessa rotta
  e stessa partenza, ciascuno con il proprio loadout) oppure in due missioni distinte, una per tipo.

**Compatibilità**: i parametri `routes`/`starts`/`speeds` restano nella prima versione come strada
interna ed equivalente. Gli scenari migrano uno per volta alle missioni (19 chiamate a `run_session`
in 6 file [V]). Rimozione dei parametri a migrazione completa (**domanda Q2**).

**Fatto quando**:
- gli scenari migrati producono la **stessa** fotografia della Fase 0 (a parità di rotte, la
  Missione è solo un contenitore);
- il `mission_id` nell'RNG cambia le estrazioni: la fotografia va **rigenerata una volta**, in un
  commit dedicato che lo dichiara.

### Fase 4: la missione come unità di ingaggio, postura continua (D3.e, D1.c)

- **Vista di missione** `MissionForce`: asset della missione, lato del blocco, `name` =
  `mission_id`, `salvo_interceptors` ristretto agli asset della missione. `resolve_engagement`
  accetta già *"`Military` o qualunque oggetto con `assets`, `side`, `name`"* [V]. Da verificare
  [I]: `morale_for`, `enemy_estimate_for`, soglia di rottura e `committed` usano solo questi
  attributi? [V in F4b: oltre a `assets`/`side`/`id`-`name` e `salvo_interceptors()`, il risolutore
  legge la CLASSE della forza (`_can_disengage`: `Military` sì, `Block` non militare no); la vista
  dichiara `can_disengage` calcolato sul blocco (adattatore). `morale_for`/`enemy_estimate_for`
  ricevono la vista (blocco in `owner_block`); rilevamento, nebbia di guerra, RWR, carburante,
  danno e munizioni leggono gli asset.]
- **Postura continua**: gli asset di un blocco **non** assegnati a nessuna missione formano una vista
  di postura del blocco, ferma per tutta la sessione e passiva o difensiva secondo la propria
  postura (D1.c).
- Disingaggio, soglia di rottura e `committed` valgono **per missione** (D3.d, D3.e).

**Fatto quando**:
- con una missione per blocco gli scenari danno la fotografia attesa;
- un nuovo scenario con due missioni dello stesso blocco mostra disingaggi indipendenti;
- un nuovo scenario con aerei parcheggiati mostra che sono colpibili.

### Fase 5: presenza, tempi e attese (D1.a/b, N2.b/c)

**`Logic/Contact_Scheduler._asset_legs`**: tratti fermi **prima** della partenza (nella posizione di
avvio) e **dopo** la fine (nella posizione finale), per tutta la sessione.

**Postura di fine missione** nel resolver:
- aereo a terra: bersaglio passivo;
- unità terrestre o navale: difesa secondo ROE e allerta.

**Azione WAIT**: tratto fermo (sosta, Hold) o circuito (orbita) di durata data o fino all'istante t.
Rende possibili TOT comune, CAP con tempo sulla stazione e sosta a terra.

**ETA effettive** riportate nel `MissionOutcome`.

**Fatto quando**:
- gli esperimenti E1 ed E3 dell'analisi del 26/09 danno presenza continua (il carro fermo a 4 km
  resta ingaggiabile);
- una CAP in orbita ha finestre di contatto per tutta la durata dell'attesa.

### Fase 6: fine missione e carburante nel tempo (D2, D5.b)

**`Fuel_Model`**: consumo **per tratto**: in distanza per il movimento, nel tempo per attese e orbite.
`FuelEvent` diventa uno per tratto, non più uno per asset.

**Pianificazione** (validatore): **bingo a priori** sulla rotta completa (andata, attesa, ritorno).
Una missione che non rientra con la riserva è rifiutata.

**Resolver: "fine di attività"** senza cambio di rotta (D2.a). Al winchester, a bersaglio distrutto
o a danno oltre soglia (se dichiarati in `EndCriteria`), l'asset smette di ingaggiare e prosegue
passivo sulla rotta pianificata. Il motivo va nell'esito.

**`MissionOutcome` completo**: COMPLETED / ABORTED con motivo / FAILED / DESTROYED, più l'esito per
asset (D2.d).

**Fatto quando**:
- l'esperimento E5 (carro a secco) non ingaggia più oltre il punto di esaurimento;
- un asset winchester smette di sparare e lo registra come motivo di fine;
- gli scenari dichiarano differenze attese e spiegate.

### Fase 7: bersagli espliciti e filtro armi per missione (N3.d/e, A4)

**Involucro di `fire_control` per missione**, sullo stesso schema di `ifv_only` di S19 [V]:
- bersagli ammessi: il bersaglio assegnato o, se NONE, qualunque nemico secondo ROE;
- armi ammesse per tipo di missione, ruolo dell'asset e categoria d'arma (restrizioni A/A, A/G).

**Bersaglio di posizione** (POINT/AREA): fuoco sull'area della **posizione stimata**. Colpisce
chi c'è davvero in quell'area all'impatto, non dove il bersaglio si è spostato. È il comportamento
osservato in `ground_sea_mission.miz`. Richiede nel resolver una salva verso un'area, oggi le salve
sono verso un asset: **domanda Q3**, la proposta di dettaglio va fatta all'inizio della fase.

**S19**: il filtro di test `ifv_only` diventa una missione con bersaglio e filtro armi.

**Fatto quando**:
- S19 senza filtro di test dà lo stesso esito di prima;
- uno scenario di fuoco d'artiglieria su posizione stimata superata colpisce solo chi c'è.

### Fase 8: sessione e campagna (D4, D6, D1.d)

**Validatore di sessione**:
- durata come parametro di campagna (default 2 h, massimo 4 h);
- missioni fuori finestra rifiutate (niente più taglio silenzioso, E4);
- un asset in una sola missione per sessione;
- sessioni disgiunte.

**Prontezza**:
- campo "pronto da t" per asset nello stato di campagna;
- turnaround per classe di velivolo e per dominio;
- riparazione funzione del danno.

I **tempi di turnaround** vengono da una ricerca dedicata: agente Sonnet con schema e tabella da
compilare, come per le RWR.

**Posizione persistente**: lo snapshot di `Campaign_State` salva già la posizione degli asset [V].
Manca il ripristino all'inizio della sessione successiva.

**Fatto quando**: una sequenza di due sessioni mostra posizione ripresa, asset non pronto escluso
dal pianificatore e riparazione in corso.

### Fase 9: documentazione

- Manuale DES aggiornato con `des-manual-writer`, insieme al ritardo già accumulato (soglia di
  rottura, E(N), RWR + R-CLS, dottrina di tiro, A6, R-INT);
- sintesi e proposta allineate allo stato finale.

---

## 2. Dipendenze e parallelismo

```
F0 ──► F3 ──► F4 ──► F5 ──► F6 ──► F7 ──► F8 ──► F9
F1 ──► F3
F2 ──► F3 (tipi di missione nella Mission)
```

F0, F1 e F2 toccano file diversi e possono andare **in parallelo**: due o tre agenti `des-developer`,
come già fatto con successo. Da F3 in poi la sequenza è stretta, perché ogni fase cambia il motore
su cui poggia la successiva.

## 3. Rischi

| Rischio | Mitigazione |
|---|---|
| Migrazione di 19 chiamate a `run_session` | parametri vecchi mantenuti finché la migrazione non è completa (Q2); fotografia di confronto |
| Più asset nello scheduler (presenza continua, postura dei non impegnati) | lo scheduler scarta già le coppie lontane [I: verificare il costo su S1-S19 in F4-F5]; se serve, ottimizzazione C di D1.c |
| Il `mission_id` nell'RNG cambia tutte le estrazioni | rigenerare la fotografia una volta, in un commit dedicato |
| Il resolver dipende da attributi di `Military` oltre a `assets`/`side`/`name` | verifica all'inizio della F4; eventuale adattatore nella vista |
| Salva su area (F7) è un'estensione non banale del resolver | proposta di dettaglio all'inizio della F7 |

## 4. Domande prima di partire

- **Q1**: approvi fasi e ordine? In particolare, va bene fermarsi a F8 lasciando C2/TSM fuori?
- **Q2**: i parametri `routes`/`starts`/`speeds` di `run_session` vanno **rimossi** a migrazione
  completata (consiglio: sì, una sola strada) o mantenuti come API di basso livello per i test?
- **Q3**: per la F7 (salva su area), proposta di dettaglio separata all'inizio della fase. Va bene?
- **Q4**: F0-F2 in parallelo con agenti `des-developer`, o in sequenza nella sessione principale?

---

## 5. Stato di avanzamento e deviazioni dal piano (aggiornato 2026-10-08)

| Fase | Stato | Commit | Note |
|---|---|---|---|
| F0 | FATTA | `d3af6980` | fotografia di 292 esecuzioni (S1-S19, S19AD, VAL, ORC); `--summary` aggiunto in F4a |
| F1 | FATTA | `20b6de72`, `680dfcb6`, `8f16cc3c` | ruoli = posizioni nella formazione; loadout e `AttackProfile` per asset; partenza aerea di default dal parcheggio |
| F2 | FATTA | `4e18d7d8`, `8f16cc3c` | tabelle confermate dall'utente; `AIR_COMBAT_TASK` per escludere i task di supporto da combat power e punteggi; **13** loadout su 14 con task assegnati (An-30M Recon lasciato vuoto) |
| F3 | FATTA | `533cd1f5` | fotografia identica; parametri `routes`/`starts`/`speeds` **già rimossi** (Q2) |
| F4a | FATTA | `951b0ee2` | regola A dell'utente: una missione si muove alla velocità del mezzo più lento; 90 esecuzioni cambiate, nessun esito di forza (`F4_Differenze_Scenari.md`) |
| F4b | FATTA | | missione come unità di ingaggio (vista `Mission_Adapter.MissionForce`), `mission_id` negli id d'ingaggio e quindi nell'RNG; esito del blocco = insieme degli esiti delle sue missioni (`SessionOutcome.outcomes_of_block`); nuovo scenario S20; differenze in `F4_Differenze_Scenari.md` |
| F4c | DA FARE | | postura continua degli asset senza missione (D1.c) |
| F5-F9 | DA FARE | | come da §1 |

**Deviazioni decise durante il lavoro**:
1. `mission_id` **non** entra nell'RNG in F3 ma in F4b. Le estrazioni sono per ingaggio fra forze, e finché la forza è il blocco un ingaggio può coinvolgere più missioni. Così F3 è rimasta pura struttura, verificata con fotografia identica.
2. F4 è divisa in tre passi (F4a, F4b, F4c), ognuno con commit, documento delle differenze e fotografia rigenerata, per attribuire ogni differenza alla sua causa.
3. Regola A (decisione dell'utente prima della F4): asset di velocità diverse nella stessa missione vanno alla velocità del più lento (`Mission_Adapter.check_mission_speed`). Chi vuole velocità diverse usa missioni separate.
4. F4b (decisione dell'utente, 2026-10-08): missioni dello stesso blocco (S7, S18, S19, S19AD) ingaggiano e disingaggiano **separatamente**, senza un'Operazione che le leghi. Il `mission_id` entra nell'RNG attraverso l'`event_id` dell'ingaggio; lo slot `mission_id` di `Session_Rng` resta None, perché un ingaggio è fra più forze (missioni di entrambi i lati) e nessuna ne possiede lo stream.
5. F4b: gli asset di un blocco senza missione mantengono il comportamento di prima (fermi, combattenti) in attesa della postura continua della F4c: un blocco senza missioni entra nel risolutore com'è, gli asset non assegnati di un blocco con missioni formano una vista residua con l'id del blocco. `SessionOrder.committed` resta chiavato per blocco e si applica a ogni missione per intersezione.
6. La rotta aerea "da base a base" (D2.c) è verificata solo sui ruoli dei punti (`DEPARTURE` all'inizio, `LAND` alla fine), non sulla presenza di una base reale. Le rotte aeree degli scenari non hanno rientro e sono annotate come semplificazione da completare con l'RTB in F5-F6.

**Punti aperti rilevati dall'aggiornamento del manuale** (capitolo 10 §9.6 del manuale DES):
- docstring obsoleti in `Session_Simulator` (dicono ancora che la selezione dell'arma resta fuori dall'orchestratore);
- `run_session` non inoltra `rwr_catalogue` al risolutore;
- nessun codice di produzione fornisce `morale_for` / `enemy_estimate_for` (solo i test);
- una missione sul posto risulta `FAILED` perché manca uno stato "in corso" (D4.e);
- ruoli, regole, bersaglio, criteri di fine e `Operation` sono validati ma non ancora letti da `Logic` (arrivano con F4-F7).
