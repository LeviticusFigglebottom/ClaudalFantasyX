---
id: M3-HER-1129
title: "Request (act1-chapters): at Coilspire's PathFoot spawn, Rhen walks off a 2 m drop and lands with a 0.3 m snap"
role: cinematics
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
The field no-snap guard (tests/unit/test_hero_field_snaps.gd, ADR 0192) fails on ch08/coilspire since big12
(b30c2cf2, M3-C08-1210: Coilspire stood upright on env-art's kit, with trimesh and ramp chains). It walks the party from
the zone's first spawn, **PathFoot** (233.85, 12.35, 108.31, yaw 271°): a run north, a reversal, a strafe, a stop and
a walk. Rhen's body:
- **frame 37** (z ≈ 106.72): drops 0.12 m in one frame, at 8.1 m/s. That's a step down with no ramp: the controller's
  floor snap takes it whole.
- **frames ~60–73** (x ≈ 233.88, z ≈ 106.10): falls from about 12.15 m to 10.22 m, accelerating under gravity. He has
  walked off an edge about 2 m above the next floor, 2 m from the spawn. At **frame 73** he lands with a **0.31 m
  pop in one frame** (18 m/s).

A player can walk off the same edge in the first two seconds of arriving at the headland path. Either the edge is
unintended (a gap in the trimesh, or the ramp chain missing a link), or it's meant to be a drop and needs a rail or
blocker.

## Acceptance criteria
- [ ] No walkable 2 m drop at PathFoot. Steps on the path are ramps, or within the controller's step.
- [ ] Remove `coilspire.tscn:rhen` from KNOWN in tests/unit/test_hero_field_snaps.gd. `--filter=hero_field_snaps`
      is green.

## Notes
Found by integration-qa (M3-HER-1121) on claude/hero-integration with big12 merged in.

## Review log
