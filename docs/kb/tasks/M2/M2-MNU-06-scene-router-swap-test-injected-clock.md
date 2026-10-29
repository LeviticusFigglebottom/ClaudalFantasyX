---
id: M2-MNU-06
title: Scene-router swap test on an injected clock (deterministic, not load-sensitive)
role: architect
status: done
owner_session: "menus (claude/menus)"
depends_on: [M2-ARC-05]
milestone: M2
request-from: lead
reviewer: qa
---
## Goal
test_scene_router_swap::test_swap_frame_stays_under_threshold_for_every_target fails on a loaded or freshly restarted container (hidden swap frames 73-186 ms against 40 ms), also on the integration branch. The Lead asked for the root cause and a deterministic test through an injected clock (FrameClock, the ARC-05 pattern), not a looser tolerance.

## Acceptance criteria
- [x] Root cause named in Notes.
- [x] The test measures with an injected clock and passes under load; no tolerance loosened.
- [x] Own commit; noted in the menus live log for the Lead.

## Notes
- **Root cause:** the test held the hidden swap frames (under the opaque fade: threaded load, instantiate, prewarm, first-use shader and font work) to a 40 ms wall-time threshold. That work scales with machine load and cold caches: 73-186 ms after a container restart or beside other Godot runs, on the integration branch too, while every visible frame stayed near 7 ms and the router's own ADR 0029 verdicts (hidden 1 s, visible 50 ms) were all within budget. The test measured the machine, not the code.
- **Fix:** `SceneRouter.set_measure_clock(now_usec)` (game/core/scene_router.gd) swaps the time source of every window (`_now_usec()`; the FrameClocks are rebuilt on it); default behaviour is unchanged. `scene_swap_probe.gd --frame-usec=<n>` installs `SceneSwapProbe.frame_clock(n)`, n µs per process frame. The test runs each target once on a 16667 µs step and asserts every hidden and visible frame is exactly one step, the threshold, and `over_budget` / `visible_over_budget` / `entry_over_budget` false, plus the existing shape checks. The threshold is unchanged; the attempts loop and the load guard are removed (perf_budgets.json `attempts`, `max_load_per_cpu`).
- **Gates:** `--filter=test_scene_router` 15/15; again 15/15 with six busy loops on 4 CPUs (load 5.1); gdlint/gdformat clean; validate_data 0/0. Docs: architecture.md § the scene swap.

## Review log
- 2026-10-28, integration-qa (architect seat, per the Lead): **accepted.** `SceneRouter.set_measure_clock` and
  `_now_usec()` are in game/core/scene_router.gd. test_scene_router_swap runs each target through scene_swap_probe on
  `--frame-usec=16667` and asserts exact one-step frames and `over_budget` false; the threshold isn't loosened. On
  claude/hero-integration (big15 merged): scene_router 15/0, also with M3-HER-1151's ShaderGlobals hold in
  `_instantiate`.
