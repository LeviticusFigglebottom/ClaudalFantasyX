---
id: M1-RND-13
title: Move test rigs' capture detection into shots.json setup
role: rendering
status: done
owner_session: "worktree-agent-aa764c62452184711"
depends_on: [M1-QA-04]
milestone: M1
reviewer: qa
request-from: "qa"
---
## Goal
M1-QA-04 added a per-shot `setup` block to `tests/screenshots/shots.json`, covering globals, node properties, viewport properties and `time_scale` (`docs/kb/qa/screenshots.md`, "Per-shot setup"). The rigs can now drop their `CAPTURE_SCENE` checks and their camera-to-mood detection: `water_test_rig.gd`, `undertow_test_rig.gd`, and (Environment) `haluna_mood.gd`.

## Acceptance criteria
- [x] Each affected shot declares its holds in `setup`: `hymn_wind_time`, `"viewport": {"use_taa": false, "screen_space_aa": 1}`, the storm clock, and the mood as an exported property.
- [x] The rigs no longer test `scene_file_path == CAPTURE_SCENE`.
- [x] Every affected shot still compares at RMSE 0.0, or any change is justified and re-approved after a look.

## Notes
- QA measured on `water_shallows`: `"globals": {"hymn_wind_time": 40.0}` reproduces the rig's own hold exactly (RMSE 0.0).

- 2026-10-23 rendering (worktree-agent-aa764c62452184711), to review (qa):
  - The 13 water_*, undertow_* and haluna_* shots carry `setup`: `globals.hymn_wind_time` 40.0 (each rig's start
    time), `viewport` `use_taa` false + `screen_space_aa` 1 (FXAA), and for water/undertow `nodes["."].mood`
    (`day`/`night`, `dusk`/`eye`/`night`/`dusk_low`). The undertow shots also hold `Storm.playing = false` (the
    storm clock stays at the mood's time).
  - `water_test_rig.gd`, `undertow_test_rig.gd` and `haluna_mood.gd` no longer test `CAPTURE_SCENE` or swap the
    viewport AA. The water and undertow rigs gained an exported `mood` (empty = follow the camera, as before, for
    opening the scene by hand). `undertow_test.tscn` no longer saves `playing = false` (the rig used to force it
    on); the storm plays by default and the bench / ghost_check still stop it themselves.
  - **Byte-identical:** all 13 shots (and the 3 veg shots) render the same PNG bytes before and after this change
    on this lavapipe. Against the committed baselines the pre-existing drift is unchanged (water_horizon 0.00507,
    water_night 0.00306, undertow_* <= 0.00031, the rest 0.0), so nothing was re-approved.
  - Docs: qa/screenshots.md (migration done), tech/water.md and tech/undertow.md.

## Review log
- 2026-10-23 qa (review-sweep-L, fresh reviewer): **approve.** No blockers.
  - **What I read:** `git show` 16eeb32: water_test_rig.gd, undertow_test_rig.gd, haluna_mood.gd, undertow_test.tscn and shots.json. I also read capture.gd's setup hold (:16-31, :84-126).
  - **Checks:** no `CAPTURE_SCENE` is left in the three rigs. The rigs still write `hymn_wind_time` every frame, but capture.gd runs at `HOLD_PRIORITY` after every node and re-applies `setup.hold()`, so the shot's pinned 40.0 wins each frame. That is why the renders are byte-identical. The `mood` exports default to empty, so hand-opened scenes behave as before. No shots re-run: the author reports 16/16 byte-identical before and after, and the Lead's full gate covers the baselines.
  - **Nit:** undertow_test.tscn no longer saves `playing = false`, so the storm plays when the scene is opened by hand. The bench and ghost_check stop it themselves. Anything else that instances the scene for a still (a future cinematic previs) must hold `Storm.playing` itself. Add a line to undertow.md Gotchas.
- 2026-10-23 lead: closing on review-sweep-L approve; the should-fixes are in M1-NIT-02.
