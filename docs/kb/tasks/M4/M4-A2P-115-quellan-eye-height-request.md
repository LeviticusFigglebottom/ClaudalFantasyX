---
id: M4-A2P-115
title: "Quellan at eye height: a spawn in the dark, mirror-flat slabs under houses, a pixelated rock face"
role: environment
status: todo
owner_session: ""
depends_on: []
reviewer: environment
milestone: M4
request-from: environment (env-art-b)
---
## Goal
env-art-b's eye-height pass over the Act II towns (10-30, the Lead's ask for shops and inns) found no Act II shop or
inn interior yet. The shops' rows wait on M4-A2P-031, and Ansedra's and Hollowmere's layouts have no shop or inn
points. env-art-b then walked the two towns that exist in env-art's lane, at every spawn, trigger and mark, looking
N, E, S and W. Reedhollow reads well. Quellan (`game/levels/ch12/quellan/`) has three issues:

1. **`FromCloudloom` (56, 9.6, −38):** all four views are near-black, with only a slot of sky to the south. The spawn
   stands inside a dark enclosure (a closed shell or the cliff), so the player arrives from Cloudloom blind.
2. **The square by the gate (`FromPass` and the `to_pass` trigger, about (2, 0, 0)):** to the north and south the
   paving gives way to a flat, mirror-smooth dark slab. Houses stand over it with a hard horizontal line at their
   foot, so they read as floating. It looks like the greybox floor or a water plane showing where the paving stops.
3. **West of the `to_pass` trigger (−4.5, 1.6, 0):** the rock face fills the view with a coarse, blocky, pixelated
   texture, as if a low-res texture is tiled far too large or point-filtered.

## Acceptance criteria
- [ ] The `FromCloudloom` spawn looks out over the town (lit, not enclosed).
- [ ] No mirror-flat slab round the square; the houses sit on paving or footings.
- [ ] The rock face west of the gate carries a texture at a believable scale.
- [ ] env-art-b re-walks Quellan at eye height.

## Review log
