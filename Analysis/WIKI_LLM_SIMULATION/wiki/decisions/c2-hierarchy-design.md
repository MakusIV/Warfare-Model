---
title: "Gerarchia C2 a due livelli, indirizzo strategico e modello sessioni"
type: decision
tags: [c2, command-control, session-model, architecture, command-package]
created: 2026-09-17
updated: 2026-09-25
status: accepted
affects: ["[[context-state]]", "[[logic-decision]]", "[[command]]"]
related: ["[[c2-planner]]", "[[tlc-model]]", "[[campaign-temporal-model]]", "[[gerarchia-unita-militari]]"]
---

## Contesto
Il progetto aveva due lacune architetturali distinte che si sono rivelate collegate: (a) non esisteva un modello concreto di comando/controllo (C2) sopra i moduli di analisi/valutazione tattica appena estratti da `Region.py` (vedi [[region-tactical-strategic-refactor]]); (b) restava aperta la domanda su come si strutturano nel tempo le sessioni di gioco DCS vs. sintetiche (vedi [[campaign-temporal-model]], ora superata da questa pagina). L'utente ha caricato un PDF (`Analysis/Document/Prospetto:Moduli.Analisi.e.Decisioni.pdf`, pag. 1-5) che descrive una gerarchia C2 di riferimento; un subagent (Opus, effort alto) l'ha confrontato col codice esistente producendo una proposta implementativa, poi l'utente ha corretto/risposto ai punti aperti. Questa pagina registra il **design concordato**, che prevale su ogni punto della proposta grezza del subagent corretto dall'utente.

## Decisione

### Gerarchia a due livelli
- **`C2_Manager`** (globale): uno per side (2 totali in un conflitto a 2 belligeranti) — "lo stato maggiore", responsabile dell'intera area di conflitto per quel side.
- **`C2_Region_Manager`** (regionale): uno per coppia (side, region) — 2×N per N regioni.
- Entrambi i livelli condividono la stessa forma a 5 funzioni: analizza stato → valutazione strategica/tattica → definisce indirizzo strategico → seleziona target → pianifica missioni aria/terra/mare.
- **Protocollo di targeting**: il C2 regionale propone una lista target al C2 globale; il globale approva, cancella o modifica. Un loop di richiesta-modifica-di-ritorno al regionale è un possibile raffinamento, esplicitamente lasciato "da valutare".

### "Indirizzo strategico"
Per-regione, per-dominio (aria/terra/mare), orientamento verso **Attacco / Mantenimento / Difesa / Ritirata**, guidato da morale, statistiche perdite per tipo/ruolo asset, stato produzione/riserve. Coincide con l'idea già presente in [[combat-power-priority-redesign]] (sezione su `feedback_combat_power_action_selection`) di un "vettore di priorità per-azione" — le due vanno implementate insieme.

