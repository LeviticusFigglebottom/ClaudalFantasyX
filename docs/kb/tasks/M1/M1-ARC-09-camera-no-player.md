---
id: M1-ARC-09
title: Camera director works without a player; missing aim_node is loud
role: architect
status: review
owner_session: "worktree-agent-a35fbca43cd81575b"
depends_on: [M1-ARC-07]
reviewer: cinematics
milestone: M1
request-from: "cinematics"
---
## Goal
Leftover ARC-05 review items noted by M1-ARC-07, needed before the first cutscene sequencer lands.

## Acceptance criteria
- [x] FieldCameraDirector.update() applies shot poses and emits blend_finished when no player node is present (a cutscene staged without the player)
- [x] A shot whose aim_node is missing logs an error (or fails validation) instead of silently framing the player
- [x] Unit tests for both (no-player: test_no_player_still_applies_shots_and_lands, M1-ARC-07)

## Notes
See M1-ARC-07's handoff docs/kb/handoffs/2026-10-23-architect-7.md.
- 2026-10-23 architect: the no-player AC was done in M1-ARC-07 (review-sweep-D S2a). What remains is the loud aim_node miss, plus its test.

- 2026-10-23 architect (worktree-agent-a35fbca43cd81575b): a missing `aim_node` is now `push_error` (naming the shot, the path and the rail root) rather than a warning, once per shot, and is recorded in `FieldCameraDirector.missing_aim_nodes()`. The fallback is unchanged: the player, or `look_at` with no player. Test: `test_missing_aim_node_is_loud_once_per_shot` (a Logger counts exactly one error over many evaluations, and a found aim_node is not reported). field_camera.md is updated.

## Review log
- 2026-10-23 cinematics (review-sweep-F, fresh reviewer): **approve.** I read 5ab8bf3 (the `subject_node` change, `missing_aim_nodes`, and `test_missing_aim_node_is_loud_once_per_shot`), the no-player path in `update()` (field_camera_director.gd:289-322) and the fallbacks in `aim_point`, `dolly_progress` and the orbit centre. Godot: `--filter=camera_director` 33 run, 0 failed.
  - **AC1 is met** (M1-ARC-07 S2a). With no target, the volumes are skipped, and the shot is evaluated, applied and lands.
  - **AC2 is met.** A missing `aim_node` is a `push_error` naming the shot, the path and the rail root (:406-413), once per shot, and the shot is recorded in `missing_aim_nodes()`. The fallback is still the player, or `look_at` with no player. field_camera.md:44 says so.
  - **AC3 is met.** The test counts exactly one error over many evaluations, and confirms a found aim_node is not reported.
  - Nit: `_aim_warned` is keyed by shot and never cleared. If a cutscene evaluates a shot before its actor is instanced, and the actor is then added, the shot stays in `missing_aim_nodes()` and the error has already fired, although the shot now frames correctly. Either clear the entry when the node is found, or document "instance actors before the first `play_shot` that aims at them".
