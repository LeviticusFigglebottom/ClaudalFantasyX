# 0111 — Hero bodies load on worker threads behind the fade and stay resident

- **Status:** proposed (the Lead's 2026-10-28 09:35 item 1; Systems Architect and Hero motion to accept)
- **Date:** 2026-10-28
- **Roles affected:** Tech (SceneRouter), Hero motion (HeroFieldActor, the battle stand-ins), Rendering (prewarm, ADR 0029), UI (title)
- **Author role:** ui-menus

## Context
ADR 0029 allows no hidden frame over 1 s. The PC's big14 walk measured four scene changes over it, each in one hidden
frame: New Game 3.0 s, Ch2 2.0 s, the first fight 1.7 s and Ch1 1.3 s (`docs/kb/qa/gate-runs/big14/README.md`).

The cloud box profiled the swap frame headless, so with no renderer at all.
- **Ch1 (Oruvel Underway):** 1.9 s, of which 1.6 s is `FieldController._ready`.
- **Ch2 (Haluna):** 4.6 s, of which 2.4 s is `FieldController._ready`.
- **Inside it:** `HeroFieldActor.attach` takes 1.6–2.6 s and `FieldHud.attach` 15–19 ms.

`attach` builds the leader's body, the followers and the cutscene-stage heroes. Each does
`load()` on a hero scene, which reads it from disk on the main thread, inside the swap frame. With the six hero scenes
already cached, `attach` takes 6–15 ms. The battle stand-ins load the full battle actor scenes the same way. Shader work
is not the cost: the frame is as long with the dummy renderer.

## Options
1. Hero motion makes `attach` incremental: one body per frame after the zone is in. That spreads the frames but still
   reads from disk on the main thread (about 1 s per hero on the cloud box).
2. **Load the hero scenes on worker threads as soon as a change starts. Hold the swap until they are in, and keep
   them for the session.** The zone's `load()` then hits the cache, and later changes pay nothing.
3. A chapter card or a longer fade. That only covers the stall: ADR 0029 counts a frozen hidden frame all the same.

## Decision
Option 2.
- **`ResidentLoads`** (`game/core/resident_loads.gd`) is installed on SceneRouter the way ShaderPrewarm is.
- **When a change starts:** SceneRouter emits `change_started(scene_path)` as `change_scene()` begins, before the fade.
  ResidentLoads then calls `ResourceLoader.load_threaded_request` for each scene in `game/data/ui/resident_loads.json`
  and holds the swap (`hold_swap`, at most `PREWARM_WAIT_MAX_FRAMES`) until they're in. It keeps every loaded scene.
- **Which scenes:**
  - every field body (`hero_motion.json` `field.heroes`, the lod1 models);
  - the battle actors of the party and the default leader (`battle_sandbox.json` `stand_ins`);
  - a change to boot (the title) starts the loads without a hold.
- **The title** calls `warm()` as it shows, so New Game finds the heroes loaded, or nearly.
- **Headless runs (the test suite)** skip it unless a test opts in (`ResidentLoads.run_headless`). Otherwise every
  test's `change_scene` would wait on six hero loads.
- **Threaded loading:** ADR 0029 rejected it for the prewarm stage (Haluna crashed 3 of 6 runs). The router already
  loads every scene this way, and these are plain model scenes, not a zone with build scripts.

## Measured (cloud box, headless, through SceneRouter: worst hidden swap frame)
| Change | Before | With ResidentLoads |
|---|---|---|
| Ch1 (Oruvel Underway) | 1911 ms | 251 ms |
| Ch2 (Haluna) | 3386 ms | 964 ms |

These were cold first changes, with no title warm-up. The cold Ch1 entry took 7.3 s while the six loads ran beside the
scene load: over ADR 0029's 3 s entry budget. In the game the title's `warm()` runs first and closes that. The PC's
next walk (windowed, real GPU) is the measurement that counts.

## Consequences
- The hero bodies stay in memory for the session: six lod1 field models plus the party's battle actors.
- **Entry time.** On a cold New Game straight from launch, the entry can be longer: the swap waits on the loads, but in
  short frames. The title's warm-up usually finishes first. `entry_ms` (ADR 0029, 3 s) shows whether it does.
- **Not covered here.** What remains in Haluna's swap frame is the zone's own build: `haluna_zone.gd` 0.8–0.9 s and
  `HalunaMood/Dresser` 0.9–1.1 s on the cloud box. If the PC still measures Ch2 over 1 s, that is first-playable's and
  env-art's to slice.
- **Not measured yet.** The first fight's arena and creature scenes are not in the list. The PC's next walk will show
  whether the hero actors were the cost.
