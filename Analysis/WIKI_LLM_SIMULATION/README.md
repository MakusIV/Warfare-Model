# Wiki LLM — Modelli di Simulazione Bellica

Una base di conoscenza wiki gestita da LLM, specializzata in modelli di simulazione e sviluppo del [Warfare-Model](../Warfare-Model/).

## Ispirazione

Basato sul modello proposto da Andrej Karpathy in [llm-wiki.md](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Utilizzo

1. **Apri questa cartella in Obsidian** per visualizzare il wiki
2. **Apri Claude Code** in questa stessa cartella
3. Lavora con Claude usando i comandi definiti in `CLAUDE.md`

### Comandi principali

| Comando | Descrizione |
|---------|-------------|
| `ingesta [file]` | Elabora una nuova fonte da RAW/ |
| `query: [domanda]` | Poni una domanda al wiki |
| `health check` | Verifica integrità del wiki |
| `panoramica` | Riassumi lo stato attuale |
| `confronta [A] vs [B]` | Analisi comparativa |

## Struttura

```
├── CLAUDE.md          ← Schema e istruzioni per il LLM
├── README.md          ← Questo file
├── RAW/               ← Fonti grezze (immutabili)
├── wiki/              ← Wiki gestita dal LLM
│   ├── index.md       ← Catalogo contenuti
│   ├── log.md         ← Registro operazioni
│   ├── overview.md    ← Panoramica del dominio
│   ├── entities/      ← Modelli, sistemi, autori
│   ├── concepts/      ← Metodologie e tecniche
│   ├── sources/       ← Riepiloghi fonti
│   └── analyses/      ← Analisi e confronti
└── Istruzioni/        ← Documentazione di progetto
```

## Fonti RAW Disponibili

- `The Theater-Level Campaign Model.pdf`
- `simulationtechniquesinthemodellingofpastconflicts.doc`
