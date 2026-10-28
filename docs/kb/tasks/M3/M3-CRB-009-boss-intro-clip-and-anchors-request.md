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
- 2026-10-28 (creatures-b), two more asks seen in a self-render of ch08 `undertows_reach` at the default battle camera
  (scratchpad render, not a shot): (3) the Reach's hand fills the frame beside the party and crowds the camera; seat it
  further back or frame that encounter wider (the model can't move itself: creatures.json stand_in has no offset key).
  (4) **The Fisher Stair** (the set-piece target) draws as a white **capsule** beside the party: a placeholder in Act I
  (ADR 0041). It needs a real stand-in (a stair marker or prop; env-art's M3-BPR-407 arena request may cover it).
