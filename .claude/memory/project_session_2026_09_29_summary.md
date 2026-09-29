---
name: project-session-2026-09-29-summary
description: "Sessione 2026-09-29 (osboxes/VM): soglia di rottura stocastica (D1-D9) + efficacia difensiva antiaerea E(N) (D4a-D4e) implementate, suite 3705 OK; NON committato al momento della scrittura"
metadata:
  node_type: memory
  type: project
  originSessionId: c96aae50-d207-4afc-a001-15c7352ab468
  modified: 2026-09-29T10:07:24.352Z
---

**Macchina**: osboxes (VM), branch `analysis/dce-dcs-persistence`, allineato a origin a inizio
sessione (`d4044024`). Suite di partenza 3668 OK; python di sistema (`python3`, nessun venv/ qui).

## Fatto: difetto §5.3 (disingaggio alla prima perdita) risolto
Proposta + decisioni + implementazione in `Analysis/Document/Proposta_Soglia_Rottura_Stocastica.md`
(§10 decisioni, §11 D4, §12 implementazione). Soglia di rottura B(t) per forza: tempra estratta una
volta (logit-normale, mediana 0,30, σ 0,5, flusso separato `temper_event_id`), modulata da morale
(ingresso `morale_for`, None = neutro, ±30%), rapporto di forze percepito (dai rilevamenti, `R` in
[0,6;1,5]), fuoco senza risposta (γ 0,3), postura ferma (×1,2); shock = 2/3·B(t) con minimo 2 perdite.
D4 (l'utente ha respinto il conteggio puro): nuovo `Context/Air_Defense_Efficacy.py`, E(N) = aerei
abbattuti attesi (p per ingaggio × ingaggi limitati da canali, cicli nel tempo di attraversamento,
scorta corrente); forza aerea: ρ = N/(2·Σ E), forza di superficie: conteggio con SAM puri a peso 0.
Tabelle con sole erosion/shock = soglie fisse di prima (compatibilità).

Esiti: S1 senza CAS rottura alla 1ª perdita 3/8 (prima 7/8); S5 2/6 formazioni arrivano al Buk.
Test aggiornati: S10 usa `FIXED_THRESHOLDS` + caso DISPERSIONE, S5 asserzione a distribuzione.

## Da fare / aperto
1. **Commit + push** (non fatto: chiedere all'utente). File: Doctrine.py, Air_Defense_Efficacy.py
   (nuovo), Engagement_Resolver.py, Session_Simulator.py, test (Doctrine, Engagement_Resolver,
   Session_Simulator, Air_Defense_Efficacy nuovo, Scenarios, S10_S18), 2 documenti Analysis.
2. Scelte implementative da far rivedere all'utente (§12 della proposta): B(t) ricalcolata a ogni
   salva, distrutti esclusi dai nemici percepiti, armi di un asset combinate indipendenti.
3. Limite emerso: gli F-15E non rilevano i SAM (nessun modo 'ground'), fuoco senza risposta sempre 1
   → legare all'avviso radar (RWR) in futuro.
4. D9: `Block.morale` rotto (success_ratio mai alimentato → 0, MF fuzzy fuori scala) — dopo.
5. Restano dalla lista del 2026-09-28: overkill stesso tiratore (§5.2), intercettazione senza tempo di
   reazione (§5.4), A4/Mission, residui volumi, Fase 0 C2, bug noti, manuale DES (ora anche soglia di
   rottura + Air_Defense_Efficacy).
