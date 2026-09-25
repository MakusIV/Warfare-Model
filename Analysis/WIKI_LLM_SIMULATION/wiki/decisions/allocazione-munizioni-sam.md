---
title: "Allocazione munizioni SAM: intercettazione vs tiro diretto"
type: decision
tags: [architecture, dwm, combat-resolution, air-defense, discrete-event]
created: 2026-09-25
updated: 2026-09-25
status: proposed
affects: ["[[block]]", "[[risolutore-ingaggio-salva-fase4]]"]
related: ["[[virtual-session-engine-des]]", "[[nebbia-di-guerra-ricognizione]]"]
---

## Contesto

Dopo l'introduzione del controllo di portata nel risolutore (`ShotSpec.max_range`, v.
[[virtual-session-engine-des]] § seguiti), è emerso un problema di allocazione munizioni per i SAM
"puri" — quelli con `Mobile.interceptor_shares_ammunition = True`, dove `interceptor_stock` è una
vista dello stesso pool fisico di `ammunition` (v. [[risolutore-ingaggio-salva-fase4]] R1/R3 e
[[block]]).

## Problema riprodotto

Scenario deterministico (seed `repro-strela-1`, disingaggio disattivato): uno Strela-10 (portata
~5 km, 8 missili) a ~1 km da 3 BMP-2, 4 A-10 con 4 Maverick ciascuno lanciati da ~16 km contro i
BMP. Osservato:

- I 16 Maverick partono a t≈163; lo Strela li intercetta 1 per evento, scorta 8→0 a t≈188.
- Lo Strela rileva gli A-10 solo dopo (t≈202-224).
- Gli A-10 entrano nei suoi 5 km a t≈238: **0 salve sparate**, munizioni esaurite.
- Media su 30 seed: le intercettazioni salvano **0.04 BMP** e costano **1.2 A-10 abbattuti su 4**
  (il rapporto costo/beneficio è invertito).

**Causa nel codice** (`Logic/Engagement_Resolver.py`, `_on_resolve`): intercetta a livello di forza
**tutti** i colpi intercettabili nella finestra, qualunque sia il bersaglio designato del colpo,
senza controllo di distanza/rilevamento, senza riserva né priorità. `salvo_interceptors` tratta
ogni asset di difesa aerea come intercettore con Pk=1.

**Perché non si vedeva nello scenario di default**: mascherato da due difetti indipendenti —
munizioni aggregate aerei abnormi (l'A-10 di default ha 1183 munizioni totali, 128 Maverick) e
soglia di disingaggio Red superata alla prima perdita (shock 0.25 contro soglia 0.20).

## Regole valutate

| Regola | Descrizione | Costo/rischio |
|---|---|---|
| **A — autodifesa** | Il SAM intercetta solo colpi diretti a sé | Minimo, subito applicabile |
| **B — riserva percentuale** (stima 50%) | Conserva una quota di missili per il tiro diretto | Nuova costante da tarare |
| **C — priorità al lanciatore entro T** | Efficace nei numeri, ma usa informazioni che il difensore non avrebbe realisticamente | Rischia di rompere il realismo del fog-of-war |
| **D — capacità antimissile nei registri** | Il task `Anti_Missile` esiste già per le armi navali, manca per quelle terrestri | Richiede estendere i registri arma |
| **E — nessuna modifica** | Il comportamento è "corretto" per un SAM che difende l'area a prescindere dal bersaglio; il problema è di composizione dello scenario/dottrina, non del motore | Nessun costo, ma non risolve i casi come quello riprodotto |
| **F — accessoria** | Consumare prima le scorte dedicate, poi i pool condivisi | Basso costo, non risolutiva da sola |

**Raccomandazione (non ancora decisa dall'utente)**: **D + B + F**, con **A** come intervento
minimo immediato. Segnalato esplicitamente: la decisione va presa **dopo** aver chiuso la
questione delle munizioni aggregate aerei (v. [[virtual-session-engine-des]] § seguiti) — altrimenti
qualsiasi test di verifica delle nuove regole resta falsato dallo stesso artefatto che ha mascherato
il problema finora.

## Motivazione

Nessuna regola è stata scelta a tavolino: derivano tutte da un difetto verificato nel codice
(nessun controllo di bersaglio/distanza/riserva in `_on_resolve`), riprodotto con uno scenario
deterministico e misurato su 30 seed, non da un'osservazione teorica.

## Conseguenze

**Se una regola viene accettata**: tocca `Logic/Engagement_Resolver.py` (`_on_resolve`,
`salvo_interceptors`) e, per la regola D, i registri arma (`Ground_Weapon_Data.py`,
`Ship_Weapon_Data.py`) per dichiarare esplicitamente la capacità antimissile lato terra.

**Se nessuna regola viene accettata (E)**: nessuna modifica; il comportamento osservato resta
accettato come proprietà del modello (un SAM puro difende l'area, non uno specifico bersaglio) e il
problema si sposta alla composizione dello scenario/dottrina d'ingaggio.

**Non fatto in questa proposta**: nessun codice di produzione toccato. Script di riproduzione
(`repro_strela.py`, `proto_rules.py`) solo in scratchpad, non versionati.

## Fonti

- `.claude/memory/project_session_2026_09_25_summary.md` (memoria di origine)
- `Analysis/Document/Proposta_Regole_Allocazione_SAM.md` (documento di proposta completo)
- [[risolutore-ingaggio-salva-fase4]] — R1/R3, meccanismo di intercettazione e munizioni per asset
  su cui questa proposta interviene
- `Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py` — stato attuale verificato nel
  codice (`_on_resolve`, `salvo_interceptors`)
