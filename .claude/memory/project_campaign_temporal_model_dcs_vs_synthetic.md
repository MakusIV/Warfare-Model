---
name: project-campaign-temporal-model-dcs-vs-synthetic
description: "Core architecture decision (not yet implemented): campaign event generation splits into real-time DCS game-session events vs. synthetically-generated events for the assets a real campaign involves but a DCS session can't; turn structure for the synthetic side is still to be designed"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9980c40e-9dcc-4a07-8d4b-87c43a9d4e36
  modified: 2026-09-08T16:37:53.330Z
---

**Decision/framing (user, 2026-09-08):** the campaign's temporal model must distinguish two categories of event source, handled differently.

## 1. DCS game-session events (real-time, human-played)
- A DCS session is structured as a set of missions, each defined by: assets involved, routes assigned, roles, targets.
- During the session, events unfold in real time describing everything that happens to the assets involved (engagements, losses, mission outcomes, etc.) — these are the results of actual real-time confrontations.
- **Hardware constraint**: a DCS session can only involve a small fraction of the assets a real military campaign would actually have active simultaneously — this is a computational/HW limit of the DCS engine, not a modelling choice.

## 2. Synthetic/simulated session events
- Because of the DCS asset-count limitation above, the model needs a **synthetic session generator**: a component that synthetically produces the volume/kind of events that would occur in a real campaign if the full (realistic) number of assets were involved, for the time unit being considered (fraction of a day, day, fraction of a week, etc.) — i.e. it extrapolates beyond what the small DCS-played subset covers.
- Workflow after each DCS session concludes:
  1. Acquire/ingest the DCS session's results.
  2. Run the synthetic session simulator to generate the events resulting from involving the realistic (full) asset count for that time unit.
  3. Combine the two: apply weights to (a) the DCS session's event results and (b) the specific results attributable to the human players who took part in that DCS session, versus the synthetic session's output — to compute the results for the campaign's time unit and/or game phase.

## The open design question (deferred to next session)
DCS sessions already provide their own results directly (real-time human confrontation outcomes) — no turn structure needed there. **What still needs to be defined is the temporal turn structure for the synthetic/simulated side** — how simulated (non-DCS-played) events are organized into turns/impulses over the campaign's time unit. This is the natural next design topic, and connects directly to [[reference_philip_sabin_simulating_war]]'s Force/Space/Time/Command framework and Igo-Ugo turn-design discussion (see also [[reference_wiki_llm_simulation]] for where that research lives/will live) — that material was being explored specifically because of this open question.

**How to apply:** any future design or implementation work on campaign turn/time structure (Fase 3 and beyond) must address these as two distinct pipelines feeding into the same per-time-unit result, not a single unified event stream. Likely touches [[project_campaign_persistence]] (`Campaign_State` snapshots, currently indexed by `mission_id` — may need to also key/aggregate by campaign time-unit once this model exists) and [[project_mra_state]] (`Air_Resources_Assigner`, which currently allocates resources at the single-mission level, not yet at the synthetic full-campaign-scale level this model implies).
