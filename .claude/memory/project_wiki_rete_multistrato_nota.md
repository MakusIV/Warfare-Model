---
name: project-wiki-rete-multistrato-nota
description: Nota (2026-11-08): piano concettuale su rete multistrato logistica/militare per la convenienza degli attacchi, da gestire nel wiki quando l'utente avra' pronti i documenti fondamentali; nessuna azione prima
metadata:
  type: project
---

L'utente (2026-11-08) prepara un piano concettuale per integrare ed evolvere la rappresentazione dei collegamenti fra blocchi (militari, urbani/civili, logistici: produzione, trasporto, immagazzinamento) per definire una logica decisionale sugli obiettivi di convenienza per l'attacco dei blocchi militari (il modello logistico esiste gia').

**Decisione:** la fase di ricerca generale va nel **WIKI_LLM_SIMULATION** (`Analysis/WIKI_LLM_SIMULATION/`), NON in una Proposta. L'utente iniziera' quando i documenti che ritiene fondamentali saranno pronti per l'ingestione: aspettare il suo via, non iniziare prima.

**Materiale gia' visto:** `Rete Multistrato Simulazione Militare.pdf` (conversazione Gemini, 9 pagine, in `/mnt/c/Users/marco/Downloads/`; formule non estratte dal PDF) e `Modello di Rete Multistrato per Simulazione Militare - Google Gemini.md` (solo la prima parte). Contenuto: rete multistrato terra/aria, matrice di adiacenza a blocchi, vettore costo arco (tempo, capacita', rischio, consumo), interdizione di rete, max-flow/min-cut, flusso multimerce con matrice di trasformazione sugli archi interstrato, funzione di utilita' `gain/(cost+rischio)` con 3 azioni (attacco militare, attacco logistico, riposizionamento), pseudocodice.

**Come trattarlo (proposta del principale, da confermare con l'utente):**
- Parte teorica generale (rete multistrato, flusso, interdizione) -> `RAW/` del wiki come **fonte debole** ("conversazione LLM, non verificata"), poi `ingesta` seguendo `Analysis/WIKI_LLM_SIMULATION/CLAUDE.md` (§ Flussi di Lavoro). Agenda di verifica con la letteratura (da cercare con oc-researcher, snapshot in `RAW/web/`): reti multistrato (Kivela 2014), network interdiction (Wood 1993), analisi dei sistemi bersaglio (Warden, CARVER), flusso su rete espansa nel tempo [I, nomi non verificati].
- Terzo prompt (definizioni dell'utente: blocchi, combat_power, 3 funzioni logistiche, 7 risorse) e parte decisionale -> materiale di PROGETTO: `Analysis/Document/` come input del suo piano, non in RAW.
- Rilievi di merito: moltiplicatori inventati (1.5, 2.0, 0.8, 100.0), `get_nodes_depending_on` dato per scontato, rapporto gain/cost con grandezze non omogenee, max-flow statico (servono scorte/tempo), nodi aerei non fissi, combat power nemico noto con certezza (contro la nebbia di guerra, Fase 2 `use_recon`).
- Gestione: si puo' lavorare dalla sessione Warfare-Model leggendo prima il CLAUDE.md del wiki (i comandi sono flussi di lavoro, non slash command; nessun `.claude/` nel wiki); mai due sessioni insieme sul wiki (index.md, log.md); per lotti lunghi una sessione dedicata nel wiki e' piu' leggera. Confine dei livelli: [[reference-wiki-llm-simulation]].

**Altro:** `pymupdf4llm` installato nel venv ProArt (permesso dell'utente) ma NON ancora in `requirements.txt` (aggiungere `pymupdf4llm` quando il working tree e' libero, dopo la delega oc-developer BI blocco 3). Conversione: `.direnv/python-3.12/bin/python3 -I -c "import pymupdf4llm,pymupdf; ..."`.
