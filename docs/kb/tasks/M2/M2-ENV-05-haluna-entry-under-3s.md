---
id: M2-ENV-05
title: Haluna's zone entry takes 3.1-3.5 s, over ADR 0029's 3 s (instance and prebuild 1.6-2.1 s)
role: environment
status: todo
owner_session: ""
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

## Notes (PC GPU, M2-RND-11 item 5, 2026-10-24): why the second launch is slow
Numbers are in `docs/kb/qa/gpu/2026-10-24-rnd-11-sweep-r.md` §5.
- A first run holds every registry entry it stages, so Haluna's set and the cast's character materials stay
  loaded and compiled. After it, Haluna's entry takes 1.5 s. A second launch holds only the resident entries,
  so the worker-thread instantiate loads and compiles them again (1.9–2.2 s against 1.1 s), and the entry's
  harvest reloads them (260 ms against 6 ms): 3.1 s on High and 3.5 s on Low.
- It isn't the scene's other resources: holding or harvesting Haluna's PackedScene at boot barely helps
  (2.7–3.3 s).
- **Measured fix:** make Haluna's 17 registry entries resident, plus the character materials, which
  `gpu/hero-materials-resident` does for Asha's 11. The second launch's entry is then 1.6 s (High) and 1.9 s (Low).
  The cost is 1.3–1.7 s more boot behind the card, with its worst hidden frame at 0.38–0.53 s.

## Review log

## Lead routing (2026-10-24)
Routed to the **m2-slice** track, which owns Haluna (game/levels/ch02/haluna/**). M1-ARC-16's router now reports `max_visible_frame_ms`, the hidden frames and the entry time, in `SceneRouter.last_swap_stats`; use them to verify. Don't use threaded loads: they crashed Haluna (ADR 0029).
- **2026-10-24, rendering (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB): one cause found and fixed, outside the Haluna
  scenes** (`gpu/hero-materials-resident`, Lead-approved).
  - **The cause.** The worker-thread prebuild loads the cutscene cast's materials (`HalunaActorPose.assign_materials`,
    ~0.7 s) unless they're already loaded.
  - **The fix.** Asha's 11 material entries in prewarm_materials.json are `resident` (held from the boot warm-up),
    per preset through `resident_presets`.
  - **Haluna's entry** (launch → title → Haluna, 4.6.3, 1440p, router `entry_ms`):
    - High: 2.94–3.00 s → 2.09–2.33 s.
    - Low: 3.48–3.58 s streaming → 2.31–2.76 s resident. Low streaming is over 3 s, so per the Lead's rule her
      materials are resident on Low too.
  - **The VRAM cost** (texture memory from the title on): Low 285 MB against 39 MB, and High 289 MB against 44 MB.
    Video memory on Low: 464 MB against 189.
  - **What's left** is the dressing itself on the worker thread: 0.65–1.3 s, against 0.37 s on the main thread
    (contention with the fade, fonts and prewarm). A high-priority WorkerThreadPool task helped only within noise.
- **2026-10-24, rendering (PC GPU): the worker-thread dressing is not prewarm contention.** That's the finding for
  m2-slice; I didn't touch the Haluna scenes or scripts.
  - **Prewarm serialized:** with the router's prewarm moved after the instance (a temporary router edit, reverted),
    the dressing still takes 1.0 s on the worker thread. Overlapped it takes 0.7–0.9 s, and the entry is no faster
    (2.24 against 2.07–2.34 s).
  - **The same work off the worker thread** takes 0.37 s (headless, `HalunaZoneDresser.adopt(...).dress()`).
  - **So the 2–3× is the dresser's own work on a worker thread.** The likeliest cause is its RenderingServer and
    resource calls (MultiMesh and mesh building, material and texture loads). From a worker thread Godot routes
    those through its command queue and locks, call by call.
  - **Suggestions:**
    - profile `HalunaDresser.dress()` on the worker (Godot's profiler, or `Time.get_ticks_usec` per pass) to find
      the costly pass;
    - batch per-instance MultiMesh writes into one `multimesh.buffer` assignment;
    - load the dresser's materials and meshes up front (or make them resident like Asha's), not inside the loops.
  - A high-priority WorkerThreadPool task didn't help either.
