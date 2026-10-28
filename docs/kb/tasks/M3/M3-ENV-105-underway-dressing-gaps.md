---
id: M3-ENV-105
title: "The Underway: the cut gauge wheel's hub, and a check against the retired M3-C01-101 layout"
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
- [ ] **The cut gauge wheel (C1-05's salvage).** The layout swaps `GaugeWheel` for `GaugeWheelCut` on
      `ch01_cut_gauge_wheel`. Yours has a piece on `GaugeWheel` but none on `GaugeWheelCut`, so after the cut the
      wheel simply vanishes. The old layout left its hub on the plinth.
- [ ] **A check:** the old layout also laid the galleries' podium as seafloor cells with a lip and an open stairwell,
      seagrass, a sand drift through a breach in the east wall, and the dead ship's ribs to the east. If yours leaves
      any out on purpose, say so. Slice-polish re-renders ch01_underway_gallery and ch01_underway_crown on yours.

## Review log
