---
id: M4-A2P-106
title: "The Drowned Choir: relayout the greybox to the kit's amphitheatre (marks to tier heights, kit collision)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
reviewer: environment
milestone: M4
request-from: environment
---
## Goal
env-art-b can't dress `ch16/drowned_choir` in its greybox frame the way it dressed the other Ch13–Ch16 zones:
- **The greybox's floor is flat** (`Floor`, 48 × 48 m at y 0). The kit's `choir_amphitheatre` is a dais (r 7.5,
  y 0), a flooded channel (r 7.5–9.5 at −0.8) and six tiers rising to 2.15 m out to r 21.5.
- **The story's marks stand on the tiers.** `kesh` is at (0, −20) and `sefir` at (5, −17), so they belong at tier
  heights, not on a flat floor.
- **The singers are in the wrong ring.** The greybox puts its `Mouth*` blocks at r ~26; the art sheet stands the
  fifteen singers at r 44 in the sea.

This is the spec's own open item (`ch16_drowned_choir.md`, "Relayout").

## Acceptance criteria
- [ ] `tools/act1/ch15_16_greybox.py`'s Choir layout drops the flat `Floor` and its walls.
- [ ] Its `collision_path` points at a collision file env-art-b writes from the kit: ramps between the tiers (the
      controller has no step-up), the channel as a step down or a bridge at the approach, the dais.
- [ ] The marks move to the tier heights, the `Mouth*` blocks move to r 44 (or drop: the singers are dressing), and
      the approach meets the ring at the gap.
- [ ] env-art-b is told; then it writes `drowned_choir_collision.json`, the dressing, the moonrise grade and the
      shots.

## Notes
- The Pale Rim (the same task, M4-A2P-046) is dressed; only the Choir waits on this.

## Review log
