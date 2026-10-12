---
name: project-session-2026-10-11-summary
description: "Sessione 2026-10-11 (ProArt P16) CHIUSA, committato e pushato (F5-A poi fatta il 2026-10-12, e723e82a), suite 4039 OK: decisioni su fuoco/rilevamenti/test S3-S5 prese e implementate (F4b+, F4b++), test S3/S5 riprogettati, F4c fatta (aerei senza missione a terra), manuale DES aggiornato; prossimo: F5 (presenza e attese, postura nell'esito)"
metadata:
  node_type: memory
  type: project
  originSessionId: a60721d7-7aaf-41fb-9dd8-e506ce71f433
  modified: 2026-10-11T16:00:56.496Z
---

**Macchina**: ProArt P16 (WSL2), branch `analysis/dce-dcs-persistence`. Python: `.direnv/python-3.12/bin/python3`
(v. [[feedback-venv]]); suite completa ~8 min (4039 test), confronto fotografia ~6 min, mai in parallelo.
**Ripresa prevista sulla STESSA macchina (ProArt P16), checkout `/home/marco/Sviluppo/Warfare-Model`**: il branch
attuale e' `analysis/dce-dcs-persistence` (pulito, allineato a origin); fare comunque `git fetch` all'inizio. Il
lavoro non verificato di F5-A sta sul branch `wip/f5-a-grounded-nel-tempo` (v. sotto). Scratchpad di log e script di
misura della sessione: `/tmp/claude-1000/-home-marco-Sviluppo-Warfare-Model/*/scratchpad/` (temporanei, non
necessari).

## LAVORO SVOLTO (v. [[project-mission-structure-decisions]] per le decisioni complete)
1. **Revisione dello stato** all'inizio: l'utente aveva ragione che parte dell'elenco era già trattata (le 6 decisioni
   missione sono D1-D6/N1-N3); restavano aperte solo 3 decisioni dopo F4b, tutte chiuse oggi.
2. **Ripartizione del fuoco e rilevamenti condivisi** (`098671d7`, F4b+): dominio di coordinamento = missioni dello
   stesso blocco OPPURE della stessa Operazione (unione transitiva, mai a cavallo di lati). Fuoco (saturazione/
   ripartizione), percezione (`seen_by`, `identified_by`, classi RWR) e lanciatori prioritari L2/L3 condivisi nel
   dominio, istantanei, NIENTE cueing del tiro. Le forze di un dominio stanno nella stessa run.
3. **Difesa di salva per dominio** (`e6f59d21`, F4b++): gli intercettori di tutto il dominio difendono; canali
   condivisi solo fra forze risolte nello stesso istante (limite noto).
4. **Test S3/S5 riprogettati** (`8bf7b11f`): S3 = frazione persa (senza stealth) e differenza a coppie z>=3 (con
   stealth); S5 = default con maggioranza + invarianti, variante a erosione 0,65 su 12 seed, terzo strato solo
   informativo. Misurati 40 seed (S3) e 24 (S5).
5. **F4c** (`af2efbe6`): aereo senza missione = A TERRA, bersaglio di superficie passivo (insieme `grounded` della
   sessione, keyword facoltativa `target_grounded` verso la fire control, classe 'Soft'); terra/mare senza missione =
   postura `Defense` dichiarata, tiro invariato. Scenari nuovi S21/S21R. Fotografia 370 esecuzioni.
6. **Manuale DES** aggiornato al commit `84a47670` (F4a-F4c) con `des-manual-writer` (Sonnet high).

## STATO DI FATTO
Piano Missione: F0-F3, F4a, F4b, F4b+/++, F4c e riprogettazione S3/S5 FATTE; F5-F9 da fare. Fotografia di non
regressione: 370 esecuzioni (`Test/baseline/scenario_baseline.json`, comando `--compare` nel docstring di
`Test/Scenario_Baseline.py`). Suite 4039 OK (7 skipped).

## F5-A FATTA E VERIFICATA (2026-10-12, stessa macchina)
Verificata dal branch `wip/f5-a-grounded-nel-tempo`: suite 4072 OK (7 skipped), fotografia IDENTICA su 370.
Documentata in `F4_Differenze_Scenari.md` («F5 passo (a)») e nel Piano §5; squash-merge in
`analysis/dce-dcs-persistence` come **`e723e82a`**, pushato. I branch `wip/f5-a-grounded-nel-tempo` (locale e
origin) sono eliminabili (non eliminati: chiedere/farlo a mano). In sessione resta l'insieme costante della F4c;
sono PREDISPOSTI e NON cablati: `Mission_Adapter.movement_legs/grounded_schedule/session_postures/final_posture/
lands_on_air_base/mission_holds`, `Contact_Scheduler.GroundedSchedule`, `SessionOutcome.postures`.
Decisione dell'utente: aereo a terra dopo la fine della rotta SOLO su una base vera (LAND su base), altrimenti esce
dalla scena come oggi finche' F6 non porta il rientro.

