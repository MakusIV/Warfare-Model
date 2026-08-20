# CLAUDE.md — Schema del Wiki LLM per Modelli di Simulazione

Questo documento è il **file di configurazione principale** del wiki. Descrive la struttura, le convenzioni e i flussi di lavoro che Claude deve seguire per gestire questa base di conoscenza. Leggi questo file all'inizio di ogni sessione.

---

## Contesto del Progetto

Questa è una base di conoscenza wiki gestita da LLM, focalizzata su:
- **Modelli di simulazione bellica e campagna militare** (campaign models, wargaming, combat simulation)
- **Metodologie di simulazione** (agenti, sistemi discreti, Monte Carlo, ecc.)
- **Sviluppo del progetto Warfare-Model** situato in `/home/marco/Sviluppo/Warfare-Model/`

Il progetto Warfare-Model è un simulatore dinamico di campagna militare (Dynamic War Manager) sviluppato in Python, che opera su missioni DCS (Digital Combat Simulator). Il wiki supporta la ricerca e lo sviluppo di questo modello.

---

## Struttura delle Directory

```
WIKI_LLM_SIMULATION/
├── CLAUDE.md               ← QUESTO FILE (schema/configurazione)
├── RAW/                    ← Fonti grezze (IMMUTABILI — solo lettura)
│   ├── *.pdf / *.doc / *.md / *.txt
│   └── assets/             ← Immagini e allegati scaricati localmente
├── Istruzioni/             ← Documentazione di progetto
│   └── Wiki_LLM.txt        ← Articolo originale di Karpathy (riferimento)
└── wiki/                   ← Wiki gestita da LLM (SOLO LLM scrive qui)
    ├── index.md            ← Catalogo di tutti i contenuti wiki
    ├── log.md              ← Registro cronologico di tutte le operazioni
    ├── overview.md         ← Panoramica del dominio e stato attuale
    ├── entities/           ← Pagine di entità (modelli, sistemi, autori, tool)
    ├── concepts/           ← Pagine di concetti e metodologie
    ├── sources/            ← Riepiloghi delle fonti RAW ingerite
    ├── analyses/           ← Analisi, confronti, query archiviate
    └── assets/             ← Immagini generate o estratte
```

**Regola fondamentale**: Claude **legge** da `RAW/`, **scrive esclusivamente** in `wiki/`.

---

## Formato delle Pagine Wiki

Ogni pagina wiki deve avere questo frontmatter YAML:

```yaml
---
title: "Titolo della Pagina"
type: entity | concept | source | analysis | overview
tags: [tag1, tag2, tag3]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [nome-fonte-1, nome-fonte-2]   # solo per entity/concept
related: [[[Pagina Collegata 1]], [[Pagina Collegata 2]]]
---
```

### Struttura per tipo:

**`entities/`** — Modelli, sistemi, organizzazioni, autori, tool, simulatori
```markdown
---
title: "Nome Entità"
type: entity
tags: [categoria, sottocategoria]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [lista fonti]
related: []
---

## Descrizione
Breve descrizione dell'entità.

## Caratteristiche Principali
- Caratteristica 1
- Caratteristica 2

## Relazioni
- Collegato a: [[Entità2]], [[Concetto1]]
- Parte di: [[SistemaParent]]

## Fonti
- Menzionato in: [[source-nome-fonte]]
- Pagina X di: [[source-nome-fonte]]

## Note
Osservazioni aggiuntive, contraddizioni, lacune da colmare.
```

**`concepts/`** — Metodologie, tecniche, paradigmi di simulazione
```markdown
---
title: "Nome Concetto"
type: concept
tags: [metodologia, simulazione, ...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [lista fonti]
related: []
---

## Definizione
Definizione precisa del concetto.

## Applicazione nel Dominio
Come si applica al warfare modeling.

## Vantaggi e Limitazioni
| Aspetto | Dettaglio |
|---------|-----------|
| Vantaggio | ... |
| Limitazione | ... |

## Relazioni con altri Concetti
- [[Concetto Padre]]
- [[Concetto Correlato]]

## Fonti
```

**`sources/`** — Riepiloghi di ogni documento RAW ingerito
```markdown
---
title: "Titolo Documento"
type: source
tags: [topic1, topic2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
file: RAW/nome-file.pdf
authors: [Autore1, Autore2]
year: YYYY
related: []
---

## Riepilogo Esecutivo
Sintesi in 3-5 frasi dei punti chiave.

## Contributi Principali
1. Contributo 1
2. Contributo 2

## Entità Menzionate
- [[Entità1]] — ruolo nel documento
- [[Entità2]] — ruolo nel documento

## Concetti Chiave Trattati
- [[Concetto1]] — come viene trattato
- [[Concetto2]] — come viene trattato

## Citazioni Rilevanti
> "Citazione testuale importante." (p. X)

## Lacune e Contraddizioni
- Aspetti non coperti o in contraddizione con [[altra-fonte]]

## Applicabilità al Warfare-Model
Come questo documento si applica al progetto in corso.
```

**`analyses/`** — Analisi, confronti, risposte a query complesse
```markdown
---
title: "Titolo Analisi"
type: analysis
tags: [topic1, topic2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
query: "La domanda originale che ha generato questa analisi"
sources: [fonte1, fonte2]
related: []
---

## Domanda
La domanda a cui risponde questa analisi.

## Risposta Sintetica
Risposta diretta in 2-3 frasi.

## Analisi Dettagliata
...

## Fonti Utilizzate
- [[source-nome1]] — sezione/pagina citata
- [[source-nome2]] — sezione/pagina citata

## Conclusioni e Implicazioni per Warfare-Model
```

