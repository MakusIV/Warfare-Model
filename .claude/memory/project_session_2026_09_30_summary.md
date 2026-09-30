---
name: project-session-2026-09-30-summary
description: "Sessione 2026-09-30 (ProArt P16) CHIUSA: R-INT (a500fdf3) e R-CLS classi RWR (440a8823) fatte, suite 3753 OK, tutto committato e pushato; prossima: attività 3 (A4 filtro armi per missione)"
metadata:
  type: project
---

**Macchina**: ProArt P16 (WSL2), branch `analysis/dce-dcs-persistence`. Sessione CHIUSA con tutto
committato e pushato. **Alla ripresa, su qualunque macchina: `git pull` prima di tutto** (python per
macchina: v. [[feedback-venv]]; qui `.direnv/python-3.12/bin/python3`). Suite completa 3753 OK
(7 skipped), ~5,5 min qui (~14 min sulla VM). Comando dalla root:
`python -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_*.py"`.
L'utente procede nell'ordine delle attività proposte (elenco sotto), una proposta con decisioni
Q1..Qn alla volta, poi implementazione + test + misura sugli scenari + commit.

## STATO DI FATTO (oltre a quanto in [[project-session-2026-09-29-summary]])

1. **R-INT — intercettazione con traccia del colpo e tempo di reazione** (difetto §5.4 di
   `Proposta_Regole_Allocazione_SAM.md`), commit `a500fdf3`. `Engagement_Resolver._in_time` accanto a
   `_may_intercept` (L1): serve t_traccia + τ ≤ t_impact. Lancio osservato (l'intercettore aveva già
   rilevato il lanciatore) → τ = VAL+COM+ATT; altrimenti colpo scoperto all'ingresso nel raggio di
   rilevamento aereo (traiettoria rettilinea, deterministico, nessuna estrazione RNG) → τ = totale.
   Rilevamento per asset. Tempo di volo nullo → mai intercettato. Nei test `REACTION_TOF = 20.0`.
   Documento `Analysis/Document/Proposta_Intercettazione_Reazione.md`. S19 invariato su 16 seed.
2. **R-CLS — minaccia percepita dalla sola RWR stimata sulla classe** (attività 2), commit
   `440a8823`. Emettitore percepito SOLO dall'RWR → E(N) MEDIA della sua classe RWR (classe più fine
   della formazione) sul catalogo degli emettitori dei registri dello stesso dominio terra/mare
   (`ADE.default_rwr_catalogue`, asset leggeri `cls.__new__` + `_model`; `class_threat_weight`);
   identificato da un sensore della forza → E(N) esatta. Parametro `rwr_catalogue` di
   `resolve_engagement` (futuro: inventario del nemico via campo `users`). Settori/ewr/confidence
   RIMANDATI al modulo rotte/evasione e al SEAD. Documento
   `Analysis/Document/Proposta_Uso_Classi_Settori_RWR.md`. Scenari di sessione con esiti identici
   (solo RWR digitali; SPO-15/SPO-10 coperti solo dai test unitari).

## PROSSIME ATTIVITÀ (in ordine, da proporre all'utente)

1. **A4 — filtro armi per missione**: legato all'entità `Mission` e alle 6 decisioni di
   `Analysis/Document/Analisi_Modello_Missione_Sessione.md` (S19 usa ancora il filtro di test
   `ifv_only`/"solo Maverick"). Rileggere il documento e riproporre le 6 decisioni.
2. **Dettagli del calcolo rotte**, poi **modulo mappe** (v. [[project-map-module-plan]]; il .docx
   `Documentazione e Guida Mappe DCS World.docx` non è ancora letto), poi volumi con terreno.
3. Residui volumi: D-4b/c, D-5 opz. 2, D-7 seconda parte, D-8.
4. **Fase 0 gerarchia C2** (la più vecchia; anche legame C2 fra unità AD, contagio del disingaggio,
   quadro condiviso per R-INT e L3).
5. D9: correggere `Block.morale` (success_ratio mai alimentato, MF fuzzy fuori scala) e alimentarlo
   dagli esiti degli ingaggi.
6. Bug noti non corretti: `get_blocks_by_criteria`, `Military.is_helibase` mancante.
7. **Manuale DES** da aggiornare (soglia di rottura, Air_Defense_Efficacy, RWR + R-CLS, dottrina di
   tiro, A6, R-INT) con `des-manual-writer`, verificando i riferimenti file:riga.
8. Futuri agganci già predisposti: Pd sul colpo in arrivo (flusso RNG separato, solo con dato RCS),
   catalogo RWR ristretto all'inventario nemico, uso dei settori RWR (evasione/SEAD).

## Note
- Skipped passati da 5 a 7 fra la sessione del 29/09 e questa: non verificato quali (non causato
  dalle modifiche di oggi, già 7 alla prima esecuzione della suite).
- File dell'utente non tracciato da non committare: `Analysis/Document/Untitled 1.odt`.
