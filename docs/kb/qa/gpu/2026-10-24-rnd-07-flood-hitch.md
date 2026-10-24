# M2-RND-07: the Drownbell's Flood mid-battle hitch (2026-10-24)

Machine: RX 9070 XT, Godot 4.6.3, 2560×1440. Branch `gpu/m2-rnd-07-flood-hitch`. Tool: `tools/gpu_bench/slice_sweep.tscn
-- --segments=tideline_battle,drownbell_battle,drownbell_flood --flood-trace`, which prints the Flood's first 12
frames. Diagnosis options: `--flood-variant=no_boss_vfx|warm_<effect>`.

## Finding the frame

| Variant (High, warm) | The Flood's worst frame |
|---|---:|
| As it was | 42.6–44.5 ms |
| Without the set piece (`BossVfx` freed) | 7–8 ms |
| `polyp_rise` played once earlier in the fight | 2.0 ms |
| Its emitter built earlier, never emitted | 7.6 ms |
| A turbulent emitter of *another* effect built first (`hit_fire` layer 1) | 0.5 ms for `polyp_rise`'s build |

**The cause.** BattleVfx builds its pooled GPUParticles3D on an effect's first play. The first emitter of a
ParticleProcessMaterial feature set (turbulence on) cost **31–32 ms** of synchronous main-thread work. A second
emitter of the same effect cost 0.0 ms; another, non-turbulent effect 0.5 ms.

**What I tried first, staging the emitters in the router's prewarm:** no gain. That was a registry "provider" whose
emitters were drawn in the stage and whose process materials were held for the session; the Flood still cost
35–44 ms. The cost is the emitter's, in the battle's own tree, so it was reverted.

## The fix

`BattleVfx.prebuild()`, called from `attach()`, builds one pooled emitter per layer of every particle effect, without
emitting. It runs in the frame the battle scene enters, under the opaque fade. Nothing plays, and the first play takes
the prebuilt emitter (tested).

| | Low | High | Ultra |
|---|---|---|---|
| The Flood's worst frame, warm (editor binary) | 1.7 ms | 1.8 ms | 1.7 ms |
| The Flood's worst frame, fresh install (release build) | 1.8 ms | 1.8 ms | 1.8 ms |
| Before | 39 ms | 44 ms | 41 ms (release, cold: 79) |
| Tideline entry: worst hidden frame / whole entry, fresh install | 521 / 1315 ms | 542 / 1376 ms | 605 / 1396 ms |
| Drownbell entry, fresh install | 348 / 929 ms | 362 / 976 ms | 348 / 1003 ms |
| Visible frames after either battle's fade | ≤ 10.3 ms | ≤ 10.3 ms | ≤ 9.5 ms |

- **The criterion is met:** under 33 ms on Low, High and Ultra, cold and warm.
- **The cost moved to the battle's hidden entry.** The worst hidden frame went from about 105–300 to 350–605 ms,
  under ADR 0029's 1 s; the entries stay under 1.4 s, against 3 s.
- **That's more than the ~45 ms I estimated.** Each feature set's first emitter costs about 30 ms, and the effects
  span several.

## Checks

- **Run:**
  - gdlint and gdformat on the touched files.
  - The Godot `battle` filter (412/0; new test `test_prebuild_makes_every_particle_emitter_without_playing`).
  - The tools unittests, validate_data and `taskboard --check`.
  - The GPU runs above, editor binary and release build (`Windows Perf`).
- **Skipped:** screenshots. The prebuilt emitters don't emit, so no frame changes.
