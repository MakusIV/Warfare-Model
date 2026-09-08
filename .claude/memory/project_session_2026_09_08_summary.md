---
name: session-2026-09-08-summary
description: "Sabin/wargaming research session — methodological reference saved, memory-vs-wiki boundary and transfer procedure defined, core DCS-vs-synthetic-events campaign architecture recorded"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9980c40e-9dcc-4a07-8d4b-87c43a9d4e36
  modified: 2026-09-08T16:39:40.765Z
---

Research + design-discussion session, no code changes. Three threads:

**1. Philip Sabin (KCL) wargame-design research.** Researched Sabin's conflict-simulation methodology as a possible reference for campaign/route time modelling — read his book structures (*Simulating War*, *Lost Battles*) and the full text of his paper "Modelling Time in Wargames" (2020, fetched and read in full, cached locally but **not yet saved into the repo/RAW** — still just a WebFetch tool-cache file). Saved as [[reference_philip_sabin_simulating_war]]: the Force/Space/Time/Command framework, turn-granularity tradeoffs, the four ways to handle "stop-go" campaign intensity (incl. points-based strategic-turns/action-impulses), and Sabin's defended case for Igo-Ugo (overlapping player-turn halves: plan/react then execute) including why sea/air is the hard case (leapfrog second-mover advantage).

**2. Memory-vs-wiki boundary and transfer procedure.** User raised the risk of dysfunction between this project's auto-memory (implementation facts) and `Analysis/WIKI_LLM_SIMULATION` (conceptual simulation-theory wiki, merged in 2026-08-20). Defined and saved as [[reference_wiki_llm_simulation]]:
- Both layers should be consulted, neither outranks the other by default (revised from an initial "consult the wiki first" framing the user correctly pushed back on — project memory/implementation reasoning can matter more than general wiki theory).
- Verified on disk that no separate Claude Code memory space exists for a session opened inside `Analysis/WIKI_LLM_SIMULATION/` — confirming the desired asymmetry (wiki doesn't see project implementation memory) already holds structurally, without extra work.
- Defined the transfer procedure for moving session research into the wiki: no separate session needed (file tools aren't cwd-scoped, only auto-memory is); sort session output into 3 buckets — primary sources → `RAW/` + normal `ingesta` workflow, secondary/web sources → **full snapshot into `RAW/web/` before ingestion** (user's explicit choice, not bare URL citation), already-synthesized analysis → straight into `wiki/analyses/`.
- Flagged that [[reference_philip_sabin_simulating_war]] itself is a temporary boundary violation (conceptual content sitting in project memory) — deliberately deferred, to be slimmed to a pointer once transferred to the wiki at Fase 3 resumption.

**3. Core campaign architecture — DCS vs. synthetic events.** User described a fundamental modelling split not previously captured anywhere: saved as [[project_campaign_temporal_model_dcs_vs_synthetic]]. DCS game sessions produce real-time human-played events but can only involve a small HW-limited fraction of a real campaign's assets; a synthetic session generator must extrapolate the events a full realistic asset count would produce for the same time unit; results are combined with weights (DCS event results + human-player-specific results vs. synthetic output) into the time-unit/phase result. DCS needs no turn structure (real-time already gives results); **the turn structure for the synthetic side is still undefined — explicitly the next design topic**, and is exactly why the Sabin research (thread 1) was being pursued.

**Why:** user is doing upfront conceptual groundwork before resuming Fase 3 implementation (`Ground_Route_Manager.py`), and wants the two knowledge systems (project memory, wiki) to stay coherent rather than silently diverge as this groundwork accumulates.

**How to apply:** next session's natural starting point is designing the synthetic-events turn structure, using [[reference_philip_sabin_simulating_war]] as a direct input and [[project_campaign_temporal_model_dcs_vs_synthetic]] as the framing. Note: an untracked file `Analysis/Document/Appunti struttura turno evento simulato` appeared in the working tree during this session (not created by the assistant) — likely the user's own notes on this exact topic; worth checking at the start of the next session.
