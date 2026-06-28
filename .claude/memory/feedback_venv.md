---
name: Usare venv per esecuzione Python
description: Come attivare/usare il venv su ciascuna macchina del progetto
type: feedback
---

Il venv varia per macchina — usare sempre il percorso corretto.

**VM e macchine con venv classico:** `venv/bin/python3`
**ProArt P16 (WSL2, direnv):** direnv gestisce il venv automaticamente in `.direnv/python-3.12/`; dopo `direnv allow`, `python3` e `pip` nel terminale puntano già al venv corretto. Per eseguire senza attivazione esplicita: `.direnv/python-3.12/bin/python3`.

**Why:** Dalla sessione 2026-06-28, il ProArt P16 usa direnv con `layout python python3.12` invece del venv manuale. Il vecchio `venv/` è stato rimosso dal tracking git tramite `.gitignore`.
**How to apply:** Su ProArt P16 non serve anteporre `venv/bin/`; sulle altre macchine sì (finché non migrano a direnv).
