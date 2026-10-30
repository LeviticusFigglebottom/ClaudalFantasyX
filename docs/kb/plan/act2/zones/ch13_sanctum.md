---
draft: pre-gate
zone: ch13/sanctum (the Sanctum of the Level)
kit: ansedra.py (sanctum_basin), lowlight.py (lowlight_nave_bay, read-only reuse)
task: M4-A2P-043
author: env-art-b, 2026-10-30
---
# The Sanctum of the Level: kit spec

**The read:** a basin held so still it is a perfect mirror, lit from beneath by a light that never moves. It is the
Order's sanctum, and its floor is the very thing the Order forbids: bound glimmer.

## The greybox it replaces
`Vestibule` (12 × 12) with `GateStep`; the `Nave` (24 × 36, walls 10 m); the `Basin` (10 × 18) with four
`KneelingLedge` blocks and the `BasinBed`; the `Apse` at the far end. Spawn `Gate`; trigger `to_city`; shot `S01`.
Ethren's binding (C4) is staged here. Kerrid never enters (`chapters/ch13.json`).

## Pieces
| Piece | Source | Where |
|---|---|---|
| `sanctum_basin` | exists (14 × 14 m, 1 m deep, salt-glass tiles over the bound light, gilt Level line, kneeling steps) | the nave's centre. **The greybox basin is 10 × 18:** relayout the nave to the kit's square basin |
| `lowlight_nave_bay` | exists (`lowlight.py`, 8 m bays) | the nave walls and vault: five bays (40 m), the material swapped to Order marble (the art sheet's own suggestion) |
| **`sanctum_vestibule`** | **new** (`b_ansedra.py`) | the gatehouse: a lacquered double door (closed behind the party), marble benches, a Level-line lintel. Kerrid stops here |
| **`sanctum_apse`** | **new** | the apse: a plain marble half-dome over a raised step, the Level line in gilt at eye height, nothing on it (no figure, no altar) |
| **`cantor_stand`** | **new**, small | where the Cantor stands beside Ysolde at the binding |

## Materials (`ch13` interior)
| Slot | Look |
|---|---|
| `kit_order_marble` | cold white, polished (roughness 0.3) on the floor near the basin so the light reflects |
| `kit_salt_glass` | the basin tiles, clear |
| `kit_bound_core` (flat, emissive) | the light beneath: `glimmer_bound` `#4FB3B0`, **steady, no flicker, no motes** (colour script rule 2) |
| `kit_gold_leaf` (**flat**) | the cold gold zone look (as Ansedra) on the Level lines |
| the basin's water | still mirror (Ansedra's look) at −0.1, roughness 0 |

## Lighting
- **The only source is the floor:** the bound light under the salt-glass, `#4FB3B0`, steady, lighting the vault and
  the kneelers' faces from below. No windows lit and no lamps (the art sheet: "no other light source than the floor").
- A dim, high fill from the vestibule door, `#8A96A4` at 0.2, so the nave walls read at the far end. Exposure
  ~1.0 (interior), with a LUT derived from `lut_ch13_still`.
- **Test it on the PC:** an upward-lit marble vault is the ch13 mirror test's interior case.

## Shot list
| Id | Frame |
|---|---|
| `S01` | the gate: the nave and the basin's glow ahead |
| `ch13_sanctum_basin` | at the kneeling steps: the vault doubled in the basin, the floor light on faces |
| `ch13_sanctum_vault` | low from the apse, looking back at the door (the scale) |
| `ch13_sanctum_binding` | Ethren's binding: Ysolde at the rim, the Cantor beside her (cinematics frames it) |

## Open items
- Ethren's bind cinematic VFX are creatures' and battle-presentation's. The zone gives them the basin's light as a
  practical they may raise.
