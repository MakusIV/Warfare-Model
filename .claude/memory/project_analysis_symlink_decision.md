---
name: project-analysis-symlink-decision
description: "RESOLVED (2026-08-17) — chose Option C: Obsidian installed natively on ProArt P16's Ubuntu/WSL2. Analysis/ stays git-tracked at its normal repo path, no symlink, no untracking."
metadata: 
  node_type: memory
  type: project
  originSessionId: 099579cf-e95a-48b7-9ac1-c44140b93f3a
  modified: 2026-08-17T08:46:16.826Z
---

**DECISION (2026-08-17): Option C chosen, implemented, and confirmed working on ProArt P16.** Installed Obsidian 1.13.7 (amd64 `.deb`, ~103MB) directly on Ubuntu/WSL2 via `sudo apt install -y <path-to-deb>`. Binary at `/usr/bin/obsidian`, confirmed via `dpkg -l` / `apt list --installed`. WSLg was already active (`$DISPLAY=:0`, `$WAYLAND_DISPLAY=wayland-0`, `/mnt/wslg` present) so no extra setup needed for GUI launch. `Analysis/` was **not** moved or touched — stays git-tracked at its normal path inside the Warfare-Model repo, synced across all 3 machines exactly as before. User confirmed: app opens, `Analysis/` opens correctly as a vault.

**Two follow-up issues hit during first launch, both resolved, keep for future installs on VM/Notebook:**
1. `error while loading shared libraries: libasound.so.2` — the `.deb` doesn't pull in ALSA as a hard dep. Fix: `sudo apt install -y libasound2t64` (or `libasound2` on older Ubuntu).
2. First-run console message `Ignored: Error: ENOENT ... /home/marco/.config/obsidian/<hash>.json` — harmless, Obsidian's own log says "Ignored"; it's looking for a window-state file that doesn't exist yet on first launch and self-recovers. Not a real problem, don't chase it if it reappears once on VM/Notebook's first launch too.

**Why this over the alternatives:** Option B (open the WSL-native folder via `\\wsl.localhost\...` from Windows Obsidian) was tried first and failed outright — compatibility problem, not just performance. Option A (untrack from git + symlink to `/mnt/c`, WIKI_LLM_*-style) was analyzed in depth and found to have a sharp edge: pushing the untracking commit and pulling it on VM/Notebook would **physically delete** `Analysis/` from their working trees (git applies "no longer tracked" as a real file deletion on clean checkouts), not just stop syncing it silently. That risk, plus the loss of automatic sync it implied, made Option A and the "double copy" idea both worse than just installing the app itself.

**Remaining work if the user wants Analysis/Obsidian usable on the other two machines too:** repeat the same native install (~102MB `.deb`, no WSLg needed there since VM/Notebook are plain Linux, not WSL2) on VM (VirtualBox Ubuntu) and Notebook (Ubuntu). Not done yet — only ProArt P16 has it as of 2026-08-17. See [[project_dev_environment]] for the three-machine list.

**Note on `sudo` in this environment:** Claude Code's Bash tool has no TTY, so `sudo` prompts fail even via the `!` interactive-passthrough prefix — user had to run the install command in a real external terminal, not inside a Claude Code session (any flavor). Keep this in mind if future work needs `sudo` on any machine: always hand the exact command to the user to run themselves outside the tool.
