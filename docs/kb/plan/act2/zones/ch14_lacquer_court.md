---
draft: pre-gate
zone: ch13/ansedra_lacquer_court (Ch14, the peace wedding)
kit: ansedra.py (lacquer_hall, lacquer_court_ground, bowl_dome, ansedra_far_domes_lit), bridal_barge.py
task: M4-A2P-044
author: env-art-b, 2026-10-30
---
# The Lacquer Court: kit spec

**The read:** a trap dressed as a wedding. Red lacquer and still water at dusk, the Conclave in its gallery; then
the steps held, the barge cut loose, and the first ripple in four hundred years.

## The greybox it replaces
The `Court` (30 × 24) with columns N/W/E (seventeen blocks), `GalleryW`/`GalleryE`, the `Dais`, the
`ConclaveGallery`, the water-steps' walls, the `Barge` (4 × 10) with rails and stern, the `WaterGate` (10 × 5), the
`EntryStep`; `Water`/`Bed` 120 × 100. Spawns `CourtEntry`, `Barge`; trigger `barge`; shot `W01`.

## Pieces
| Piece | Source | Where |
|---|---|---|
| `lacquer_court_ground` | exists (40 × 33, eight water-steps, the water-gate with its drop-gate) | the court. **The greybox court is 30 × 24:** relayout into the kit's frame |
| `lacquer_hall` | exists (15 × 10 × 10) | three halls on N, W and E (the art sheet: halls' fronts 6 m back from the steps) |
| **`conclave_gallery`** | **new** (`b_ansedra.py`) | the raised gallery for the five Conclave revenants, seen at a distance: lacquered screens, five seats, a gilt canopy |
| **`wedding_dais`** | **new** | the dais: three marble steps, a red bridal carpet, two gilt standards with red streamers hanging dead still |
| **`court_galleries`** | **new** | the side galleries (W, E) on red columns: the guests' benches |
| `bridal_barge` | exists | Merel's barge at the water-steps (the arena's floor too), lamp hook empty, canopy dressed for the wedding (no bier yet) |
| `pursuit_barge` | exists | moored off the court until the trap, then the boss's barge |
| `bowl_dome`, `ansedra_far_domes_lit` | exist | behind the court across the water: the lit windows (the city watches) |
| **`stillguard_rack`**, **`wedding_offerings`** | **new**, small | spears racked by the gallery; offerings on the dais (cloth bolts, sealed jars), nothing alive |

## Materials (`ch14`)
| Slot | Look |
|---|---|
| `kit_lacquer_red` (**flat**) | `zl.lacquer`, pushed toward blood under the LUT (hue −4°) |
| `kit_lacquer_black` (**flat**) | `zl.lacquer` black |
| `kit_gold_leaf` (**flat**) | cold gold (as Ansedra), catching the red band |
| `kit_order_marble` | the court: cool white going rose at dusk |
| `kit_roof_tile` | kept |
| water | the still mirror until the trap; then ripples (the rendering item) |
| red bridal cloth | `kit_keth_red` shader or a new `kit_bridal_red` woven look (not flat) |

## Lighting (`ch14`)
- 18:30 dusk: sun 1° / 270°, key `#FFAA5F` 1.4, rim `#B3261E` 0.5, fill `#4A5A78` 0.4; sky `#2E3448` → `#B85A3A`;
  fog `#4A3A3A` 0.01; exposure 0.90, **S-curve 0.70 (the game's peak contrast)**, saturation ×0.9;
  `lut_ch14_wedding` (exists).
- **Practicals with sources:** gilt lamp-stands on the dais and along the galleries, lit for the ceremony (the
  one night the Order lights the court). Each light sits on its stand.
- **After the trap:** the stands knocked down (a `states` row hides some and shows fallen versions), lights out
  one by one; the lagoon's ripples catch the red band.

## Shot list
| Id | Frame |
|---|---|
| `W01` | the entry: the court, the dais, the halls, the water-steps |
| `ch14_court_ceremony` | the dais from the guests' benches, the Conclave gallery high left |
| `ch14_court_steps` | the water-steps from the court: the barge, the gate, the lit city beyond (the step-hold) |
| `ch14_court_gate` | the water-gate from the water: Merel's last frame |
| `ch14_court_after` | the court after the trap: stands down, the lagoon rippling |

## Open items
- **The step-hold set piece** fights on the court steps: a new arena, `lacquer_court_steps` (see
  [arenas_ch13_16.md](arenas_ch13_16.md)).
- The relayout must keep `CourtEntry`, `Barge` and every mark cinematics uses.
