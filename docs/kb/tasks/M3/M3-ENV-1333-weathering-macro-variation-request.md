---
id: M3-ENV-1333
title: "env_weathering: a world-space macro variation, so a far slope isn't one flat tone (PC pass 7 row 80, Pemakar's hillside)"
role: environment
status: todo
owner_session: ""
depends_on: []
reviewer: environment
milestone: M3
request-from: environment (env-art-b)
---
## Goal
The PC's pass 7, row 80: the Pemakar hillside behind the village is one flat brown untextured surface, and the
big37 re-measure found it unchanged.
- **The piece:** `mountain_massif` (Pemakar kit), which an id-pick confirms, seen at its LOD1, in `kit_volcanic_far`.
- **What env-art-b tried in the zone, reverted, all viewed in ch05_pemakar_harbour_day:**
  - More relief and cavity shading: no visible change, because the 8 m tile mipmaps to one tone at 100–400 m.
  - A 40 m tile: the far slope still read smooth, and the near slope (the same mesh, by the harbour stairs) turned
    into huge dark pore blotches.
- **The gap:** `env_weathering` has no large-scale term. `variation_value` is per piece, and the massif is one piece.

## Ask (env-art: `game/shaders/environment/**`)
Add an optional world-space macro layer to `env_weathering_body.gdshaderinc`: a low-frequency noise of a few tens of
metres from the detail texture or a 3D noise. It would darken and tint the albedo (scree vs ash vs moss) and bend the
normal, fading in with distance so near views keep the fine tile. Then turn it on in `kit_volcanic_far` (and
`kit_ash_soil`, if it helps).

## Acceptance criteria
- [ ] `ch05_pemakar_harbour_day` and the PC's view of the hillside show slopes with patches and gullies, not one tone,
      while the near slope by the stairs keeps its fine grain.

## Review log
