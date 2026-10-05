---
name: project-mission-structure-decisions
description: "Struttura della Missione: 9 decisioni (D1-D6, N1-N3) prese dall'utente il 2026-10-05 in Proposta_Struttura_Missione_Decisioni.md; aperta solo N3.f (posture vs tipi di missione); nulla ancora implementato salvo il rename Retrait->Retreat"
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

**Aperta N3.f** (emersa dalla nota dell'utente sulle tabelle di decisione): `Ground_Action`/`Sea_Task` sono
posture ORDINATE per aggressività (output fuzzy di `evaluateGroundTacticalAction`) e chiavi di combat power,
efficacia, priorità di Region; i nuovi tipi non stanno su quella scala. Raccomandato B: due assi (postura
invariata + tipo di missione) con tabella di compatibilità tipo -> posture. Per l'aria `AIR_TASK` è già tipo di
missione. Dopo N3.f: piano di implementazione a fasi.
