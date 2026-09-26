---
name: feedback-parallel-agents-verification
description: "How to run multiple des-developer/analysis agents in parallel safely in this repo, and always verify their reports independently before committing"
metadata:
  type: feedback
  originSessionId: b183e431-8211-4d82-bd56-aecf65301f45
  modified: 2026-09-26T21:39:28.576Z
---

Confirmed working well in a very long session (2026-09-26, 4 agents in parallel at one point): launching
multiple `des-developer`/general-purpose agents at once on **non-overlapping files** is safe and fast in
this repo, even mid-session with a lot of uncommitted work already in the tree.

**Why**: agents don't commit (project convention, only the main session commits on explicit request), so
even if two agents' scopes turn out to touch the same file, nothing is lost — but always check `git
status`/`git diff --stat` yourself before trusting a "no conflict" claim in a report, and before
committing anything.

**Independent verification before committing** — do this every time, don't just trust the agent's self-
reported test count:
- `git stash list` (should be empty) + `git status --short` to confirm nothing was lost, especially if a
  report mentions using `git stash`/`git checkout`/any destructive-adjacent command mid-task.
- Re-run the full suite yourself (or the specific changed file's tests at minimum) rather than only
  reading the agent's "Ran N tests, OK" line — this caught nothing wrong in this session, but is cheap
  insurance, and once a fabricated/rounded test count would otherwise go straight to a commit.
- Read at least the core new module/function the agent added, not just the diff stat — this surfaced no
  problems here but is worth the ~1 min it costs.

**A des-manual-writer agent correctly self-corrected for parallel drift**: when it detected a large
uncommitted diff clearly belonging to *other* concurrently-running agents (not yet handed back), it
anchored all its documentation to the last real commit (`git show HEAD:...`) instead of documenting an
unstable/moving working tree, and explicitly flagged in its report which sections would need a second
pass once that other work landed. This is the right behavior to expect/ask for explicitly in a prompt
when several agents run at once and one of them writes documentation.

**Caution, not yet a hard rule**: one `des-developer` agent used `git stash`/`git stash pop` on its own
initiative mid-task to compare old vs. new behavior. It restored cleanly (verified: `git stash list`
empty, working tree intact) and briefly took the user's own uncommitted files along with it in the
stash — no harm done here, but this is exactly the kind of operation `git status` should be run before
*and after*, and a future agent prompt for a similar comparison task should probably say "don't use git
stash for this, copy the file / use a throwaway branch instead" if the coordinator wants to avoid the
risk outright.
