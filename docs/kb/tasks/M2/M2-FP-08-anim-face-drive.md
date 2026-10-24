---
id: M2-FP-08
title: Drive @anim and @face onto real clips and face shape keys when the rig has them
role: architect
status: done
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M2-FP-01]
milestone: M2
request-from: lead
---
## Goal
The sequencer plays body clips by name already; add idle/talk/walk defaults, and blend `@face` to shape keys on the actor's meshes when keys matching emotion ids exist (otherwise record only, as now). M2-FP-07 asks Character for the clips.

## Acceptance criteria
- [x] `@face actor expr sec` blends matching blend shapes on the actor's MeshInstance3Ds over sec; a line's [emotion] does the same.
- [x] While an actor is moved by `@mark` a `walk`/`run` clip plays if present; on their lines `talk`, otherwise `idle`.
- [x] Tests with a synthetic rig (an ArrayMesh with blend shapes and an AnimationPlayer).

## Review log
- 2026-10-24 review-sweep-Q (character): **approve.** `@face` and line emotions blend matching shape keys, `walk`/`talk`/`idle` clips play when present, and rigs without them are left alone. `test_cutscene_face.gd` tests all three on a synthetic ArrayMesh and AnimationPlayer rig. M2-FP-18 builds on it. `--filter=cutscene`: 33/0.