### Modello sessioni (DCS vs. sintetiche) — sostituisce [[campaign-temporal-model]]
- Discriminante DCS/virtuale: presenza/assenza di slot giocatore umano (binario, operativo — non il conteggio asset).
- Le sessioni virtuali portano molte più missioni/asset di quelle DCS, per limiti computazionali del motore DCS.
- **Cadenza CONFERMATA 2026-09-23** (rilettura dello stesso PDF pag. 3, OCR doppio — fast e docling, concordi — poi confermata dall'utente): dopo una sessione DCS il motore esegue **6 sessioni virtuali** prima della sessione DCS successiva (il diagramma originale mostra anche "3 sessioni DCS" sulla stessa pagina, quindi un rapporto 3:6 nel disegno originale, ma solo il numero **6** è stato ri-confermato come vincolante finora).
- Scarto temporale tra sessioni DCS e virtuali: **1-2 ore** (correzione — una prima lettura del PDF aveva erroneamente inteso "1-20h").
- Esecuzione **interlacciata e guidata dal giocatore**, non un calendario precompilato: dopo che il giocatore finisce una missione DCS ed esce, il modulo campagna principale gira, chiede se terminare anticipatamente altre missioni previste per quel game-day, poi verifica se sono dovute sessioni sintetiche/virtuali e le esegue. Questo sostituisce l'idea di un calendario fisso `Session_Mission_Planner.build_session_calendar()` con uno scheduler event-driven agganciato ai confini reali delle sessioni di gioco.
- **Dopo OGNI sessione (DCS o virtuale) la campagna aggiorna il proprio stato — perdite, consumi, e riarmo degli asset — prima che la sessione successiva possa essere pianificata ed eseguita** (parole dell'utente, 2026-09-23; v. punto 5 di `Theater_Session_Manager` sotto). Non solo dopo le virtuali: vale per il ciclo intero.
- Il ciclo C2 gira **prima e dopo ogni singola sessione**, non una volta per unità di tempo di campagna.
- Le sessioni sono **condivise tra i due side** (una sessione contiene le missioni di entrambi i belligeranti, come nel gioco DCS reale). Un eventuale fog-of-war a livello di dati di sessione è esplicitamente rimandato a una versione futura.

### `Theater_Session_Manager` — arbitro di campagna (CONFERMATO 2026-09-18)
Componente in `Command/`, sopra entrambi i `C2_Manager` di side, deliberatamente "stupido" (solo assembly/scheduling, mai targeting/dottrina, che restano interne a ciascuna gerarchia C2 di side):
1. **Assembly della sessione**: fonde le missioni decise indipendentemente dai due `C2_Manager` in un unico oggetto `Session` fisico (un file missione DCS o una sessione virtuale contiene per forza gli asset/missioni di entrambi i belligeranti).
2. **Tipo e timing della sessione**: decide se la prossima è DCS o sintetica, e quando scatta — fatto di livello campagna che nessun side può conoscere da solo.
3. **Trigger simmetrico del ciclo C2**: fa scattare "analizza→pianifica" per entrambi i side prima della sessione e "analizza" per entrambi dopo, in ordine fisso.
4. **Proprietario di `session_id`** (vedi rename sotto): unico componente che vede la sessione unificata.
5. **Aggiornamento stato post-sessione — RAFFINATO 2026-09-23**: raccoglie risultati/perdite di entrambi i side dopo l'esecuzione (`Session_Simulator`), **riarma gli asset** (rifornimento munizioni — il contatore introdotto dalla Fase 4 del motore DES, v. [[risolutore-ingaggio-salva-fase4]] R3, rimanda esplicitamente il rifornimento "al ciclo di campagna": è questo il punto) e scrive tutto su `Campaign_State` in un solo passaggio, **prima** che la sessione successiva possa essere pianificata/eseguita. Vale dopo ogni sessione, DCS o virtuale.
6. **Futuro hook fog-of-war**: punto naturale per filtrare/oscurare la sessione unificata se in futuro si implementa l'occultamento delle info nemiche (oggi deferred).

### Persistenza `Campaign_State`: rename `mission_id` → `session_id` (CONFERMATO 2026-09-18)
`mission_id`, oggi l'unica chiave top-level di `Campaign_State._state`, viene **rinominata `session_id`**. `mission_id` viene riusato un livello sotto, per identificare ciascuna missione (aria/terra/mare) definita da un side dentro una `session_id` — coerente col vocabolario "una sessione contiene missioni" del modello sopra. **Non ancora implementato**: `Campaign_State.py` e `Target_Status_History.py` (unico altro utilizzatore in produzione di `mission_id`) usano oggi ancora `mission_id` come unica chiave top-level — corretto per quello che esiste oggi (non c'è ancora un concetto di missione singola nel codice). La migrazione va fatta insieme alla costruzione di `Command/Session.py`/`Session_Mission_Planner.py`, non prima; **non va fatto un find-replace ora**.

### Cleanup confermato (punto 6 approvato dall'utente)
- Eliminare `Context/Coalition.py` (non compila, inutilizzato, nessun salvataggio necessario).
- Eliminare la classe `CommandControl` in `Logic/Scenario_Manager.py`, ma **prima estrarne il docstring** (elenca già livelli operazione aria/terra/mare + risorse/energia/umane — probabile contenuto letterale dell'"indirizzo strategico") in `StrategicOrder`/dove finirà a vivere la dottrina strategica.
- Rinominare o eliminare `Manager.py` (root di `Source/`) per liberare il nome `C2_Manager` — oggi è uno stub rotto di 106 righe, erroneamente indicato nella wiki come "C² Planner" (vedi [[c2-planner]], da aggiornare).
- `wiki/concepts/c2-planner.md` va aggiornato: riferimenti obsoleti a `Manager.py` e a `Military_Resources_Assigner.py` (rinominato da tempo in `Air_Resources_Assigner.py`).

**Nessuno di questi cleanup è stato ancora eseguito nel codice** — sono decisioni confermate, non lavoro completato.

## Motivazione
La separazione a due livelli (globale/regionale) rispecchia il pattern C² Planner del modello TLC ([[c2-planner]], [[tlc-model]]) — decisioni adattive che leggono lo stato corrente invece di seguire script fissi. Tenere l'arbitro di sessione "stupido" (solo scheduling) preserva la separazione Blue/Red necessaria per un futuro fog-of-war multiplayer: se l'arbitro decidesse anche targeting, un side avrebbe visibilità indiretta sulle decisioni dell'altro.

## Conseguenze

### TASK 1 — fix dottrina di targeting per-side — FATTO 2026-09-18
`Region._attack_weight`/`_weight_priority_target` erano per-Region invece che per-side: due C2 avversari sulla stessa regione si sarebbero scavalcati la dottrina a vicenda. Fix: passati da scalare a `Dict[str, ...]` chiavato `'Blue'`/`'Red'`; le property dirette sostituite da `get_attack_weight(side)`/`set_attack_weight(side, value)`/`get_weight_priority_target(side)`/`set_weight_priority_target(side, value)` (una property non può prendere un parametro `side`) + guard `_validate_belligerent_side`. `Campaign_State` serialize/restore e i test aggiornati al nuovo formato, nessuno shim di retrocompatibilità (nessuno snapshot in produzione usa il vecchio formato). Suite completa: 2519 test OK (skipped=5). Merged in `main` (PR #187, commit `cb4e27e8`).

### TASK 2 (Fase A) — RegionInfoReport / Meteo_Analysis / limes — FATTO 2026-09-18
Property pubblica `Region.limes` (sola lettura, copia difensiva). Nuovo `Logic/Meteo_Analysis.py`: placeholder deterministico `get_meteo_conditions(region_name, date, time) -> {'day', 'night', 'adverse_weather'}` (giorno/notte da una finestra oraria fissa, meteo avverso da una regola fissa mesi-invernali + parità nome/giorno — esplicitamente non `random`), shape identica a `mission_requirements['usability']` di `Air_Resources_Assigner`. Agganciato a `Region.get_meteorological_reports`, la cui firma è cresciuta `(side) -> (side, date, time)` (nessun chiamante esisteva, nessun problema di retrocompatibilità). Nuovo package `Command/` (`__init__.py` + `Command_Types.py::RegionInfoReport`, import di `Region.BlockItem` solo sotto `TYPE_CHECKING` per evitare il ciclo con `Region`, che importa `RegionInfoReport` a livello di modulo). Nuovo `Region.build_info_report(side, date, time) -> RegionInfoReport`, puro orchestratore che assembla tutti i campi `(*) INFO` di pag. 3 da metodi `Region` già esistenti e testati — nessun calcolo proprio.

Suite completa: **2540 test OK (skipped=5)**, +21 rispetto a TASK 1 (`Test_Meteo_Analysis.py` 13, `Test_Command_Types.py` 2, `TestRegionLimes`/`TestRegionBuildInfoReport` in `Test_Region.py` 6).

**Bug trovato, non corretto (fuori scope)**: `Payload.__eq__` (`DataType/Payload.py:127-133`) considera "diversi" due `Payload` entrambi a zero (il suo ciclo richiede un attributo *truthy* per contare come match, e zero è sempre falsy). `wiki/project/datatype.md` afferma erroneamente che gli operatori di confronto di `Payload` sono "completi" — da correggere in una prossima sessione, non qui.

### Layout moduli proposto — parzialmente costruito
Package `Command/` (stateful, distinto da `Logic/` stateless): **`Command_Types.py` esiste** (`RegionInfoReport`); `C2_Region_Manager.py`, `C2_Manager.py`, `Theater_Session_Manager.py`, `Session_Mission_Planner.py`, `Session.py` **non esistono ancora**. `Logic/Meteo_Analysis.py` **esiste** (v. sopra). `Context/Theater.py`, `Logic/Strategical_Analysis.py` (fatti, omologo di `Tactical_Analysis.py`), `Logic/Session_Simulator.py` **non esistono ancora**. `Strategical_Evaluation.py` (oggi tutto stub, vedi [[logic-decision]]) manterrà solo le vere funzioni di scoring; 4 dei suoi 11 stub (`evaluateTotalProduction/Transport/Storage`, `calcCombatPowerCentrum`) sono fatti e andranno spostati nel futuro `Strategical_Analysis.py`.

### Non ancora deciso
- Meccanica esatta del loop di negoziazione quando il C2 globale modifica/rifiuta una proposta regionale.
- Se la persistenza di `Campaign_State` avrà bisogno di ulteriori chiavi oltre a `session_id`/`mission_id` per il modello sessione-come-turno.
- **Se la gerarchia a due livelli (globale/regionale) qui descritta va estesa con un livello
  `Formation` intermedio** (Corpo d'Armata/Divisione/Brigata) e una base comune `C2_Node` condivisa
  — proposta 2026-09-25 in [[gerarchia-unita-militari]], compatibile con questo design e lo
  generalizza, ma non ancora decisa. Va risolta **prima** di scrivere `C2_Manager.py`/
  `C2_Region_Manager.py` (v. sotto, ancora non costruiti), perché `C2_Node` andrebbe progettata
  insieme a questi due.

## Fonti
- [[project_c2_hierarchy_design]] (memoria di origine, autorevole — consultare per dettagli operativi come il recupero di TASK 1 da un worktree abbandonato)
- [[project_campaign_temporal_model_dcs_vs_synthetic]] (framing precedente, superato da questa pagina per la parte modello-sessioni)
- [[feedback_combat_power_action_selection]] (origine dell'idea di vettore di priorità per-azione, ora confermata come "indirizzo strategico")
