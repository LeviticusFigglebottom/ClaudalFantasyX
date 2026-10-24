---
id: M2-RND-07
title: The Drownbell's Flood phase is a visible 39-61 ms frame mid-battle (at risk of the 50 ms limit)
role: rendering
status: doing
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: combat
depends_on: [M2-RND-04]
milestone: M2
request-from: "rendering"
---
## Goal
The slice perf sweep (docs/kb/qa/gpu/2026-10-24-slice-perf-sweep.md) forced the Drownbell's Flood phase mid-battle.
- **The worst frame:** 39–44 ms on Low, High and Ultra, and 61 ms in a trial run (the first Flood in its process).
  It's visible, and over SPEC §4.2's 50 ms at its worst.
- **Likely cause:** the polyps joining (`combatants_joined`: their models' and spawn_wound lights' first draw) and
  the flood rig's first rise (BattleBossVfx, M2-RND-04). These aren't in the battle's prewarm.

## Acceptance criteria
- [ ] Find which draw costs the frame (`tools/gpu_bench/drownbell_probe.tscn` or the sweep's `drownbell_flood`),
      and warm it with the battle: polyp models in the prewarm registry, or staged at battle start.
- [ ] The Flood's worst visible frame is under 33 ms on Low, High and Ultra, cold and warm.

## Review log
