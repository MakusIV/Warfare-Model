# Piano di implementazione dell'entità Missione

**Stato**: APPROVATO (2026-10-05, Q1-Q4 sì) e IN CORSO: fatte F0, F1, F2, F3, F4a, F4b, F4b+, F4b++, la riprogettazione dei test S3/S5, F4c, F5-A, F5-B, F5-C, F6-A, F6-B1, F6-B2, F6-B2bis, G1-G5, (2026-10-18) F7a e (2026-10-20) F7b; da fare F8-F9 (v. §5 "Stato di avanzamento").
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
| `Operation` | `operation_id`, scopo, `mission_ids`, regola d'esito (nessun TOT comune: il TOT è di ogni missione, `Mission.tot`, decisione dell'utente del 2026-10-12) | D3.a, D2.e |
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
in 6 file [V]). Rimozione dei parametri a migrazione completa (**domanda Q2**). **[Esito: rimossi in F3, v. §5.]**

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
Rende possibili TOT per missione, CAP con tempo sulla stazione e sosta a terra. **[Esito: il TOT comune
d'Operazione previsto qui è stato rimosso il 2026-10-12, decisione dell'utente: il TOT è di ogni missione,
`Mission.tot`; v. §5, F5-C.]**

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

**Proposta di dettaglio (Q3)**: `Proposta_F7_Bersagli_Filtro_Armi.md`. La fase e' divisa in **F7a** (regole d'ingaggio
di missione: FATTA 2026-10-18, v. §5 deviazione 23) e **F7b** (fuoco su posizione: FATTA 2026-10-20, v. §5 deviazione 24). Il testo che segue e'
quello del piano originale.

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
- uno scenario di fuoco d'artiglieria su posizione stimata superata colpisce solo chi c'è. (FATTO dalla F7b: S29-AREA).

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

## 5. Stato di avanzamento e deviazioni dal piano (aggiornato 2026-10-18)

