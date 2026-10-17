---
name: project-session-2026-10-17-summary
description: "Sessione 2026-10-17 (ProArt P16) CHIUSA, tutto pushato, suite 4375 OK: G3 approvato (802); G4a+G4b+uscita di scena senza basi APPROVATI insieme, fotografia 878 installata, committati e pushati; G2 alla partenza invariato (F6-A); prossimo G5"
metadata:
  type: project
---

**Stato**: branch `analysis/dce-dcs-persistence`. `origin` a `ed97eccb`; in locale anche `f526cc0a` (proposta G4,
`Analysis/Document/Proposta_G4_Ri_scheduling.md`). Lavoro G4a NEL WORKING TREE, non committato (12 file).

## Fatto
1. Suite 4321 OK e `--compare` G3 rifatti su ProArt P16 (802 = 372/422/8): G3 approvato, fotografia 802 (`20f0e0db`).
   Lo script va lanciato come modulo: `-m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline`.
2. Proposta G4 (episodi + ri-pianificazione) approvata, v. [[project-bingo-reverse-route-decision]].
3. **G4a implementato**: `G4_EPISODES`, `EPISODE_GAP` = 300 s, `_episodes`, `_trim_busy`, `CS.trim_contact_window`,
   `ActivityCriteria.reference_health`, `assemble_session_outcome(chained=)`, contabilita' carburante come passo finale.
   **Verificato da me**: suite 4344 OK (7 skipped); confronto 814 = 762 identiche, 40 cambiate (S5 36, S6 4: solo
   force_outcomes e ammunition_events), 12 nuove 'episodes_off' = vecchie 'default'. Cattura in scratchpad (persa a
   fine sessione: rifare `--compare --save`).
4. **Effetto S5**: formazione disingaggiata a L1 prosegue passiva e L2 la ri-ingaggia (default: Blue distrutti
   17->28 su 12 seed, L2 spara 12/12 invece di 1/12).

## Decisioni utente 2026-10-17
- Disingaggio di un aereo di missione: **rientro in G4b** (il disingaggio fa scattare la ri-pianificazione con la
  regola di combattimento dell'albero di bingo).
- Erosione/shock della soglia di rottura: **per episodio** (scelta 9 dell'agente confermata).
- Approvazione G4a: **"non ancora"** (motivo da chiarire con l'utente). 12 scelte dell'agente elencate nel suo rapporto
  e in `F4_Differenze_Scenari.md` sezione G4a / Piano deviazione 20.

## Prossimi
Dettaglio S5/S6 mostrato all'utente (prima il disingaggio rendeva Blue "andato via" per L2, ora e' bersaglio passivo:
entrambi artificiali). DECISO: G4a resta NON committato nel working tree, G4b (replan per carburante E per
disingaggio) costruito sopra, approvazione e fotografia INSIEME a G4a+G4b. Poi G5 (S27, manuale).

## G4b (aggiornamento sera 2026-10-17)
G4b implementato (des-developer Opus high, lasciato finire su decisione utente) e VERIFICATO da me: suite 4368 OK;
confronto 866 vs fotografia 802 = 746/56/64; vs cattura G4a = 798 identiche, 16 cambiate (S26 transfer_continue x8:
perso per esaurimento in ingaggio; S24-ORBIT per_leg_off x8: a secco sul rientro), 52 nuove (S5 with_base,
with_base_resistant, replan_off; S26 post_engagement_bingo, replan_off). S5 senza basi Blue: rientro = NO_BASE, resta
passivo. DECISO dall'utente: aereo comparso in volo senza basi del lato che deve rientrare -> ritroso fino al punto di
comparsa e ESCE DI SCENA (off_scene). Da implementare (des-developer Opus medium) PRIMA dell'approvazione unica
G4a+G4b+uscita di scena e della fotografia. Nulla committato di G4.

## Chiusura G4 (2026-10-17, tardi)
Uscita di scena implementata (des-developer Opus medium): `Fuel_Model.BINGO_EXIT`, `bingo_decision(exit_scene=)`,
`BingoEnd.exits`, sotto-interruttore `G4_OFF_SCENE_EXIT`, variante S5 'exit_off'. Effetto ampio: 138 esecuzioni
cambiate in 15 scenari (quasi tutti usano formazioni comparse in volo senza basi). VERIFICATO da me: suite 4375 OK,
cattura 878 identica a quella dell'agente; vs fotografia 802 = 637/165/76. **APPROVATI dall'utente G4a+G4b+uscita
insieme**, fotografia 878 installata, commit e push (incluso f526cc0a). DECISO: alla partenza (G2) restano le regole
F6-A (nessuna uscita immediata). Prossimo: G5 (S26 riscritto, S27 doppia intercettazione, Piano §5, F4, manuale).

**Sessione CHIUSA 2026-10-17**: working tree pulito (salvo file non tracciati dell'utente), tutto pushato. Riprendere con `git pull` e G5.
