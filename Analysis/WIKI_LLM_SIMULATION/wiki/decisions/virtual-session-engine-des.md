---
title: "Motore sessioni virtuali: architettura DES a coda eventi"
type: decision
tags: [architecture, dwm, simulation, discrete-event, combat-resolution, routing]
created: 2026-09-21
updated: 2026-09-23
status: accepted
affects: ["[[logic-routing]]", "[[asset-air]]", "[[asset-ground-naval]]", "[[block]]", "[[command]]"]
related: ["[[core-simulator-agnostic]]", "[[c2-hierarchy-design]]", "[[event-driven-simulation]]", "[[route-model-unification]]"]
---

## Contesto

Il design C2 (v. [[c2-hierarchy-design]]) prevede sessioni di campagna "virtuali" — turni
sintetici eseguiti senza un giocatore DCS, che nel modello a due velocità (DCS interattivo vs
sintetico in background) devono coprire ore di tempo di gioco in tempo di calcolo ragionevole
(budget dichiarato dall'utente: fino a minuti). Serviva un motore di esecuzione per queste
sessioni. L'utente ha proposto due strategie candidate in
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali.txt`:

1. **Tick a 1 ms con slot per asset**, con un ciclo di decisione per agente ispirato all'OODA
   loop (RIV/VAL/COM/ATT — Rileva/Valuta/Comunica/Attacca).
2. **Risoluzione probabilistica** dell'esito di un ingaggio, senza simulazione passo-passo.

Un'analisi dedicata (4 subagent: due di ricerca esterna, uno per strategia, due di esplorazione
del codice esistente) ha prodotto il verdetto sotto, documentato per esteso in
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` (525 righe, con
bibliografia).

## Decisione

**Nessuna delle due strategie proposte, presa alla lettera, è adottata. Il motore è un DES
(discrete event simulation) a coda eventi con scheduling analitico dei contatti**, in secondi
assoluti, senza alcun tick globale.

### Verdetto sulle due strategie

- **Strategia 1 (tick 1 ms) — scartata come motore primario.** 2 ore di sessione × 10.000 asset
  = 6,687·10¹⁰ aggiornamenti: 3,2 ore al pavimento assoluto di CPython (loop vuoto), **74 giorni**
  a costo Mesa reale (95,7 µs/agente-step), 3,6–21 **anni** se il rilevamento è O(N) per asset. Il
  passo è dimensionato sul missile ipersonico, che lo stesso testo esclude dalla simulazione a
  tick. Nessun simulatore entity-level reale funziona così: JTLS è time-stepped ma **aggregato**
  (battaglione/brigata, Lanchester); JCATS/BRAWLER/AFSIM/ESAMS sono **event-driven**. Trovata
  anche un'incongruenza aritmetica nel testo originale (divisore `4,21/0,1=43` non riconducibile
  né allo slot né al ciclo dichiarati).
- **Da salvare della Strategia 1**: RIV/VAL/COM/ATT è l'OODA loop, e i suoi ordini di grandezza
  sono corretti e utili (Osa 26 s, S-300P 28 s, Tor 5-8 s, pilota 1-2 s, equipaggio carro ~31 s).
  Vanno conservati come **latenze di reazione schedulate come eventi futuri**, non come conteggio
  di cicli — decidono *chi spara per primo*, l'informazione la cui assenza fa fallire i modelli a
  rapporto di forze puri.
- **Strategia 2 (probabilistica) — direzione giusta ma incompleta.** Non specifica **quando e se**
  due forze si incontrano: è il buco più grave, da colmare analiticamente (CPA/TCPA + intersezione
  rotta↔volume), non con un tick.

### Architettura scelta

Quattro strati, tempo in secondi assoluti:

0. **Contratto** `SessionOrder`/`SessionOutcome` puro dominio (v. [[core-simulator-agnostic]]) +
   RNG seedato esplicitamente.
1. **Scheduler dei contatti** (il pezzo mancante in entrambe le strategie): rotta↔cilindro →
   intervalli temporali via `Route.travelTimeToEdge`; CPA/TCPA fra mobili con
   `t* = −(Δr·Δv)/|Δv|²`; potatura gerarchica a livello `Block` prima delle coppie di asset (è
   ciò che evita la complessità O(N²)).
