---
id: M3-HER-1156
title: "Saltgrass Causeway: the fixed C07 shot looks away from the BeforeHarrier spawn its volume covers (Rhen behind the camera)"
role: environment
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
The PC's real-GPU Act I QA, row 37 (docs/kb/qa/act1_gpu_qa.md on gpu/act1-qa-2): "at BeforeHarrier Rhen isn't in
frame at all". The new guard `tests/integration/test_qa_field_camera.gd` reports it as "the leader is behind the
camera".

`saltgrass_causeway_layout.json` camera volume **C07** spans x 67.97–83.97, z -55.42 to -39.42 (centre (75.97, 1.5,
-47.42), size 16). It is a **fixed** shot at (75.97, 1.2, -47.42) looking at (85.05, 1.6, -51.63), toward +x and the
Harrier ground. The **BeforeHarrier** spawn, (70.56, -0.05, -44.82), lies inside that volume but about 5 m behind the
camera, so the player arrives with the camera facing away from him.

Either:
- shrink C07 so it starts past the camera (x > ~77), letting C02's dolly frame the spawn;
- make C07 a pan_follow shot from a position behind the spawn; or
- move the spawn in front of the camera.

## Acceptance criteria
- [ ] test_qa_field_camera passes with its `saltgrass_causeway.tscn:BeforeHarrier` KNOWN row removed.

## Notes
Filed by integration-qa. The rest of row 37 (a follower between the camera and Rhen at AfterHarrier and Encounter) is
fixed in HeroFieldParty (sight_clear_m); the guard finds no follower on a camera line at any of 106 spawns. Row 38
(Coilspire's spire wall) is fixed by the director's new occlusion pull-in (field_camera.json "occlusion").

## Review log
