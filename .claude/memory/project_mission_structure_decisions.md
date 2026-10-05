---
name: project-mission-structure-decisions
description: "Struttura della Missione: 9 decisioni (D1-D6, N1-N3) + N3.f=B prese il 2026-10-05; piano F0-F9 APPROVATO (Q1-Q4 sì, Q4 = agenti in parallelo); F0, F1, F2 FATTE 2026-10-05 (suite 3868 OK, scenari 292 identici); prossima F3"
metadata:
  type: project
---

Documento: `Analysis/Document/Proposta_Struttura_Missione_Decisioni.md` (stato DECISO), commit `f122eca2`.
Tutte le raccomandazioni (R) applicate dall'utente, tranne **N2.a = C**. In sintesi:
- **D3**: terminologia dell'utente (doc `Architettura_esecuzione_sessioni_virtuali.txt`):
  Operazione (facoltativa, blocchi diversi) ⊃ Missione (asset di UN blocco, ruoli, direttive, una rotta di
  riferimento con offset per asset); fine e aborto per missione; la missione diventa l'unità di ingaggio del
  resolver (il blocco resta l'unità di appartenenza).
- **N2**: `MissionWaypoint` CONTIENE un `Waypoint` (la Route resta geometrica); ETA pianificata nella missione ed
  effettiva nell'esito; azione "attendi"; solo condizioni pre-calcolabili.
- **N3**: livello comune Attacco/Trasporto/Posizionamento/Supporto; aria + AWACS, Tanker, Transport; terra +
  Fire_Support, Movement, Recon, Supply; mare + Patrol, Escort, Shore_Bombardment, Transport; bersaglio =
  asset/gruppo, punto/area, zona o nessuno, con provenienza (osservato+istante o stimato).
  `Retrait` -> `Retreat` FATTO (`1d5dc863`, suite 3753 OK).
- **D2**: criteri pre-calcolabili + "fine di attività" senza cambio di rotta per i criteri di stato; criteri
  dichiarati nella Missione; RTB sempre nella rotta aerea; esito per missione (COMPLETATA/ABORTITA+motivo/
  FALLITA/DISTRUTTA) e per asset; esito dell'Operazione da regola dichiarata.
- **D1**: presenti fermi prima della partenza e dopo la fine (postura di fine missione); non impegnati presenti
  come bersagli; posizione persistente fra sessioni.
- **D4**: sessioni disgiunte; durata parametro (default 2 h, max 4 h); missioni troppo lunghe rifiutate; fra
  sessioni solo processi di campagna; attività lunghe = sequenza di missioni con ordine permanente.
- **D6**: asset "pronto da t" con turnaround per classe (ricerca dedicata) e riparazione funzione del danno;
  anche terra/mare. **D5**: rifornimento in volo solo vincolo di pianificazione, consumo anche nel tempo,
  rifornimento terra/mare fra sessioni. **N1**: rimandata all'adapter.

**N3.f = B DECISO** (emersa dalla nota dell'utente sulle tabelle di decisione): `Ground_Action`/`Sea_Task` sono
posture ORDINATE per aggressività (output fuzzy di `evaluateGroundTacticalAction`) e chiavi di combat power,
efficacia, priorità di Region; i nuovi tipi non stanno su quella scala. Raccomandato B: due assi (postura
invariata + tipo di missione) con tabella di compatibilità tipo -> posture. Per l'aria `AIR_TASK` è già tipo di
missione.

**Piano**: `Analysis/Document/Piano_Implementazione_Missione.md` (commit `96cbc5fa`, PROPOSTA). Fasi: F0 fotografia
scenari S1-S19 (non regressione) · F1 `Command/Mission_Types.py` (Mission, MissionWaypoint contiene Waypoint,
Target con provenienza, MissionAction, EndCriteria, Operation, MissionOutcome) · F2 tassonomia + tabella
`MISSION_TYPE_POSTURES` + AIR_TASK AWACS/Tanker/Transport (14 loadout con tasks vuoto) · F3 Missione nella porta
(`SessionOrder.missions`, mission_id nell'RNG) · F4 `MissionForce` come unità di ingaggio (resolve_engagement accetta
qualunque oggetto con assets/side/name) + postura dei non impegnati · F5 presenza prima/dopo + WAIT · F6 fine di
attività + carburante per tratto/tempo + bingo a priori · F7 filtro armi/bersagli per missione (involucro di
fire_control come `ifv_only`) + salva su area · F8 validatore sessione, prontezza, posizione persistente · F9 manuale.
Domande aperte: Q1 fasi/ordine, Q2 rimuovere routes/starts/speeds da run_session, Q3 proposta separata salva su
area, Q4 F0-F2 in parallelo con des-developer.

**Avanzamento (2026-10-05)**: Q1-Q4 approvate (fermarsi a F8; rimuovere routes/starts/speeds da run_session a
migrazione completa; proposta separata per la salva su area in F7; F0-F2 con agenti in parallelo).
- F0 `d3af6980`: `Test/Scenario_Baseline.py` (fuori discovery) + `Test/baseline/scenario_baseline.json` (292
  esecuzioni). Confronto: `PYTHONPATH=$PWD/Code:$PWD <python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline
  --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json` (~210 s). Catturata su copia di
  HEAD via `git archive` con PYTHONPATH sovrascritto (aggira il problema dei worktree).
- F1 `20b6de72`: `Command/Mission_Types.py` (90 test). `route_waypoints(route)` dà l'ordine di percorrenza
  (Route.getWaypoints è un heap per nome). DA CONFERMARE con l'utente le prime stesure: ruoli per dominio,
  formazioni, EMCON, default (ROE weapon_free in tutti i domini, evade_fire, allerta auto, partenza runway, bingo
  True) e validazioni aggiunte (EndCriteria richiede last_waypoint o max_duration; POSITIONING richiede
  bersaglio ZONE/POINT/AREA/GROUP, quindi Defense senza zona rifiutata).
- F2 `4e18d7d8`: tassonomia in Context + `AIR_COMBAT_TASK` (vecchio AIR_TASK); task di supporto a 0 in
  combat power ed esclusi dai punteggi; 13 loadout supporto con task, An-30M Recon lasciato vuoto.
