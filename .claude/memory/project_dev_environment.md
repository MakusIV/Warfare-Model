---
name: project-dev-environment
description: "Three-machine dev setup, git remote, memory sync workflow, per-machine venv/direnv paths"
metadata: 
  node_type: memory
  type: project
  originSessionId: 54069b25-fc3b-495d-81bb-9efd11133381
  modified: 2026-08-16T16:08:33.619Z
---

## Machines
Three machines: **VM** (VirtualBox Ubuntu), **Notebook** (Ubuntu), **ProArt P16** (Asus, WSL2 Ubuntu 26.04 su Windows 11 Pro).

## Git
- Remote: `git@github.com:MakusIV/Warfare-Model.git` (SSH) — ProArt P16 usa SSH confermato 2026-06-28

## Memory sync
- Memory lives in repo: `Warfare-Model/.claude/memory/` — tracked by git
- On all machines: `~/.claude/projects/-home-marco-Sviluppo-Warfare-Model/memory/` → symlink to repo folder:
  ```bash
  ln -s ~/Sviluppo/Warfare-Model/.claude/memory ~/.claude/projects/-home-marco-Sviluppo-Warfare-Model/memory
  ```
- Sync workflow: `git push` at end of session → `git pull` on other machines

## Python environment per machine
See [[feedback_venv]] for which interpreter path to use.
- **ProArt P16 (2026-06-28):** direnv 2.37.1 + Python 3.12.13 (deadsnakes PPA); `.envrc`: `layout python python3.12`; venv at `.direnv/python-3.12/`; hook in `~/.bashrc`. The classic `venv/` folder present in the repo on this machine is stale/broken (its `python3` symlink resolves to system Python 3.14, missing project dependencies) — always use `.direnv/python-3.12/bin/python3` here.
- **VM/Notebook:** venv classico in `venv/` (escluso da git tramite `.gitignore`)
