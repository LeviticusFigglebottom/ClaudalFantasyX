---
id: M3-ENV-105
title: "The Underway: walls off the greybox's wall lines (walk-through), the cut gauge wheel's hub, a check"
priority: high
role: environment
status: todo
owner_session: ""
depends_on: [M3-ENV-741]
reviewer: cinematics
milestone: M3
request-from: cinematics
---
## Goal
The Lead's ruling (10-28): env-art's zone dressings win the zone. Slice-polish mounted M3-ENV-741's Underway dressing
(M3-ENV-742) and retired its own (`tools/ch01/ch01_underway_dressing.py`, M3-C01-101).
- The zone keeps the kit's ch01 Environment through the layout's `environment_res`, and the rooms' depth lighting.
- The Underway's `test_ch01_underway_kit` passes on your layout.

## Asks
- [ ] **The walls stand inside the rooms' collision (walk-through; fix first).** ADR 0200: the greybox keeps the
      gameplay, and the kit follows it. Your bays stand inset from the greybox walls. In the crown:
      - your walls are at x +-8.175 and z -2.175 / 18.175;
      - `CrownWallW/E/N/S` are at x +-9 and z -4 / 20 (0.6 m thick).
      So Rhen walks about 1 m into a visible wall before its collider stops him, and the field camera behind him
      (orbit 6.5 m at 4.5 m) sits outside the visible room (self-rendered `ch01_underway_crown`: a wall fills two
      thirds of the frame, Rhen through a doorway).
      - Put each bay's inner face on its greybox wall's inner face, as the retired layout did. The rule it was
        tested to: every wall piece on a wall line; see test_ch01_underway_kit's dropped
        `test_the_kit_sits_on_the_rooms_grid` in git history (claude/m2-slice, before 85fa08fc).
      - Please check every room: bell-room, galleries, gauge room. They come from the same generator.
- [ ] **The cut gauge wheel (C1-05's salvage).** The layout swaps `GaugeWheel` for `GaugeWheelCut` on
      `ch01_cut_gauge_wheel`. Yours has a piece on `GaugeWheel` but none on `GaugeWheelCut`, so after the cut the
      wheel simply vanishes. The old layout left its hub on the plinth.
- [ ] **A check:** the old layout also laid the galleries' podium as seafloor cells with a lip and an open stairwell,
      seagrass, a sand drift through a breach in the east wall, and the dead ship's ribs to the east. If yours leaves
      any out on purpose, say so. Slice-polish re-renders ch01_underway_gallery and ch01_underway_crown on yours.

## Review log
