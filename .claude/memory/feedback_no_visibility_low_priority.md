---
name: feedback-no-visibility-low-priority
description: "User's design decision: an undetected/no-visibility target should map to LOW priority, not high (opposite of the naive 'high uncertainty = high priority' framing) — reasoning is about where recon resources were spent, not about risk from the unknown. _target_affinity explicitly stays neutral, unaffected by this."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 68a4bcf0-0d82-4d78-95f3-8034f1d81a8d
  modified: 2026-09-14T14:49:23.302Z
---

# "No visibility" on a target → LOW priority, not high

2026-09-14. The user's first framing of this ("un report vuoto/non rilevato dovrebbe mappare come
un segnale di alta incertezza/alta priorità") sounded like the common wargaming heuristic
"unknown = dangerous, prioritize finding out." **When asked to confirm where this applies, the
user reversed it**: they'd treat "no visibility" as **LOW** priority instead.

**Why (user's own reasoning):** if there's no minimum intelligence/recognition on a target, it
means the recon resources available were spent on more important targets instead. Absence of
recon effort is itself a revealed signal about relative importance — it's not neutral information
starvation, it's an implicit ranking already made by wherever recon allocation happens upstream.

**How to apply:** this is about the Fase 2 fog-of-war `target_cp` estimate for `_calculate_priority`
(see [[project_priority_calc_combat_power_redesign]]) — not yet built, this is the design principle
to use when it is. **Do not** treat an undetected/no-report target as a high-risk/high-priority
signal; treat it as evidence the target is lower priority (or at minimum, don't inflate it).

**Explicitly excluded from this policy — `_target_affinity` stays as-is:** the user was asked
directly whether this should also change `Region._target_affinity`'s existing behavior (empty
target profile → neutral `1.0` multiplier, see [[project_air_priority_target_specific_loadout]]),
and said to keep it neutral. That method answers a different question ("what's the best loadout
against an unknown composition") where neutral-on-unknown is deliberately not a ranking judgment
about the target's importance — don't conflate the two mechanisms again.
