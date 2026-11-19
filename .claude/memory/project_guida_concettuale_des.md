---
name: project-guida-concettuale-des
description: "Guida concettuale al motore DES per un responsabile di progetto (senza codice, con letteratura e rimandi al manuale): flusso A scaletta+bibliografia, B stesura, C verifica; decisioni Q1-Q11 prese il 2026-11-19"
metadata:
  node_type: memory
  type: project
  originSessionId: b8957df7-0ff6-4dda-a9b7-1a02488a0423
  modified: 2026-11-19T15:59:01.303Z
---

Richiesta dell'utente il 2026-11-19: un documento che spiega struttura, funzionamento, caratteristiche e LIMITI del DES a un **responsabile di progetto non esperto di programmazione**, senza riferimenti al codice, con letteratura di riferimento e rimandi ai capitoli/paragrafi del Manuale DES. Lunghezza decisa dalla chiarezza (non fissata). Formato: Markdown con diagrammi concettuali (Mermaid) e schemi.

**Flusso approvato:** A (scaletta + bibliografia verificata, agenti in parallelo) -> B (stesura con agente Opus high, in 2-3 parti) -> C (verifica della sessione principale: rimandi al manuale, campione di affermazioni sul codice, etichette dei limiti).

**STATO a fine sessione 2026-11-19:** fase A FATTA (scaletta `Guida_Concettuale_DES_Scaletta.md`, 977 righe, 16 sezioni, ~58-67 pagine; bibliografia `Guida_Concettuale_DES_Bibliografia.md`, 592 righe, 8 argomenti coperti, verificata dall'agente con Crossref/Open Library; 6 DOI ricontrollati a campione dalla sessione principale, tutti corretti). Prima della fase B restano: (1) **aggiornare la scaletta** con le decisioni (formule SI nel testo e centrali, sezione propria sui pianificatori di rotta e d'attacco = cap. 7 §7.8-§7.9, sezione 12 fuori dalla guida in un documento di stato, riassunto iniziale, sezione sui limiti); (2) **riconfermare Q10** (rapporto con le sessioni DCS giocate) con una formulazione proposta; (3) ricontrollare ISBN e anni dei libri sul frontespizio (schede editori bloccate), la nota Swerling (conoscenza generale dell'agente, da verificare), e le voci «Non verificate» (ISBN Hughes 3a ed., Taylor 1983, DoDI 5000.61, Pd 0,5/0,9 come convenzione della portata radar); (4) correggere nel wiki le discordanze trovate (Hillestad & Moore 1996 non 1994; Bracken solo Ardenne; Fleet Tactics 1999/2000; le equazioni a salve sono nell'articolo Hughes 1995 NRL, DOI 10.1002/1520-6750(199503)42:2<267::AID-NAV3220420209>3.0.CO;2-Y). Le fonti del wiki su Hughes e Lanchester sono conversazioni con assistenti AI: non citarle. Fase B: stesura con agente Opus high in 2-3 parti, citando solo dalla bibliografia; fase C: verifica della sessione principale. Il manuale ha prima richiesto §1.1 ripristinata e §9.6 aggiornata (fatti).

**File (cartella `Analysis/Document/Manuale_Motore_DES/`):** `Guida_Concettuale_DES_Scaletta.md` (des-manual-writer Opus high; COMMITTATA a fine sessione 2026-11-19), `Guida_Concettuale_DES_Bibliografia.md` (agente general-purpose Sonnet con web; **NON committata**: l'utente aveva autorizzato il commit della sola scaletta, chiedere l'ok per la bibliografia all'inizio della prossima sessione; il file e' nel working tree di osboxes), poi `Guida_Concettuale_DES.md` (da scrivere, fase B).

**Decisioni dell'utente (2026-11-19) sulle domande Q1-Q11 della scaletta:**
- Q1 titolo `Guida_Concettuale_DES.md`, data e commit del manuale in testa, aggiornata da des-manual-writer.
- Q2 **le formule restano e sono parte centrale** (legge di Pd, saturazione, regola di permanenza ecc.), spiegate bene nel testo, non in riquadri facoltativi.
- Q3 nel testo descrizioni piane, sigle di progetto (D-5, BI, VA, FP...) nella tabella di corrispondenza.
- Q4 ripristinare la §1.1 del capitolo 1 (sparita) prima della fase B; Q5 descrivere "1103 installata, 1219 in attesa"; Q6 fonti primarie, secondarie solo come indicazioni; Q8 la guida dice che oggi il motore serve per confronti relativi con repliche e che non c'e' validazione su dati reali; Q9 sezione 12 (decisioni aperte) in un documento di stato separato; Q10 risposta "ok" ambigua: la formulazione del rapporto con le sessioni DCS giocate va riconfermata prima della stesura; Q11 lunghezza completa con riassunto iniziale.
- Q7 **i pianificatori di rotta e d'attacco vanno DESCRITTI bene** (non solo citati): la scaletta va ampliata con una sezione propria e il manuale li tratta in cap. 7 §7.8-§7.9.

**Problemi trovati nel manuale dalla scaletta (verificati 2026-11-19):** §1.1 mancante dal capitolo 1 (ancora citata da cap. 1 e cap. 7; testo in git a `355b1017`); voci 30, 31, 32 di §9.6 "APERTE" ma corrette nel codice da `dad7c66f`. Fonti del wiki su Hughes e Lanchester = conversazioni con assistenti AI, NON letteratura primaria: non citarle come fonti. Il motore NON e' un modello alla Lanchester.

**Why:** il manuale e' scritto sul codice; il lettore finale e' un responsabile che deve capire cosa fidarsi. **How to apply:** in fase B citare solo dalla bibliografia verificata, mantenere le etichette [V]/[S]/[D]/[NV], nessun limite trasformato in proprieta'. Link: [[project-dwell-dw9-estensione]] (stato D-5 e limiti), [[feedback-model-effort-delegation]].
