---
id: M3-C07-1211
title: Ch7 greybox to final, ch07/tamsule_bell_galleries on env-art's Tamsule Bell kit (galleries, platforms, pool, moorings)
role: cinematics
status: review
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M3-ENV-01, M3-C07-02]
milestone: M3
reviewer: qa
request-from: ""
---
## Goal
Swap the story's stand-in for the Bell's galleries to env-art's kit in the kit's arena frame, keeping every beat
(B04 galleries, B05 naming at the rim, the Reefball seam, B07 after the match, B09 the moorings, the way to the port).

## Acceptance criteria
- [x] `tools/act1/ch07_tamsule_bell_dressing.py`: the dressing (the preview's placement; Oruvel's moorings moved to
      azimuth 325 on the party's side, a boardwalk staging and bridge, Tavi's boat) and the collision (walkways with
      front rails open at the platforms and the bridge, tier fronts, the platforms with rails and ramps to the walkway
      and the prow step, the staging and its bridge, a floor under the water). The story points moved once
      (`--relayout`); the grade and water copied from the preview.
- [x] `test_ch07_thread`, `test_ch07_tidecup_match` pass; `test_ch07_bell_walkable` walks gallery→prow,
      catch-pool→moorings, entrance→port, and checks the party's marks stand on floors.
- [x] `zone_maps.json` POIs, hints and bounds follow.
- [x] Shots `ch07_bell_galleries`, `ch07_bell_moorings` rendered on the PC, viewed, approved. Baselines approved by the Lead's gates (big13 1fa92b81 / a4410fd9; tracks never write baselines, TRACK-RULES).

## Notes
- The pool's coping has no collision (the divers and the poolkeeper are stage actors on it; Rhen never goes there).
- The bridge's boardwalk is drawn level halfway between the staging (1.6) and the walkway (2.4); its collision is a
  ramp, so feet sit up to 0.4 m off the boards at its ends. A sloped boardwalk piece would fix it (env-art, later).

## Review log
- 2026-10-29 act1-chapters: to review (every criterion met; the stand-ins listed in Notes wait on their own requests).
