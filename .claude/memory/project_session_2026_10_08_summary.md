---
name: project-session-2026-10-08-summary
description: "Sessione 2026-10-08 (osboxes) CHIUSA, tutto committato e pushato, suite 3951 OK: regola modelli/sforzi salvata, F4b FATTA (a4d8acf0, missione = unità di ingaggio); prossimo sul ProArt P16: 3 decisioni aperte post-F4b, poi F4c"
metadata:
  type: project
---

**Macchina**: osboxes (VM), branch `analysis/dce-dcs-persistence`. Sessione CHIUSA, tutto committato e
pushato. **Prossima sessione su ProArt P16: `git pull` prima di tutto** (python lì:
`.direnv/python-3.12/bin/python3`; su osboxes `/usr/bin/python3` di sistema, nessun venv; v. [[feedback-venv]]).
Su osboxes la suite completa impiega ~15 min (916 s), il confronto della fotografia ~12 min (733 s).

## LAVORO SVOLTO
1. Regola modelli/sforzi: principale Opus 5.5 effort **high** (impostato con `/effort high` come default),
   tabella di delega ai sub-agenti in [[feedback-model-effort-delegation]] (commit `cf4cd34e`).
2. **F4b FATTA** (`a4d8acf0`, delegata a `des-developer` Opus medium, verificata da me): la missione è l'unità
   d'ingaggio (`Mission_Adapter.MissionForce`), dettagli in [[project-mission-structure-decisions]] e in
   `Analysis/Document/F4_Differenze_Scenari.md` §F4b. Decisione utente: missioni dello stesso blocco
   ingaggiano/disingaggiano separatamente, nessuna Operazione le lega. Suite 3951 OK (7 skipped); fotografia
   328 esecuzioni rigenerata e riconfermata IDENTICA da me. Hash nel piano + memoria: `091957cd`.

## STATO DI FATTO
Piano Missione (`Piano_Implementazione_Missione.md`): F0, F1, F2, F3, F4a, F4b FATTE; F4c e F5-F9 da fare.

## ATTIVITÀ DA SVOLGERE (in ordine proposto; l'utente non ha ancora scelto l'ordine fra 1-2 e F4c)
1. **Decisione utente — ripartizione del fuoco fra missioni dello stesso lato** (overkill riaperto in S19AD
   standoff: Maverick 8-10 -> 16, lo Strela sopravvive, Red-Line DESTROYED -> HELD). Opzioni: per blocco, per
   Operazione, per lato. **Raccomandato: per Operazione** (coerente con D3; missioni senza Operazione restano
   scoordinate; S19AD legherebbe le 4 missioni in un'Operazione); proposta scritta prima di implementare.
2. **Decisione utente — test S3/S5** passano solo con più repliche (S3 10->20, S5 6->8): asserzioni al limite
   statistico. Proposto: riprogettarle (frazioni di perdita in S3, frequenze su più seed in S5), sub-agente
   Sonnet medium.
3. Condivisione dei rilevamenti fra missioni: assente (la scorta non informa lo strike); limite noto D3.e,
   proposto di trattarla con il punto 1 o con la Fase 0 C2.
4. **F4c**: postura continua degli asset senza missione (D1.c), oggi nella vista residua `MissionForce.unassigned`
   con id del blocco; stessa procedura di F4b (`des-developer` Opus medium, diff documentata, fotografia
   rigenerata, verifica mia, commit dedicato). Criterio del piano: scenario con aerei parcheggiati colpibili.
5. F5-F9, piccoli punti dal manuale, manuale DES da aggiornare a F4a/F4b, arretrato più vecchio: invariati,
   v. [[project-session-2026-10-05-summary]].
