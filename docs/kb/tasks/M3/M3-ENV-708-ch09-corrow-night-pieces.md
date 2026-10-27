---
id: M3-ENV-708
title: "Corrow kit: Ch9's night and dawn pieces (shrouds, strand lamps, Stillguard shields, the Ebbing raft, flood debris, the milestone)"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-04B]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
The kit half of M3-C09-04 (act1_ch09.md §9): the pieces Ch9's night variant of Corrow and the dawn road need, so
act1-chapters can dress `ch09/corrow_night` (or Ch8's zone's night variant) without greybox.

## Acceptance criteria
- [x] `assets_src/environments/kits/corrow/cw_night.py` (job `corrow_kit`, older pieces identical):
  - `shroud_a`, `shroud_b`, `shroud_small`: the drowned under sailcloth, **shapes only, faces covered**, tied at the
    neck and ankles; three variants for the rows (vary yaw and spacing too). 1.0 x 0.2 x 2.1 m (small 0.7 x 1.35);
    lying along Z, the head at -Z.
  - `strand_lamp`: a clay oil lamp on a stake (emissive wick; place a warm OmniLight3D with fog energy 0 every few).
  - `round_shield`: a Stillguard shield of red lacquer laid at a man's feet.
  - `ebbing_raft`: lacquered, poled, a low deck with no rail, the lantern-staff's socket at its centre (2.6 x 4.2 m).
  - `flood_debris`: a 4 x 4 m float of planks, a door, a shutter, a basket and a cloth, at y 0 on the water.
  - `milestone`: the dawn road's laterite milestone, the distance cut in strokes.
  - The cut hoist rope coiled on the wall-head: the Haluna kit's `rope_coil` (by kit_dir). The fallen Watchers and
    the breach: M3-ENV-04B's pieces.
- [ ] act1-chapters places them (M3-C09-04's other criteria are theirs and Rendering's: the zone decision, water).
