---
id: M3-CRB-009
title: "Request (creatures-b): play a boss model's `intro` clip in BattleBossIntro, and start boss intro/phase VFX at the model's vfx_* anchors"
role: combat
status: todo
owner_session: ""
reviewer: art
depends_on: []
milestone: M3
request-from: creatures-b
---
## Goal
Every Act I boss model gains an `intro` clip (its display while the camera holds on it) and unweighted anchor bones `vfx_wound`, `vfx_core`, `vfx_phase` (M3-CRB-002..007). Ask: (1) BattleBossIntro plays `intro` on the boss's CreatureActor (`has_clip(&"intro")` then `play_clip`) when the camera starts in, falling back to nothing; (2) the boss's phase-change and intro VFX spawn at `vfx_phase` / `vfx_core` through creatures' CreatureActor.vfx_anchor (M3-CRE-651) once it lands, the stand-in heights otherwise. No data key needed: the clip and bone names are the contract.

## Review log
