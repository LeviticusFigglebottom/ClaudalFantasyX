---
draft: pre-gate
zone: ch16/pale_rim (the white shallows)
kit: drowned_choir.py (pale_rim_flats), keth.py (cairn, read-only reuse), the Hollowmere ship (ch15_hollowmere.md)
task: M4-A2P-046
author: env-art-b, 2026-10-30
---
# The Pale Rim: kit spec

**The read:** the edge of the world goes white. Days of wading with no shadows; the horizon dissolves. The game's
lowest contrast.

## The greybox it replaces
`Sand` (260 × 60) and `Shallows`; four `Haze*` walls; the `Ship` (6 × 3 × 18); eight `Cairn*`. Spawn `Rim`; trigger
`to_choir`; shot `P01`. The wade is a time-skip montage (C2), not days of walking.

## Pieces
| Piece | Source | Where |
|---|---|---|
| `pale_rim_flats` | exists (a heightfield ring r 25–600 just under the water, sandbars breaking it; origin the Choir's centre) | **The Rim zone needs its own ground:** a strip variant `pale_rim_strand` (**new**, the same heightfield along X, 260 × 60 walkable plus the ring to the horizon), or the existing ring placed with the zone at its edge. The spec prefers the new strip (the montage walks a line) |
| `cairn` | exists (`keth.py`) | the wade's cairns: eight, in a line south, half in the water, salt-crusted (a material swap, not a new mesh) |
| `hm_ship` | new (shared with Hollowmere) | at anchor in the shallows, the waiting Hollowmere ship (C1) |
| **`rim_marker_pole`** | **new**, small | Cantors' old marker poles, bleached, at long intervals: the only verticals besides the cairns |
| `glass_skate`, `rim_crawler` | creatures' | the Rim's wildlife and foes (data exists; models don't) |

## Materials (`ch16`)
| Slot | Look |
|---|---|
| `kit_rim_sand` (shader) | kept: white sand |
| `cairn` stone | a salt-crusted zone look (Haluna shrine stone, desaturated, `use_salt`) |
| water | `pale_rim` (validated): absorption ×0.8, deep `#5E8C90`, near-white |

## Lighting (`ch16`, the Rim)
- White overcast noon: sun 70° / 180°, key `#E6EBFF` 2.2, fill `#E6EBF0` 1.0, rim `#FFFFFF` 0.4; sky `#D8DEE4` →
  `#F2F2EE`; fog `#E8ECEC` 0.012; exposure 0.70, **S-curve 0.25, saturation ×0.7**; **`lut_ch16_rim` (missing:
  write it)**. No shadows to speak of; the horizon dissolves into fog.
- **The montage** (C2) runs a few `variants` rows: noon, an evening, a grey dawn. The same ground and the same
  white; only the sky's tone shifts.

## Shot list
| Id | Frame |
|---|---|
| `P01` | the ship waits in the shallows (C1) |
| `ch16_rim_wade` | the party wading south past a cairn, the horizon gone |
| `ch16_rim_cairns` | the line of cairns into the white |
| `ch16_rim_evening` | the montage's evening frame |

## Open items
- A strip ground versus the ring: the spec's choice, the new strip, needs one new piece. The montage's camera
  decides it (cinematics).
