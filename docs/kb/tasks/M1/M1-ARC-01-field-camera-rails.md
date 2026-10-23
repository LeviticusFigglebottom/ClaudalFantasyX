---
id: M1-ARC-01
title: Field controller and camera-rail volumes
role: architect
status: review
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
