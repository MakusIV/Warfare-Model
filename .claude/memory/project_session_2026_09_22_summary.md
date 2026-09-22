---
name: project-session-2026-09-22-summary
description: "Recap sessione 2026-09-22 (con crash e ripresa a metà): Fase 2-3 del motore DES, chiusura Q1-Q3 e dei 3 punti residui, ingestione Lanchester (S1-S11), analisi LLM-locale, ingestione Hughes/salvo model. Tutto committato e pushato su analysis/dce-dcs-persistence."
metadata: 
  node_type: memory
  type: project
  originSessionId: 263ff385-5fa2-4cbf-96cc-1dac090b00a7
  modified: 2026-09-22T19:58:59.143Z
---

**ALL'INIZIO DELLA PROSSIMA SESSIONE: ripresentare il report di stato completo.** Richiesta
esplicita dell'utente a fine sessione 2026-09-22, che ha chiuso qui perché ha esaurito il tempo di
lavoro disponibile (non perché il lavoro fosse finito). **La prossima sessione si apre su un'altra
macchina, l'Asus ProArt P16** — fare `git pull` prima di tutto (v.
[[project_dev_environment]] per il workflow di sync; la memoria vive dentro il repo ed è quindi già
sincronizzata da questo commit). Il report va costruito da questo file + da
[[project_virtual_session_engine_design]] (stato Fasi 1-3, roadmap) — non ripetere l'analisi,
riassumere dov'è il lavoro e la domanda aperta sulle 3 proposte in coda a "Prossimo passo".

Sessione lunga, con un **crash a metà** (limite di 5h raggiunto) durante l'ingestione della fonte
Hughes; ripresa nello stesso giorno e completata senza perdite (verificato: tutti i commit fino al
crash erano già pushati, il lavoro non committato era su disco e intatto — solo l'ingestione Hughes
era a metà, con pagine collegate mancanti e `index.md`/`log.md` non aggiornati).

## Cosa è stato fatto, in ordine

1. **Fase 2 del motore DES** (percezione): `Mobile.detection_range`, fabbrica `ThreatAA` in
   `Air_Route_Manager`. Dettaglio in [[project_virtual_session_engine_design]].
2. **Le 3 questioni aperte del §9 chiuse**: Q1 (`DataType.Route` canonico, `Route_Adapter.py`), Q2
   (contratto del danno, `Damage_Model.py`, `Asset.apply_damage`), Q3
   (`Military.air_defense_power()` come dimensione separata dal combat power).
3. **Fase 3**: `Logic/Contact_Scheduler.py` (scheduler analitico dei contatti: threat windows,
   CPA/TCPA, potatura gerarchica a livello Block). 96 test nuovi.
4. **3 punti residui chiusi**: SEAD collegato a `air_defense_power()`, `MIN_EFFECTIVE_HIT_DAMAGE`
   confermata, `Edge.calcLength()` — il commento era il bug, non il codice.
5. **Ingestione Lanchester** (9 docx, `RAW/Lanchester/`): esito negativo sulla matematica (nessun
   coefficiente utilizzabile), positivo su 3 punti — batteria di scenari di test, regola di
   disingaggio a soglia, forma del fallback aggregato. Estesa la batteria di validazione da S1-S5 a
   **S1-S11** (S6-S11 nuovi: navale, logistico, scala, fog-of-war, disingaggio, confine DCS/sintetico).
   V. [[project_virtual_session_engine_design]] per il dettaglio completo (memoria già aggiornata).
6. **Analisi "LLM locale nel motore DES"**: proposta dell'utente di usare un LLM locale (Qwen 7-27B
   su RTX 3090) per valutare le condizioni dei passi event-driven. Verdetto: **per evento** e **per
   decisione dottrinale a runtime** respinti (budget di calcolo + riproducibilità — Qwen2.5-7B ha
   solo il 17,6% di risposte byte-identiche a temperatura 0 fra seed); **debrief narrativo a valle**
   e **uso offline a tempo di progettazione** ammessi. Reperto collaterale: bug di prestazioni in
   `closest_point_of_approach` (2.450× più lento del necessario per colpa di `sympy.Point3D`, non
   corretto in questa sessione). Pagine: `wiki/analyses/llm-locale-nel-motore-des.md`,
   `wiki/decisions/llm-locale-ruolo-e-confini.md` (`status: proposed`).
7. **[QUI IL CRASH]** — a metà dell'ingestione della fonte Hughes.
8. **Ripresa e completamento ingestione Hughes** (`RAW/Event_Driven_Salva_Hughes/`, 7 documenti,
   sessione conversazionale con un altro assistente AI): D1 verificato e solido (attribuzione,
   equazioni base), D2-D7 con 11 difetti aritmetici/logici accertati (violazione di causalità,
   errori di somma, doppi conteggi, codice che non implementa il termine dichiarato). Pagine create:
   `wiki/sources/source-hughes-salvo-event-driven.md`, `wiki/entities/wayne-hughes.md`,
   `wiki/concepts/salvo-combat-model.md`, `wiki/analyses/hughes-salvo-vs-engagement-resolver.md`,
   `wiki/decisions/risolutore-ingaggio-salva-fase4.md` (`status: proposed`: saturazione difensiva
   per-salva, soglia di shock da salva, scorte munizioni per asset come **precondizione nuova**,
   congelamento del payload all'istante di fuoco).

## Stato git a fine sessione
Branch **`analysis/dce-dcs-persistence`**, tutto committato e pushato su origin
(`7d76d9f8`, dopo `67d204e6`). Nessuna perdita dal crash.

## Prossimo passo concreto
**Fase 4**: `Logic/Engagement_Resolver.py` + `Context/Reaction_Profile.py`. Ha tutte le
precondizioni (Contact_Scheduler, Damage_Model, ThreatAA) più tre proposte `status: proposed` non
ancora decise dall'utente che la riguardano direttamente:
- [[soglie-disingaggio-e-attrito-aggregato]] (soglia di disingaggio P1/P2, scenari S1-S11)
- [[llm-locale-ruolo-e-confini]] (nessun impatto diretto sul codice — conferma solo che nessun LLM
  entra nel risolutore)
- [[risolutore-ingaggio-salva-fase4]] (termini del modello a salva: R1-R4)

**Prima di scrivere codice per la Fase 4, conviene chiedere all'utente quali di queste proposte
accetta** — sono tre decisioni indipendenti che cambiano la forma di `Engagement_Resolver.py`.

## Nota per la prossima sessione
La memoria [[project_session_2026_09_21_summary]] conteneva un'istruzione ("ripresentare il report
di stato a inizio sessione") che è stata soddisfatta durante questa sessione, prima del crash — non
ripeterla.
