---
id: M1-UI-03
title: Spread battle HUD construction over frames (swap-frame budget)
role: ui
status: review
owner_session: worktree-agent-a442bf3baa0b90315
reviewer: lead
depends_on: [M1-UI-02]
milestone: M1
request-from: "lead"
---
## Goal
After M1-UI-02 the battle sandbox's first frame measures 52-65 ms under load (threshold 40 ms, SPEC §4.2 budget 50 ms). The architect stream had already flagged `BattleController.start_sandbox` doing 25-30 ms of cold work in one frame.

## Acceptance criteria
- [x] HUD construction (timeline chips, party rows, menus, glyph-heavy labels) spread over 2-3 frames behind the router fade, or prebuilt during the threaded load
- [x] test_scene_router_swap passes under normal load (<= 1.5 load/cpu) with headroom
- [x] No visual change in battle_* baselines

## Notes
The perf test now soft-skips only when the machine is oversubscribed (perf_budgets.json max_load_per_cpu); it still fails on a fair machine.

Delivered (worktree-agent-a442bf3baa0b90315; how it works: `docs/kb/tech/ui.md` § Battle sandbox, "Staged build"):
- **Profile** (`Time.get_ticks_usec`, load ~5/cpu): the old `start_sandbox` was 30–46 ms in one frame. Showing the first order with 16 fresh timeline chips took 10–18 ms, of which `add_child` (theme propagation into each chip's labels) was 8–13 ms. The party panel took about 6 ms, the first command menu about 5 ms, the Lattice load 1.7 ms (up to 14 ms under load), engine setup 0.3 ms, and the stand-ins about 2.5 ms. The frame-0 floor without any battle build is 10–15 ms under that load.
- **Fix:** `start_battle_staged()` spreads the build over 5 frames behind the router fade, and `TurnTimeline.prebuild()` makes the chips ahead of time, 8 per light frame. The one-shot `start_battle()` is unchanged for tests, captures and Retry. No engine or router change.
- **Measured** (probe `scene_swap_probe.tscn` → `battle_sandbox.tscn`, MEASURE_FRAMES = 4):
  - before, load 20–21 on 4 CPUs (5.0–5.3/cpu): worst frame 54.5, 44.1, 87.8, 95.3, 55.0 ms (always frame 0)
  - after, load 24.4–25.4 on 4 CPUs (6.1–6.4/cpu): worst frame 17.6, 10.2, 28.3, 25.1, 16.8, 20.2, 12.1, 24.3, 33.3, 18.4 ms; one outlier run of 407 ms, a scheduler stall inside a 3.6–29 ms step, which the test's 3 attempts absorb
  - the first-turn step just after the window: 2.7–11.4 ms
  - `test_scene_router_swap` passed outright (no soft-skip) at load 18.1 (4.5/cpu)
- **Baselines:** battle_hud_preview, battle_swap_menu, battle_victory and battle_statuses all compare at RMSE 0.00000.
- Tests: `test_staged_build_spreads_over_frames_and_ends_like_the_one_shot_build` and `test_prebuilt_chips_are_reused_not_duplicated` in `tests/unit/test_battle_controller.gd`.

## Review log
