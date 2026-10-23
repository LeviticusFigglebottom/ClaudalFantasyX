---
id: M1-ARC-01
title: Field controller and camera-rail volumes
role: architect
status: done
owner_session: architect-stream-2
reviewer: cinematics
depends_on: []
milestone: M1
request-from: ""
---
## Goal
SPEC §6.6 directed camera.

## Acceptance criteria
- [x] CharacterBody3D field controller (`game/world/field_controller.gd` plus the pure `FieldMotor`). Movement is camera-relative, with an input latch that holds across cuts and blends until the stick is released. Tuning lives in `game/data/world/field_movement.json`.
- [x] Camera volumes blend between authored shots. `CameraShot` supports fixed, pan-follow, dolly along a Path3D by projected progress, and orbit behind the hub flag only, each with FOV and DOF. `CameraVolume` carries the priority, then recency, rule. `FieldCameraDirector` blends with eases or Curves from data, or makes hard cuts.
- [x] Test zone with 3 volumes (`game/levels/_tests/field/field_test.tscn`): lane fixed (H02), court pan (H07), causeway dolly (C02).
- [x] Interactables and touch triggers emit on the EventBus (`field_interacted`, `field_trigger_entered`) and use flags only through `Game.get_flag` and `Game.set_flag`. Two test flags were declared.
- [x] Headless tests: `test_camera_director.gd`, `test_field_motor.gd`, `test_field_controller.gd` and `test_field_interactables.gd`.
- [x] Screenshot baselines `field_lane_fixed`, `field_court_pan` and `field_causeway_dolly`, bit-exact across runs at 30 settle frames.

## Notes
- Delivered 2026-10-22 by architect-stream-2. The reference is `docs/kb/tech/field_camera.md`.
- Volume containment is geometric and polled each update, not driven by physics signals. That makes it deterministic and testable headlessly.
- Off a physics frame (tests and scripted moves), `FieldController.step()` slides with `move_and_collide`, because the physics delta is 0 there.
- Requests: the Lead should declare `field_interacted` and `field_trigger_entered` in `event_bus.gd`, and move the `field_*` actions into `project.godot` if wanted. Both are optional, because the runtime fallbacks already work.
- Reviewer (cinematics): check how the blend eases and the latch feel with a stick, and whether the CameraShot fields cover the Haluna shot list (§5).

## Review log
- 2026-10-23 cinematics (review-sweep-A): **approve with fixes**. The volume selection, blends, cuts and input latch all work as documented. The 472-test suite is green. A headless probe walked the player north with the stick held: the latch engaged at the lane-to-court blend and held at the same reference yaw (8.3°) through to the causeway, and releasing the stick dropped it. For field play this is ready. For cutscenes the director has no entry point yet.
  - **should-fix** (cutscene readiness): there is no public way for a sequencer to take the camera. `update()` re-picks the volume every frame (`field_camera_director.gd:108-111`), so a shot pushed with the private `_activate()` lasts one frame. The probe's history went `[lane_fixed, cutscene_h06, lane_fixed]`. The only workaround is `auto_update = false` plus driving `Camera3D` by hand, which loses blends and DOF. Suggested fix: an override layer, `play_shot(shot, blend_sec, ease)` / `release(blend_sec)`, that suspends volume selection while it is held and blends back to the winning volume on release. I'll open the request from Cinematics when the sequencer task starts. ARC-01's acceptance criteria don't require it, so this doesn't block done.
  - **should-fix** (shot coverage for the Haluna list): every tracking mode aims at `target`, the player. The two-shots and reaction shots in Cutscene A/B (H05, H06, S07, S09) need an aim or track node other than the player (an actor or a mark), and H05 needs a timed crane (0.4 m to 0.9 m on `rhen sit_up`). Suggested fix: add `aim_node: NodePath` to `CameraShot`, and leave timed moves to the sequencer, which needs the override above. FIXED, PAN and DOLLY otherwise cover the field shots (H02, H07, C02, S03 pitched down, C07 tilted up), and `roll_deg` and practical DOF are enough.
  - **nit**: `snap()` doesn't cancel an in-progress blend when the target lands in the shot that is already active, because `_activate` returns early at `field_camera_director.gd:283-285`. Scenario: teleport (F5) or `place_at()` mid-blend into the court. The probe showed `blending=true, weight=0.03` after `snap()`, so a "hard cut" keeps easing from the old shot for up to 1.2 s. Fix: in `snap()`, clear `_blending`, `_previous_shot` and `_from_snapshot`, and set the weight to 1.
  - **nit**: `snap()` emits `shot_changed(hard_cut=true)`, which latches the stick on a teleport to the yaw of a camera that is no longer on screen. Consider skipping the latch for snaps, for example with a `snapped` flag on the signal. A `snap()` outside every volume also keeps the previous zone's shot; `initial_shot` only applies when there is no active shot.
- 2026-10-23 lead: closing on review-sweep-A approve-with-fixes; cutscene camera control is in M1-ARC-05.
