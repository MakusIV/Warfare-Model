---
name: feedback-combat-power-action-selection
description: "User's design direction for which action/task to use when comparing combat power in priority calc — use 'Attack' specifically for attack-priority ratio, not a sum/average across tasks; also wants a per-action priority list for later tactical decisions"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 68a4bcf0-0d82-4d78-95f3-8034f1d81a8d
  modified: 2026-09-17T16:52:19.695Z
---

Use the **'Attack' task specifically** (not a sum/average across all tasks of the force) when computing the combat-power ratio that drives *attack* priority in `Region._calculate_priority` (see [[project_priority_calc_combat_power_redesign]] for where this applies — Fase 0 used a sum-over-all-tasks stand-in that the user now says is wrong).

**Why:** the user wants the attack-priority number to mean something specific and legible: *high priority = the block has a clear combat-power advantage over the target; low priority = no advantage (or a disadvantage)*. Summing/averaging across unrelated tasks (Defense, Maintain, Retrait) dilutes that signal into something that doesn't cleanly answer "should I attack this target."

**How to apply:** when picking which `action` to pass to `Military.combat_power(force, action)` inside the attack-priority path, use the force's 'Attack' task (`GROUND_ACTION['Attack']` / `Sea_Task.ATTACK.value` — for air there's no literal 'Attack' in `AIR_TASK`, that mapping is still unresolved, flag it explicitly rather than guessing).

**Broader idea to keep in mind (not yet scoped/designed):** the user also wants to eventually compute a **separate priority value per action** — not just Attack, but also Retrait, Defense, and Maintain — for ground/sea blocks. The idea: these per-action priorities become *inputs* to a later decision layer that picks the actual action to assign to a block, using additional tactical/strategic context not yet part of this calculation (asset availability, overall campaign orientation/posture, morale, etc.). So the near-term redesign should produce a small *vector* of priorities (one per relevant action) rather than a single scalar, even though only the Attack one is being fixed right now. Don't implement the full multi-action vector without discussing scope first — this note is to make sure it isn't forgotten when `_calculate_priority`/`_calc_attack_priority`/`_calc_defense_priority` are revisited.

**2026-09-17 update:** this "per-action priority vector" is now confirmed to be the same concept as the "indirizzo strategico" in [[project_c2_hierarchy_design]] — a per-region, per-domain (air/ground/sea) Attack/Maintain/Defense/Retreat orientation driven by morale, loss stats, production/reserves. Implement together with that design, not separately.
