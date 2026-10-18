---
name: project-session-2026-10-18-summary
description: "Sessione 2026-10-18 (ProArt P16): G5 approvato (fotografia 918, suite 4385 OK), nuovo schema agenti (principale Sonnet high, des-planner Opus high, des-developer Sonnet high) condiviso via git; prossimo manuale DES del bingo G1-G5"
metadata:
  type: project
---

- **G5** fatto da `des-developer` (Opus medium, ultima volta con lo schema vecchio), verificato da me: suite 4385 OK,
  confronto 878 identiche + 40 nuove S27; approvato dall'utente, fotografia 918, commit `6e7a9b81`. Piano G1-G5 chiuso
  (v. [[project-bingo-reverse-route-decision]]).
- **Schema agenti nuovo** deciso dall'utente (consumo di token): v. [[feedback-model-effort-delegation]]. File:
  `.claude/settings.json` (model sonnet, effortLevel high), `.claude/agents/des-planner.md` (nuovo),
  `.claude/agents/des-developer.md` (Sonnet high, si ferma se il piano non torna). Condiviso via git per osboxes.
  Nota: `~/.claude/settings.json` di ProArt ha Opus 5.5 a effort medium (personale, non incide sugli agenti).
- Domanda dell'utente sulla quota del terreno nel DES -> perimetro del modulo mappe esteso, v. [[project-map-module-plan]].
- **Prossimo**: manuale DES sul bingo G1-G5 (`des-manual-writer`, Sonnet high); poi gli aperti della deviazione 22
  (F6-B3 S24-GLIDE, registro emergency/time, validatore fuori da run_session, salve dopo il bingo), F7-F9.
- Manuale DES aggiornato a a784a9e7 (`234071d3`). Proposta F7 (`des-planner` Opus high) committata `35c1336d`;
  DECISO dall'utente: tutte le raccomandazioni accettate (tabella MISSION_WEAPON_POLICY com'e', ROE default
  weapon_free), decisione 15 rimandata alla F7b, correzione self_escort_capability A-10C dopo verifica utente in DCS
  (`4f6fa196`). F7a avviata con `des-developer` Sonnet high (primo uso del nuovo schema); atteso 918 identiche + S28.
- Incongruenze da pulire dopo la F7 (trovate dal manual writer, manuale §9.6 voci 15-21): intestazione/colonna
  Commit del Piano, residui "TOT comune" in Piano/Proposta_Struttura/F4 F5-C, docstring superati
  (Mission_Adapter:165,:348; Session_Types:164; Engagement_Resolver:322).
