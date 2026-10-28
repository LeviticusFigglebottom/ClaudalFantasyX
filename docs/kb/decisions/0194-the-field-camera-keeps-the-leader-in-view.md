# 0194 — The field camera keeps the leader in view

- **Status:** accepted
- **Date:** 2026-10-28
- **Roles affected:** systems (FieldCameraDirector), environment (zone shots and spawns), cinematics (scripted shots unaffected), hero motion (followers)
- **Author role:** qa (integration-qa, the hero-integration track; assigned the field camera by the PC's real-GPU Act I QA)

## Context
SPEC §6.6 gives the field a directed camera: authored shots picked by volume, no free orbit. The PC's real-GPU Act I
QA (docs/kb/qa/act1_gpu_qa.md, rows 21, 37 and 38) and the human's playtest found the player losing sight of Rhen in
three ways:
- a follower walking straight behind him stands on the camera's line to him and hides him (Haluna's start, the
  causeway);
- a drawn wall stands between a shot's camera and him (Coilspire's spire shell, a hub orbit pressed against it);
- a shot's camera faces away from a spawn inside its volume (the causeway's C07 at BeforeHarrier).

Collision is the wrong judge of "a wall the player sees". Coilspire's shell collider misses the part of the shell
that hides him, while invisible bounds and greybox walls hidden for a cutaway have colliders nobody sees.

## Options
1. Leave framing to each zone's authors and catch problems in GPU passes. This is slow, and every new spawn can
   regress.
2. Pull the camera in when collision blocks the line to him. This is the usual spring arm, but it would pull in for
   invisible bounds (Haluna's beach shot sits outside them on purpose) and miss Coilspire's shell.
3. Pull the camera in when a drawn mesh blocks the line to him, tested by its triangles. Keep followers off the line
   to him. Report shot-versus-spawn mistakes to their owners through a guard test.

## Decision
Option 3:
- **FieldCameraDirector.clear_view**, for volume shots only (scripted cutscene shots are composed and left alone):
  - when a drawn wall (`view_blocker`) stands between the camera and the leader's chest, the camera slides in along
    its line to him, at once, to `margin_m` short of the wall;
  - it eases back out at `release_mps` once the view is clear, and comes no nearer him than `min_distance_m`;
  - a wall is any MeshInstance3D at least `min_size_m` across with no transparent surface, the leader's own body
    aside, tested by its cached TriangleMesh;
  - tuning lives in `game/data/world/field_camera.json` "occlusion".
- **HeroFieldParty.sight_clear**: a follower's spot that falls on the camera's line to the leader (within
  `sight_clear_m`, short of him) steps aside off it.
- **The guard** `tests/integration/test_qa_field_camera.gd`, at every Act I spawn, checks that the leader is in frame,
  not walled off and not covered. Mistakes in a zone's own shots or spawns go to their owner as KNOWN rows with a
  request task (M3-HER-1156, M3-HER-1157).

## Consequences
- A shot can no longer lose the leader behind scenery, whatever the shot's position. Authors still own composition:
  a pulled-in camera is a fallback, not a framing, and the guard reports spawns that need a better shot.
- Each frame costs one AABB test per occluder mesh, plus a native triangle test for the few the segment's box
  touches. Occluders are collected on snap() (zone load, teleport); a mesh added later counts from the next snap.
- A large mesh with a transparent surface (foliage, water, glass) never pulls the camera in.
