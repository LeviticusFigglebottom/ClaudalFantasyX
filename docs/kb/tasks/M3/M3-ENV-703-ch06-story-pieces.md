---
id: M3-ENV-703
title: "Brine Shoals kit: Ch6's six story pieces for act1-chapters (tide-wheel, ridge fire, Level-stone shrine, vendor's boat, hatch, chalk mark)"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-02]
milestone: M3
request-from: cinematics
reviewer: rendering
---
## Goal
act1-chapters' request M3-ENV-1201 (on `claude/act1-chapters`): six Ch6 story blocks still draw as greybox because
the Brine Shoals kit had no piece for them. Build them in the kit, on each block's footprint.

## Acceptance criteria
- [x] `assets_src/environments/kits/brine_shoals/bs_story.py` (job `brine_shoals_kit`), LOD chains, PROVENANCE rows:

  | Block | Piece(s) | Size (x, y, z m) | Origin and facing |
  |---|---|---|---|
  | `TideWheel` | `tide_wheel`, `tide_wheel_burned` (charred, a quarter of the rim gone, slumped 0.55 m off the axle, embers in the trestle's foot) | 0.52 x 4.05 x 4.04 | foot centre; the axle along X |
  | `Fire` | `ridge_fire` (stone ring, driftwood star, ember bed; the flames stay VFX) | 0.65 x 0.14 x 0.65 | foot centre |
  | `Shrine` | `level_stone_shrine` (an Order Level-stone in a wreck's bow-stem, chipped, tended: bowl, shells, a teal cloth; the level line glows #9FD8E0 at 0.6) | 1.07 x 1.6 x 0.62 | foot centre; front +Z |
  | `VendorBoat` | `vendor_boat` (a beached clinker skiff, teal awning on two hoops, crates, jars, a lamp) | 2.0 x 1.53 x 4.05 | foot centre; bow -Z |
  | `Hatch` | `hatch` (planked, iron-strapped, ring pull, in its coaming) | 0.11 x 1.2 x 1.4 | the panel's centre; faces +X |
  | `ChalkMark` | `chalk_mark`, `chalk_mark_heavy` (the camp-sign drawn over twice, with a tally: nearer the camp) | 0 x 0.8 x 0.67 | the sign's centre, 4 mm proud; faces +X |
- [x] Materials `bs_chalk`, `bs_level_stone`, `bs_level_glow`.
- [ ] act1-chapters places them (`tools/act1/ch06_brine_shoals_dressing.py`, the block ids out of `greybox.keep`).
      Greybox block centres are mid-height: put the pieces at `pos.y - size.y / 2` except `hatch` and the chalk
      marks (centred). The vendor boat is taller than its 0.8 m block (the awning): keep its collision block.
- [ ] Rendering review of the preview views (M3-ENV-703 notes).

## Notes (env-art, 2026-10-27)
- The vendor boat's hoops reach 1.53 m; the tide-wheel's paddles dip 0.0 m (undershot, they sit in the channel).
- The burned wheel sinks 0.8 m into the mud where it fell, by design (it reads collapsed from B06's angle).