2. **Risolutore d'ingaggio**: probabilità di detezione → latenza di reazione (chi spara primo) →
   regole d'ingaggio → probabilità di uccisione da `accuracy × destroy_capacity`; **modello a
   salva di Hughes** per gli scenari molti-contro-molti.
3. **Applicazione stato** per-asset → `SessionOutcome` → `Campaign_State`, in una sola passata.

Un micro-passo fine (1-5 s) è ammesso **solo dentro una finestra di ingaggio attiva**, mai come
passo globale della simulazione.

### Vincoli dell'utente registrati (non negoziabili, non frutto dell'analisi)

1. I 10.000 asset sono un **limite superiore teorico**, non un caso tipico da ottimizzare.
2. La sessione deve essere **riproducibile da seed** — e l'**ordine di risoluzione degli eventi**
   fa parte del contratto di riproducibilità: salvare il solo seed non basta.
3. Perdite e danni sono **per singolo asset**, mai aggregati.
4. Budget di calcolo per sessione: fino a **minuti**.

### Avvertimento metodologico permanente

I modelli Lanchester non si validano su dati storici (9 test falliti su Ardenne/Kursk citati
nella bibliografia); la regola 3:1 in versione RAND usata da JICM azzecca solo il **19%** su 98
ingaggi storici — peggio del caso casuale. Conseguenza diretta per Warfare-Model:
`Logic/Tactical_Evaluation.py:251 calcFightResult` (modello a rapporto di forze con coefficienti
tabellati a mano) resta un **fallback aggregato**, mai il risolutore primario. Se in futuro serve
comunque un livello aggregato, i coefficienti vanno stimati con un **ATCAL interno** (far girare
offline il risolutore fine e ricavarne i coefficienti), non inventati a tavolino.

**Riesaminato il 2026-09-22 contro una fonte nuova e confermato invariato.** L'ingestione di
[[source-lanchester-scenari-ai]] (9 documenti su modelli Lanchester e scenari applicati) non porta
alcuna evidenza che scalfisca questo avvertimento: nessun coefficiente con provenienza, nessuna
equazione a salva, nessun contenuto che tocchi lo strato 1. Il fit Ardenne/Kursk che quella fonte
presenta come "validazione" ($p \approx q \approx 0{,}5$ nella forma di Bracken) **concorda** con i
9 test falliti citati qui — dice anch'esso che né la legge lineare né la quadratica tengono; la
differenza è solo che chiama validazione un fit a posteriori con due parametri liberi su una sola
battaglia. Valutazione completa in [[lanchester-vs-motore-des]]; tre raccomandazioni che ne
discendono, **non ancora decise**, in [[soglie-disingaggio-e-attrito-aggregato]] (`status:
proposed`) — di cui la sola rilevante per la Fase 4 è che l'`Engagement_Resolver` avrà bisogno di
una **soglia di disingaggio**, perché altrimenti ogni ingaggio risolve fino all'annientamento.

## Motivazione

La scelta discrimina fra le due proposte sulla base di numeri verificabili (costo computazionale
misurato/proiettato) e di precedenti reali nel campo della simulazione entity-level militare
(nessun sistema citato in letteratura usa tick fissi su scala individuo/asset per una campagna
intera), non su preferenza di design. La combinazione "scheduling analitico dei contatti +
risoluzione a eventi" preserva sia il realismo del chi-spara-primo (che la Strategia 1 catturava
correttamente) sia la scalabilità (che solo un approccio event-driven garantisce ai volumi
dichiarati).

## Conseguenze

