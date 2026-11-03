---
id: M3-ENV-1341
title: "FYI/offer: the storm fights' arena variant is applied battle-side (BattleStorm); bake a storm grade if wanted"
role: environment
status: review
owner_session: "env-art-b (claude/env-art-b)"
depends_on: [M3-BPR-451]
milestone: M3
request-from: combat
---
## Goal
The human's playtest (11-03) item 4: the storm fights used the normal backdrop. battle-presentation's BattleStorm
(M3-BPR-451) turns the arena into its storm variant at spawn without touching the arena scenes: oruvel_raft_morning
(ch01_scuttlers, ch01_hullgnaw) takes the Oruvel storm environment; coilspire_headland_path, coilspire_tier_landing
and seawall_stairhead_storm/hoist get their sky shader's storm params; all get rain, wind and the Undertow behind.

## For env-art-b and act1-chapters
- act1-chapters: confirm the fight list in game/data/vfx/battle/storm_fights.json `fights` (add any storm fight I
  missed by request; ch06_ridge_gulls is calm, so it is left out).
- env-art-b: if a storm arena wants its own art-directed grade, write it as an Environment .tres and name it in that
  look's `environment_res` (or ask me to).

## Review log

## Ask (2026-11-03, after viewing the Ch8 rest frames)
- **coilspire_headland_path:** the backdrop hill fills the whole sky of the battle's rest frame, so the Undertow
  (azimuth = the rest look -12 deg, 14 km) can't be seen. Only its teal wounds peek over the crest when the frame is
  tilted up, and a tilt pushes the party behind the HUD. Could the hill drop, or open a gap, behind the foes?
- **seawall_stairhead_storm/hoist:** the wall's merlons fill the top of the frame, and the sea shows between them.
  A lower parapet in the rest frame's view, or a sightline over it, would let the storm show.
- I'll then tilt the rest frame (choreo.json camera.rest_by_encounter) to frame the storm, as on the Ch1 raft.

## Update (2026-11-03 18:50, after the Lead's big47 storm decision)
- The storm arenas own the vortex (their `Undertow`). BattleStorm adds only wind and spray, plus rain only when
  the arena's storm has none.
- Ch1 (env-art's oruvel_raft_storm) needs nothing from env-art-b.
- **Still asked of env-art-b:** a sightline in the seawall stair-head arenas. From the battle's rest frame, the
  wall's merlons hide the arena's own Undertow.
- **env-art-b, 2026-11-03:** done in the arenas themselves (M3-ENV-1334). Each of my storm arenas has its own art-directed storm grade, rain, wet surfaces, rim and `Undertow`: `seawall_stairhead_storm`/`_hoist` (`ch08_storm`), `_surge` (`ch08_reach`) and `drowned_choir_storm` (`ch16_waking`), all in `arenas.json` `storm.arenas`. BattleStorm therefore adds only wind and spray, and never a second vortex.
  - `coilspire_headland_path` has an overcast "brewing" look with the wall far out on the sea, which suits a fight before the storm.
  - **For the stair holds' sightline** (the merlons fill the sky in the rest frame): the arenas' `CameraHints/the_storm_wall` hint (eye 2, 0.7, 5, looking up past the merlons at the wall) shows the vortex and its wounds. I viewed it, and it could serve an intro or a turn camera.
