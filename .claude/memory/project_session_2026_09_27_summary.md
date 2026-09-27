---
name: project-session-2026-09-27-summary
description: "Sessione 2026-09-27 (ProArt P16): Proposta B (rotte d'attacco/quota di sgancio) IMPLEMENTATA senza Mission — Logic/Weapon_Delivery.py + Command/Attack_Types.py + B6 in Fire_Control; suite 3645 OK; committato e pushato"
metadata:
  node_type: memory
  type: project
  originSessionId: c7d639f1-f437-4837-9469-9d5731544461
  modified: 2026-09-27T07:46:29.904Z
---

**Macchina**: ProArt P16 (WSL2), branch `analysis/dce-dcs-persistence`, suite con `.direnv/python-3.12/bin/python3`.

## Fatto (lavoro inline, nessun agente)
Proposta B di `Analysis/Document/Proposta_Munizioni_Compatibili_e_Rotte_Attacco.md` implementata
(primo giro, entità `Mission` ancora assente). Decisioni utente del 2026-09-27:
- perimetro completo senza Mission (balistica + pianificatore + transiti base→IP/uscita→base);
- B6 subito: il DES ricava `max_range` (gittata obliqua) e `time_of_flight` delle bombe da
  `Weapon_Delivery.bomb_engagement_estimate`, quota = z tiratore − z bersaglio, velocità = `attack.speed`
  del loadout; fuori finestra si porta al valore ammesso più vicino (come l'IA DCS);
- balistica: un solo modello vettoriale nel vuoto (pitch <0 picchiata, >0 loft a 30°) + fattori drag
  dichiarati (low 0,9/1,05; high 0,5/1,3), glide_ratio e standoff_range_km come casi speciali;
- drag selezionabile: finestra low_drag se la quota ci sta, altrimenti high_drag;
- B2 (tutte le missioni) e B3/D-8 (due liste di minacce, `t_lancio = max(t_in V_I, t_contatto V_R +
  acquisition) + min_fire_time`) adottate come da raccomandazione.

File: `Logic/Weapon_Delivery.py` (nuovo), `Command/Attack_Types.py` (nuovo: `AttackProfile`,
`ThreatExposure`), `Logic/Fire_Control.py` (B6), `Block/Military.air_defense_threats` (ora imposta
`source_id` — prima solo `build_air_defense_threats` lo faceva, e V_I/V_R non erano collegabili),
`Test/Test_Weapon_Delivery.py` (nuovo), `Test/Test_Fire_Control.py` (+`TestFireControlBombRelease`),
`Scenario_Fixtures.LOGGER_TARGETS` (+Weapon_Delivery). Stato scritto in testa al documento della proposta.

Nessuno scenario DES ha cambiato esito con B6 (verificato: suite invariata a parte i nuovi test) — gli
aerei degli scenari volano a 5000 m di default, gittata ~8 km, ingaggi già dentro.

## Aperto
- Commit e push fatti su richiesta utente (codice+documento, poi memoria).
- Scostamento dichiarato: il tratto d'attacco usa l'intervallo analitico
  (`Air_Route_Manager._segment_cylinder_interval`) e non `route_threat_windows` (sympy, troppo lento):
  `threat_windows` resta senza consumatori di produzione.
- Limiti: geometria picchiata/cabrata solo nella balistica; sfera DES senza distanza minima; A-10/aerei
  con quota sotto il min_altitude della bomba vengono "alzati" dal DES (clamp).
- Resto invariato dalla lista di [[project_session_2026_09_26_summary]]: D4 KGBU, A4/A6, D-4b/c, D-5
  opz. 2, 6 decisioni missione, manuale DES (ora da aggiornare anche per Weapon_Delivery), Fase 0 C2.
