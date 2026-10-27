---
id: M3-ENV-1201
title: Ch6 story pieces the Brine Shoals kit lacks (tide-wheel, campfire, Level-stone shrine, vendor's boat, chalk mark, hold hatch)
role: environment
status: todo
owner_session: ""
depends_on: [M3-C06-1200]
milestone: M3
request-from: cinematics
---
## Goal
Ch6's zone is dressed with the Brine Shoals kit (M3-C06-1200, ADR 0200). Six story blocks still draw as greybox
because no kit piece exists for them (`brine_shoals_dressing.json` `greybox.keep`). Each needs a kit piece in
`assets/environments/kits/brine_shoals/` on the block's footprint (sizes from
`game/levels/ch06/brine_shoals/brine_shoals_layout.json`):

| Block | Footprint (x, y, z m) | What (act1_ch06.md) |
|---|---|---|
| `TideWheel` | 0.4 × 4 × 4 | the Saltwrights' tide-wheel, intact and collapsing (B03–B06) |
| `Fire` | 0.6 × 0.4 × 0.6 | the party's driftwood fire on the high hull at dusk (W15) |
| `Shrine` | 1 × 1.6 × 0.6 | the wayside Level-stone shrine set in a wreck's bow (B08) |
| `VendorBoat` | 2 × 0.8 × 4 | the purser's small boat at the dusk camp |
| `ChalkMark` | a decal, 0.8 × 0.8 | the Saltwright chalk sign on the hull (B02), thickening toward the camp |
| `Hatch` | 0.1 × 1.2 × 1.4 | the hold's hatch in the hull's side (B03) |

When a piece lands, add it to `tools/act1/ch06_brine_shoals_dressing.py` with its `block` and drop the id from
`greybox.keep` (act1-chapters does this, or env-art may; tell act1-chapters in its live log).

## Acceptance criteria
- [ ] Each piece built, reproducible, with PROVENANCE rows and LOD chain, fitting its footprint.

## Notes

## Review log
