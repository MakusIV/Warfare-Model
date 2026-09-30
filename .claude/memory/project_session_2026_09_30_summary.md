---
name: project-session-2026-09-30-summary
description: "Sessione 2026-09-30 (ProArt P16): attività 1 (R-INT, a500fdf3) e 2 (R-CLS classi RWR, 440a8823) fatte e pushate, suite 3753 OK; prossima: attività 3 (A4 filtro armi per missione)"
metadata:
  type: project
---

**Macchina**: ProArt P16, branch `analysis/dce-dcs-persistence`. Suite completa 3743 OK (7 skipped),
~5 min qui. L'utente ha chiesto di procedere nell'ordine delle "PROSSIME ATTIVITÀ" di
[[project-session-2026-09-29-summary]].

## Fatto
1. **R-INT** (difetto §5.4 di `Proposta_Regole_Allocazione_SAM.md`), commit `a500fdf3`:
   `Engagement_Resolver._in_time` accanto a `_may_intercept`. Decisioni utente: Q1 τ differenziato
   (lancio osservato → VAL+COM+ATT, colpo scoperto dalla geometria → totale), Q2 rilevamento del colpo
   deterministico (una Pd futura solo su flusso RNG separato e con dato RCS), Q3 per asset (fino alla
   Fase 0 C2). Documento: `Analysis/Document/Proposta_Intercettazione_Reazione.md`.
   S19 invariato su 16 seed (il Tor ha già in traccia gli A-10C).
   Nei test: `REACTION_TOF = 20.0` per i colpi intercettabili.

2. **R-CLS** (attività 2), commit `440a8823`: un emettitore percepito SOLO dall'RWR pesa nel
   rapporto di forze con la E(N) MEDIA della sua classe RWR (classe più fine della formazione),
   catalogo = emettitori dei registri dello stesso dominio terra/mare (`ADE.default_rwr_catalogue`,
   asset leggeri `cls.__new__` + `_model`); identificato dai sensori → E(N) esatta. Decisioni utente:
   Q1 media, Q2 sensori identificano, Q3 settori/ewr/confidence RIMANDATI (nessun consumatore: rotte
   fisse, disingaggio senza direzione, niente SEAD guidato da RWR). Documento
   `Analysis/Document/Proposta_Uso_Classi_Settori_RWR.md`. Scenari di sessione con esiti identici
   (usano solo RWR digitali).

## Prossimo
Attività 3: A4 filtro armi per missione (entità `Mission`, 6 decisioni di
`Analisi_Modello_Missione_Sessione.md`), poi rotte → mappe, residui volumi, Fase 0 C2, D9 morale,
bug noti, manuale DES.
