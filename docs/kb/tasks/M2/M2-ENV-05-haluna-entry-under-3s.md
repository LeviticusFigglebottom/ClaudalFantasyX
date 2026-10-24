---
id: M2-ENV-05
title: Haluna's zone entry takes 3.1-3.5 s, over ADR 0029's 3 s (instance and prebuild 1.6-2.1 s)
role: environment
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
reviewer: rendering
depends_on: []
milestone: M2
request-from: "rendering"
---
## Goal
The slice perf sweep (docs/kb/qa/gpu/2026-10-24-slice-perf-sweep.md, RX 9070 XT, 1440p) measured Haluna's entry,
from the change request to the scene being in, under the opaque fade:
- **The whole entry:** 3.1 s at High, 3.5 s at Low and 3.1 s at Ultra, against ADR 0029's 3 s zone-entry limit
  (SPEC v1.3 §4.2). The worst single frame, 0.5 s, is fine.
- **SceneRouter's `last_swap_stats`:** `instantiate_ms` is 1570–2050 on the worker thread, and HalunaZone's
  prebuild runs inside it. `prewarm_ms` is 470–490, on top of the threaded load.

## Acceptance criteria
- [ ] Haluna's entry is under 3 s on Low, High and Ultra (measure with
      `tools/gpu_bench/slice_sweep.tscn -- --segments=haluna_beach`).
      Candidates: cache or bake what the prebuild computes at runtime, or split it so part runs after the fade lifts
      without visible frames over 50 ms.
- [ ] No visible frame over 50 ms afterwards (the same tool's `visible_max_ms`).

## Notes
- 2026-10-24 m2-slice, **for review by rendering. The 3 s criterion needs the PC to re-measure** (`tools/gpu_bench/slice_sweep.tscn -- --segments=haluna_beach`).
- **Profiled the prebuild** (headless, this 4-CPU cloud box, shared with another agent's Blender job) at about 1.65–1.8 s. The biggest part was not the dressing:
  - `HalunaActorPose.assign_materials`: about 920 ms per entry. Asha's ~25 material textures (about 18 MB) decode on every entry, because they leave the cache when the zone frees.
  - Terrain: 330–430 ms. Collision: 130–250 ms. Pieces, plants and scatter: about 150 ms. Water: about 35 ms.
- **Three changes, none of which changes a value:**
  - The cast's materials load on the loader's threads (`request_materials`, `load_threaded_request`) while prebuild dresses and builds collision; `assign_materials` collects them.
  - The terrain fills mesh rows in parallel (WorkerThreadPool group task, one holder object per row; identical values and order).
  - The walk collision reads the terrain's cached core heights (`grid_height`: exactly `height_at` at those grid points, at the heightmap's 32-bit precision) instead of recomputing about 52,000 samples.
- **Measured locally:** prebuild **1.65 s → 0.94 s** (−43%, three runs each). On the PC that should bring the 1.6–2.1 s `instantiate_ms` to about 0.9–1.2 s, so the 3.1–3.5 s entry lands under 3 s. To be confirmed there.
- **Tests:** `tests/integration/test_haluna_entry_cost.gd` checks the heights' exactness and that the threaded material assignment still lands on every surface. The haluna and fp_ suites are green.

## Review log

## Lead routing (2026-10-24)
Routed to the **m2-slice** track, which owns Haluna (game/levels/ch02/haluna/**). M1-ARC-16's router now reports `max_visible_frame_ms`, the hidden frames and the entry time, in `SceneRouter.last_swap_stats`; use them to verify. Don't use threaded loads: they crashed Haluna (ADR 0029).
