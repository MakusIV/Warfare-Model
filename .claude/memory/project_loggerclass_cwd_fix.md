---
name: project-loggerclass-cwd-fix
description: "LoggerClass/Utility.py os.getcwd()-logs bug fixed 2026-08-25 (commit 9a7342a1, pushed). Also: numpy2/matplotlib ABI conflict fixed on the 'osboxes' machine, and a still-open mpl_toolkits/Axes3D shadowing issue needing user sudo."
metadata:
  type: project
  originSessionId: unknown
  modified: 2026-08-25T16:09:50.432Z
---

**The systemic risk flagged in [[project_fase2_design_decisions]] and [[project_module_audit]] is now fixed.** Commit `9a7342a1`, pushed to `origin/main` on 2026-08-25.

## What changed
- `LoggerClass.py:28-31` and `Utility.py:26-29` both computed their log directory as `os.getcwd()/logs` — any module crashed with `FileNotFoundError` if run with cwd != repo root. Both now anchor to `__file__` (4 levels up from `Code/Dynamic_War_Manager/Source/Utility/`) and call `os.makedirs(log_dir, exist_ok=True)`.
- `visualizer.py`'s `os.chdir()` workaround in `__main__` (added earlier to route around this same bug) is now redundant and was removed.
- Verified by instantiating `Logger` with cwd forced away from repo root — resolves to the real repo `logs/` correctly. Full suite re-run clean after the fix.
- This is a pure code fix, anchored to `__file__` (identical on every clone) — safe and portable to the other 2 machines (VM/Notebook, ProArt P16) once they `git pull`. No behavior change for the documented always-run-from-repo-root convention.

## Separate, machine-local finding: numpy2/matplotlib ABI break (fixed only on this machine)
While re-running the suite to verify the fix above, `Test_Air_Route_Manager` failed to import with a NumPy 1.x/2.x ABI error — unrelated to the LoggerClass fix, caused by `matplotlib 3.8.2` (pre-dates numpy 2.0 support) installed alongside `numpy 2.2.6`, both as `pip install --user` packages in `~/.local/lib/python3.10/site-packages` on **this machine** (hostname `osboxes` — no `venv/` or `.direnv/` found here, contradicting [[feedback_venv]]'s assumption that VM/Notebook use a classic `venv/`; this machine runs project deps straight off system `python3` + user site-packages instead. Worth checking whether `osboxes` **is** the documented "VM" or a machine not yet in [[project_dev_environment]]).

Fixed here via `pip install --user --upgrade matplotlib` (pulled in `matplotlib 3.10.9`, and pip's resolver incidentally downgraded `numpy` to 1.26.4 to satisfy a stale `contourpy 1.2.0` pin, breaking `opencv-python>=2`'s numpy>=2 requirement — corrected by `pip install --user --upgrade "numpy>=2" contourpy`). End state: `numpy 2.2.6`, `matplotlib 3.10.9`, `contourpy 1.3.2`, `pip check` clean (aside from an unrelated pre-existing `py7zr`/`pycryptodome` gap). Full suite: 2316 tests green (2268 + `Test_Air_Route_Manager`'s 48, which takes ~4.5 min stand-alone due to heavy debug-print volume in its multi-threat recursive pathfinding tests — not a hang, just slow).

**This is entirely local to this machine's Python environment — it does not propagate via git and was not checked on VM/Notebook/ProArt P16.** `requirements.txt` pins no versions, so the other machines may or may not hit the same conflict; if `Test_Air_Route_Manager` ever fails to import there with a numpy/matplotlib ABI error, apply the same upgrade there.

## mpl_toolkits/Axes3D shadowing — RESOLVED 2026-08-25
`from mpl_toolkits.mplot3d import Axes3D` (needed by `visualizer.py`'s 3D plots) used to resolve to a stale system-level `python3-matplotlib 3.5.1` (apt package, `/usr/lib/python3/dist-packages`) instead of the pip-installed 3.10.9, because the apt package's `mpl_toolkits/__init__.py` is a *regular* package while the pip one is a namespace package — Python's import resolution lets a regular package found later in `sys.path` win over a namespace portion found earlier. Fixed on this machine (`osboxes`) by the user running `sudo apt-get remove python3-matplotlib python-matplotlib-data` (note: package is `python-matplotlib-data`, **no** `3` — the first attempt used the wrong name and apt silently removed nothing). Verified: `mpl_toolkits.mplot3d` now resolves to `~/.local/lib/python3.10/site-packages`, 3D figure creation works end-to-end. Same caveat as above: local to this machine only, not checked on VM/Notebook/ProArt P16.
