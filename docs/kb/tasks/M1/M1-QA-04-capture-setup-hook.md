---
id: M1-QA-04
title: Screenshot capture: per-shot setup hook
role: qa
status: done
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
- 2026-10-23 rendering (review-sweep-I, fresh reviewer): **approve-with-fixes.** No blockers.
  - **What I read:** the task, handoff qa-1, `git log -p` for capture.gd, capture_setup.gd, compare.py and test_screenshots.py (merge ae733de), and docs/kb/qa/screenshots.md "Per-shot setup".
  - **Checks:** Godot `--filter=capture_setup` 7 run, 0 failed. Tool tests 359 OK. `compare.py --manifest-only` runs in ci_local. No shot in shots.json has a `setup` yet, so baselines are untouched by construction.
  - **What passes:** an absent setup is a no-op (begin, attach, hold and end all change nothing). Every failure path calls `end()`, so `Engine.time_scale` and the viewport are restored even when the shot errors. A typo fails the shot: an unknown key, node, property or global. Type coercion refuses a mismatch. Globals are typed from the project.godot declaration. The hold priority (`1 << 20`, capture.gd:18 and :25) beats per-frame rig writes, which the measurement confirms (hymn_wind_time 80: 0.079).
  - **Should-fix:**
    - **S1 (hold order is not "last write").** capture_setup.gd:103-120 runs in `_process`. SceneTree processes Tweens *after* node `_process`, and `AnimationPlayer` in physics or manual callback modes and `RenderingServer.frame_pre_draw` callbacks can also write later. A held property that a Tween animates is overwritten every frame. The docs (screenshots.md "Hold order") promise "the last write before each frame is drawn". Either re-apply on `RenderingServer.frame_pre_draw` as well, or document the Tween and AnimationPlayer exceptions, and pair `nodes` with `time_scale: 0` for animated properties.
    - **S2 (globals restore to the project default, not the prior live value).** capture_setup.gd:131-133. After a shot with a `setup.globals` entry, the next shot in the same process starts from the project.godot default, not from what the previous scene left. That is arguably cleaner, but it makes results depend on which shots a `HYMN_SHOTS` subset runs together. State in screenshots.md that capture scenes must not rely on globals inherited from an earlier shot (rigs that set their globals in `_ready` are fine).
  - **Nits:**
    - `coerce` passes unknown types through, so a `nodes` value for a Transform3D or Basis property fails only at `_set_prop`'s type check, with a generic message. Fine, but list the supported JSON shapes in the docs table.
    - `time_scale: 0` also freezes physics. Mention it beside "frame-counting rigs keep counting".
    - The M1-RND-13 request (move the rigs off `CAPTURE_SCENE`) is the real payoff. Please keep it on the board.
- 2026-10-23 lead: closing on review-sweep-I approve-with-fixes; the Tween ordering and global restore are in M1-QA-06.
