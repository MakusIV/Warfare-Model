---
name: feedback-model-effort-delegation
description: "Regola modelli/sforzi: dal 2026-10-18 principale Sonnet high, des-planner Opus high = piano, esecuzione a scelta des-developer Sonnet high oppure (dal 2026-10-19) oc-developer OpenCode; come proporre le deleghe"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4b5fdb17-4e5b-46ee-ad95-08f076180fc8
  modified: 2026-10-18T12:00:00.000Z
---

## Schema in vigore dal 2026-10-18 (deciso dall'utente per ridurre il consumo di token)
- **Principale: Sonnet high**, impostato in `.claude/settings.json` del progetto (`model`, `effortLevel`),
  condiviso via git su tutte le macchine (osboxes compresa). Dialoga con l'utente, delega, verifica
  (suite + `--compare` contro l'esito ATTESO dal piano), committa.
- **Analisi, valutazione, piano di intervento → `des-planner` (Opus high)**, scrive solo in
  `Analysis/Document/Proposta_*.md` con struttura fissa (problema, alternative, decisioni aperte, piano con
  file/funzioni, effetti, vincoli RNG/interruttori/nomi della fotografia, test, esito atteso del confronto).
  L'utente legge il documento direttamente.
- **Esecuzione del piano → `des-developer` (Sonnet high)**: segue il piano, si FERMA e riferisce se il
  codice non torna; fa girare suite e confronto mentre lavora.
- **Nessun agente di test separato di norma**: la verifica indipendente e' del principale. Solo con molte
  esecuzioni cambiate (es. le 165 dell'uscita di scena G4) l'analisi delle differenze va a `des-planner`.
- **Riserva Opus high** (`des-developer` con override o `des-planner`) per bug difficili/causa ignota.
- Restano: manuale → `des-manual-writer` Sonnet high; ricerche → `Explore`; ingestione documenti lunghi →
  Sonnet medium.

**Why:** il principale porta tutto il contesto della sessione ed e' il consumo maggiore; il giudizio di
design si concentra nel piano scritto da Opus, che e' anche il passaggio di consegne verso Sonnet.

## Corsia OpenCode (dal 2026-10-19, protocollo in AGENTS.md/CLAUDE.md)
- **Opzione in piu', non sostitutiva**: per eseguire un piano gia' approvato si sceglie OGNI VOLTA tra
  `des-developer` (Claude, come oggi) e `oc-developer` (OpenCode, `openrouter/deepseek/deepseek-v4-pro`,
  costo in $ OpenRouter, nessun consumo del piano Pro). Compiti meccanici: `oc-helper` (locale su Game_PC,
  richiede `attiva_llm`). Seconda opinione su un diff: `oc-reviewer` (`openrouter/z-ai/glm-5.3`).
- Proposta all'utente nella solita riga "compito -> agente, modello, motivo", attendere conferma.
- Criterio indicativo: piano dettagliato e a basso rischio -> `oc-developer`; piano con zone grigie, molte
  esecuzioni cambiate attese o codice delicato (RNG, interruttori) -> `des-developer`.
- Il principale prepara il branch `ai/oc-<tema>`, l'utente lancia `oc`; il principale verifica rapporto,
  diff, suite e confronto (`tools/ai/verifica.sh`) prima del merge. Solo il principale scrive la memoria.
- **Pilota 2026-10-19 RIUSCITO** (`Proposta_Pulizia_Incongruenze_Doc.md`, manuale §9.6 voci 14-18, commit `d1686b28`):
  oc-developer in 22 min, modifiche identiche al piano carattere per carattere, suite 4490 OK e 970 identiche
  (rieseguite dal principale), costo 0,12 $ OpenRouter. Il rapporto era veritiero ma TACEVA un intoppo superato
  (verifica.sh uccisa dallo strumento bash di OpenCode, poi corretto con setsid): nel verificare, guardare anche
  il log della sessione OpenCode (`.ai-run/pilota_oc.log` o `oc export`), non solo il rapporto.
- Piano per oc-developer = stile des-planner ma con testi/firme ESATTI dove possibile: piu' il piano e' preciso,
  meno l'esecutore decide e piu' e' facile verificarlo.

## Regola precedente (2026-10-08, superata dallo schema sopra salvo le regole di conferma)

Modello principale: **Opus 5.5, sforzo high** (deciso dall'utente 2026-10-08). Decide con l'utente, orchestra i sub-agenti e verifica prima del commit.

Assegnazione per tipo di attività:
- Decisioni di design, analisi, revisione piani → principale (Opus high), insieme all'utente
- Implementazione con criteri già decisi (fasi F4b, F4c…) → `des-developer`, Opus medium
- Modifiche meccaniche/ripetitive (rinomine, test a schema fisso, inserimento dati armi DCS) → sub-agente Sonnet medium
- Manuale DES / doc Markdown+Mermaid → `des-manual-writer`, Sonnet high
- Ricerche nel codice → `Explore`, Haiku o Sonnet low
- Ingestione documenti lunghi (PDF, doc DCS) → sub-agente Sonnet medium
- Bug difficili/causa ignota → principale o `des-developer`, Opus high

**Why:** l'utente vuole che il principale lo aiuti a decidere l'uso di modelli e sforzi adeguati; il risparmio viene dal delegare l'esecuzione, non dall'abbassare il principale.

**How to apply:** prima di delegare, proporre in una riga "compito → agente, modello, sforzo, motivo" e attendere conferma; se una scelta si ripete senza obiezioni diventa regola e non si chiede più. Le verifiche pre-commit restano sempre al principale (v. [[feedback-parallel-agents-verification]]).

**Deroghe (2026-10-17):** ogni scostamento dallo sforzo/modello della regola o del frontmatter dell'agente (es.
`des-developer` a effort high invece di medium) va proposto in una riga DEDICATA con il motivo e confermato
dall'utente; mai inserito nella descrizione di un'opzione di una domanda su altro, mai esteso da un passo al
successivo (G4a -> G4b) senza chiedere. Una nota di memoria che dice "proposta Opus high" riguarda l'analisi del
principale, non l'implementazione delegata. Origine: G4a e G4b lanciati a effort high senza conferma esplicita.
