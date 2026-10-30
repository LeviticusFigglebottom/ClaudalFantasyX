---
draft: pre-gate
zone: ch17/hollowmere, first visit (Ch15's dawn; Act III's Ch17 reuses the zone)
kit: hollowmere.py (M3-ENV-723; art sheet hollowmere.md); grades assets/environments/zones/ch17/
task: M4-A2P-045 (with M3-ENV-723)
author: env-art-b, 2026-10-30
---
# Hollowmere, first visit: kit spec

**The read (Ch15):** dawn fog, a current-song, and Hollowmere answers. Grey-rose light, the first oil lamps on the
hulls, warmth returning low. Act III's dusk grade (Ch17) is the same zone later. **Build it once, at final quality.**

## The greybox it replaces
The `Dock` (64 × 4) with eighteen piles, rails and bounds; three `Jetty*` (16 × 4) to three `HousePlatform*`
(10 × 8) with `HullHouse*`; the `PyreRaft` (3 × 4); the `Ship` (16 × 3 × 5: the Hollowmere ship that carries the
party to the Rim in Ch16); `Water`/`Bed` 130 × 90. Spawn `Dock`; trigger `ship`; shot `H01`.

## Pieces
| Piece | Source | Where |
|---|---|---|
| `hm_lashed_hulls` | exists | the homes: on the three house platforms, and 8–12 more in lanes 4–6 m wide round them (the art sheet's composition) |
| `hm_windmill` | exists | the outer edge, 4–6 |
| `hm_tide_wheel` | exists | in the channels between homes, 3–4 |
| `hm_signal_lamp` | exists | at the lane corners, lit (bound teal): the only cool light |
| `dace_hull_frame` | exists | **Ch17's heart; in Ch15 it stands at the zone's edge** (seen, not visited: the beat is Liss and her father) |
| `hm_far_flotilla` | exists | the raft-city beyond, 220–460 m |
| **`hm_dock_6m`** | **new** (`b_hollowmere.py`) | the dock and the jetties: a floating timber walk on log pontoons, lashing, bollards; along `Dock` and each `Jetty*` |
| **`pyre_raft`** | **new** | Tobin's pyre-raft: a small log raft with a driftwood bier and a folded red cloth; Toma carries him to it. **Unlit until the cutscene lights it** (cinematics) |
| **`hm_ship`** | **new** | the Hollowmere ship that waits and later carries them south (also Ch16's `Ship` at the Rim): a twin-hulled Saltwright trader, sand-cloth sails, Lit Age plating patches |
| **`hm_supper_table`** | **new**, small | the side scene's supper (C8): a deck table, stools, bowls, an oil lamp |
| **`hm_oil_lamp`** | **new**, small | the first oil lamps on the hulls at dawn: a hanging clay lamp, its flame a real light |

## Materials
Every `hollowmere.py` slot is the Haluna kit's woven, timber and thatch shaders, plus `kit_bound_core` and
`kit_salt_glass` for the signal lamps. **No flat slot needs a zone look**, except `kit_bound_core` (flat,
emissive), which stays `glimmer_bound`, steady.

## Lighting
- **Ch15 dawn (05:40, the colour script):** fog `#1C3A4A` → grey-rose, density **0.03**; no sun yet (−5°, east);
  sky grey-rose at the horizon; the oil lamps on the hulls warm (`#FFB16E`, small, each on its lamp); the signal
  lamps teal. **Needs a new grade:** `hollowmere_dawn_environment.tres` and a LUT (`lut_ch15_hollowmere_dawn`)
  from `hollowmere_grades.py`. The zone already has the Ch17 dusk grade (`ch17_hollowmere_dusk_environment.tres`,
  `lut_act3_dusk`).
- **Ch17 dusk** (Act III, later): the existing grade, the gold returning.

## Shot list
| Id | Frame |
|---|---|
| `H01` | arrival out of the fog: the first hulls and a signal lamp |
| `ch15_hollowmere_dock` | the dock at dawn: Liss's father waiting, oil lamps on the hulls |
| `ch15_hollowmere_lanes` | a water-lane between homes: windmills, a tide-wheel turning |
| `ch15_hollowmere_pyre` | the pyre-raft at the dock's end |
| `ch15_hollowmere_supper` | the supper table (C8, Rhen and Liss's father) |
