---
draft: pre-gate
zone: ch15/open_sea (the unlamped drift)
kit: bridal_barge.py (M3-ENV-720; art sheet open_sea_ch15.md)
task: M4-A2P-045
author: env-art-b, 2026-10-30
---
# The open sea at night: kit spec

**The read:** fugitives in the dark on a wedding barge, with a dead man under the bridal cloth. The only light is
the sea, and the dead coming up out of it toward Kerrid. Quiet, cold, honest.

## The greybox it replaces
The `Deck` (4 × 10) with four rails, the `Bier`, the `Shoal` (30 × 20, below), `Water`/`Bed` 160 × 160. Spawn
`Deck`; trigger `dawn`; shot `U01`.

## Pieces
| Piece | Source | Where |
|---|---|---|
| `bridal_barge` | exists (16 × 7.5 m deck at y 0; the stern canopy and Tobin's bier under Merel's bridal cloth; the empty lamp hook; punt poles on the rails) | the whole walkable zone. **The greybox deck is 4 × 10:** relayout to the barge (rails to the kit's 0.35 m rail, the bier to its canopy) |
| the shoal's held dead | **VFX reuse:** env-art-b's `EbbingMotes` rig (Ch9) with one attractor | a held field below the barge, its motes drifting toward Kerrid (`follow=kerrid`), and a few of his own leaving his hands sideways (kerrid.md §9's emission sockets are characters') |
| **`bow_fog_bank`** | **new**, VFX/volume | dawn: the fog the barge drifts into (the SmokeColumn raymarcher as a flat bank, or a fog volume) |
| nothing else | — | no land, no other boat (the art sheet). The emptiness is the set |

## Materials (`ch15`)
| Slot | Look |
|---|---|
| `kit_lacquer_red` (**flat**) | the hull: `zl.lacquer` red. At night only the sea-glow and the moon touch it |
| `kit_gold_leaf` (**flat**) | the sheer band: cold gold, a moonlit line |
| `kit_keth_red` | the bridal cloth over the bier (woven, kept) |
| `kit_timber` | the deck (kept) |
| water | `night_sea`, absorption ×1.0, deep `#061A2B`, sea-glow 0.12 (validated) |

## Lighting (`ch15`)
- **No warm source anywhere:** no lamp, fire or flame on the barge (rule). Moon `#D2DFFF` 0.25 (rule 3b: ≤ 2.5 ×
  the sea-glow), fill `#0B1630` 0.15, rim `#9DB4D9` 0.4; fog `#1C3A4A` 0.004; exposure 1.10, S-curve 0.5,
  saturation ×0.85; `lut_ch15_unlamped` (exists, in the arena).
- **The reveal (C3):** the shoal's `glimmer_held` (energy 2.0) is the only other light. Skin takes only the moon and
  the sea.
- **Dawn (`dawn` trigger):** fog density to 0.03, the sky grey-rose; no sun yet. A `variants` row.

## Shot list
| Id | Frame |
|---|---|
| `U01` | the deck from the bow: the canopy, the bier, the dark |
| `ch15_sea_bier` | the bier under the bridal cloth (still; the cloth doesn't flutter) |
| `ch15_sea_shoal` | over the rail: the held dead below, drifting toward the barge |
| `ch15_sea_reveal` | Kerrid seated, hands still, the motes leaving them sideways (cinematics frames it) |
| `ch15_sea_dawn_fog` | the bow into the fog at dawn |
