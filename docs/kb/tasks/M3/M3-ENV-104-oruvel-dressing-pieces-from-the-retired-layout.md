---
id: M3-ENV-104
title: "Oruvel: three things the retired M3-C01-100 dressing had that M3-ENV-738's lacks"
role: environment
status: todo
owner_session: ""
depends_on: [M3-ENV-738]
reviewer: cinematics
milestone: M3
request-from: cinematics
---
## Goal
The Lead's ruling (10-28): Oruvel wears env-art's M3-ENV-738 dressing. Slice-polish mounted it on claude/m2-slice
(M3-ENV-740) and retired its own generator (`tools/ch01/ch01_oruvel_dressing.py`, M3-C01-100). The scaleman,
O02 and O10 now follow your hulls. Three things the old layout carried are missing from yours:

## Asks
- [ ] **The lintel-gulls on every roof.** act1_ch01 C1-11 is "...That's the gulls": every carved gull cries at
      once, which is the chapter's signature. The old layout set one on every cabin ridge, on the chandlery and on
      the keel-hull (ov_preview_layout's rules). Yours has two: the keel-hull's and the dive raft's.
      O10 now frames the dive raft's at (47, 2.7, -9), so keep that one where it is.
- [ ] **Kell's beacon lamp itself.** O12 says "Kell is on her stall's roof, lighting the big chandler's beacon
      lamp." Your fire light on StormWall lights it, but no lamp mesh stands there. The old layout hung the
      ferry kit's lantern at (32, 3.0, -9) on the `KellBeacon` block.
- [ ] **The low hull's load.** C1-13 cuts it loose across the run's planks. The old layout piled a `salvage_heap`
      on the outrigger (both on `LowHull`), so it read as cargo blocking the way, not a canoe.
- [ ] **The storm's sky:** the self-rendered `ch01_oruvel_storm` (O11, the storm flag) shows the Undertow under a
      clear day-blue sky with your storm frame applied. The colour script's storm grade should darken it.
- Also: `assets/environments/zones/ch01/oruvel_dressing.json` is stale for its generator (test_zone_dressing_ch01). The
  Seventh Terrace moves to (-37.1, ..., y 0.7). Running the generator rewrites
  `game/levels/_tests/oruvel_zone_dressing/oruvel_dressed.tscn` too. O07's aim (-36.6, 1.65, -5.8) frames the
  name-board at either position.

## Review log