| Fase | Stato | Commit | Note |
|---|---|---|---|
| F0 | FATTA | `d3af6980` | fotografia di 292 esecuzioni (S1-S19, S19AD, VAL, ORC); `--summary` aggiunto in F4a |
| F1 | FATTA | `20b6de72`, `680dfcb6`, `8f16cc3c` | ruoli = posizioni nella formazione; loadout e `AttackProfile` per asset; partenza aerea di default dal parcheggio |
| F2 | FATTA | `4e18d7d8`, `8f16cc3c` | tabelle confermate dall'utente; `AIR_COMBAT_TASK` per escludere i task di supporto da combat power e punteggi; **13** loadout su 14 con task assegnati (An-30M Recon lasciato vuoto) |
| F3 | FATTA | `533cd1f5` | fotografia identica; parametri `routes`/`starts`/`speeds` **già rimossi** (Q2) |
| F4a | FATTA | `951b0ee2` | regola A dell'utente: una missione si muove alla velocità del mezzo più lento; 90 esecuzioni cambiate, nessun esito di forza (`F4_Differenze_Scenari.md`) |
| F4b | FATTA | `a4d8acf0` | missione come unità di ingaggio (vista `Mission_Adapter.MissionForce`), `mission_id` negli id d'ingaggio e quindi nell'RNG; esito del blocco = insieme degli esiti delle sue missioni (`SessionOutcome.outcomes_of_block`); nuovo scenario S20; differenze in `F4_Differenze_Scenari.md` |
| F4b+ (dominio di coordinamento) | FATTA | `098671d7` | deviazioni 6 e 7: ripartizione del fuoco e percezione condivise nel dominio (stesso blocco oppure stessa Operazione, unione transitiva, mai fra lati), `Mission_Adapter.coordination_domains` + `coordination_of` di `resolve_engagement`; nessun cueing; 8 esecuzioni cambiate (S19AD standoff torna a 8-10 Maverick e Red-Line DESTROYED; S20 split 2 grandezze fini), differenze in `F4_Differenze_Scenari.md` |
| F4b++ (intercettori di dominio) | FATTA | `e6f59d21` | deviazione 8c: una salva diretta a un asset di una forza è intercettata dagli intercettori di qualunque forza del suo dominio di coordinamento (ordine globale della regola F, canali per evento condivisi fra forze del dominio risolte nello stesso istante); geometria L1, tempi R-INT e scorta R3 invariati; senza `coordination_of` identico; fotografia: v. `F4_Differenze_Scenari.md` |
| Test S3/S5 (deviazione 9) | FATTA | `8bf7b11f` | solo test e docstring (commit vuoto per il motore): S3 su frazioni e soglia a 3 errori standard, S5 con maggioranza + invarianti per replica e variante «formazione resistente» (erosione Blue 0,65, 12 seed); 20 esecuzioni nuove, nessuna cambiata; v. `F4_Differenze_Scenari.md` |
| F4c | FATTA | `af2efbe6` | postura continua (D1.c, deviazione 11): aereo senza missione a terra (insieme `grounded` della sessione, bersaglio di superficie passivo, keyword `target_grounded` della fire control), unità di superficie in `Defense` dichiarata; nuovo scenario S21/S21R (aerei parcheggiati colpiti, 21/32 e 23/24 distrutti); fotografia rigenerata a 370 esecuzioni (2 cambiate accettate dall'utente, 22 nuove); v. `F4_Differenze_Scenari.md` |
| F5-A | FATTA | `e723e82a` | `grounded` dipendente dal tempo (`Contact_Scheduler.GroundedSchedule`, finestre spezzate a decollo/atterraggio, risolutore con stato all'istante di ogni regola); in sessione resta l'insieme costante della F4c; predisposti ma non cablati `Mission_Adapter.movement_legs`/`grounded_schedule`/`session_postures` e `SessionOutcome.postures`; fotografia IDENTICA su 370, suite 4072 OK; v. `F4_Differenze_Scenari.md` |
| F5-B | FATTA | `90f2d4de` | presenza e postura cablate in sessione (interruttori separati `F5_PRESENCE`=True e `F5_WAITS`=False): terra/mare ferme in `Defense` prima/dopo, aerei a terra fino al decollo e dopo l'atterraggio su base vera (`AIR_BASE_AREA_RADIUS_M` = 3000 m, stima), `SessionOutcome.postures` per tutti gli asset; nuovo scenario S22 (E1/E3/aerei, 72 esecuzioni); 2 esecuzioni cambiate (S6-0, S6-2, presenza navale dopo l'arrivo), ACCETTATE dall'utente il 2026-10-12; fotografia rigenerata a 442; suite 4101 OK; v. `F4_Differenze_Scenari.md` |
| F5-C | FATTA | `4da618b1` | WAIT (`hold`/`orbit`, orbita = presenza ferma nel punto, approssimazione dichiarata), ETA bloccate e TOT attivi con `F5_WAITS`=True (TOT comune d'Operazione `operation_tots` RIMOSSO il 2026-10-12 per decisione dell'utente: il TOT è di ogni missione, anche nella stessa Operazione; S23-TOT rifatto con TOT diversi sweep/strike); ETA effettive (`actual_etas`) nell'esito; nuovo scenario S23 (CAP in orbita, sosta, TOT; 80 esecuzioni); nessuna esecuzione esistente cambiata; fotografia a 522; suite 4131 OK; raffinamento dell'orbita (distanza di riferimento/zona) da decidere, v. `F4_Differenze_Scenari.md` |
| F6-A | FATTA | `00b6b531` | carburante per tratto (`FuelEvent` per tratto, `F6_FUEL_PER_LEG`) e vincolo sul movimento e sui contatti (`F6_FUEL_CONSTRAINT`); consumo delle attese pari alla crociera; terra/mare fermi nel punto di esaurimento; aereo a secco: planata su base del lato (`GLIDE_RATIO`=10, STIMA) -> ABORTED, altrimenti DESTROYED (`FUEL_EXHAUSTED`); nuovo scenario S24 (88 esecuzioni); 38 esecuzioni esistenti cambiate nel solo carburante e 126 nella forma di `fuel_events`, ACCETTATE dall'utente il 2026-10-12; fotografia a 610; suite 4166 OK; precedenza provvisoria dello stato di missione DESTROYED > COMPLETED > ABORTED(FUEL) > FAILED fino a F6-B; v. `F4_Differenze_Scenari.md` |
| F6-B1 | FATTA | `15ac3d3d` | criteri di fine attivita' letti dal risolutore (`winchester`, `damage_threshold`, `target_destroyed` per asset/gruppo, `max_duration_s`; `F6_END_CRITERIA`): l'asset smette di lanciare e prosegue passivo, motivo e ora nell'esito; stato di missione con regola unica DESTROYED > COMPLETED > ABORTED(motivo) > FAILED (confermata dall'utente 2026-10-12); postura `destroyed` nell'esito (`F6_DESTROYED_POSTURE`, accettata dall'utente: 429 esecuzioni cambiate nel solo campo `postures`); nuovo scenario S25 (112 esecuzioni); fotografia a 722; suite 4195 OK; v. `F4_Differenze_Scenari.md` |
| F6-B2 | FATTA | `6b1b7225` | bingo a priori nel validatore di pianificazione `Mission_Adapter.check_mission_bingo` (missione aerea che non rientra alla base idonea piu' vicina con la riserva `Fuel_Model.BINGO_RESERVE` = 0,10 del pieno, STIMA: rifiutata con il motivo; senza base idonea rifiutata; NON chiamato da `run_session`, e' del pianificatore) e bingo in volo con rientro (`F6_BINGO`): rientro in linea retta alla base del lato piu' vicina, a terra sulla base, nessuna salva dal bingo, esito BINGO / ABORTED(`AbortReason.BINGO`, nuovo); stesso criterio a priori e in volo (`Fuel_Model.bingo_point`); `EndCriteria.bingo` False = nessun controllo ne' rientro; nuovo scenario S26 (40 esecuzioni); nessuna esecuzione esistente cambiata con S24-GLIDE che dichiara `bingo=False` (con il bingo di default cambierebbero 24 esecuzioni di S24-GLIDE, da accettare); v. `F4_Differenze_Scenari.md` |
| F6-B2bis | FATTA | `96942ca7` | deviazione 16: bingo rifatto con rientro lungo la rotta a ritroso fino al DEPARTURE (partenza in volo: fino al punto di comparsa, poi diretto alla base piu' vicina), fabbisogno 1,2 x il ritorno (`BINGO_RETURN_FACTOR`, stima dell'utente) al posto della riserva 0,10, anello per la via piu' breve, divert escluso; interruttore `F6_BINGO_REVERSE_ROUTE`; S26 rifatto (carburante 0,28, variante nuova 'reverse_off', 48 esecuzioni); v. `F4_Differenze_Scenari.md` |
| G1 (nuovo modello di bingo) | FATTA | `c1c0f576` | deviazione 17: riserva di disimpegno `Fuel_Model.disengagement_reserve` = 5 minuti (`DISENGAGE_TIME`, stima dell'utente) alla massima spinta MILITARE (`Aircraft.emergency_fuel_flow`, kg/h dedotti, non documentati) / carico pieno del loadout, ripiego sul regime 'max' del loadout; nuovo validatore di pianificazione `Mission_Adapter.check_mission_fuel` (carburante caricato > rotta intera + riserva), NON chiamato da `run_session`; comportamento in sessione invariato (fotografia identica) |
| G2 (nuovo modello di bingo) | FATTA, verificata e approvata 2026-10-16 (fotografia 794) | `e1d08121`, `e5465b31` | deviazione 18: soglia di bingo = resto della rotta fino al LAND (attese comprese, alla crociera) + riserva di disimpegno del G1, albero di decisione per tipo di missione (trasferimento = categoria TRANSPORT: continua / ritroso / base piu' vicina / F6-A; combattimento: interrompe, candidata raggiungibile piu' vicina in percorso fra base di partenza e basi entro `Fuel_Model.ALTERNATE_BASE_MAX_OFFSET` = 3000 m dalla rotta, poi base piu' vicina / F6-A); funzione generale `Fuel_Model.bingo_decision` (posizione e residuo qualunque, per G4), in sessione valutata solo alla partenza (consumo deterministico); interruttore `F6_BINGO_DISENGAGE_RESERVE` (sostituisce la regola 1,2 della F6-B2bis); validatore `check_mission_bingo(disengage_reserve=True)` = stesso criterio; `AssetMissionOutcome.crew_recovered` (True per l'aereo perso per esaurimento); S26 rifatto (9 varianti, 72 esecuzioni); v. `F4_Differenze_Scenari.md` |
| G3 (nuovo modello di bingo) | FATTA, verificata e approvata 2026-10-17 (fotografia 802) | `b1931ec3`, `20f0e0db` | deviazione 19: consumo di carburante in ingaggio: un aereo di missione IN VOLO che partecipa a un ingaggio (tiratore, bersaglio di una salva, intercettore) consuma, all'istante della prima partecipazione, `Fuel_Model.engagement_fuel` = 5 minuti alla massima spinta militare (la riserva di disimpegno del G1, unico punto di calcolo) con un `FuelEvent` istantaneo (regime 'engagement'); il movimento resta alla crociera (sostituisce, per gli aerei, il regime 'max' di chi ha combattuto della F6-A); terra e mare invariati; esaurimento in ingaggio = solo contatore a zero, nessun ri-scheduling (G4); interruttore `G3_ENGAGEMENT_FUEL`; S26 + variante 'engagement_fuel_off' (80 esecuzioni); v. `F4_Differenze_Scenari.md` |
| G4a (nuovo modello di bingo) | verificata e approvata 2026-10-17 (fotografia 878, con G4b) | `9de461e0` | deviazione 20: episodi d'ingaggio: la componente connessa di forze e' spezzata in EPISODI (finestre legate da una forza o un dominio di coordinamento comune e sovrapposte entro `EPISODE_GAP` = 300 s = `Fuel_Model.DISENGAGE_TIME`), un `resolve_engagement` per episodio in ordine di tempo con esito applicato subito; forza occupata fino al `t_end` dell'esito (finestre successive ritagliate, `Contact_Scheduler.trim_contact_window`); RNG `counter` = ordinale degli episodi con lo stesso insieme di forze (tempra nuova); forza disingaggiata (e asset a fine attivita') passiva negli episodi successivi; soglia di danno sulla salute d'inizio sessione (`ActivityCriteria.reference_health`); un consumo d'ingaggio G3 per episodio; contabilita' del carburante spostata in un passo finale; interruttore `G4_EPISODES`; S5 + variante 'episodes_off'; v. `F4_Differenze_Scenari.md`, "G4a" |
| G4b (nuovo modello di bingo) | verificata e approvata 2026-10-17 (fotografia 878, con G4a e uscita di scena) | `9de461e0` | deviazione 21 (con l'uscita di scena senza basi, `G4_OFF_SCENE_EXIT`, del 2026-10-17): ri-pianificazione dopo l'episodio d'ingaggio: alla fine di ogni episodio gli aerei di missione in volo che vi hanno consumato (G3) o la cui forza si e' disingaggiata sono ri-pianificati dal residuo ANALITICO (`Fuel_Model.fuel_at`): a secco regole della F6-A dal punto a fine episodio (sostituisce il "solo contatore a zero" del G3), sotto la soglia bingo con l'albero del G2 (basi alternative comprese), forza disingaggiata = rientro forzato con la regola di combattimento indipendentemente dal carburante (`bingo_decision(forced=True)`, decisione dell'utente del 2026-10-17; nuovi motivi `AssetEndReason.DISENGAGED` / `AbortReason.DISENGAGED`), esaurimento ricalcolato sui nuovi tratti (`fuel_exhaustion(fuel=)`); tratti, programma a terra e contatti non ancora risolti ricalcolati (`schedule_contacts(only_assets=)`), episodi rimasti ricostruiti; interruttore `G4_REPLAN`; S5 + 'with_base', 'with_base_resistant', 'replan_off'; S26 + 'post_engagement_bingo', 'replan_off'; v. `F4_Differenze_Scenari.md`, "G4b" |
| G5 (nuovo modello di bingo) | FATTA, verificata e approvata 2026-10-18 (fotografia 918) | `6e7a9b81` | deviazione 22: chiusura del piano G1-G5, nessun cambio del motore. S26 riorganizzato sul modello finale (docstring, varianti divise in modello finale e controprova degli interruttori, `FINAL_MODEL`/`SWITCH_CHECKS`; nomi, ordine e scenari invariati: 96 esecuzioni identiche); nuovo scenario S27-DOUBLE (doppio ingaggio dello stesso aereo: due consumi d'ingaggio, ri-pianificazione dopo ciascun episodio, bingo solo dopo il secondo con rientro sulla base alternativa; trasferimento che continua; controprova `G4_REPLAN`/`G4_EPISODES`/`G3_ENGAGEMENT_FUEL`; 40 esecuzioni); `--compare` contro la fotografia 878: 878 IDENTICHE, 0 cambiate, 40 nuove; fotografia NON rigenerata; v. `F4_Differenze_Scenari.md`, "G5" |
| F7a (regole d'ingaggio di missione) | FATTA, verificata e approvata 2026-10-18 (fotografia 970) | `9f87a3ad` | deviazione 23: la missione decide chi si ingaggia e con che arma, su due strati con interruttori `F7_WEAPON_POLICY` (politica d'armi per tipo di missione come involucro della fire control, `Context.MISSION_WEAPON_POLICY`) e `F7_TARGET_RULES` (bersaglio designato, ROE e armi designate come `TargetRules` nel risolutore); `Target.asset_ids`, `MissionAsset.weapons`, loadout di missione coerente con quello assegnato; S19AD senza filtri di test; nuovo S28 (52 esecuzioni); `--compare` contro la fotografia 918: 918 IDENTICHE, 0 cambiate, 52 nuove; fotografia NON rigenerata; v. `Proposta_F7_Bersagli_Filtro_Armi.md` §5 e `F4_Differenze_Scenari.md`, "F7a" |
| F7b (fuoco su posizione) | FATTA, verificata e approvata 2026-10-20 (fotografia 982) | `dcedc541` | deviazione 24: una missione di terra o di mare con bersaglio POINT o AREA e un'azione `Fire_At_Point` spara sulla posizione STIMATA del bersaglio come evento di sessione `AREA_FIRE_EVENT` (`Logic/Area_Fire`, interruttore `F7_AREA_FIRE`), separato dal risolutore: nessun rilevamento, nessuna forza d'ingaggio, solo geometria e RNG di sessione; costanti STIMATE (dispersione 50 m, raggio letale 0,25 m/mm, ripiego 25 m); nuovo S29 (12 esecuzioni); suite 4555 OK (7 skipped); `--compare` contro la fotografia 970: 970 IDENTICHE, 0 cambiate, 12 nuove; fotografia NON rigenerata; v. `Proposta_F7_Bersagli_Filtro_Armi.md` §6 e `F4_Differenze_Scenari.md`, "F7b" |
| F8a (tipi di campagna e validatore di sessione) | FATTA, verificata 2026-10-22 (fotografia 982 identiche, suite 4619) | `c1182d8a` | `Command/Campaign_Types.py`, `Logic/Session_Validator.py`, `Mission_Adapter.mission_planned_end`, `Session_Simulator.session_blocks` e warning E4; eseguita da `oc-developer` (DeepSeek V4 Pro 0423); rapporto con i costi in `Rapporti/Rapporto_F8a_oc-developer.md` (Proposta F8 §4.1). |
| F8b, F8c, F8-R, F9 | DA FARE | | F8 = sessione e campagna (validatore di sessione, che potra' chiamare il bingo a priori; prontezza; posizione persistente); F9 = documentazione (manuale DES, togliere il 'TOT comune' nei capitoli 03 e 10, documentare F5/F6); `abort_on_threat` fuori dal Piano di F6 |

**Deviazioni decise durante il lavoro**:
1. `mission_id` **non** entra nell'RNG in F3 ma in F4b. Le estrazioni sono per ingaggio fra forze, e finché la forza è il blocco un ingaggio può coinvolgere più missioni. Così F3 è rimasta pura struttura, verificata con fotografia identica.
2. F4 è divisa in tre passi (F4a, F4b, F4c), ognuno con commit, documento delle differenze e fotografia rigenerata, per attribuire ogni differenza alla sua causa.
3. Regola A (decisione dell'utente prima della F4): asset di velocità diverse nella stessa missione vanno alla velocità del più lento (`Mission_Adapter.check_mission_speed`). Chi vuole velocità diverse usa missioni separate.
4. F4b (decisione dell'utente, 2026-10-08): missioni dello stesso blocco (S7, S18, S19, S19AD) ingaggiano e disingaggiano **separatamente**, senza un'Operazione che le leghi. Il `mission_id` entra nell'RNG attraverso l'`event_id` dell'ingaggio; lo slot `mission_id` di `Session_Rng` resta None, perché un ingaggio è fra più forze (missioni di entrambi i lati) e nessuna ne possiede lo stream.
5. F4b: gli asset di un blocco senza missione mantengono il comportamento di prima (fermi, combattenti) in attesa della postura continua della F4c: un blocco senza missioni entra nel risolutore com'è, gli asset non assegnati di un blocco con missioni formano una vista residua con l'id del blocco. `SessionOrder.committed` resta chiavato per blocco e si applica a ogni missione per intersezione.
6. **Ripartizione del fuoco fra missioni (decisione dell'utente, 2026-10-11)**: dominio di coordinamento = missioni dello stesso **blocco OPPURE** della stessa **Operazione** (unione transitiva; la vista residua degli asset senza missione ha l'id del blocco, quindi si coordina con le sue missioni). Saturazione (`_coverage`) e ripartizione (`_engaged_shooters`) contano le salve del dominio invece di quelle della sola forza; tetto "due missili, poi guarda" per tiratore e esenzione dei lanciatori prioritari (L2) invariati; condivisione istantanea (senza latenza di comunicazione, dichiarato). Implementata (adapter calcola la chiave, `Mission_Adapter.coordination_domains`; `resolve_engagement` la riceve come `coordination_of`, default = la forza stessa); anche i lanciatori prioritari L2/L3 sono registrati contro il dominio; un'Operazione con missioni di lati diversi lega solo quelle dello stesso lato. Effetto: S19AD torna a 8-10 Maverick con Red-Line DESTROYED (`F4_Differenze_Scenari.md`).
7. **Condivisione dei rilevamenti fra missioni (decisione dell'utente, 2026-10-11, opzione B)**: la percezione (`seen_by`, `identified_by`) è condivisa nello stesso dominio di coordinamento della ripartizione del fuoco (blocco oppure Operazione), istantanea (senza latenza, dichiarato), e ogni missione la confronta con la propria forza. NIENTE cueing del tiro (un tiratore spara solo ai bersagli che ha rilevato lui, come sempre): EWR→SAM, AWACS→caccia, scorta→strike restano una funzionalità futura da proporre a parte con la Fase 0 C2. Implementata insieme al punto 6 (le forze di uno stesso dominio sono risolte nella stessa run). Verifica: le differenze di disingaggio S7/S18/S19 rispetto a F4a NON si riducono, perché in quegli scenari ogni missione aveva già rilevato da sé gli stessi nemici a ogni valutazione (misura in `F4_Differenze_Scenari.md`); cambia solo S20 in due grandezze fini.
8. **Conferme sull'implementazione di 6 e 7 (decisioni dell'utente, 2026-10-11, dopo `098671d7`)**: (a) i lanciatori prioritari L2/L3 valgono per DOMINIO (come per il blocco prima della F4b); (b) le forze dello stesso dominio sono messe nella stessa run anche senza nemici in comune (`_connected_components`), con `event_id` dello stream RNG della run unita; (c) la difesa di salva (`salvo_interceptors`, fino ad allora per missione: una salva su un asset di X era intercettata solo dagli intercettori di X) è ESTESA al dominio: gli intercettori di qualunque forza del dominio del bersaglio, con geometria (`_may_intercept`) e tempi (`_in_time`) invariati — FATTA (F4b++, v. tabella), prima della riprogettazione S3/S5.
9. **Test S3/S5 da riprogettare (decisione dell'utente, 2026-10-11)**: misura su 40 seed (S3) e 24 (S5), script fuori dal progetto. S3: senza stealth Blue perde il 97,5% dei suoi aerei e Red il 46% (40 seed su 40), ma in numero assoluto i due lati sono indistinguibili (3,90 contro 3,68, z = -1,4); con stealth la frazione persa è uguale (46% e 47,5%) ma Red perde in media 1,95 aerei in più per replica (z = 10, rapporto di scambio 2,05-2,4). Quindi: senza stealth si confronta la FRAZIONE persa; con stealth il rapporto di scambio assoluto con soglia statistica (differenza media a coppie ≥ 3 errori standard); 20 repliche. S5: con la dottrina di default 23 formazioni su 24 si fermano al primo strato e l'ad oltranza arriva al terzo 1 volta su 24 (due test dipendono dal seed S5-7); con soglia di erosione Blue 0,6/0,75 le frequenze sono 7/24 e 18/24. Quindi: default con asserzione di maggioranza + invarianti per replica (dopo la rottura nessuno spara, chi si ferma al primo strato non vede sparare il secondo); variante con soglia di erosione dichiarata (0,6-0,75, da calibrare) e 12 seed per «entrambi gli esiti compaiono»; terzo strato da variante dichiarata oppure declassamento a «almeno due strati in ogni replica». Eseguita dopo i punti 6-7 (solo test e docstring): FATTA, v. «Riprogettazione dei test S3/S5» in `F4_Differenze_Scenari.md`.
10. La rotta aerea "da base a base" (D2.c) è verificata solo sui ruoli dei punti (`DEPARTURE` all'inizio, `LAND` alla fine), non sulla presenza di una base reale. Le rotte aeree degli scenari non hanno rientro e sono annotate come semplificazione da completare con l'RTB in F5-F6.
11. **F4c, postura continua (decisioni dell'utente, 2026-10-11)**: (a) un aereo senza missione è A TERRA, bersaglio di SUPERFICIE passivo: colpibile da bombe, razzi, cannoni e missili aria-suolo, mai ingaggiato da SAM/AAA/caccia come minaccia aerea, non spara mai; riconosciuto dall'appartenenza alla vista residua o a un blocco senza missioni, senza stati nuovi nell'`Aircraft`: la sessione calcola l'insieme `grounded` e lo passa a scheduler e risolutore (predisposto per la F5, dove anche gli aerei non ancora partiti saranno a terra); (b) unità terrestri e navali senza missione in postura `Defense` dichiarata (`MissionForce.postures`), tiro invariato, nessun ROE "hold fire". Scelte di implementazione (peso di minaccia nullo, dottrina sui soli asset che possono ritirarsi, estensione `target_grounded` del protocollo di fire control) in `F4_Differenze_Scenari.md`.
12. **Postura nell'esito di forza (decisione dell'utente, 2026-10-11)**: la postura continua (`MissionForce.postures`, oggi solo un dato della vista residua) entra nell'esito con la F5, quando smette di essere un'etichetta costante (postura di fine missione D1.a, aereo a terra che dipende dal tempo): un campo di `ForceOutcome` o del `SessionOutcome` per blocco, con una sola rigenerazione della fotografia. Per un blocco senza missioni, che entra nel risolutore tale e quale, oggi la postura non è salvata da nessuna parte: la F5 deve chiudere anche questo.
13. **F5 scomposta in tre sessioni (2026-10-11, per limite di utilizzo)**: **F5-A** passo (a), `grounded` dipendente dal tempo con insieme costante equivalente, fotografia IDENTICA su 370; **F5-B** postura nell'esito di forza (anche per i blocchi senza missioni) + presenza prima della partenza e dopo la fine (terra/mare in `Defense`; aerei a terra prima del decollo; aerei a terra dopo la fine SOLO su una base vera, altrimenti escono dalla scena come oggi: decisione dell'utente) + scenari E1/E3/aerei, fotografia rigenerata UNA volta con ogni differenza attribuita; **F5-C** azione WAIT (hold/orbit), ETA effettive, TOT comune, scenario CAP in orbita, solo esecuzioni nuove. Il brief completo di F5 (decisioni 1-5 e procedura) è nel messaggio di delega del 2026-10-11 e riassunto nella deviazione 12 e nelle decisioni D1/N2 del documento delle decisioni.
14. **F6 scomposta in due passi e regola sul carburante (decisioni dell'utente, 2026-10-12)**: **F6-A** = `Fuel_Model` per tratto (un `FuelEvent` per tratto, consumo nel tempo per attese e orbite pari alla CROCIERA dell'asset, nessuna costante nuova) + il carburante vincola il movimento e i contatti (E5); **F6-B** = criteri di fine attivita' nel risolutore (winchester, bersaglio distrutto, danno), `MissionOutcome` completo, bingo a priori nel validatore, bingo in volo con rientro. Regola dell'esaurimento: **terra/mare** restano fermi nel punto di esaurimento (presenti, bersagli); **aereo**: (1) a bingo fuel durante la rotta deve tornare indietro, esito ABORTED (F6-B); (2) se a secco ma con carburante/quota sufficienti per raggiungere, anche in planata, una base idonea nelle vicinanze, esito ABORTED; (3) se a secco in volo senza base idonea raggiungibile in planata, esito DESTROYED. La postura `destroyed` nell'esito di sessione (F5-B, rimandata) va rivalutata con F6-B.
15. **F6-B2, scelte di implementazione DA CONFERMARE (2026-10-13)**: il bingo a priori e' un validatore di PIANIFICAZIONE (`Mission_Adapter.check_mission_bingo`) non chiamato da `run_session` (l'esecutore, come DCS con "RTB on bingo", non rifiuta: fa tornare l'aereo; a priori e in volo usano lo stesso criterio, quindi un rifiuto dentro `run_session` renderebbe irraggiungibile il bingo in volo); base idonea = qualunque base aerea del lato; `EndCriteria.bingo` False = nessun controllo ne' rientro; dal bingo l'aereo non lancia piu' (fine di attivita' della F6-B1); rientro in linea retta 3D alla base a quota 0 alla crociera; riserva unica `Fuel_Model.BINGO_RESERVE` = 0,10 del pieno (STIMA); bingo valutato sui tratti della sessione, a priori sulla missione intera. Dettagli in `F4_Differenze_Scenari.md`, "F6 passo B2".
16. **F6-B2bis, bingo rifatto (decisioni dell'utente, 2026-10-15)**: il rientro rettilineo della F6-B2 e' stato giudicato irrealistico (ignora rotta, terreno e minacce). (1) **Rientro = rotta percorsa a ritroso**: dal punto di bingo l'aereo ripercorre al contrario i suoi tratti di MOVIMENTO pianificati fino al DEPARTURE (il DES non devia le rotte negli ingaggi, quindi la rotta percorsa coincide con quella pianificata), alle quote dei waypoint (discesa sul tratto finale), senza ripercorrere le soste (WAIT, orbite), consumato alla crociera. (2) **Fabbisogno di bingo = 1,2 x il carburante del ritorno** (`Fuel_Model.BINGO_RETURN_FACTOR`, decisione dell'utente, STIMA non tarata): il +20% SOSTITUISCE la riserva fissa 0,10 (che resta solo a interruttore spento); la riserva all'arrivo e' proporzionale al ritorno, piccola vicino alla base (accettato). (3) **Destinazione finale esclusa**: il LAND su un'altra base (divert) non conta (una missione di trasferimento richiede quindi carburante per circa 2,2 volte la rotta). (4) **Missioni ad anello** (LAND sulla base del DEPARTURE, `Mission_Adapter.is_loop_mission`: stesso blocco base dei riferimenti dei due punti, o in mancanza punti entro `AIR_BASE_AREA_RADIUS_M`): ritorno = min(ritroso, resto della rotta fino al LAND), soli tratti di movimento alla crociera; l'aereo prende la via piu' breve; una missione ad anello e' cosi' sicura con circa 1,1 volte il carburante della rotta. (5) **Partenza in volo**: ritroso fino al punto di comparsa, poi tratto diretto alla base del lato piu' vicina (discesa su quel tratto), +20% sul totale; senza base del lato nessun bingo (regole della F6-A). Invariati rispetto alla F6-B2: niente salve offensive dal bingo, bersaglio e intercettore, a terra (`parking_cold`) sulla base raggiunta, BINGO / ABORTED(BINGO), `EndCriteria.bingo` False = nessun controllo, a secco sul rientro le regole della F6-A, validatore ed esecutore con lo stesso criterio (`Fuel_Model.bingo_point` con la stessa `ReturnRule`). Interruttore `Session_Simulator.F6_BINGO_REVERSE_ROUTE` (spento = la F6-B2 com'era; il validatore lo segue con il parametro `reverse_route`). Il bingo in sessione e' ora calcolato sulla missione intera (anche oltre la fine della sessione, per leggere il resto della rotta dell'anello). Limiti rimasti: idoneita' della base per tipo d'aereo non modellata (qualunque base aerea amica); consumo deterministico alla crociera (un aereo che combatte consuma di piu' nella contabilita', nessun ri-scheduling); il ritroso ripassa sulle minacce dell'andata. Dettagli in `F4_Differenze_Scenari.md`, "F6 passo B2bis".
17. **Nuovo modello di bingo G1-G5, passo G1: riserva di disimpegno e minimo di pianificazione (decisioni dell'utente, 2026-10-15)**. Modello complessivo dell'utente: la **riserva** e' il carburante per 5 minuti alla massima spinta (stima dell'utente: il tempo per disimpegnarsi da un'intercettazione e tornare in rotta); il **minimo di pianificazione** e' carburante caricato > rotta intera + riserva; la **soglia di bingo in volo** e' residuo < resto della rotta + riserva, e al bingo c'e' un albero di decisione (continuare, rientro a ritroso, base alternativa entro 3 km dalla rotta, base piu' vicina, perdita). Piano: **G1** riserva + validatore del minimo (fatto); **G2** soglia di bingo e albero di decisione (sostituira' la regola 1,2 della F6-B2bis, che e' un passo intermedio); **G3** consumo di 5 minuti alla massima spinta a ogni ingaggio; **G4** riprogrammazione dopo l'ingaggio; **G5** scenari (S26 riscritto, nuovo S27), Piano, `F4_Differenze_Scenari.md` e manuale.
    - **Dato e unita' (verifica del 2026-10-15)**: fonte `speed_data['emergency']['consume']` di `Aircraft_Data` (66 aerei), letta da `Aircraft.emergency_fuel_flow`. L'unita' NON e' documentata (l'intestazione dei dati documenta solo velocita', quota e portate; il campo non e' mai usato; nessuna fonte in `Analysis/`); e' dedotta **kg/h** per coerenza con il regime `sustained` e con dati reali noti. Evidenze (svuotamento = `fuel_internal_max / consume`; riserva = consumo x 300 s / interno):

      | Aereo | sustained | combat | emergency | interno [kg] | svuot. sustained [h] | svuot. emergency | riserva 5 min |
      |---|---|---|---|---|---|---|---|
      | F-16C Block 52d | 1150 | 2500 | 4500 | 3200 | 2,78 | 43 min | 11,7% |
      | F-15C Eagle | 1500 | 3500 | 6000 | 6103 | 4,07 | 61 min | 8,2% |
      | F/A-18C Hornet | 1350 | 2700 | 4900 | 4925 | 3,65 | 60 min | 8,3% |
      | F-14B Tomcat | 1300 | 3000 | 5200 | 7348 | 5,65 | 85 min | 5,9% |
      | MiG-29S | 1400 | 3500 | 6000 | 4825 | 3,45 | 48 min | 10,4% |
      | Su-27 | 1800 | 4200 | 7000 | 9400 | 5,22 | 81 min | 6,2% |
      | Mirage 2000C | 2000 | 7000 | 10000 | 3900 | 1,95 | 23 min | 21,4% |
      | A-10C (senza postbruciatore) | 1400 | 2200 | 3000 | 4853 | 3,47 | 97 min | 5,2% |

      In kg/h `sustained` e' coerente (F-16 1100-1200 contro circa 1300-1400 kg/h reali in crociera, 2,5-4 h di autonomia interna) e `emergency` lo e' per gli aerei senza postbruciatore (A-10: 3000 contro circa 2 x 1500 kg/h dei TF34 alla spinta massima); lb/h (crociera F-16 di circa 500 kg/h), kg/min e "kg nel `time` del regime" danno valori incompatibili. Per i caccia con postbruciatore pero' `emergency` e' circa la spinta MILITARE (100% a secco) o meno: F-16A 4200 contro circa 4600 kg/h a spinta militare e 25 000-27 000 a postbruciatore pieno (circa 1/6); svuotamenti di 40-85 minuti contro circa 7-8 minuti reali a postbruciatore. I valori reali citati sono ordini di grandezza (consumo specifico x spinta), non fonti del repository.
    - **Scelta dell'utente (strada A)**: si usa il dato com'e', in kg/h, e la riserva e' **ridefinita come "5 minuti alla massima spinta MILITARE"** (non postbruciatore pieno): stima non tarata, che per i caccia con postbruciatore sottostima il consumo reale a postbruciatore pieno di circa 1/6. Motivazione: e' il solo dato di consumo per regime presente nel registro per tutti i 66 aerei; con un vero postbruciatore pieno la riserva dell'F-16 sarebbe circa il 70% del carburante interno e molte missioni non passerebbero il minimo. Alternative scartate per ora: (B) fattore postbruciatore stimato (il registro non dice quali motori lo hanno), (C) correzione del registro, (D) ripiego come fonte primaria.
    - **Implementazione**: `Fuel_Model.DISENGAGE_TIME` = 300 s (STIMA dell'utente); `disengagement_reserve(asset)` = consumo militare [kg/h] x 300 / 3600 / `fuel_capacity_kg()` (interno + serbatoi esterni del loadout, coerente con il contatore in frazione del pieno); provenienza dichiarata da `disengagement_reserve_with_source` (`military_flow`); **ripiego** se mancano il dato o la capacita': `fuel_for_distance(velocita' massima x 300 s, 'max')`, il profilo `attack` del loadout (`max_regime`); altrimenti None (non controllato). Validatore `Mission_Adapter.check_mission_fuel`: per ogni aereo con carburante modellato, `fuel > rotta intera (airborne_legs alla crociera, attese comprese, route_fuel_demand) + riserva`, altrimenti `ValueError` con asset, carburante, fabbisogno, riserva (con la provenienza) e mancanza; funzione separata da `check_mission_bingo` (altra regola: il carico, non il criterio del rientro in volo; i due si possono chiamare entrambi); `EndCriteria.bingo` False o missione non aerea = nessun controllo; NON chiamato da `run_session`, quindi nessun interruttore e fotografia identica.
    - **Arretrato (lavoro futuro, non ora)**: correggere il registro `Aircraft_Data` con dati reali documentati (valori `emergency.consume` e `time` dei 66 aerei: `time` oggi e' letto come minuti, 60 di emergenza, incompatibile con un postbruciatore) ed eventualmente indicare quali motori hanno il postbruciatore, per poter distinguere spinta militare e postbruciatore pieno (strade B e C).
18. **Nuovo modello di bingo, passo G2: soglia di bingo e albero di decisione (decisioni dell'utente, 2026-10-15)**.
    - **Soglia**: l'aereo e' in bingo al primo istante in cui residuo < carburante per il resto della rotta pianificata fino al LAND (attese comprese, alla crociera, come `route_fuel_demand`) + `disengagement_reserve(asset)` (G1). Riserva non modellata = nessun controllo.
    - **Classificazione per tipo di missione**: TRASFERIMENTO = missione aerea di categoria TRANSPORT nella mappa tipo -> categoria di Context (oggi il task 'Transport', `Mission_Adapter.is_transfer_mission`); tutte le altre (aria-aria, aria-suolo, AWACS, Tanker, Recon...) seguono la regola di COMBATTIMENTO.
    - **Albero, trasferimento**: (1) se il residuo basta a CONCLUDERE (resto della rotta, senza riserva) l'aereo continua consumando la riserva, nessun aborto; (2) altrimenti ritroso fino al DEPARTURE (partenza in volo: fino al punto di comparsa, poi diretto alla base del lato piu' vicina, meccanica della F6-B2bis); (3) altrimenti la base amica piu' vicina in linea retta; (4) altrimenti verso la base piu' vicina e, all'esaurimento, le regole della F6-A (planata = ABORTED(FUEL); altrimenti DESTROYED/FUEL_EXHAUSTED con l'equipaggio recuperato).
    - **Albero, combattimento** (attivita' conclusa o no, stessa regola): la missione si interrompe sempre; candidate (a) la base di partenza per la via piu' breve della F6-B2bis (ritroso; anello: anche il resto della rotta; partenza in volo: ritroso fino al punto di comparsa e diretto) e (b) ogni base aerea amica entro `ALTERNATE_BASE_MAX_OFFSET` = 3000 m (decisione dell'utente, STIMA, distinta da `AIR_BASE_AREA_RADIUS_M`) in orizzontale dalla rotta programmata, raggiunta lungo la rotta (in avanti o a ritroso) fino al punto piu' vicino e poi con un tratto diretto in discesa a quota 0 (la base del LAND di una missione non circolare rientra qui); vince la raggiungibile col percorso piu' breve, a parita' la base di partenza e poi (x, y); nessuna raggiungibile: i passi 3 e 4 del trasferimento.
    - **Raggiungibilita'**: il residuo basta per il SOLO percorso alla crociera (la riserva si consuma nel rientro).
    - **Invariati**: dal bingo (se non continua) niente salve offensive, bersaglio e intercettore, a terra (`parking_cold`) sulla base raggiunta, BINGO / ABORTED(BINGO), `EndCriteria.bingo` False = nessun controllo, terra e mare senza bingo, stesso criterio per validatore ed esecutore.
    - **Equipaggio**: `AssetMissionOutcome.crew_recovered` (Optional[bool]): True per l'aereo perso per esaurimento in volo (F6-A e G2), None altrimenti (perdite in combattimento comprese: l'equipaggio non e' modellato); un valore e' ammesso solo con stato DESTROYED. Non e' nella fotografia (l'esito per asset non vi e' registrato).
    - **Conseguenza (solo alla partenza fino a G4)**: con consumo deterministico residuo e resto della rotta calano insieme, quindi la soglia scatta all'inizio dei tratti oppure mai. La funzione di decisione e' GENERALE (`Fuel_Model.bingo_decision`: aereo, tratti della missione intera, istante qualunque, residuo qualunque -> `BingoDecision` con azione e spezzata di rientro), testata su posizioni e residui arbitrari perche' G4 la richiamera' dopo ogni ingaggio; in sessione si applica UNA volta all'inizio dei tratti della missione (`airborne_legs`, come la F6-B2bis): trasferimento che puo' concludere continua, altrimenti ritroso di lunghezza zero (resta a terra sul DEPARTURE, BINGO all'istante della partenza) o, partito in volo, diretto alla base; combattimento: resta a terra o, partito in volo, va alla candidata migliore (alla partenza in volo il diretto alla base piu' vicina al punto di comparsa non e' mai piu' lungo del percorso verso un'alternativa, per la disuguaglianza triangolare: le alternative contano lungo la rotta, da G4).
    - **Interruttore e validatore**: `Session_Simulator.F6_BINGO_DISENGAGE_RESERVE` (default True) sostituisce la regola 1,2 della F6-B2bis (`F6_BINGO_REVERSE_ROUTE` non e' letto); spento, la F6-B2bis o la F6-B2 come prima. `check_mission_bingo(..., disengage_reserve=True)` rifiuta esattamente le missioni che in sessione vanno in bingo (residuo < soglia all'inizio dei tratti, anche il trasferimento che poi continua), con soglia, riserva, istante e decisione nel messaggio; le basi non sono piu' richieste. Rapporto con `check_mission_fuel` (G1): stessa grandezza; il G1 rifiuta con carburante <= minimo, il G2 con carburante < soglia: differiscono solo all'uguaglianza esatta.
    - **Scelte dove le decisioni lasciavano margine**: istante del bingo alla partenza = inizio del primo tratto che consuma (decollo, dopo un'eventuale sosta a terra); basi della linea retta (passi 3 e 4) = basi del lato piu', partendo da una base, il DEPARTURE; partenza in volo senza alcuna base: nessun rientro possibile (`BINGO_NO_BASE`), regole della F6-A come nella F6-B2bis; il trasferimento a ritroso non usa il resto della rotta dell'anello (se il residuo non basta a concludere, il resto della rotta non e' raggiungibile); per una base alternativa il "punto della rotta piu' vicino" e' il minimo globale della distanza orizzontale dalla spezzata dei tratti di movimento, a parita' quello col percorso piu' breve; ogni asset di una base e' un punto d'atterraggio (come la planata della F6-A).
    - Dettagli e fotografia in `F4_Differenze_Scenari.md`, "G2".
19. **Nuovo modello di bingo, passo G3: consumo di carburante in ingaggio (decisioni dell'utente, 2026-10-15/16)**.
    - **Regola**: a ogni ingaggio a cui un aereo partecipa, nell'ISTANTE dell'ingaggio, l'aereo consuma il carburante di `DISENGAGE_TIME` (5 minuti) alla massima spinta militare, la stessa quantita' della riserva di disimpegno del G1. Il movimento resta al suo regime normale (crociera, attese comprese): sostituisce la sovrastima della F6-A (tutto il movimento al regime 'max' se l'asset ha combattuto) per gli aerei.
    - **Punto unico di calcolo**: `Fuel_Model.engagement_fuel[_with_source]` (delega a `disengagement_reserve_with_source`, nessuna formula duplicata); `build_engagement_fuel_event` produce un `FuelEvent` ISTANTANEO (distanza e durata nulle, `regime` = `Fuel_Model.ENGAGEMENT_REGIME` = 'engagement', etichetta che non e' una chiave di `Mobile.FUEL_REGIMES`), limitato al disponibile; nessun evento a serbatoio vuoto.
    - **Regola futura NON implementata**: aerei la cui emergenza dura meno di 5 minuti (WW2): "emergency per min(300 s, `speed_data['emergency']['time']`), poi regime 'combat'"; rimandata perche' il campo `time` del registro non e' affidabile (unita' ignota); da decidere allora se la riserva del G1 la segue.
    - **Partecipa** (`Session_Simulator._engagement_instants`) = la definizione di "ha combattuto" della F6-A: ha lanciato una salva, e' stato bersaglio di una salva (anche mancato o intercettato) o ha intercettato; istante = il primo fra i lanci delle salve sue o dirette a lui e le sue intercettazioni. Il rilevamento senza salve non conta. Solo aerei di MISSIONE (dominio 'air') IN VOLO all'istante: un aereo a terra colpito sul parcheggio non consuma. Un ingaggio = un `resolve_engagement` di una componente connessa: oggi ogni forza e' in una sola componente per sessione, quindi al piu' un consumo per aereo e per sessione (il codice ne conta uno per esito d'ingaggio).
    - **Ordine nella contabilita'**: il consumo d'ingaggio e' inserito fra gli eventi per tratto in ordine di tempo, PRIMA del tratto in cui cade (nessun tratto spezzato, "un evento per tratto" della F6-A invariato); se l'evento MOVEMENT dell'aereo e' gia' passato, applicato subito.
    - **Esaurimento in ingaggio (soluzione minima, coerente con il limite gia' dichiarato dalla F6-A per il regime 'max')**: il contatore va a zero (evento `exhausted`), nessun evento dopo; l'aereo NON e' fermato ne' perso, perche' tratti, contatti e ingaggio sono calcolati a monte alla crociera e non sono ricalcolati (ri-scheduling = G4); esito per asset, planata/perdita F6-A e `crew_recovered` invariati. Il bingo resta valutato solo alla partenza (G2). Caso visibile: S26 'transfer_continue' (0,27, sotto la soglia: se Red spara il contatore arriva a zero poco prima della fine della rotta, completata lo stesso).
    - **Terra e mare**: invariati (regola 'max' della F6-A, quantita' identica alla crociera perche' il registro non distingue i regimi; nessun consumo d'ingaggio).
    - **Interruttore**: `Session_Simulator.G3_ENGAGEMENT_FUEL` (default True); spento, la regola della F6-A esattamente come prima.
    - Dettagli e fotografia in `F4_Differenze_Scenari.md`, "G3".

20. **Nuovo modello di bingo, passo G4a: episodi d'ingaggio (decisioni dell'utente del 2026-10-17, proposta `Proposta_G4_Ri_scheduling.md` §3 "G4a" e §4)**.
    - **Problema**: fino al G3 l'ingaggio era un blocco unico per la sessione (una `resolve_engagement` per componente connessa di forze): X contro A al mattino e contro B la sera era un solo ingaggio, un solo consumo d'ingaggio, nessuna decisione possibile "dopo l'ingaggio" (G4b).
    - **Episodio** (`Session_Simulator._episodes`): gruppo di finestre di contatto legate, direttamente o per tramite di altre, perche' appartengono a coppie di forze che condividono una forza (o forze dello stesso dominio di coordinamento) e si sovrappongono entro `EPISODE_GAP` = 300 s (= `Fuel_Model.DISENGAGE_TIME`, stima dell'utente del G1; legato per costruzione). La componente connessa di prima e' l'unione dei suoi episodi. Ordine deterministico: inizio, `event_id`, prima finestra.
    - **Coda**: un ENGAGEMENT per episodio all'istante della sua prima finestra; `resolve_engagement` sulle sole finestre e forze dell'episodio; esito applicato subito (concatenazione di salute e scorte fra episodi, `assemble_session_outcome(chained=True)` non emette piu' il warning del limite noto).
    - **Forza occupata**: dal primo istante del suo episodio al `t_end` dell'esito (salve in volo comprese); le finestre non ancora risolte delle sue forze che cominciano prima sono ritagliate (CPA e reciproco ricalcolati, `Contact_Scheduler.trim_contact_window`) o scartate; se cambia qualcosa gli episodi rimasti sono ricostruiti.
    - **RNG**: `event_id` invariato, `counter` = ordinale degli episodi con lo stesso insieme di forze (0 per il primo), anche per la tempra (tempra nuova per episodio). Una componente che e' un solo episodio ha lo stream e l'esito di prima.
    - **Forza disingaggiata** passiva negli episodi successivi (`ActivityCriteria.until` = istante del disingaggio, combinato come per il bingo): nessuna salva offensiva, bersaglio e intercettore, nessun ri-instradamento, esito di missione invariato. Esteso (scelta) alle fini di attivita' della F6-B1 scattate in un episodio precedente.
    - **Soglia di danno**: nuovo campo `Engagement_Resolver.ActivityCriteria.reference_health` (None = salute all'ingresso nella run, comportamento precedente); la sessione passa la salute d'inizio sessione.
    - **Consumo d'ingaggio G3**: uno per episodio a cui l'aereo partecipa (nessun codice nuovo: un consumo per esito).
    - **Carburante**: contabilita' spostata in un passo finale, dopo tutti gli episodi, ripercorrendo la stessa coda (ingaggi risolti + MOVEMENT nello stesso ordine): stessi `FuelEvent`. Verificato che il risolutore non legge il carburante e il carburante non legge danno ne' scorte.
    - **Interruttore**: `Session_Simulator.G4_EPISODES` (default True); spento, la componente connessa esattamente come prima.
    - Dettagli, scelte e fotografia in `F4_Differenze_Scenari.md`, "G4a".

21. **Nuovo modello di bingo, passo G4b: ri-pianificazione dopo l'episodio d'ingaggio (decisioni dell'utente del 2026-10-17, proposta `Proposta_G4_Ri_scheduling.md` §3 "G4b" e §4; rientro dopo il disingaggio deciso dall'utente il 2026-10-17)**.
    - **Problema**: col G3 un aereo che dopo un ingaggio e' sotto la soglia di bingo prosegue la rotta e uno che finisce il carburante in ingaggio ha il contatore a zero ma vola e combatte (S26 'transfer_continue'); col G4a una forza disingaggiata prosegue passiva sulla rotta e incontra gli strati successivi (S5).
    - **Quando e chi**: alla fine di ogni episodio (`t_r` = `t_end` dell'esito), gli aerei di MISSIONE che vi hanno consumato (G3, stessa regola della contabilita') o la cui forza vi e' DISINGAGGIATA; in volo, non distrutti, non gia' a secco. Istante della decisione per l'aereo `t_d` = `t_r`, o la fine dei suoi tratti di movimento se la rotta finisce dentro l'episodio (allora conta solo l'esaurimento): scelta necessaria per S26 'transfer_continue', dove l'episodio dura oltre la fine della rotta.
    - **Residuo analitico** (`Fuel_Model.fuel_at`): carburante d'inizio sessione - tratti fino a `t_d` alla crociera (in corso in proporzione) - consumi d'ingaggio fino a `t_d`; stessa aritmetica della contabilita' (test di coerenza).
    - **Esaurimento in ingaggio** (residuo zero): regole della F6-A dal punto a `t_d` (planata o perdita con l'equipaggio recuperato).
    - **Bingo**: `mission_bingo_decision(..., time=t_d, fuel=residuo)` sulla missione intera, albero del G2; se rientra, `BingoEnd` da `t_d` con la meccanica del G2 (BINGO, ABORTED(BINGO)).
    - **Rientro forzato dopo il disingaggio**: `bingo_decision(..., forced=True)` (nessun controllo di soglia, nessun "continua"), sempre con la regola di COMBATTIMENTO (anche per un trasferimento); senza alcuna base nessun rientro (passivo sulla rotta, G4a). Motivo nuovo `AssetEndReason.DISENGAGED`, missione `AbortReason.DISENGAGED`, precedenza a parita' d'istante dopo il bingo (FUEL > BINGO > DISENGAGED > AMMUNITION > DAMAGE). Se fanno rientrare sia il bingo sia il disingaggio vince il bingo. Non dipende da `EndCriteria.bingo`.
    - **Esaurimento sui nuovi tratti**: `Fuel_Model.fuel_exhaustion(..., fuel=residuo)` da `t_d`. Un aereo gia' in rientro e' ri-pianificato di nuovo solo per esaurimento.
    - **Ri-scheduling**: tratti e programma a terra sostituiti da `t_d`; `schedule_contacts` rieseguito sulle sole coppie con un aereo ri-pianificato (nuovo parametro `only_assets`, sottoinsieme esatto); finestre nuove ritagliate a `t_r` e alle forze occupate, finestre non risolte di quegli aerei scartate, episodi rimasti ricostruiti. Scelta aggiunta: il tratto di una finestra nuova gia' coperto da una finestra RISOLTA della stessa coppia di asset con la geometria di prima (prima dell'istante da cui i tratti cambiano) e' tolto (niente seconda estrazione sullo stesso intervallo con gli stessi tratti: visto in S24-ORBIT 'per_leg_off', dove il solo esaurimento anticipato sul rientro creava un secondo episodio sulla coda della finestra gia' risolta).
    - **Terra e mare**: invariati (nessun consumo d'ingaggio, nessun rientro), dichiarato.
    - **Interruttore**: `Session_Simulator.G4_REPLAN` (default True), letto solo con `G4_EPISODES`; spento, il G4a esattamente.
    - **Scenari**: S5 senza basi Blue (partenza in volo) non cambia (`BINGO_NO_BASE`): nuove varianti con una base Blue; S26 'transfer_continue' ora perso per carburante a fine rotta; nuove varianti S26 'post_engagement_bingo' / 'replan_off'; S24-ORBIT 'per_leg_off' (MiG a secco sul rientro dopo l'ingaggio, perso).
    - **Uscita di scena senza basi (decisione dell'utente del 2026-10-17, estensione del G4b)**: un aereo COMPARSO IN VOLO (`start_mode` AIR, nessuna base di partenza) senza alcuna base aerea del suo lato che nella ri-pianificazione dopo un episodio deve rientrare (rientro forzato per disingaggio o bingo dopo l'episodio) non resta piu' passivo sulla rotta (`BINGO_NO_BASE`): ripercorre la rotta a ritroso fino al punto di comparsa (meccanica del ritroso F6-B2bis/G2, alle quote dei waypoint, senza le soste) e li' ESCE DI SCENA: nessuna presenza dopo (come l'aereo che finisce la rotta senza atterrare su una base vera, F5-B), mai a terra, postura `off_scene` a fine sessione se uscito, non distrutto; nessuna salva offensiva dal rientro; esito per asset e missione = il motivo del rientro (DISENGAGED o BINGO, ABORTED(...)) all'istante della decisione. Il ritroso consuma alla crociera; residuo insufficiente: regole della F6-A sul ritroso (senza basi: perso, DESTROYED/FUEL_EXHAUSTED, equipaggio recuperato). Codice: nuova azione `Fuel_Model.BINGO_EXIT` di `bingo_decision(exit_scene=True)` (al posto di NO_BASE, solo con partenza in volo), passata da `Mission_Adapter.mission_bingo_decision(exit_scene=)`, `BingoEnd.exits` in sessione (nessuna sosta, nessun intervallo a terra, postura `off_scene`). Ambito conservativo: SOLO la ri-pianificazione G4b; la decisione del G2 alla partenza (`_decision_end`) resta senza rientro. Sotto-interruttore `Session_Simulator.G4_OFF_SCENE_EXIT` (default True, letto solo con `G4_REPLAN`); spento, il G4b di prima. Scenari: cambiano tutte e sole le esecuzioni con un aereo comparso in volo senza basi del lato che rientra dopo un episodio (S5 'default'/'resistant', e altri scenari con formazioni aeree disingaggiate senza basi, v. `F4_Differenze_Scenari.md`, "G4b: uscita di scena"); nuova variante S5 'exit_off' (uscita spenta).
    - Dettagli, scelte e fotografia in `F4_Differenze_Scenari.md`, "G4b".

22. **Nuovo modello di bingo, passo G5: scenari e chiusura del piano G1-G5 (2026-10-18)**.
    - **Codice del motore**: nessun cambio. Scenari e documenti soltanto; il manuale DES e' aggiornato a parte.
    - **S26 riscritto sul modello finale**: docstring e test organizzati intorno al bingo di G1-G4 (riserva, soglia e
      albero, consumo d'ingaggio, episodi e ri-pianificazione); le varianti sono divise in **modello finale** ('none',
      'bingo', 'transfer_return', 'transfer_continue', 'no_base', 'bingo_off', 'post_engagement_bingo') e
      **controprova degli interruttori** ('switch_off' = `F6_BINGO`, 'reverse_off' = la F6-B2, 'reserve_off' = la
      F6-B2bis, 'engagement_fuel_off' = la F6-A senza consumo d'ingaggio, 'replan_off' = il G3 senza G4b), con un test
      che verifica la partizione e che ogni controprova spenga davvero il suo interruttore. Nomi, ordine e costruzione
      delle varianti invariati (chiavi della fotografia): le 96 esecuzioni di S26 sono identiche.
    - **S27-DOUBLE**: un F-16C 'Strike' con carburante 0,53 su una rotta di 500 km con due siti Red separati (due
      episodi, finestre a ~480 s di distanza > `EPISODE_GAP`) e una base alternativa sulla rotta oltre il secondo sito:
      due consumi d'ingaggio nella stessa sessione (il limite "uno per sessione" del G3 e' risolto dal G4a), dopo il
      primo episodio il residuo resta sopra la soglia (nessun rientro), dopo il secondo e' sotto: BINGO e rientro sulla
      base alternativa; lo stesso caso in trasferimento CONTINUA e completa la rotta; controprova con `G4_REPLAN`,
      `G4_EPISODES` e `G3_ENGAGEMENT_FUEL` spenti. Il carburante 0,53 e' dimostrato nel test fra rotta + 2 riserve e
      rotta + 3 riserve (con il solo moto alla crociera la soglia dopo k consumi non dipende da dove e' l'aereo).
    - **Stato finale del modello di bingo** (G1-G5 approvati, fotografia 918): riserva di disimpegno
      = 5 minuti alla massima spinta militare (`DISENGAGE_TIME`); validatore del minimo `check_mission_fuel` e bingo a
      priori `check_mission_bingo`; soglia = resto della rotta + riserva con albero trasferimento/combattimento e basi
      alternative entro 3 km; consumo d'ingaggio per episodio; episodi d'ingaggio con `EPISODE_GAP` = 300 s;
      ri-pianificazione a fine episodio (bingo, esaurimento, rientro forzato dopo il disingaggio, uscita di scena senza
      basi). Interruttori tutti attivi: `F6_BINGO`, `F6_BINGO_DISENGAGE_RESERVE` (`F6_BINGO_REVERSE_ROUTE` letto solo
      a G2 spento), `G3_ENGAGEMENT_FUEL`, `G4_EPISODES`, `G4_REPLAN`, `G4_OFF_SCENE_EXIT`.
    - **Limiti residui noti** (il piano G1-G5 si chiude con questi aperti):
      - dati `speed_data['emergency']` del registro `Aircraft_Data` non tarati: `consume` letto in kg/h per deduzione
        (unita' non documentata, ~1/6 del postbruciatore pieno per i caccia che lo hanno), `time` di unita' ignota e non
        usato (deviazione 17, arretrato); riserva e consumo d'ingaggio restano STIME;
      - regola per gli aerei la cui emergenza dura meno di 5 minuti (WW2: emergenza per min(300 s, `time`), poi
        'combat') NON implementata, in attesa di un `time` affidabile (deviazione 19);
      - i validatori di pianificazione `check_mission_fuel` (G1) e `check_mission_bingo` NON sono chiamati da
        `run_session`: sono del pianificatore (F8, validatore di sessione, da confermare);
      - nessuna salva offensiva dopo il bingo (scelta della F6-B2): dal rientro l'aereo resta solo bersaglio e
        intercettore, non attacca piu' nemmeno una minaccia che reincontra sul ritroso;
      - decisione presa alla FINE dell'episodio, non a meta'; il rientro a ritroso ripercorre le minacce dell'andata;
        nessun rientro per danno (aereo oltre la soglia della F6-B1 passivo sulla rotta); terra e mare senza bingo;
      - F6-B3 aperto: S24-GLIDE dichiara ancora `EndCriteria(bingo=False)`; con il bingo di default cambierebbero le
        sue esecuzioni (decisione dell'utente da prendere);
      - G4a: esito degli episodi "vuoti" per finestre di aerei gia' distrutti (lo scheduler non le tronca).
    - Dettagli, S27 e confronto in `F4_Differenze_Scenari.md`, "G5".

23. **F7a: regole d'ingaggio di missione (decisioni dell'utente del 2026-10-18, proposta `Proposta_F7_Bersagli_Filtro_Armi.md` §2-§5)**.
    - **Scomposizione e architettura** (decisioni 1-2): la F7 e' divisa in F7a (qui) e F7b (fuoco su posizione, fatta
      dopo: deviazione 24); la F7a ha due strati: (W) politica d'armi per tipo di missione come involucro della fire control
      (`Fire_Control.restrict_by_policy`, conosce i registri) e (T) `Engagement_Resolver.TargetRules` per asset nel
      risolutore (il risolutore continua a non leggere la missione). Interruttori `Session_Simulator.F7_WEAPON_POLICY`
      e `F7_TARGET_RULES` (attivi, indipendenti; spenti entrambi il comportamento e' quello di prima).
    - **Semantica ROE** (decisione 3) della tabella del piano §2.3, con le correzioni dell'utente del 2026-10-18:
      `weapon_hold` senza fuoco ma con le intercettazioni; `return_fire` solo contro ostili (chi ha lanciato contro il
      dominio di coordinamento), con reazione NELLA STESSA run: un candidato escluso perche' non ostile non e' esaurito
      ma rimandato, e il lancio di un nuovo ostile risveglia i tiratori `return_fire` del dominio dopo il loro
      `refire_interval` (evento `_WAKE`, come la reazione L3); `only_designated` con l'esenzione d'autodifesa aerea;
      `priority_designated` (solo aerei) in due fasi: in AVVICINAMENTO nessun tiro sulle opportunita' di superficie
      (un aereo che sorvola una colonna andando al bersaglio non spara, non consuma armi e carburante d'ingaggio ne'
      apre un episodio; il designato si ingaggia quando e' rilevato e a portata; i bersagli aerei non cambiano), DOPO
      L'ATTACCO opportunita' ammesse con le armi residue (le riservate restano escluse) e precedenza al designato solo
      se rilevato E a portata (altrimenti si spara alle opportunita', senza attendere). Fine dell'attacco = designato
      distrutto OPPURE punto ATTACK raggiunto e superato sui tratti REALI dell'aereo (`TargetRules.attack_point`,
      `Mission_Adapter.attack_point`; attese, ritardi e ri-pianificazioni compresi, non l'ETA pianificata); senza punto
      ATTACK o con punto mai raggiunto l'aereo resta in avvicinamento (comportamento conservativo). ROE di default
      invariata `weapon_free` (decisione 4, B1).
    - **Politica d'armi** (decisioni 5-8): tabella `Context.MISSION_WEAPON_POLICY` confermata riga per riga (solo
      aria; terra e mare `None`); classe `air_defence` = `Vehicle` `isSAM`/`isAAA`/`isEWR`; armi assenti dai registri
      (`test:*`) senza vincoli; autodifesa da `self_escort_capability` (la F7a non tocca i registri; il dato dei 5 loadout
      A-10C II con AIM-9M, flag False, e' stato poi CORRETTO a True dall'utente: v. sotto).
    - **Bersagli e armi designate** (decisioni 9-12): `Target.asset_ids` (sottoinsieme del GROUP);
      `MissionAsset.weapons` (implicito da `AttackProfile.weapon`, sul designato solo quelle e nessun ripiego,
      riservate sui non designati); `Mission_Adapter.TARGET_POINT_RADIUS_M` = 500 m (STIMA) piu' l'incertezza
      ESTIMATED; `target_destroyed` per POINT/AREA/ZONE resta non rappresentabile.
    - **Coerenza e memoria** (decisioni 13-14, 16): loadout di missione diverso da quello assegnato = `ValueError`;
      memoria di `return_fire` per sessione (ostili degli episodi precedenti come `known_hostile_ids`); scorta senza
      protezione del gruppo (bersaglio amico = nessun designato).
    - **Scenari**: S19AD senza filtri di test (arma designata + bersaglio ristretto + `only_designated`), 24
      esecuzioni identiche; nuovo S28 (ROE con andata/ritorno e punto ATTACK, politica d'armi, ZONE), 52 esecuzioni nuove.
    - **Limiti** (v. `F4_Differenze_Scenari.md`, "F7a"): la designazione geometrica (area) e' valutata alla prima
      decisione sulla coppia e il candidato fuori area e' esaurito per la finestra: un bersaglio che entra nell'area dopo
      la prima valutazione non e' ingaggiato (LIMITE DICHIARATO, non implementato per decisione dell'utente); la F7b
      (deviazione 24) e' fatta.
    - **Limite "self_escort A-10C non corretto" CHIUSO** (decisione 8, 2026-10-18): `self_escort_capability` = True sui
      5 loadout A-10C II con AIM-9M in `Aircraft_Loadouts.py` ('Low Level Bomb Run', senza AIM-9, resta False);
      4 esecuzioni di S28 cambiate (`S28-CLASS/*/self_defence`), v. `F4_Differenze_Scenari.md`, "Correzione dati A-10C".
    - Dettagli, scelte e confronto in `F4_Differenze_Scenari.md`, "F7a".

24. **F7b: fuoco su posizione (decisione 15 dell'utente del 2026-10-20, proposta `Proposta_F7_Bersagli_Filtro_Armi.md` §6)**.
    - **Regola**: missione di terra o di mare con bersaglio POINT o AREA e azione `MissionAction(TASK, 'Fire_At_Point',
      params={'rounds', 'weapon'})` su un waypoint (validata in `Mission`); istante di tiro = arrivo al waypoint e
      condizione d'avvio (ON_ARRIVAL / AT_TIME / AFTER_DURATION); impatto a `t_fire + time_of_flight` (formula di
      `shot_spec_for`); punto mirato = posizione STIMATA (N3.e), dispersione uniforme nel disco di raggio `max(radius_m,
      uncertainty_m ESTIMATED, 50 m)`, letalita' a soglia (raggio 0,25 m/mm x calibro, ripiego 25 m, con la sola
      `destroy_capacity` della riga del template): colpisce solo chi c'e' davvero nel disco all'impatto, non dove il
      bersaglio si e' spostato (comportamento osservato in `ground_sea_mission.miz`).
    - **Scelte 15a-15g** (tutte come raccomandate): solo terra e mare (aerei esclusi e armi `missile` escluse); raggio letale
      STIMA 0,25 m/mm con ripiego 25 m; dispersione minima 50 m (STIMA); niente fuoco amico; nessuna intercettazione; un solo
      evento all'impatto; nessun effetto dottrinale (tempra, disingaggio, shock) sul lato colpito (l'esito ha zero forze).
    - **Architettura**: terzo tipo di evento di sessione `AREA_FIRE_EVENT` (ENGAGEMENT < AREA_FIRE < MOVEMENT), risolto
      fra gli episodi d'ingaggio; RNG `order.rng(mission_id=<missione>, event_id='area_fire|<missione>|<asset>|<wp>|<azione>',
      counter=0)` (primo uso dello slot `mission_id`); esito applicato subito e accodato a `results`/`resolved`
      (`EngagementResult` con `forces=()`); le distruzioni entrano nelle conoscenze degli episodi successivi. Interruttore
      `F7_AREA_FIRE` (attivo; spento le azioni sono ignorate con un warning).
    - **Scenario**: S29-AREA ('stale', 'on_target', 'switch_off', 4 seed = 12 esecuzioni nuove): l'artiglieria che spara dove
      i blu erano colpisce solo chi c'e' ancora (criterio della Fase 7, "Fatto quando").
    - **Limiti** (v. `F4_Differenze_Scenari.md`, "F7b"): modello volutamente semplice (costanti STIMATE non tarate);
      l'istante d'impatto che ordina l'evento e' stimato senza la scorta; `target_destroyed` per POINT/AREA resta non
      rappresentabile (decisione 12 della F7a).
    - Dettagli, scelte e confronto in `F4_Differenze_Scenari.md`, "F7b".

**Punti aperti rilevati dall'aggiornamento del manuale** (capitolo 10 §9.6 del manuale DES):
- docstring obsoleti in `Session_Simulator` (dicono ancora che la selezione dell'arma resta fuori dall'orchestratore);
- `run_session` non inoltra `rwr_catalogue` al risolutore;
- nessun codice di produzione fornisce `morale_for` / `enemy_estimate_for` (solo i test);
- una missione sul posto risulta `FAILED` perché manca uno stato "in corso" (D4.e);
- ruoli e criteri di fine: i ruoli restano validati ma non letti da `Logic`; bersaglio e regole (ROE, armi designate) sono letti dalla F7a e le azioni `Fire_At_Point` dalla F7b (F5-F6 per i criteri di fine); `Operation` è letta dalla F4b+ (`coordination_domains`: `Operation.mission_ids` e `Mission.operation_id`).
