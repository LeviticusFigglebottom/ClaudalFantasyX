---
id: M2-RND-15
title: "Cold first launch: Haluna's first entry within ADR 0029, and the launch's 'visible' 825 ms frame"
role: rendering
status: done
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: environment
depends_on: [M1-RND-29, M2-ARC-08]
milestone: M2
request-from: "lead"
---
## Goal
From the M2-ARC-08 re-measure with every cache cleared, the driver's included
(docs/kb/qa/gpu/2026-10-24-arc-08-first-launch.md):
- Haluna's cold first entry had a 1.6–1.7 s hidden frame, and took 4.4 s on Low. ADR 0029 allows 1 s and 3 s, and
  the first-launch exception covers only the 1.35 s boot frame.
- On cold Low, an 825 ms frame showed up just after the lift, which the router's visible window seemed to miss.

## Acceptance criteria
- [x] Find which pipelines Haluna's cold first entry compiles, and stage them under the boot card. The cold first
      entry is within ADR 0029.
- [x] The 825 ms frame: fix the frame, and the measurement that missed it.

## Notes (PC GPU, 2026-10-24)
**Measured with a new `slice_sweep --pipeline-trace`.** It prints each frame over 50 ms, or with a draw-time
compile, together with that frame's `Performance` pipeline-compilation counts: canvas, mesh, surface, draw and
specialization.
- Haluna's 1.77 s frame compiled **92 surface pipelines and 22 specializations at once**, on the zone's first drawn
  frame.
- They're the surfaces Haluna builds at runtime: the dresser's MultiMeshes, the ocean grid and the cast's
  materials. No SceneState lists them, so the first-run harvest never staged them, and on an empty driver cache
  each costs about 17 ms.

**Fix 1: live scenes in the first run.** The registry gets `first_run_live_scenes` (Haluna) and
`max_live_materials`.
- A first run instances each one on a worker thread, as SceneRouter does, so HalunaZone prebuilds itself off the
  tree and its `_ready` never runs.
- It stages a draw of every mesh, MultiMesh and material the live instance holds, then frees the instance.
- The live scenes start once the regular staging has drained. Started together with it, their instancing landed on
  the boot's heaviest frames (2.9 s against 1.05).

**Item 2: there's no visible 825 ms frame.**
- The sweep's launch wait gave up at its 30 s transition timeout (`hidden total 30,570 ms` over 65 frames), while
  a cold card holds for 30–36 s.
- So the sweep's "visible" 60 frames were the last seconds *under the card*. The SLICE_DUMP of those frames showed
  the first-run stage still drawing Haluna's vegetation and kit.
- The router's window does start at the lift: `measure_reveal` runs when the card opens. Its 17.6–43.7 ms was right,
  so the router isn't changed.
- The sweep now waits up to 300 s for the launch (`LAUNCH_TIMEOUT_S`) and warns `SLICE_TIMEOUT` whenever a wait
  gives up. With that, the cold launch's visible worst is 1.5 ms (the router's own: 43 ms).

**Results** (a baked release, every cache cleared, the driver's included; RX 9070 XT, 2560×1440):

| | Low before | Low after | High before (ARC-08) | High after |
|---|---|---|---|---|
| Haluna's cold first entry: hidden worst / total | 1,771 / 4,426 ms | **637 / 2,312** | 1,607 / 3,767 | **407 / 2,045** |
| Launch: worst hidden frame | 1,581 | 1,606 | 2,890 | 2,894 |
| Card wait (`reveal_wait_ms`) | 30.6 s | 36.1 s | 26.6 s | 30.4 s |
| Launch's visible worst (the sweep / the router) | "825" (under the card) / 17.6 | 1.5 / 43 | 0.7 | 28.1 |

- Haluna's cold first entry is within ADR 0029 on both presets. The cost is 4–6 s more on a cold first launch,
  behind the card.
- The launch's worst hidden frames (1.6 s Low, 2.9 s High) predate this change. They're the renderer's first-use
  pipelines on an empty driver cache, on the first launch only, under the card. That's beyond the 1.35 s exception
  (measured with the driver cache warm in M1-RND-29); for the Lead.

## Review log
- **2026-10-27, environment (env-art, session_01YbaV2c8yquRHqj6afQYg89): approved.**
  - **What was checked:** `first_run_live_scenes` lists Haluna and the shrine (`prewarm_materials.json`), and
    `ShaderPrewarm` stages them off the tree. `--filter=shader_prewarm` 22/0.
  - **Environment's side:** the dresser's runtime MultiMeshes and the ocean grid are exactly what env-art's Haluna
    builds at runtime, so the live-scene harvest is the right fix.
  - **The cold-entry timings** are the PC's measurement. Done.
