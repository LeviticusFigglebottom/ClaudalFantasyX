---
id: M1-ARC-16
title: SceneRouter measures ADR 0029's two budgets (hidden frames under the fade, the first 60 visible frames)
role: architect
status: done
owner_session: "worktree-agent-a30d6e9e3e395d6ec"
reviewer: lead
depends_on: [M1-RND-22]
milestone: M1
request-from: "lead"
---
## Goal
Review-sweep-Q accepted ADR 0029, which makes the 50 ms limit apply to visible frames, among them "the first 60 frames after any fade lifts". Hidden frames get a 1 s limit. The ADR says "the router can measure it (its frame_ms after the fade)", but `SceneRouter._swap` measures `MEASURE_FRAMES` (4) frames right after `change_scene_to_node`, while the screen is still opaque (`_fade_to(0.0)` runs after `_swap`). So:
- `swap_measured` / `last_swap_stats` measure hidden frames, and `_record` warns "over the 50 ms budget" for them, which ADR 0029 no longer calls a hitch;
- nothing measures the visible frames the ADR budgets.

## Acceptance criteria
- [x] Keep the hidden-frame measurement, but judge it against a hidden-frame budget (1 s, as a named constant). Its warning text names that budget.
- [x] Measure the first `VISIBLE_MEASURE_FRAMES` (60) frames after the fade starts to lift and the first after it ends, against `SWAP_BUDGET_MS` (50). Record them in the stats (for example `visible_frame_ms`, `max_visible_frame_ms`, `visible_over_budget`) and warn over budget.
- [x] Tests in test_scene_router_swap.gd for both windows, using an injected clock or frame times, the way `frame0_start` is tested.
- [x] graphics_settings.md or architecture.md documents the two stats. The tools that read `max_frame_ms` (prewarm_bench, gpu_bench) say which window they report.

## Notes
- The SPEC §4.2 wording itself is the Lead's edit (ADR 0029, accepted by sweep-Q), with a SPEC version note.

## Notes (2026-10-24, worktree-agent-a30d6e9e3e395d6ec)
- `game/core/scene_router.gd`, additive: `HIDDEN_FRAME_BUDGET_MS` 1000, `ENTRY_BUDGET_MS` 3000,
  `VISIBLE_MEASURE_FRAMES` 60; `is_measuring()`, `visible_measured(stats)`; static `judge_hidden`, `judge_entry`,
  `judge_visible`; `SceneRouter.VisibleWindow` (timestamps in, so tests inject a clock).
- **Hidden** `frame_ms` / `max_frame_ms` / `over_budget` keep their names; `budget_ms` is now 1000 and the
  warning names "the 1000 ms hidden-frame budget". **Entry** `entry_ms` is `change_scene()` until the fade starts
  to lift, against 3 s. **Visible** is every frame while the fade lifts (`lift_frames`) plus the 60 after it has
  lifted, against 50 ms (`visible_frame_ms`, `max_visible_frame_ms`, `visible_over_budget`, `visible_complete`).
  It finishes after `change_scene()` returns; `is_busy()` is unchanged, and a new change cuts it short.
- Headless probe, boot → battle sandbox: hidden max 9.3 ms, entry 475 ms, 53 lift frames + 60, visible max 11.5 ms.
- Tests: five new in `test_scene_router_swap.gd` (budgets, hidden, entry, visible window by injected clock, a 70 ms
  visible hitch); the probe-driven test also asserts both windows were recorded. `scene_swap_probe.gd` waits for
  `is_measuring()`. Docs: architecture.md "The two measured windows"; prewarm_bench and gpu_bench headers.
- Left alone: `game/levels/ch02/haluna/README.md` quotes a hidden `frame_ms[0]` of 33 ms as "(budget 50)"; under
  ADR 0029 that is a hidden frame (1 s budget). Environment's file; worth a one-line fix by its owner.

## Review log
- 2026-10-24 review-sweep-R (lead): **approve.** Every criterion is in `scene_router.gd`. `HIDDEN_FRAME_BUDGET_MS` (1000), `ENTRY_BUDGET_MS` (3000) and `VISIBLE_MEASURE_FRAMES` (60) are named constants. `judge_hidden` writes `budget_ms` 1000 and its warning names the hidden-frame budget. The visible window (`_measure_visible` with `VisibleWindow`) samples wall-clock frames from the start of the lift through 60 fully-lifted frames and is judged against `SWAP_BUDGET_MS`. A new change cancels it through a generation counter, and `visible_measured` still fires with `visible_complete` false. `VisibleWindow.tick` takes timestamps, so the tests inject the clock. architecture.md has "The two measured windows", and the prewarm_bench and gpu_bench headers say which window they report. `--filter=scene_router`: 16/0. Nit, not filed: the Haluna README's "(budget 50)" for a hidden frame (noted by the task, environment's file).
