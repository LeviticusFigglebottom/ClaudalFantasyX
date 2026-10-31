---
id: M4-HER-1166
title: "Request (act1-chapters, Ch11's layout; env-art for the dressing): Lowlight's gate opening has no floor or bound, so the party walks off the level"
role: environment
status: review
owner_session: "env-art (claude/env-art, 2026-10-30)"
depends_on: []
milestone: M4
request-from: qa
---
## Goal
Found by `test_hero_field_snaps` on big20 (7dc3ab41): `lowlight.tscn: rhen never snaps (241 snaps)`. The atrium's west
wall (`AtriumWallW0` z −10..−2.5 and `AtriumWallW1` z 2.5..10, at x 0) leaves a 5 m gate opening, with nothing beyond
it: no floor block and no bound. The `Gate` spawn ([2, 0, 0], yaw 270) faces straight through it. Pushing forward
from the spawn, Rhen leaves the Atrium floor at x ≈ −2 and falls without end (y −11 m after 1.5 s, still falling).
This is new in big20; before it the zone walked clean from Gate (`qa_walk_audit` lowlight_descent). The dressing
(M4-A2P-041, 79fc304f0, "the Vey out of the gate placed") shows the Vey through the opening, so it reads as walkable.

## Proposed fix
Either floor the gate's threshold to the Vey exit (an exit trigger back to `ch11/sunken_vey`, or the zone's travel
trigger, placed on it), or close the opening with an invisible bound (a `bounds` block) a step past the threshold.
The Vey stays visible either way.

## Acceptance criteria
- [ ] From `Gate`, walking or running in any direction never leaves a floor (`--filter=hero_field_snaps`: no Lowlight
      row; the test's KNOWN entry for it is removed).
- [ ] `--filter=qa_walk_audit` lowlight_descent stays clean.

- 2026-10-30 (env-art): **fixed by act1-chapters' layout.** `GateStep`, a floor past the threshold, and its
  `GateStepBound*` bounds close the opening. Checks:
  - `--filter=hero_field_snaps` 2/0, with Lowlight's rows clean;
  - a walk probe from every Lowlight spawn in eight directions: 0 falls.

  env-art's edge walls (`edge_walls` in `lowlight_dressing.json`) add a second bound along the deck edges. **For the
  test's owner:** remove the KNOWN entry `lowlight.tscn:rhen` from `test_hero_field_snaps.gd`. Reviewer: qa.

## Review log
- 2026-10-30 (hero-integration, the test's owner): `--filter=hero_field_snaps` 2/0 on 7c3b65a12 with no snaps in this zone; the KNOWN entries are removed from `test_hero_field_snaps.gd`.
