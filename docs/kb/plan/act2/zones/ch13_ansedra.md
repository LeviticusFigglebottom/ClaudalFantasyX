---
draft: pre-gate
zone: ch13/ansedra (Ch13 by day; Ch14's lagoon at night is a variant of this zone)
kit: assets_src/environments/kits/haluna/ansedra.py (M3-ENV-721; art sheet docs/kb/art/environments/ansedra.md)
task: M4-A2P-043 (Ch13 zones), M4-A2P-044 (Ch14)
author: env-art-b, 2026-10-30
---
# Ansedra, the holy city: kit spec

**The read:** beautiful and airless. Gold bowl-domes doubled in a mirror lagoon under a white-grey sky. Then, in
Ch14's variant, the first ripple in four hundred years and the whole city at its windows.

## The greybox it replaces
`ch13/ansedra_layout.json` (M4-C13-02): the `Moorings` platform (16 × 16 m) with `BargeA`/`BargeB`; four causeways
(`CausewayN`, `W`, `E`, `Sanctum`: 4 m wide, 28–36 m long, rails and five lamp blocks a side) to the `Centre`
(20 × 20), `CorranIsle` (with `CorranHouse`), `ArchiveIsle` (with `ArchiveIsleDome`) and `SanctumIsle` (with
`SanctumIsleDome`); `SefirHouse` and its dome on the centre; `Water`/`Bed` 120 × 150. Spawns `Moorings`,
`FromSanctum`, `FromArchive`; triggers `to_sanctum`, `to_archive`; one shot, `A01`.

## Pieces
| Piece | Source | Where |
|---|---|---|
| `bowl_dome` | exists | one per island: `SanctumIsleDome` (scale ~1.2), `ArchiveIsleDome` (~0.8), `SefirHouseDome` (~0.5); plus 6–10 free-standing domes on their own islands inside 150 m to fill the near skyline |
| `ansedra_far_domes` | exists | the skyline ring at 300–700 m, centred on the lagoon |
| `ansedra_far_domes_lit` | exists | **Ch14 variant only** (the city at its windows), in place of the unlit ring |
| `lacquer_hall` | exists | Sefir's house (one hall, scaled 0.6, on `SefirHouse`); Corran's old house (one hall, scaled 0.5, plainer: the black-lacquer slot swapped to weathered timber) |
| `bridal_barge` | exists (`bridal_barge.py`) | `BargeA`/`BargeB` at the moorings, scaled 0.6 as poled mooring barges, canopies dressed down (no bier) |
| **`ansedra_causeway_6m`** | **new** (`b_ansedra.py`) | a 6 m causeway module: white Order-marble deck on low piers into the lagoon, a low marble kerb each side; laid along the four causeways' arcs |
| **`gold_lamp_post`** | **new** | the causeways' gold lamp-posts (bible §5.8): a slender marble shaft, a gilt cage, an **unlit** salt-glass globe (the Order lights nothing on the water); on every `Causeway*Lamp*` block |
| **`island_plinth_16m`** | **new** | the white-stone island edge for `Centre`, `CorranIsle`, `ArchiveIsle` and `SanctumIsle`: stepped marble down into the water, the Level line inlaid in gilt; sized per island |
| **`mooring_platform`** | **new** | the outer moorings: a marble landing stage with bollards, punt-pole racks and a lacquered mooring arch; at `Moorings` |
| `cairn`, plants | no | nothing grows and nothing is piled: no seabirds, no dogs, no children's games (bible §5.8). The emptiness is the dressing |

**Budget:** the near domes at LOD0 inside 120 m; the skyline ring is a single low-poly piece. Total under ~400k
triangles in view.

## Materials (Act II palette, `ch13`)
| Slot | Look |
|---|---|
| `kit_order_marble` (shader) | kept; tint toward cold white (`#E8E8E2`), salt in the joints only at the waterline |
| `kit_gold_leaf` (**flat**) | zone look on `env_bronze`: `zl.GOLD` cooled 300 K (col_bronze ~`#C9A85A`), roughness 0.25, wear at the edges only. Gold may reach 12 % of the frame here, never warm |
| `kit_lacquer_red` (**flat**) | `zl.lacquer((0.62, 0.14, 0.11))`: deep red, hollows aged in the same hue |
| `kit_lacquer_black` (**flat**) | `zl.lacquer` black with an oxblood undercoat at the chips |
| `kit_roof_tile` (shader) | kept (red tile, gilt ridges) |
| `kit_window_lit` (flat, emissive) | Ch14 only, warm `#FFB16E` at low energy: the far, small windows, the only warm points in the frame |
| water | **the still mirror**: `overcast_lagoon`, absorption ×1.5, deep `#5E6E80`, **zero wave amplitude, roughness 0, planar reflection** (a rendering gap, below) |

## Lighting
- **Ch13 (`ch13`):** 16:30 overcast, sun 25° / 230°, key `#FFF9F2` 1.6, fill `#8A96A4` 0.6, rim `#F1D27A` 0.9;
  sky `#8A96A4` → `#C8C4BA`; fog `#B8B8B2` 0.008; exposure 0.75, S-curve 0.35, saturation ×0.8; **`lut_ch13_still`
  (missing: write it with `zone_lut.py`)**. No practical lights: the causeway globes are unlit by rule.
- **Ch14 lagoon variant (`ch14`):** 18:30 dusk, sun 1° / 270°, key `#FFAA5F` 1.4, rim `#B3261E` 0.5, fill `#4A5A78`
  0.4; fog `#4A3A3A` 0.01; exposure 0.90, S-curve 0.7; `lut_ch14_wedding` (exists, in the arena). The lit skyline
  ring; the bells (audio).
- The layout's `environment` row must carry the grade's fill (Act I's lesson at Ashcrown: `apply_variant` writes it
  over the grade).

## Rendering items (env-art-b's zone looks)
- **The still mirror:** the water shader in its still mode (wave amplitude 0, roughness 0) with an exact planar
  reflection of the domes, re-checked under `ch13` light (the colour script lists `ch13 mirror` as not validated).
  Perf on the PC (plan risk R5).
- **Ch14's ripple propagation:** ring sources per pole stroke and the barge's wake, breaking the domes' reflections
  apart. Shared with the Lacquer Court and the arena.

## Shot list (proposed ids; the greybox's `A01` kept)
| Id | Frame |
|---|---|
| `A01` | arrival at the moorings: the causeway north, the Sanctum's dome doubled in the water |
| `ch13_ansedra_moorings` | the moorings from the water: barges, mooring arch, the first domes |
| `ch13_ansedra_causeway` | eye height on a causeway: the lamp-posts' rhythm to the centre, the mirror both sides |
| `ch13_ansedra_mirror` | low over the lagoon: a dome and its exact reflection (the still-mirror check) |
| `ch13_ansedra_sefir_house` | Sefir's house on the centre isle |
| `ch13_ansedra_corran_house` | Corran's old house: the plainer hall, the side scene (C8) |
| `ch14_ansedra_lagoon_night` | the lit city from the water at dusk |
| `ch14_ansedra_ripple` | the first ripple: the barge's wake breaking a dome's reflection |

## Open items
- **Relayout:** the causeways' arcs and the islands' plinths need the kit's sizes. Move the story points once.
- Which hull the mooring barges are: the plan reuses `bridal_barge` scaled. A plain `mooring_barge` piece is the
  alternative if the wedding barge must stay unique (Narrative).
