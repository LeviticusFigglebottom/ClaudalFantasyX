---
id: M3-ENV-104
title: "Oruvel: three things the retired M3-C01-100 dressing had that M3-ENV-738's lacks"
role: environment
status: review
owner_session: "env-art (claude/env-art, 2026-10-29)"
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
- [x] **The lintel-gulls on every roof.** act1_ch01 C1-11 is "...That's the gulls": every carved gull cries at
      once, which is the chapter's signature. The old layout set one on every cabin ridge, on the chandlery and on
      the keel-hull (ov_preview_layout's rules). Yours has two: the keel-hull's and the dive raft's.
      O10 now frames the dive raft's at (47, 2.7, -9), so keep that one where it is.
- [x] **Kell's beacon lamp itself.** O12 says "Kell is on her stall's roof, lighting the big chandler's beacon
      lamp." Your fire light on StormWall lights it, but no lamp mesh stands there. The old layout hung the
      ferry kit's lantern at (32, 3.0, -9) on the `KellBeacon` block.
- [x] **The low hull's load.** C1-13 cuts it loose across the run's planks. The old layout piled a `salvage_heap`
      on the outrigger (both on `LowHull`), so it read as cargo blocking the way, not a canoe.
- [x] **The storm's sky:** the self-rendered `ch01_oruvel_storm` (O11, the storm flag) shows the Undertow under a
      clear day-blue sky with your storm frame applied. The colour script's storm grade should darken it.
- Also: `assets/environments/zones/ch01/oruvel_dressing.json` is stale for its generator (test_zone_dressing_ch01). The
  Seventh Terrace moves to (-37.1, ..., y 0.7). Running the generator rewrites
  `game/levels/_tests/oruvel_zone_dressing/oruvel_dressed.tscn` too. O07's aim (-36.6, 1.65, -5.8) frames the
  name-board at either position.

## Notes (env-art, 2026-10-29, e2358df5 + 2ff511ab; MERGE-READY @ 2ff511ab)
- **Gulls:** a ridge gull on the keel-roof cabin (the preview's rule) and one on the chandlery's ridge, beside the keel-hull's
  and the dive raft's (O10's stays where it was). Oruvel has no `cabin_patched` (the commons has one cabin).
- **The cabin:** it was scaled to the greybox CabinRoof block (ridge 2.4 m), which left `roof_child` (y 3.45) floating a
  metre over it. It is now scaled so its ridge is under her feet (0.986).
- **Kell's beacon:** the chandlery carries its own beacon lantern on a post off the keel-roof's fore end (ov_heroes). A
  ferry lantern hung at the KellBeacon block floated beside it, so none is added: the storm's fire light moves into the
  chandlery's lantern (33.8, 4.63, -11.7) instead of the block's centre.
- **The low hull's load:** `salvage_heap` (scale 0.65) on the run's planks over LowHull, following the block (it drifts clear
  with it at C1-13).
- **The storm's sky:** the storm frame's cumulus sky had the shader's noon zenith. It now takes the palette's storm_slate
  family (zenith #242E38, horizon #707F8C, ground #394754, no sun disc); the Undertow is the cloud mass.
- **Viewed (self-rendered):** the beacon, the cabin and the low hull at player eye; `ch01_oruvel_storm`, `zone_oruvel_storm_o12`,
  `zone_oruvel_storm_o16`, `oruvel_o17_pen_split` (the slate overcast replaces the day-blue), `zone_oruvel_o09`, `zone_oruvel_o12`.
- **The stale dressing** the task notes: the generator and its output agree (test_zone_dressing_ch01 OK).

## Review log
