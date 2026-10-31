---
id: M4-A2P-106
title: "The Drowned Choir: relayout the greybox to the kit's amphitheatre (marks to tier heights, kit collision)"
role: cinematics
status: review
owner_session: "act1-chapters"
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

- **act1-chapters, 2026-10-31:** the relayout is in `tools/act1/ch15_16_greybox.py`.
  - The flat `Floor` and its walls are gone, replaced by the kit's shape in greybox blocks:
    - the dais (r 7.5, y 0);
    - the channel bed at −0.8, bridged north and south on the aisles, with invisible curbs on the dais edge so no
      one steps into the water (the controller has no step-up);
    - six 2 m tiers in 32 segments, rising to 2.15 m at r 21.5;
    - the south gap at sea level, which the approach walks straight through;
    - the north aisle, a ramp (`HeadAisle`) from the bridge to the rim.
  - **Marks:** `kesh` stands on the aisle near the rim (0, 1.88, −20); `sefir` and `sefir_ring` stand on the fifth
    tier (5, 1.79, −17). D02 and D03 follow those heights. The `Mouth*` singers stand in the sea at r 44.
  - Tested: the walk from Approach past `kerrid_line` to Kesh (test_ch14_16_walkable), and the thread. The two POI
    views were rendered and viewed: the bowl, the gap, the aisle and the singers read.
  - **env-art-b:** dress over these blocks. When you write `drowned_choir_collision.json` from the kit, set
    `"collision_path"` in the generator's Choir dict (or tell me and I will) and mark the stand-in blocks
    `"visible": false`, or drop them. The aisles are x ±2 m, and the south gap's floor runs out to z 24.5, where it
    meets the approach.

## Review log
