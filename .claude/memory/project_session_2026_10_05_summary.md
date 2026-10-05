---
name: project-session-2026-10-05-summary
description: "Sessione 2026-10-05 (ProArt P16): avviata la struttura Mission (A4); ingestione documentazione missioni DCS e sintesi Analisi_Informazioni_Missione.md, committate (51c1cb06 + missione di prova terra/mare, non pushato); prossimo: 6 decisioni missione + N1-N3"
metadata:
  node_type: memory
  type: project
  originSessionId: 8a355fb2-022f-4395-b932-414e85ccf31c
  modified: 2026-10-05T11:29:01.222Z
---

**Macchina**: ProArt P16, branch `analysis/dce-dcs-persistence`. L'utente ha scelto di iniziare
dall'attività A4 (struttura di una missione), partendo dalla documentazione DCS che ha messo in
`Analysis/Document/documentazione missioni dcs/` (manuale DCS 2020 390 pp., `DCS_GND_Charts.pdf`,
`DCS World List of all available Beacons EN.pdf`, 23 foto del Mission Editor, `1975 Georgian War_first.miz`).

## Fatto (commit 51c1cb06: solo estratti/ e sintesi; NON pushato)
- Estratti in `documentazione missioni dcs/estratti/`: `Manuale_ME_parte1..4_*.md` (pp. 84-357, 4 agenti
  Sonnet + secondo passaggio sulle figure), `Foto_Mission_Editor.md` (agente Opus),
  `Struttura_File_MIZ.md` (agente Sonnet, parser `lupa`), registri `DCS_Aeroporti_Caucaso.csv` (21 aeroporti)
  e `DCS_Beacons_Caucaso.csv` (214 radioaiuti) con relativi .md.
- Sintesi: `Analysis/Document/Analisi_Informazioni_Missione.md` — modello Sessione ⊃ Missione (pacchetto) ⊃
  Elemento (gruppo DCS); blocchi comuni chi/quando/dove/azioni-regole/carico; specifiche aria/terra/mare;
  postura continua; dati di sessione; registro Airbase; impatti sulle 6 decisioni; nuove decisioni N1-N3.

## Aperto
- Decisione utente: committare SOLO `estratti/` e la sintesi; i documenti originali (PDF, foto, .miz,
  ~140 MB) restano non tracciati, i `*:Zone.Identifier` sono già ignorati da git.
- RISOLTO: l'utente aveva ragione, veicoli e navi ricevono bersagli espliciti (`AttackGroup` su gruppo,
  `FireAtPoint` su punto; navi contro navi e contro terra). Verificato su `ground_sea_mission.miz`
  (missione di prova dell'utente), estratto `Struttura_Missione_Terra_Mare.md`, sintesi aggiornata.
  Lezione: il manuale DCS 2020 è superato su alcuni punti; quando l'utente contesta una deduzione
  dal manuale, verificare su un `.miz` reale. Uso delle info DCS: v. [[feedback-core-simulator-agnostic]].
- Prossimo passo: con la sintesi in mano, riproporre le 6 decisioni di `Analisi_Modello_Missione_Sessione.md`
  §6 più N1-N3, poi progettare l'entità `Mission`.

## Lezioni tecniche
- Il tool Read NON apre `DCS_User_Manual_EN_2020.pdf` e `pdftoppm` non c'è: rendere le pagine in PNG con
  pymupdf (`~/.claude/skills/pdf-to-markdown/.venv/bin/python3`, `page.get_pixmap(dpi=150)`) e passarle agli
  agenti; al primo giro gli agenti avevano guardato le figure solo a campione.
- Docling perde righe sulla tabella dei beacon (iniziava dalla riga 126): usare `page.find_tables()` di
  pymupdf; per le carte aeroportuali la modalità veloce (pymupdf4llm) è migliore di Docling.
- Gli estratti degli agenti vanno verificati: nella sintesi avevo scritto valori di ROE/Reaction to Threat
  di memoria e risultavano sbagliati rispetto al manuale.
