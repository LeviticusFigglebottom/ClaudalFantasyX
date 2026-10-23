---
id: M1-UI-03
title: Spread battle HUD construction over frames (swap-frame budget)
role: ui
status: todo
owner_session: ""
depends_on: [M1-UI-02]
milestone: M1
request-from: "lead"
---
## Goal
After M1-UI-02 the battle sandbox's first frame measures 52-65 ms under load (threshold 40 ms, SPEC §4.2 budget 50 ms). The architect stream had already flagged `BattleController.start_sandbox` doing 25-30 ms of cold work in one frame.

## Acceptance criteria
- [ ] HUD construction (timeline chips, party rows, menus, glyph-heavy labels) spread over 2-3 frames behind the router fade, or prebuilt during the threaded load
- [ ] test_scene_router_swap passes under normal load (<= 1.5 load/cpu) with headroom
- [ ] No visual change in battle_* baselines

## Notes
The perf test now soft-skips only when the machine is oversubscribed (perf_budgets.json max_load_per_cpu); it still fails on a fair machine.

## Review log
