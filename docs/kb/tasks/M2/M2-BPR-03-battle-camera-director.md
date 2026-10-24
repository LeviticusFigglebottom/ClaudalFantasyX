---
id: M2-BPR-03
title: Battle camera director with speed, skip and reduced-motion settings
role: combat
status: review
reviewer: lead
owner_session: battle-presentation (claude/battle-presentation)
depends_on: [M2-BPR-01]
milestone: M2
request-from: lead
---
## Goal
Framed shots for an actor's turn, the target, a cast and a finisher, over a readable default, with tactical clarity first (the timeline and HUD are never covered and the default frame returns before input). Accessibility: battle speed, skip animations, reduced motion (cuts, no sweeps), no flashes beyond battle_vfx caps.

## Acceptance criteria
- [x] BattleCameraDirector, listen-only, data in choreo.json
- [x] Default framing returns before every command menu opens
- [x] Battle speed and battle animations settings in accessibility.json (appended rows)
- [x] Reduced motion: no camera travel, no shake
- [x] Tests

## Notes
- Battle-presentation track standing queue (Lead, 2026-10-24). Listen-only presentation: the engine stays headless (CLAUDE.md §3).

- 2026-10-24 (worktree subagent): done. `BattleCameraDirector` (game/battle/scene/battle_camera_director.gd), attached
  by `BattleChoreo.attached` (no controller line); shots in `choreo.json → camera`, validated by
  `tools/validate_choreo.py camera_errors`. Default / actor / target / cast / finisher, plus `push` for enemy actions;
  all framed off one battle axis from the authored default (never crossed, never rolled, no orbit). The camera is a
  pure function of plan time (`BattleChoreo.time()`, new `posed(t)` signal) and lands exactly on the default at the
  sequence end. Reduced motion and skip keep the camera on the default (no cuts). Settings rows `battle_speed` and
  `battle_animations` appended to accessibility.json; loc keys appended to strings.csv. Docs:
  battle_presentation.md § Camera director. Tests: tests/unit/test_battle_camera_director.gd (13).
- **Reviewer focus:** the shot numbers in choreo.json on a real render (only the sandbox geometry was checked, and
  only numerically; no screenshot shows a mid-sequence frame), and the reduced-motion choice (stay on default).

## Review log
