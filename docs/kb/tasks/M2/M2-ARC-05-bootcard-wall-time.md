---
id: M2-ARC-05
title: BootCard measures its hidden frames from the process delta, which Godot caps at ~150 ms
role: architect
status: review
owner_session: "agent-a887cc9b547e8d5de"
reviewer: lead
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
- [x] BootCard measures each frame by wall clock (`Time.get_ticks_usec` between frames), not `delta`, for its wait
      stats and its ADR 0029 warnings. Keep `step(frame_ms)` for tests.
- [x] A test pins it: a stalled frame (e.g. `OS.delay_msec(400)`) shows in `reveal_wait_max_frame_ms` at ≥ 400 ms.

## Notes (architect, agent-a887cc9b547e8d5de, 2026-10-24)
- **One helper:** `FrameClock` (`game/core/frame_clock.gd`): `reset()`/`reset_at()`, `lap()`/`lap_at()` (wall ms since
  the last mark, from `Time.get_ticks_usec`), `since_ms()`. A fake clock is injected as `FrameClock.new(callable)`.
- **BootCard:** `_process` ignores `delta` and steps by `clock.lap()` (the clock starts in `_ready`). `step(frame_ms)`
  stays for tests. The wait stats, `MAX_WAIT_MS`, the fade-in and the lift are all wall time now.
- **SceneRouter:** already wall time; its hidden frames, reveal wait and `VisibleWindow` now go through FrameClock
  (no behaviour change).
- **ShaderPrewarm:** left alone. M1-RND-29 (being merged) already moved it to `Time.get_ticks_usec`; putting it on
  FrameClock is a two-line follow-up after that merge, kept out to avoid a conflict.
- Nothing else in `game/` judges a frame against a budget from `delta`; tools/gpu_bench already uses wall time.
- Tests: `tests/unit/test_frame_clock.gd` (7, new); `test_boot_card.gd` +3 (a 500 ms stall handed a 147 ms delta
  reads 500 ms; a real `OS.delay_msec(400)` reads >= 400 ms; the time-out is wall time).
- Docs: architecture.md, "Frame times are wall time, never `delta`".

## Review log