## PROSSIMO: F5-B poi F5-C (una sessione ciascuna, con `des-developer` Opus medium, v. [[feedback-model-effort-delegation]])
Ogni passo: commit dedicato, verifica mia di suite (~8 min) + `--compare` (~6 min) mai in parallelo, log nuovi.
- F5-B: cablare in `Session_Simulator` presenza prima/dopo (terra/mare `Defense`, aerei non partiti a terra),
  postura nell'esito di forza anche per i blocchi senza missioni, scenari E1 (carro fermo a 4 km ingaggiabile),
  E3 (partenza ritardata), aerei (parcheggiato colpibile finche' a terra); fotografia rigenerata UNA volta con
  ogni differenza attribuita (interruttori o `--only`).
- F5-C: azione WAIT (`hold`/`orbit`), ETA effettive nel `MissionOutcome`, TOT comune, scenario CAP in orbita.
Comando fotografia: `PYTHONPATH=$PWD/Code:$PWD .direnv/python-3.12/bin/python3 -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json`

## PROSSIME ATTIVITA' (in ordine proposto)
1. **F5** — presenza, tempi e attese (D1.a/b, N2.b/c): tratti fermi prima/dopo la rotta in `Contact_Scheduler`,
   postura di fine missione, azione WAIT, ETA effettive nel `MissionOutcome`. Include per decisione dell'utente
   (2026-10-11): la **postura nell'esito di forza** (campo di `ForceOutcome` o per blocco nel `SessionOutcome`, anche
   per i blocchi senza missioni) e `grounded` **dipendente dal tempo** (aereo con missione non ancora partita =
   a terra). Una sola rigenerazione della fotografia. Procedura: `des-developer` Opus medium, diff documentata in
   `F4_Differenze_Scenari.md`, verifica mia (suite + confronto), commit dedicato.
2. **F6** fine missione e carburante nel tempo; **F7** filtro armi/bersagli per missione (A4) + salva su area (proposta
   separata prima); **F8** validatore di sessione, prontezza (turnaround, ricerca dedicata), posizione persistente
   (D1.d); **F9** manuale. Piano: `Analysis/Document/Piano_Implementazione_Missione.md`.
3. Piccoli punti aperti (manuale cap. 10 §9.6): `run_session` non inoltra `rwr_catalogue`; nessun codice di
   produzione fornisce `morale_for`/`enemy_estimate_for`; manca lo stato di missione «in corso»; etichette con
   maiuscole incoerenti in `evaluateGroundCriticality`.
4. Limiti di modello dichiarati, da riprendere quando servono: cueing del tiro (EWR->SAM, AWACS->caccia: proposta
   separata con la Fase 0 C2), condivisione dei canali di intercettazione per finestra di salva, nessuno shelter,
   missione di un solo asset DESTROYED alla prima perdita.
5. Arretrato più vecchio, invariato (v. [[project-session-2026-09-30-summary]]): Fase 0 gerarchia C2 (9 decisioni
   D1-D9 in `Analisi_Gerarchia_Unita_Militari.md`), rotte -> modulo mappe (`.docx` non letto), residui volumi D-4b/c,
   D-5 opz.2, D9 morale, bug noti (`get_blocks_by_criteria` con `@lru_cache` su metodo, `Military.is_helibase`
   chiamato a `Military.py:464` ma non definito).

## Lezioni della sessione
- Per riprogettare test al limite statistico: misurare PRIMA su molti seed (40) la metrica giusta (frazione, non
  numero assoluto; frequenza dell'evento) e poi scegliere asserzioni con margine; una costante di scenario va
  dichiarata come stima, mai tarata sul risultato.
- Un agente fermato da un limite API si riprende con SendMessage (conserva il contesto): F4c è stata completata così.
- Verificare sempre io suite e fotografia prima del commit, con nomi di file di log nuovi nello scratchpad (un agente
  ha segnalato un falso allarme per un log condiviso).
- I file DCS non tracciati in `Analysis/Document/documentazione missioni dcs/` restano non tracciati per scelta
  dell'utente.
