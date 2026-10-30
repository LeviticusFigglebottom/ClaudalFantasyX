---
id: M4-A2P-1201
title: "Request: battle effects for the Ch14 and Ch16 people fights' 13 foe skills"
role: combat
status: todo
owner_session: ""
depends_on: [M4-A2P-1200]
reviewer: rendering
milestone: M4
request-from: cinematics
---
## Goal
To battle-presentation (tools/vfx/gen_act2_ability_vfx.py; game/data/vfx/battle/effects.json `map.skills`).
act1-chapters built the three Act II fights that audio pre-wired (M4-A2P-1200): `ch14_water_steps`,
`ch14_malcor_venn` and `ch16_abiding_guard`. test_battle_act2_ability_vfx needs an effect for each of their foe skills.
The design sheets' VFX column is the brief: plan/act2/bosses/malcor_venn.md §4, abiding_guard.md §4, and act2
ch14.md §4.
- **Malcor Venn:**
  - `venn_sentence`: a cold line across the water, no glimmer.
  - `grapnel_line`: the line stays taut.
  - `rod_sweep`: `boss_sweep`.
  - `still_hand`: the `target` shot.
  - `level_guard`: guard.
  - Nothing about him may show motes or held light.
- **The flat-engine:**
  - `flat_pulse`: the water pressed flat in a ring, the window held bright (bound light, its only light).
  - `engine_churn`: the paddles lifting, no effect.
- **The Abiding Guard:**
  - `hook_sweep`: `boss_sweep`.
  - `hook_draw`, `hook_thrust`, `close_ranks`: no light.
  - `storm_bearing`: protect, and they never look at the sky.
- **The Court Stillguard:** `seize_the_line`. Its covered form `seize_blow` is staged on the coverer, and
  `haft_strike` is Act I's and already mapped.
- ADR 0204's no-ice rule covers Ch12–Ch15, so the two Ch14 fights' effects carry no salt-glass or moon-blue swatches.
  Ch16's are free of it.

## Acceptance criteria
- [ ] test_battle_act2_ability_vfx has no gap for these skills (the conduit crawler's are M3-BPR-445).

## Review log
