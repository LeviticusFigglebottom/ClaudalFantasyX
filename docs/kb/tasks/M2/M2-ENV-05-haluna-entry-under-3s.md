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
