---
id: M3-HER-1157
title: "Coilspire Tier4: the hub orbit camera looks at Rhen through the spiral's own steps (they rise above his chest behind him)"
role: environment
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
The PC's real-GPU Act I QA, row 38 (docs/kb/qa/act1_gpu_qa.md on gpu/act1-qa-2): "coilspire spawns SpireBase,
Tier2, Tier4: the field camera is pressed against the spire wall with Rhen out of view".

integration-qa fixed the camera side. FieldCameraDirector now pulls a volume shot's camera in front of any drawn wall
between it and the leader (field_camera.json "occlusion"). That cleared SpireBase, Tier2, PathMid and Gallery
(self-rendered SpireBase: Rhen framed inside the spire base).

**Tier4 remains.** At the Tier4 spawn, (309.56, 66.285, 158.80), facing 290.65°, the mesh between the hub orbit
camera and Rhen is `Dressing/coilspire_tiers/coilspire_tiers`, 0.1 m from his chest. The spiral's steps behind him
rise above his chest, and the orbit sits behind and above him, so no pull-in that keeps 0.6 m from him can get past
them.

Either turn the spawn to face up the spiral, so the orbit camera falls on the open side, or give Tier4 a camera
volume with a shot from the open side (or above the steps).

## Acceptance criteria
- [ ] test_qa_field_camera passes with its `coilspire.tscn:Tier4` KNOWN row removed.

## Notes
Filed by integration-qa. The guard, `tests/integration/test_qa_field_camera.gd`, checks all 106 Act I spawns for the
leader in frame, not walled off and not covered by a follower.

## Notes (integration-qa, 2026-10-30: the PC's GPU QA pass 3, row 38, "Tier4: the camera is inside Rhen's head")
- **The Tier4 spawn stands inside the spiral's step mass.** On big18 plus claude/hero-integration, from the spawn's
  chest point (feet + 1.3 m), a segment in every one of 24 directions (12 around, at chest height and 0.6 m above,
  1.9 and 2.5 m out) hits `coilspire_tiers` within 0.02-0.13 m. Straight up hits it at 0.51 m. His upper body is
  boxed in by the next turn of the spiral, so no camera can see him clearly. **The fix is the spawn:** move Tier4
  to the landing's open side, away from the turn above.
- The camera side is done (integration-qa):
  - deep occlusion cranes up, or looks in from a ring of side spots, instead of pulling the camera into his face;
  - when nothing clears, as here, it keeps the shot's own pose: Rhen seen down the shaft, framed by the valve wheels.
  - Verified: stills of the spawn before and after.

## Review log
