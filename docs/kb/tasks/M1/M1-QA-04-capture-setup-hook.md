---
id: M1-QA-04
title: Screenshot capture: per-shot setup hook
role: qa
status: review
owner_session: "worktree-agent-aafc786bec1f4e2c5"
depends_on: [M1-QA-01]
milestone: M1
request-from: "rendering"
---
## Goal
A per-shot `setup` dictionary in shots.json (globals, node properties, time) instead of camera-detection hacks in scenes.

## Acceptance criteria
- [x] setup supports shader globals, node property overrides, and a fixed time (plus viewport properties, for the TAA → FXAA swap the rigs do)
- [x] Existing shots unchanged (baselines still pass)
- [x] Documented in qa/screenshots.md

## Notes
- **Reviewer: rendering.**
- `tests/screenshots/capture_setup.gd` (`CaptureSetup`) is wired into `capture.gd`. It supports `globals`, `nodes` (`"."` is the root), `viewport` and `time_scale` (0 = fixed time). Values are held every frame after the scene's own `_process` (capture `process_priority = 1 << 20`) and restored at the end of the shot. Globals return to their project.godot default, because Godot won't read a live global outside the editor. Errors fail the shot. Keys are checked by `compare.py --manifest-only`.
- **Baselines:** no shot has a `setup`, so all 58 run the old path unchanged, and **no baseline changed**. `water_shallows` rendered through the new capture.gd is byte-identical to its baseline (RMSE 0.0). `HYMN_SHOTS=boot_title,battle_hud_preview tools/ci_local.sh` passes.
- **Measured** with a scratch manifest: `hymn_wind_time: 40` matches the water rig's own capture hold (RMSE 0.0); `80` changes the frame (0.079), so the hold beats the rig's per-frame write; `Sun.visible: false` gives 0.28; with `time_scale: 0`, a TIME probe reads 0.016 s after 60 frames, against 1.0 s at scale 1; a misspelt property fails the shot.
- Tests: `tests/unit/test_capture_setup.gd` (7 tests, headless) and 2 new tests in `tools/tests/test_screenshots.py`.
- Moving the rigs off `CAPTURE_SCENE` detection belongs to their owners: request **M1-RND-13**.

## Review log