---

## Flussi di Lavoro

### 1. INGESTIONE di una nuova fonte

Quando l'utente dice `ingesta [file]` o `elabora [file]`:

1. **Leggi** il file dalla cartella `RAW/`
2. **Discuti** brevemente i punti chiave con l'utente
3. **Crea** la pagina `wiki/sources/[nome-normalizzato].md` con riepilogo completo
4. **Identifica** tutte le entità (modelli, sistemi, autori, tool, organizzazioni) → crea o aggiorna `wiki/entities/`
5. **Identifica** tutti i concetti e metodologie → crea o aggiorna `wiki/concepts/`
6. **Aggiorna** `wiki/index.md` con le nuove pagine
7. **Aggiorna** `wiki/overview.md` se il documento modifica il quadro generale
8. **Aggiungi voce** in `wiki/log.md`: `## [DATA] ingestione | Titolo Documento`
9. **Segnala** eventuali contraddizioni con fonti già presenti

**Convenzione nomi file**: `kebab-case-del-titolo.md` (es. `theater-level-campaign-model.md`)

### 2. QUERY al wiki

Quando l'utente pone una domanda:

1. **Leggi** `wiki/index.md` per identificare le pagine pertinenti
2. **Leggi** le pagine pertinenti
3. **Sintetizza** una risposta con citazioni alle pagine wiki
4. **Valuta** se la risposta merita di essere archiviata come nuova pagina `wiki/analyses/`
5. **Aggiungi voce** in `wiki/log.md`: `## [DATA] query | Titolo Query`

### 3. CONTROLLO DI INTEGRITÀ (health check)

Quando l'utente dice `health check` o `verifica wiki`:

1. Cerca **contraddizioni** tra pagine
2. Identifica **pagine orfane** (nessun link in entrata)
3. Trova **concetti menzionati ma senza pagina** dedicata
4. Segnala **riferimenti incrociati mancanti**
5. Suggerisci **lacune** da colmare con nuove fonti
6. Aggiungi voce in `log.md`: `## [DATA] health-check | Sintesi risultati`

### 4. AGGIORNAMENTO di una pagina esistente

Quando nuove informazioni aggiornano una pagina:
1. Aggiorna il frontmatter (`updated:`, `sources:`)
2. Integra le nuove informazioni senza cancellare quelle precedenti
3. Se c'è contraddizione, segnalala in **Note** con riferimento alla fonte
4. Aggiorna `wiki/log.md`

---

## Convenzioni Speciali per questo Dominio

### Tassonomia dei Tag
```
simulazione:
  - campaign-model       # Modelli di campagna militare
  - combat-simulation    # Simulazione del combattimento
  - wargame              # Wargaming
  - agent-based          # Simulazione ad agenti
  - discrete-event       # Simulazione a eventi discreti
  - monte-carlo          # Simulazione Monte Carlo
  - historical           # Modellazione di conflitti storici

dominio:
  - air                  # Componente aerea
  - naval                # Componente navale
  - ground               # Componente terrestre
  - joint                # Operazioni congiunte

warfare-model:           # Specifico del progetto
  - dwm                  # Dynamic War Manager
  - dcs                  # Digital Combat Simulator
  - implementation       # Aspetti implementativi
  - architecture         # Architettura del sistema
```

### Link Wikilink
Usa sempre la sintassi `[[Nome Pagina]]` per i link interni di Obsidian.
Per link a sezioni specifiche: `[[Nome Pagina#Sezione]]`.

### Riferimenti alle Fonti RAW
Usa il nome breve della pagina source: `[[source-theater-level-campaign-model]]`

### Relazione con Warfare-Model
Quando un concetto o entità ha **diretta applicabilità** al progetto Warfare-Model in sviluppo, aggiungi una sezione `## Applicabilità al Warfare-Model` con note specifiche su come integrarlo.

---

## Indice Rapido dei Comandi

| Comando utente | Azione Claude |
|----------------|---------------|
| `ingesta [file]` | Workflow di ingestione completo |
| `query: [domanda]` | Ricerca e sintesi dal wiki |
| `health check` | Verifica integrità del wiki |
| `panoramica` | Legge e riassume `wiki/overview.md` |
| `aggiorna [pagina]` | Aggiorna una pagina specifica |
| `nuova entità: [nome]` | Crea pagina entità da zero |
| `nuovo concetto: [nome]` | Crea pagina concetto da zero |
| `confronta [A] vs [B]` | Crea analisi comparativa |

---

## Note Operative

- **Inizia sempre** ogni sessione leggendo `wiki/log.md` (ultime 10 voci) e `wiki/index.md`
- **Non modificare mai** i file in `RAW/` — sono la fonte di verità
- **Aggiorna sempre** `index.md` e `log.md` dopo ogni operazione
- **Usa Obsidian** come IDE per visualizzare il wiki — l'utente lo tiene aperto mentre lavora
- **Stile**: italiano tecnico, preciso, senza ridondanze; le citazioni rimangono nella lingua originale
- **Finestra di contesto**: su wiki grandi, leggi `index.md` prima di caricare le pagine complete; prioritizza le pagine più recenti e rilevanti
