---
name: project-session-2026-10-18-summary
description: "Sessione 2026-10-18 (ProArt P16) CHIUSA: G5, F7a, correzione A-10C approvati e pushati (fotografia 970, suite 4490); G5 approvato (fotografia 918, suite 4385 OK), nuovo schema agenti (principale Sonnet high, des-planner Opus high, des-developer Sonnet high) condiviso via git; prossimo manuale DES del bingo G1-G5"
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
- F7a fatta da des-developer, verificata da me (suite 4475 OK, 918 identiche + 52 S28). Correzioni approvate e
  rimandate all'agente: return_fire ri-valutato al lancio nemico nello stesso episodio (ingresso in zona = limite);
  **priority_designated (aerei)**: all'andata NESSUN tiro sulle opportunita' (il sorvolo di una colonna non distoglie
  dalla missione), dopo l'attacco opportunita' ammesse. **Decisione utente**: la fine dell'attacco va valutata sul
  raggiungimento/superamento EFFETTIVO del waypoint ATTACK lungo la rotta reale (ritardi, attese, replan), non
  sull'ETA pianificata; vale anche per gli aggiornamenti futuri. Dopo l'approvazione F7a: flag
  self_escort_capability=True sui 5 loadout A-10C II con AIM-9M (Aircraft_Loadouts.py ~1679-1818), passo separato.
- **F7a APPROVATA** (`9f87a3ad`, fotografia 970, suite 4489). **Correzione A-10C** (self_escort_capability True sui 5
  loadout con AIM-9M) approvata: S28 'self_defence' ora caso positivo, 4 esecuzioni cambiate, suite 4490, fotografia 970
  aggiornata, commit finale della sessione.
- **SESSIONE CHIUSA 2026-10-18**, tutto pushato. Prossima sessione (principale Sonnet high da settings di progetto):
  F7b (decisione 15 da prendere all'inizio: 7 scelte in Proposta_F7 §6), pulizia incongruenze documentali (v. sopra),
  F6-B3 S24-GLIDE, F8. Limiti F7a: ingresso in zona designata dopo la prima valutazione non gestito; fine attacco per
  distruzione solo per designati per id.