**Roadmap a 7 fasi** (dettaglio completo in
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md`):

`0` contratto+RNG → `1` cinematica → `2` percezione → `3` `Logic/Contact_Scheduler.py` → `4`
`Logic/Engagement_Resolver.py` + `Context/Reaction_Profile.py` → `5` danno per-asset → `6`
`Logic/Session_Simulator.py` → `7` validazione + test di agnosticismo (v.
[[core-simulator-agnostic]]).

**Fase 1 (cinematica) — FATTA e pushata, 2026-09-21** (commit `3af377c5`, branch
`analysis/dce-dcs-persistence`): schema canonico `Mobile.speed` in m/s, ponte
registry→istanza, `Route.positionAtTime(t)`, `Military._speed_regime`, fix del default mutabile e
del setter rotto su `Mobile.speed`. Sblocca le precondizioni 1 e 2 dell'elenco sotto. Suite: 2540
→ 2608 test OK. Dettaglio in [[asset-base]] §Stato attuale.

**Fase 2 (percezione) — FATTA e pushata, 2026-09-22** (commit `30a6ee55`, stesso branch):
`Mobile.detection_range(mode, sensor, range_type)` (raggi radar/TVD, mai esposti prima) e la
fabbrica `build_threat_aa()` in `Logic/Air_Route_Manager.py` (da `Mobile.air_defense_volume()` +
dati arma reali + tabella SAM di riferimento per le latenze). Sblocca le precondizioni 3 e 4.
Suite: 2608 → 2685 test OK. Dettaglio in [[asset-base]] §Stato attuale, [[logic-routing]]
§`Air_Route_Manager.py`, [[block]] §`Military.py`.

**Undici precondizioni bloccanti** trovate nel codice riga per riga durante l'analisi (elenco
completo nel documento sorgente) — oltre alle 4 già risolte da Fase 1-2: nessuna API di raggio di
rilevamento (risolta Fase 2), `ThreatAA` mai costruito da un asset reale (risolta Fase 2), nessuna
`apply_damage` (solo `asset.health = int`), `random` non seedato a livello di modulo, **tre
modelli `Route`/`Edge`/`Waypoint` incompatibili** (v. sotto), `DataType/Event.py` rotto, un bug in
`evaluateGroundRouteDangerLevel`, **SAM/AAA/EWR con combat power ≡ 0 per costruzione**.

**Le 3 questioni aperte pre-Fase 3 (documento sorgente, §9) sono state chiuse il 2026-09-22**
(commit `6c421579`/`f1f5b7d4`/`64538f16`/`27d53e56`, stesso branch; suite 2685 → 2753 test OK):

- **Q1 — modello Route**: `DataType.Route` confermato unico modello di dominio, esteso
  esplicitamente anche all'aria; i modelli locali di `Air_`/`Ground_Route_Manager` restano come
  stato di lavoro privato dell'algoritmo di ricerca. Fase 1 di un piano a 5 fasi fatta
  (`Logic/Route_Adapter.py`). Decisione completa: [[route-model-unification]].
- **Q2 — perdita per-asset**: nuovo `Logic/Damage_Model.py` + `Asset.apply_damage()`. Contratto:
  `accuracy`=P(colpo a segno), `destroy_capacity`=P(distruzione|colpo) — nessuna costante nuova,
  è la Pk già usata nei registri arma scomposta in Ph×Pk|h. Tre esiti (KILL/DAMAGE/MISS), un
  colpo può uccidere direttamente, l'accumulo (~1/dc colpi) è emergente non parametrico. Soglia
  `Destroyed ≤ 15` **confermata invariata** (il "mission kill" a ≤50 e la "distruzione" a ≤15
  erano già entrambi nel modello via `State.isOperative()`). RNG mai interno al modulo:
  `resolve_hit` riceve `draw` dal chiamante (RNG di sessione, Fase 0).
- **Q3 — SAM/AAA/EWR nel combat power**: **restano a 0, confermato intenzionale** (la tabella
  misura fuoco/manovra terra-terra, non ciò che questi asset fanno). Il bisogno pratico di un
  numero (un C2 non vedrebbe mai un sito SAM come bersaglio prioritario) è risolto con una
  **dimensione separata**, non una tabella di efficacia inventata: `Military.air_defense_power()`
  in [0,1], `1 − Π(1 − danger_level_i)` sui `ThreatAA` della Fase 2.

**3 punti lasciati aperti dopo Q1-Q3 — chiusi 2026-09-22** (commit `efb93cab`, `5a87ebb2`):
1. **SEAD collegato**: `Tactical_Evaluation.calculate_priority` legge `air_defense_power()` del
   bersaglio quando l'attaccante è aereo e il target ha combat power 0, mappando `[0,1]→[0.1,10.0]`
   invece di saturare sempre al floor. Attaccanti ground/sea invariati.
2. `Damage_Model.MIN_EFFECTIVE_HIT_DAMAGE = 1` confermata, nessuna modifica.
3. `Edge.calcLength()` non distingue per `path_type`: **il commento era il bug**, corretto —
   la distanza 3D è fisicamente corretta anche per il ground (le posizioni asset portano già
   quota reale), il codice non è stato toccato per non alterare lunghezze/tempi già in uso.

Bug collaterale trovato e corretto nello stesso giro (non uno dei 3 punti, emerso rileggendo
`Route_Adapter.py`): `Edge.intersectPoint(Line2D)` usava `self._line` (3D) invece di
`self._line2d`, producendo un'intersezione vuota silenziosa per ogni edge non a quota zero — v.
commit `5a87ebb2`, nuovo `Test_Edge.py`.

**Precondizioni bloccanti aggiuntive risolte da questo lavoro** (elenco delle 11 sopra): #5
(`apply_damage`, ora esiste), #7 (Route/Edge/Waypoint, v. Q1), #10 (SAM/AAA/EWR, v. Q3).

**Fase 3 (scheduler dei contatti) — FATTA 2026-09-22** (commit `42cc67f1`): `Logic/Contact_Scheduler.py`,
96 test nuovi. Suite 2753 → 2858.

**Fase 4 (risolutore d'ingaggio) — FATTA e COMMITTATA 2026-09-23** (commit `44bc6950`, non pushato):
`Logic/Engagement_Resolver.py` + `Context/Reaction_Profile.py`. Decisioni di design accettate lo
stesso giorno: soglie di disingaggio (P1) in dottrina di lato per forza intera, saturazione
difensiva per-salva (R1) come funzione dedicata separata da `air_defense_power()`, munizioni per
asset (R3) senza rifornimento nel motore, congelamento del payload (R4). Rifiniture successive:
ripartizione del fuoco round-robin, munizioni aerei dal loadout assegnato
(`Aircraft.assigned_loadout`), degradazione della Pd da meteo/notte collegata a `Meteo_Analysis`.
Suite 2858 → 3027. Vedi [[soglie-disingaggio-e-attrito-aggregato]] e
[[risolutore-ingaggio-salva-fase4]] per il dettaglio delle decisioni; [[llm-locale-ruolo-e-confini]]
resta rimandata (nessun LLM nel motore).

**Fase 5 (contratto SessionOutcome, RNG di sessione, carburante) — FATTA 2026-09-23**, da
committare: `Command/Session_Types.py` (`SessionOrder`/`SessionOutcome`/`assemble_session_outcome`
— chiude anche la "Fase 0" mai fatta finora), `Utility/Session_Rng.py` (seed = SHA-256 su chiave
canonica `(session_id, mission_id, event_id, counter)`, mai `hash()` di Python), `Logic/Fuel_Model.py`
+ carburante su `Mobile`/`Aircraft` (unità: **frazione del carico pieno [0,1]**, non kg — Vehicle/Ship
non hanno una capacità di serbatoio nei registri, solo l'autonomia in km/nm; per gli aerei dal
loadout assegnato con fattore 2× sul raggio d'azione dichiarato; navi nucleari non modellate,
scelta corretta non di comodo). Suite 3027 → 3115. Nessun `apply_session_outcome`/scrittura
`Campaign_State`: resta responsabilità del futuro `Theater_Session_Manager`.

**Prossimo passo**: Fase 6 (`Logic/Session_Simulator.py`, l'orchestratore a coda eventi) o Fase 7
(validazione, scenari S1-S11, test di agnosticismo).

## Fonti

- [[project_virtual_session_engine_design]] (memoria di origine, dettaglio completo Fase 1-5)
- [[project_session_2026_09_21_summary]] (recap sessione, stato git)
- `Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` (analisi completa, 525
  righe, bibliografia con URL)
- `Analysis/Document/Architettura_esecuzione_sessioni_virtuali.txt` (proposta sorgente dell'utente)
