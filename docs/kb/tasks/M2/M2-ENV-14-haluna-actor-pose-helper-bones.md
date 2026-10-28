---
id: M2-ENV-14
title: "HalunaActorPose: pose the heroes' helper bones after the placeholder pose"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M1-CHR-15]
milestone: M2
request-from: "character"
reviewer: character
priority: normal
---
## Goal
M1-CHR-15 gave Asha skirt-panel bones and every hero shoulder-corrective bones. The clips carry them baked, but a
pose set by hand does not move them. `game/levels/ch02/haluna/haluna_actor_pose.gd` (`HalunaActorPose.apply()`) sets
Asha's beach kneel with `world_pose`, so until it calls the solve her skirt hangs at rest while her raised thigh goes
through it.

## Acceptance criteria
- [x] After the `world_pose` loop in `apply()` (and before the ground lowering), call
      `HeroHelperBones.drive(skeleton)` (game/characters/hero_helper_bones.gd). One line; it is a no-op for a
      skeleton without helper bones. It costs a fraction of a second once, so it is fine in `prebuild()`'s thread.
- [ ] The Haluna kneel viewed: the skirt drapes over the raised knee.

## Notes
- The character stage does the same (`AshaStage._apply_pose`, game/levels/_tests/characters/asha/asha_stage.gd).
- The solve's parameters are game/data/characters/helper_bones.json; `tests/unit/test_hero_stage.gd`
  checks it matches the clips' baked keys.

- **2026-10-27 (env-art):** `HeroHelperBones.drive(skeleton)` is called in `apply()` after the `world_pose` loop,
  before the ground lowering (`haluna_actor_pose.gd` is m2-slice's file; a one-line change routed here by this task).
  The kneel isn't viewed from this session (no captures here): Character, check it on the next render of H05 or the
  beach shot.

## Review log
