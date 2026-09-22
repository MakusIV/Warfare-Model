---
title: "Vincolo architetturale: core simulator-agnostic"
type: decision
tags: [architecture, dwm, dcs, dce, core, adapter, simulator-agnostic]
created: 2026-09-18
updated: 2026-09-18
status: accepted
affects: ["[[virtual-session-engine-des]]", "[[command]]", "[[logic-routing]]"]
related: []
---

## Contesto

Il 2026-09-18 è stato analizzato in profondità il Dynamic Campaign Engine (DCE di MBot,
ScriptsMod NG 20.47.105), un progetto Lua esistente che implementa una campagna dinamica sopra
DCS, come termine di paragone per Warfare-Model. L'analisi ha rilevato che **DCE non ha alcun
core indipendente**: `oob_ground` replica letteralmente la struttura del file `mission` del
`.miz`, `targetlist` usa coordinate mappa DCS, `DC_Weather` scrive direttamente
`mission.weather`, e non esiste alcun modello di combattimento proprio — è DCS stesso a
risolvere gli ingaggi. Tolto DCS, DCE non produce nulla: è un insieme di adapter senza dominio
sottostante.

Warfare-Model parte da una posizione migliore (`Combat_Power_Estimation`, `Tactical_Evaluation`,
`Strategical_Evaluation` sono l'embrione di un risolutore proprio), ma il rischio di
contaminazione era ed è alto: tutta l'analisi e i dati DCS ingeriti in quella stessa sessione
(schema `debrief.log`, struttura `.miz`, enum `S_EVENT_*`, tabelle armi `db_firepower.lua`) sono
per natura materiale da adapter, non da core.

## Decisione

Il core Python di Warfare-Model deve modellare **tutti** gli aspetti del dominio (forze, terreno,
logistica, combattimento) **indipendentemente da quale simulatore lo esegue**. DCS è uno dei
simulatori possibili, integrato tramite moduli di interfaccia dedicati — non l'unico. In linea
teorica il core deve poter far girare una campagna **con sole sessioni sintetiche**, senza alcun
simulatore esterno.

**Test operativo di agnosticismo**: cancellando l'adapter DCS, la campagna deve continuare a
funzionare. Se qualcosa si rompe, quella cosa era nel posto sbagliato.

**Cosa non entra mai nel core**: dipendenze da `lupa`/`zipfile`/`minizip` (lettura file DCS); ID
del simulatore (`unitId`, `groupId`, `airdromeId`, `DictKey_*`); stringhe di tipo DCS (es.
`"MiG-21Bis"`); unità di misura o convenzioni del simulatore; orologio del simulatore
(`timer.getTime()`).

**Contratto di confine**: le porte `SessionOrder` (core → sessione) e `SessionOutcome`
(sessione → core) vanno definite per prime, dimensionate sull'**unione** di ciò che DCS e un
risolutore sintetico sanno produrre, con campi non universali opzionali e **provenienza
dichiarata per campo** (`measured`/`derived`/`estimated`) — coerente con la distinzione
osservato/stimato già introdotta per il fog-of-war (v. [[combat-power-priority-redesign]]).

**Ordine di lavoro imposto (controintuitivo)**: 1) contratto delle porte; 2) un
`SyntheticResolver` nel core, anche rozzo; 3) far girare una campagna intera **senza
simulatore**; 4) **solo dopo**, l'adapter DCS, vincolato a produrre lo stesso `SessionOutcome`.
Invertire l'ordine (partire dall'adapter DCS) farebbe nascere il contratto modellato su DCS,
perdendo l'agnosticismo fin dall'inizio.

**Warehouse come concetto di dominio**: DCE non usa i warehouse — scelta corretta nell'ottica
agnostica. Le warehouse DCS (scriptabili da 2.8.8) sono una **proiezione** dell'adapter verso lo
stato del core, mai la sua rappresentazione.

**Separazione dati**: fisica reale e dottrina (inviluppi SAM, tempi di acquisizione, tipo
contromisura, layout dei siti, priorità SEAD, anni di servizio, tassonomie) → core. Rappresentazione
specifica DCS (codici HARM, simboli RWR, nomi di tipo DCS, preset nuvole, ICAO/TACAN) → adapter.
Un sito SAM è un gruppo di asset eterogenei, non un asset singolo.

## Motivazione

Il pezzo davvero mancante in entrambi i progetti (Warfare-Model e DCE) è la **risoluzione
dell'ingaggio** più il consumo di munizioni/carburante — non esiste in nessuno dei due. Costruirlo
nel core, dietro un contratto stabile, è l'unico modo per non ripetere l'errore strutturale di
DCE: se il risolutore vive nell'adapter (o, come in DCE, non esiste affatto e si delega tutto al
simulatore), il core smette di essere un modello e diventa un traduttore.

## Conseguenze

Questo vincolo guida direttamente il design del motore DES per le sessioni virtuali (v.
[[virtual-session-engine-des]]): lo scheduler dei contatti, il risolutore d'ingaggio e
`Session_Simulator` sono pensati da subito come componenti del core, capaci di girare senza DCS.
Guida anche `Command/` (v. [[c2-hierarchy-design]]): `SessionOrder`/`SessionOutcome` sono il
contratto che il `Theater_Session_Manager` scambierà con l'esecutore di sessione, DCS o
sintetico che sia.

Tre elementi utili di DCE, letti attraverso questa lente (non copiati, adattati al vincolo core/
adapter):
- `DC_Weather.lua` → riferimento per sostituire il placeholder `Logic/Meteo_Analysis.py` con un
  modello sinottico a zone (core), mantenendo la generazione METAR/preset nuvole nell'adapter.
- `DC_Tactical.commander()`/`airDirective()` → riferimento per `Logic/Strategical_Evaluation.py`
  e per l'"indirizzo strategico" del design C2 (v. [[c2-hierarchy-design]]) — metriche
  differenziali su perdite/costo perdite, interpolazione su soglie, tutto dominio puro.
- `camp_triggers` → DSL dichiarativo per eventi di campagna, assente in Warfare-Model; si lega al
  lavoro fog-of-war (v. [[combat-power-priority-redesign]]).

Non ancora fatto: il `SyntheticResolver` minimo (punto 2 dell'ordine di lavoro) e il contratto
`SessionOrder`/`SessionOutcome` formale non esistono ancora come codice — restano una direzione
di design, applicata finora solo per coerenza nelle scelte di [[virtual-session-engine-des]].

## Fonti

- [[feedback_core_simulator_agnostic]] (memoria di origine, vincolo dichiarato dall'utente)
- [[project_dce_analysis]] (analisi completa di DCE, controesempio)
- [[project_session_2026_09_18_summary]] (recap della sessione)
- `Analysis/Document/documentazione_dcs/ARCHITETTURA_CORE_AGNOSTICO.md` (documento completo)
- `Analysis/Document/documentazione_dcs/ANALISI_DCE.md` (analisi DCE, §7 tabella di corrispondenze)
