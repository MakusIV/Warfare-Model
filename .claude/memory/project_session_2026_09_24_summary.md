---
name: project-session-2026-09-24-summary
description: "Sessione 2026-09-24 (osboxes): manuale DES fatto, scelta arma dai registri (Fire_Control) e controllo di portata fatti e committati (suite 3444 OK); aperti: analisi SAM/intercettazioni, bombe senza portata, munizioni aggregate aerei, poi nebbia di guerra (C), capitolo manuale, volumi generici (D); agenti .claude/agents/des-manual-writer (sonnet high) e des-developer (opus medium)"
metadata:
  node_type: memory
  type: project
  originSessionId: a651c837-4953-4797-b84a-72907b5a4a7b
  modified: 2026-09-24T09:53:35.911Z
---

**Macchina**: osboxes. Nessun venv nel repo: la suite gira con il `python3` di sistema (3.10.12),
3371 test OK (skipped=5), ~10 min. Leggere il riepilogo dal log completo, non da `tail` in pipe
(un primo tentativo ha perso le righe `Ran/OK`).

**Piano approvato** (copia versionata: `Analysis/Document/Piano_Lavori_2026_09_24.md`, leggerla per il
dettaglio):
- A. Manuale del motore DES in `Analysis/Document/Manuale_Motore_DES/`, diagrammi Mermaid (niente
  Java/PlantUML su osboxes), agente `des-manual-writer` (Sonnet 5, effort high), in background.
- B. Scelta arma dai registri: nuovo `Logic/Fire_Control.py` (`make_registry_fire_control`),
  motore non toccato. B1 prima: tabella proposta di efficacia antiaerea vs aerei da sottoporre
  all'utente PRIMA di scrivere nei registri.
- C. Nebbia di guerra: factory `recon_detection_factor_fn` + `combine_detection_factors` in
  `Engagement_Resolver.py`, istantanea di ricognizione fissata PRIMA della sessione (decisione
  utente: niente RNG globale nel motore), S9 esteso con Region vera.
- Sviluppo B e C con agente `des-developer` (Opus 5.5, effort medium, scelta utente per economia);
  la sessione principale verifica sempre (rilettura + suite completa). Commit solo su richiesta.

**Regola dell'utente per l'antiaerea** (B1, testuale nella sostanza): un aereo è in linea di
massima un bersaglio `Soft`. Attacker dedicato CAS (A-10, Su-25; NON un F-16, che è
fighter-bomber) ≈ `Armored` se non ci sono incongruenze evidenti a parità di arma, altrimenti
Soft; Fighter e Fighter_Bomber con valori inferiori all'attacker; Bomber/Heavy_Bomber:
più strutturati ma più grandi e meno manovrabili (più facili da colpire), classificazione
inferiore o uguale al fighter. Tabelle da aggiornare: `AMMO_TARGET_EFFECTIVENESS`,
`_EFF_AA_CANNON*`, `_EFF_SAM_*` in `Ground_Weapon_Data.py` (i `_EFF_SAM_*` oggi hanno bersagli
terrestri inadatti) + analoghi in `Ship_Weapon_Data.py`. Accuracy vs aerei va definita a parte
(le righe Soft/Armored dei SAM sono accuratezze vs terra).

**Stato al momento della scrittura**: agenti creati ma `.claude/agents/` è una cartella nuova →
serve riavviare Claude Code (`claude --continue`) perché vengano caricati. Nessun codice toccato.
Prossimo passo dopo il riavvio: lanciare A (background) e B1 in parallelo.
Opus 5.5 medium vs Opus 5 high: nessun dato di confronto verificato, scelta dell'utente per costo;
se una consegna risulta debole, alzare a high quella parte.

## Aggiornamento (stesso giorno)
- Manuale DES FATTO (`Analysis/Document/Manuale_Motore_DES/`, 10 file, 9 diagrammi Mermaid); corretto D7 (stati salute: Healtful/Damaged dentro Operative). Divergenza wiki segnalata all'utente, non corretta: `soglie-disingaggio-e-attrito-aggregato.md` righe 53/138 dicono che una forza disingaggiata "rientra nello scheduler", ma il re-scheduling è rimandato nel codice.
- B1+B2 FATTI e verificati (suite 3426 OK): righe aeree nei template, `Context.get_air_target_class`, campi `ground_fire_armored`/`air_target_class` in Aircraft_Data (Su-24M, Su-24MR confermato dall'utente, MiG-25RB come fighter), `Logic/Fire_Control.py`, test S19. Proposta valori in `Analysis/Document/Proposta_Efficacia_Antiaerea.md`.
- In corso (agente des-developer): controllo di portata nel motore (`ShotSpec.max_range` opzionale, tiro rimandato all'ingresso in portata, funzione isolata e sostituibile) + SOLO analisi del problema "SAM puri consumano tutto in intercettazione e non tirano mai sugli aerei" (regole alternative da far scegliere all'utente).
- Attività D ACCETTATA dall'utente: volumi di rilevamento/ingaggio generici (sfera, cilindro, fascia di quota, cono, orizzonte radar + unione/intersezione/differenza di intervalli), dopo C; prima proposta di progetto. Fatto chiave: `run_session` oggi usa solo sfere (distanza 3D ≤ portata di rilevamento); il cilindro ThreatAA lo usano solo Air_Route_Manager e `threat_windows` (non chiamato dalla sessione).
- Anomalie dati segnalate, non corrette: Harpoon con righe contro carri; URK-5 (ASW) fra i SAM navali; 9M331/9M37M fra gli ATGM; MERAD terrestre con missili SHORAD.

## Controllo di portata FATTO (suite 3444 OK, skipped=5) — NON committato al momento della scrittura
- `ShotSpec.max_range` opzionale; geometria isolata in `Engagement_Resolver.engagement_intervals` (sfera via `range_intervals`) e `engagement_intervals_without_legs` (ripiego), sostituibile via `_EngagementRun.engagement_intervals` → punto d'aggancio dell'attività D (volumi). Tiro rimandato con `not_before`, il tiratore intanto può ingaggiare altri bersagli. `Fire_Control` riempie max_range; corretto bug velocità ASM (m/s, non Mach).
- APERTO per l'utente: (1) bombe senza portata nel registro → F-16 'Strike' sganciano Mk-83 da 60 km: serve portata di sgancio stimata o dato di registro; (2) munizioni aggregate aerei (523 per F-16 Strike) → salve di bombe oltre le bombe reali.
- Compito 2 (analisi SAM) RIMANDATO per budget (utente al 97% del limite settimanale). Osservazioni già raccolte: con portata attiva il Buk spende i missili in tiro offensivo; lo Strela-10 (5 km) consuma gli 8 missili in intercettazioni di Maverick (15 km), anche di munizioni dirette ad altri asset della forza, e resta vuoto quando arrivano gli A-10. Script: scratchpad `t2diag.py`, `t2diag_b.py` (effimeri).
- Prossimi passi: analisi SAM → C (nebbia di guerra) → capitolo manuale su B/C → D (volumi, prima proposta). Wiki P1 da correggere se l'utente lo chiede.
