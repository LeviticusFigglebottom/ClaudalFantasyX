---
draft: pre-gate
zone: ch16/drowned_choir (the ring of colossal mouths; a hero zone, SPEC §7.4)
kit: drowned_choir.py (choir_singer, choir_amphitheatre, pale_rim_flats); Rendering's UndertowStorm (reused)
task: M4-A2P-046
author: env-art-b, 2026-10-30
---
# The Drowned Choir: kit spec

**The read:** the ring of colossal mouths at moonrise. This is where every Cantor ends. Kesh is bound in its stones,
and here the party learns what the Hush really does. Then the storm wakes early.

## The greybox it replaces
The `Floor` (48 × 48) with four walls; fifteen `Mouth*` blocks (7 × 14 × 4) in a ring (ids 0–15 without 8); the
`Approach` (6 × 8) and its bound; `Water`/`Bed` 120 × 120. Spawn `Approach`; no trigger yet; shot `D01`.

## Pieces
| Piece | Source | Where |
|---|---|---|
| `choir_amphitheatre` | exists (dais r 7.5 at y 0, the flooded ring channel, six tiers to r 21.5, broken in places) | the `Floor`. The greybox's 48 × 48 floor matches the amphitheatre's 46 m |
| `choir_singer` | exists (24 m, robed, hands folded, head tilted up 25°, mouth open) | one on each `Mouth*` block. **The greybox's mouths are at the floor's edge (~r 24); the art sheet stands them at r 44 in the sea.** Relayout the ring to r 44 (the arena already does). Fifteen singers; the gap at 8 is the approach's opening |
| `pale_rim_flats` | exists | round the ring to the horizon, centred on the Choir |
| **`choir_approach_causeway`** | **new** (`b_choir.py`) | the drowned processional way into the bowl: worn ceramic flags under 0.2 m of water between two singers |
| **`choir_votive_rings`** | **new**, small | Cantors' offerings at the singers' feet: ceramic rings, salt-white, half buried. Sparse |
| the storm | **reuse:** `UndertowStorm` (Rendering's), with a waking preset | C8: the storm wakes early over the ring (Ch8's Reach is the precedent, with `StormFarPlane`) |
| Kesh | creatures' | a colossal woman of standing seawater (no model yet: the plan's gap) |

## Materials
| Slot | Look |
|---|---|
| `kit_iskarra_ceramic` (shader) | the singers: Lamplighters' white ceramic, weathered; the sea's band at the foot. At moonrise, cold |
| `kit_iskarra_paving` (shader) | the dais and tiers |
| `kit_rim_sand` | the flats |
| water | `pale_rim` at night: deep `#2E4C50`, sea-glow 0.1 |

## Lighting
- **Moonrise:** the moon low in the east, `#D2DFFF` 0.35; fill `#2A3A4E` 0.25; exposure 1.1; `lut_ch16_choir`
  (exists, in the arena): moonlit, stone faces cold. The moon rises between two singers in the hero frame.
- **The singers' mouths are dark.** No light inside, until Kesh's binding (`glimmer_held` pale cyan, creatures'
  VFX).
- **The storm's waking:** the Undertow's lightning and the storm grade (`ch08_storm`'s precedent) over the moonlit
  base.

## Shot list
| Id | Frame |
|---|---|
| `D01` | the approach: the ring ahead, the moon low between two singers |
| `ch16_choir_ring` | wide from the dais: the ring of mouths, heads tilted to the sky |
| `ch16_choir_mouth` | low at a singer's foot, up its robe to the open mouth |
| `ch16_choir_sefir` | Sefir on the tiers (C5), the ring behind him |
| `ch16_choir_storm` | the storm waking over the ring (C8) |

## Open items
- **Perf:** fifteen 24 m singers with LOD0 inside 80 m. Plan risk R5: the PC measures it.
- **Kesh's memory sequence** (C4) is a new cinematic look (her point of view a thousand years ago: the ring new,
  unweathered). It may need a "new" material variant of the singers. Cinematics and creatures decide.
