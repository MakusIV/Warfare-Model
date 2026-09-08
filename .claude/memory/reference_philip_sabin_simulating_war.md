---
name: reference-philip-sabin-simulating-war
description: "Philip Sabin (King's College London) wargame-design theory as a possible methodological reference for Warfare-Model's campaign/combat modelling — Force/Space/Time/Command framework, Igo-Ugo turn design"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9980c40e-9dcc-4a07-8d4b-87c43a9d4e36
  modified: 2026-09-08T13:36:23.643Z
---

**Layering note (2026-09-08):** this file holds conceptual/methodological content that, per the user's stated boundary (see [[reference_wiki_llm_simulation]]), belongs in the `Analysis/WIKI_LLM_SIMULATION` wiki (entity `philip-sabin.md` already exists there, stale relative to this research), not in project auto-memory. Deliberately kept here in full for now — transfer to the wiki was explicitly deferred to the Fase 3 resumption (see [[project_module_audit]]). **When that transfer happens, slim this file down to a short pointer** (what was researched, when, that it now lives in the wiki) to avoid two divergent copies of the same conceptual material.

## Who / what
Philip Sabin — Emeritus Professor of Strategic Studies, King's College London (Dept. of War Studies, taught 1985–2019, conflict-simulation course from 2003). Co-founder of the King's Wargaming Network (2017). Designed dozens of published/free manual wargames (ancient to modern) and wrote the academic literature on conflict-simulation *design methodology* (not just history) — this is the part potentially useful as a modelling reference for Warfare-Model, not the games themselves.

## Key sources
- **Book**: *Simulating War: Studying Conflict through Simulation Games* (Bloomsbury, 2012) — course textbook, theory + mechanics + worked examples. Structure: Part I Theory (Modelling war, Accuracy vs simplicity, Educational utility, Simulation research), Part II Mechanics (Designing the components, **Modelling conflict dynamics**, **Modelling command dynamics**, Integration and testing), Part III Examples (Ancient, WW2, Tactical combat).
- **Book**: *Lost Battles: Reconstructing the Great Clashes of the Ancient World* (2008) — where Sabin first articulated the **Force / Space / Time / Command** framework as the four interacting variables any conflict model must represent.
- **Paper (full text captured)**: ["Modelling Time in Wargames"](https://paxsims.wordpress.com/wp-content/uploads/2021/01/modelling-time-in-wargames-sabin-4.20.pdf), April 2020 — generalizes the Force/Space/Time/Command framework and gives a detailed, concrete argument for turn-structure design choices (see below). Read in full 2026-09-08.
- Design catalogue with 30+ free wargames and design notes: https://sites.google.com/view/sabinwargames/home
- King's Wargaming Network: https://www.kcl.ac.uk/research/wargaming-network

## The Force/Space/Time/Command framework
Sabin's core modelling claim: any wargame/conflict-simulation must represent four interacting elements. Force and Space are comparatively easy (units on a map — this is what most of Warfare-Model's `Vehicle_Data`/`Aircraft_Data`/`Ship_Weapon_Data`/`Region`/`Route` machinery already does). **Time and Command are the hard, contested parts** — see [[project_module_audit]] Fase 3 (Ground_Route_Manager) for where the project is currently mid-build on the Space side.

## Turn/time modelling techniques (from "Modelling Time in Wargames")
- **Turn granularity tradeoff**: fewer/longer turns → more differentiation between unit speeds, less interactivity; more/shorter turns → more reactivity, longer playtime. No universal right answer — pick per the decision-cycle length of the level being modelled.
- **Equal-length turns** are simplest (fewer subjective judgements, standard intervals for movement/production) but force artificially uniform activity per turn, when real conflict is "stop-go" (bursts of intense action separated by long passive/prep intervals — his go-to example is the WW2 North African campaign).
- **Four ways to handle stop-go variability**:
  1. Scope the sim to only the intense period, ignore the rest (what Sabin does in his own air-combat games).
  2. Make turns long enough to absorb both a flurry and a lull (e.g. seasonal/biannual turns for a WW2 campaign instead of monthly).
  3. Variable-length turns for known slowdowns (night, weather) — simple but deterministic/abstract.
  4. **Points-based activation**: accumulate a stock of supply/command/fatigue points during passive "strategic turns", spend them in bursts of shorter "action impulses" when a side goes active. This is the most direct simulation of *why* intensity varies, and is the technique closest to a resource-budget model.
- **Igo-Ugo (alternating full-force player turns) — Sabin's defended position**: widely dismissed by gamers as artificial/outdated, but Sabin argues it is usually the *best* fit because real land warfare is dominated by sequential attack/counterattack (one side plans+executes an offensive, the other reacts with prepared reserves), not simultaneous symmetric clashes. Key technique: treat player turns as **overlapping in time** (first half of non-phasing player's next turn = planning/reacting to what just happened, second half = execution), rather than as strictly sequential slices — this resolves the "why does the loser just freeze" objection.
  - Reaction-speed asymmetry is modelled *within* Igo-Ugo, not by breaking it: opportunity fire / reserves reacting inside the enemy's own player-turn = fast reaction; delaying a strategic reserve's arrival by several turns = slow reaction. No need for variable turn lengths per side.
  - Alternatives (simultaneous secret plotting à la Kriegsspiel; interleaved unit-by-unit impulses) each carry real costs: plotting has heavy overhead and needs an umpire/AI to resolve clashing orders; impulse activation creates an artificial "spent unit = harmless" state and rewards impulse-by-impulse opportunism over actual planning, unless randomized (which then makes outcomes chit-draw-dependent).
- **Command/decision-cycle framing**: ties directly to Boyd's OODA loop — turn length should approximate how fast the modelled echelon can actually observe/orient/decide/act. Bigger force → slower cascade of planning → longer realistic turn length at that echelon.
- **Sea/air is the hard case for Igo-Ugo**: ships/aircraft have no static "front" and are in continuous motion, so pure alternating movement gives a large, artificial advantage to whichever side moves second (they can dodge or gang up with full knowledge of the first mover's new position). Sabin's fixes: simultaneous plotting (works well operationally/strategically, where uncertainty about enemy location is realistic anyway; poor fit tactically, where real reaction times are shorter than a turn); or accept Igo-Ugo with fire resolved at the *end of each unit's own activation* rather than end-of-turn (works surprisingly well for forward-firing aircraft chasing/covering each other; harder to justify for broadside-firing ships unless turns are short).
- **Default state is passivity**: a recurring modelling point — most forces are static/defensive most of the time; treating "every unit activates every turn because it can" as the norm (common wargame default) understates real inertia. Constraining how many units/how much command bandwidth is usable per turn is itself a more realistic Time/Command model than adding turn-structure complexity.

## Applicability notes for Warfare-Model
See the assistant's 2026-09-08 conversation turn for the detailed mapping of this framework onto `Campaign_State`, `Air_Resources_Assigner`, `Region`/`Route` and the still-open Fase 3 (`Ground_Route_Manager`) — not duplicated here since it is analysis, not a fact about Sabin's work. Re-derive if needed rather than trusting a stale summary.
