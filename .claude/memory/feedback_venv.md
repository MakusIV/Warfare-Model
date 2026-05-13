---
name: Usare venv per esecuzione Python
description: Tutti i comandi Python devono usare venv/bin/python3, non python3 di sistema
type: feedback
---

Usare sempre `venv/bin/python3` per eseguire script e test in questo progetto.

**Why:** Il progetto è definito in un ambiente virtuale (venv); le dipendenze e i moduli sono installati lì.
**How to apply:** Ogni volta che si esegue `python3 -m unittest` o qualsiasi script Python, anteporre `venv/bin/`.
