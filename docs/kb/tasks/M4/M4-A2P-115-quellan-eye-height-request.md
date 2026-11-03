---
id: M4-A2P-115
title: "Quellan at eye height: a spawn in the dark, mirror-flat slabs under houses, a pixelated rock face"
role: environment
status: review
reviewer: environment (env-art-b)
owner_session: env-art (claude/env-art)
depends_on: []
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

## Notes
- 2026-11-03, env-art: all three came from one cause plus a bare terrace, in `keth_zones.py` (env-art's Keth kit).
  - **The cause:** `zone_height` raised a crag behind every cliff block with no limit on how far behind it reached.
    So the road-up walls (`RoadUpWallW/E`) lifted everything west of x 53.75 (and east of 58.25) into a 19–21 m mesa.
    That made:
    - (3) the sheer face beside the gate at x −6.5 (its "pixelated" look was triplanar rock seen 2 m away);
    - (1) rock all round the FromCloudloom spawn;
    - the terrace sunk in a pit.
  - **The fix, three per-zone tables:**
    - `CLIFF_BAND_M`: the road walls' crag stops 10 m behind them, then falls to the valley.
    - `CLIFF_SHOULDER`: the road's crag follows the road's own height with a 0.9 m shoulder.
    - `CLIFF_NOTCH`: the mountainside behind the terrace gives way within 4–22 m of the road, so the road is cut
      into a hillside.
  - Keth Pass and Cloudloom grounds rebuilt byte-identical.
  - **(2):** the yards are flagged (the new piece `quellan_yards`, keep 0.55, the turf in the gaps; its own glb, since
    `quellan_town` is at the 5 MB rule), and every house stands on a dry-stone footing course (0.32 m, 0.14 m proud).
  - **Viewed** (walk stills, the 12 views env-art-b took):
    - FromCloudloom looks down the road over the town, between lit hillside slopes;
    - west of the gate is a low parapet over the valley;
    - the square is flagged round footed houses.
  - Test `test_quellan_falls_to_the_valley_and_its_road_top_looks_out`.

## Review log
