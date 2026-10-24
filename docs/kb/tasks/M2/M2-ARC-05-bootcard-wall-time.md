---
id: M2-ARC-05
title: BootCard measures its hidden frames from the process delta, which Godot caps at ~150 ms
role: architect
status: todo
owner_session: ""
reviewer: rendering
depends_on: [M2-ARC-03]
milestone: M2
request-from: "rendering"
---
## Goal
Found by M1-RND-29 (docs/kb/qa/gpu/2026-10-24-rnd-29-first-launch.md).
- **The cap.** Godot caps the process `delta` at about 140–150 ms, on 4.6.3 and 4.7.2: a 500 ms stall reports
  135–147 ms.
- **The effect.** `BootCard._process` feeds `step(delta * MSEC_PER_SEC)`, so the launch's
  `reveal_wait_max_frame_ms` reads ~149 ms whatever the real worst frame is. The perf build's sweep measured 1266 ms
  on that launch, by wall clock.
- **Where else.** ShaderPrewarm had the same problem; it now uses `Time.get_ticks_usec` (M1-RND-29). The router's
  swap and reveal loops already use wall time.

## Acceptance criteria
- [ ] BootCard measures each frame by wall clock (`Time.get_ticks_usec` between frames), not `delta`, for its wait
      stats and its ADR 0029 warnings. Keep `step(frame_ms)` for tests.
- [ ] A test pins it: a stalled frame (e.g. `OS.delay_msec(400)`) shows in `reveal_wait_max_frame_ms` at ≥ 400 ms.

## Review log
