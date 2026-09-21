---
name: project-session-2026-09-21-summary
description: "Recap sessione 2026-09-21: analisi delle due strategie per il motore di esecuzione delle sessioni virtuali + architettura decisa (DES a coda eventi) + Fase 1 (cinematica) implementata e testata. L'utente ha chiesto di ripresentare il report di stato all'inizio della prossima sessione."
metadata:
  type: project
---

**ALL'INIZIO DELLA PROSSIMA SESSIONE: ripresentare il report sullo stato del lavoro.**
Richiesta esplicita dell'utente a fine sessione 2026-09-21. Il report va costruito da
[[project_virtual_session_engine_design]] (verdetto sulle strategie, architettura, le 11
precondizioni, la roadmap a 7 fasi) piu' lo stato git qui sotto. Non ripetere l'analisi:
riassumere dov'e' il lavoro e qual e' il prossimo passo (Fase 2).

## Cosa e' stato fatto in questa sessione
1. **Analisi delle due strategie** proposte dall'utente in
   `Analysis/Document/Architettura_esecuzione_sessioni_virtuali.txt` (tick a 1 ms con slot per
   asset e RIV/VAL/COM/ATT, vs risoluzione probabilistica). Quattro agenti: due di ricerca web
   (uno per strategia) e due di esplorazione del codice.
2. **Documento prodotto**: `Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md`
   (525 righe, 10 sezioni, bibliografia con URL).
3. **Fase 1 della roadmap implementata e testata** (dettaglio completo in
   [[project_virtual_session_engine_design]]): schema canonico di velocita' in m/s, ponte
   registry->istanza, `Route.positionAtTime`, `Military._speed_regime`.

## Stato git a fine sessione
Branch **`analysis/dce-dcs-persistence`** (non `main`), tutto committato e pushato su origin.
Due commit: uno per il documento di analisi, uno per la Fase 1 (codice + test + memoria).
Nota: il nome del branch parla di analisi ma ora porta anche codice di implementazione —
l'utente e' stato avvisato e puo' volerlo separare o rinominare.

## Prossimo passo concreto
**Fase 2**: `Mobile.detection_range(mode)` sulla falsariga di `combat_range()` (i dati radar/TVD
con `acquisition_range`/`tracking_range`/`engagement_range` per modo air/ground/sea esistono gia'
per ogni modello nei registry, in km), e la fabbrica di `ThreatAA` da `Mobile.air_defense_volume()`
+ dati arma. Sono le precondizioni 3 e 4; le 1 e 2 sono state chiuse dalla Fase 1.

## Da decidere prima della Fase 3
Restano aperte le tre questioni gia' elencate nel documento (§9): quale modello di `Route` vince
fra i tre incompatibili, la semantica della perdita per-asset (`Destroyed` a `health <= 15`), e
se SAM/AAA/EWR vadano nelle tabelle di efficacia o trattati fuori dal combat power.
