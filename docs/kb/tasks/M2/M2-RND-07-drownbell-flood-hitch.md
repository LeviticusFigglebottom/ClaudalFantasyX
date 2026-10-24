---
id: M2-RND-07
title: The Drownbell's Flood phase is a visible 39-61 ms frame mid-battle (at risk of the 50 ms limit)
role: rendering
status: done
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
- [x] Find which draw costs the frame (`tools/gpu_bench/drownbell_probe.tscn` or the sweep's `drownbell_flood`),
      and warm it with the battle: polyp models in the prewarm registry, or staged at battle start.
- [x] The Flood's worst visible frame is under 33 ms on Low, High and Ultra, cold and warm.

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
Report: `docs/kb/qa/gpu/2026-10-24-rnd-07-flood-hitch.md`.
- **The cause.** The first emitter of a turbulent ParticleProcessMaterial feature set costs 31–32 ms of main-thread
  work when it's built in the battle's tree; `polyp_rise`'s first play built it mid-fight.
- **What didn't work:** a staged prewarm of the emitters, with their materials held for the session. Tried, no gain,
  reverted.
- **The fix.** `BattleVfx.prebuild()` at attach (under the fade) builds every effect layer's first pooled emitter,
  without emitting.
- **Result.** The Flood's worst frame is 1.7–1.8 ms on Low, High and Ultra, warm and on a fresh-install release
  build (was 39–44, and 79 cold). The battle entries' worst hidden frame rose to 0.35–0.6 s, and the entries take
  0.9–1.4 s: inside ADR 0029.

## Review log
- 2026-10-24 review-sweep-R (environment): **approve.** The cause is pinned down by trace: the first turbulent ParticleProcessMaterial emitter costs about 32 ms of main-thread work in the battle tree. The staged prewarm was tried, gave nothing, and was reverted. `BattleVfx.prebuild()` runs at `attach`, under the router's opaque fade, and builds one pooled emitter per layer of every particle effect (28 today) without emitting. `polyp_rise` is among them in effects.json. The Flood's worst frame is 1.7–1.8 ms on Low, High and Ultra, warm and in a fresh-install release build, against the 33 ms target. Battle entries stay inside ADR 0029 (hidden 0.35–0.6 s). Test added in `test_battle_vfx.gd` (`--filter=battle_vfx` 8/0). The two re-approved battle shots differ only in particle phase and were viewed (8009387).
