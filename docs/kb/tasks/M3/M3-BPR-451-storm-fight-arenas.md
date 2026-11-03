---
id: M3-BPR-451
title: "FAST-TRACK: the storm fights show the storm (sky, rain, wind, the Undertow behind)"
role: combat
status: doing
owner_session: claude/battle-presentation
depends_on: []
milestone: M3
reviewer: environment
request-from: lead
---
## Goal
The human's playtest (11-03): the seagull/storm scene's fights used the normal sunny backdrop and never showed the
Undertow. The storm fights (Ch1 after the Rising: the scuttlers and Hullgnaw; Ch8: the headland path, the tier
landing, the three stair holds and the Reach) get their storm variant, battle-side.

## Acceptance criteria
- [x] game/data/vfx/battle/storm_fights.json: fights -> looks (an undertow.json preset, the sky, the sun, rain, wind).
- [x] BattleStorm (game/vfx/battle/battle_storm.gd): the arena's sky turned to storm (a duplicate; the arena scenes
      are untouched), the sun dimmed, rain and wind over the field, the Undertow in the battle camera's view, no
      screen flashes; tests/unit/test_battle_storm.gd.
- [x] Self-rendered the Ch1 and Ch8 storm fights, viewed. Ch1 (the gulls/Rising fights): the Undertow's wall fills
      the sky over Hullgnaw (rest frame tilted 8 deg, choreo.json camera.rest_by_encounter).
- [ ] Ch8: the arenas hide the sky (the headland's hill, the stair's merlons); M3-ENV-1340 asks env-art-b for a
      sightline. The rain, wind, storm grade and dim sun are in.
- [ ] PC-QUEUE: the Undertow's cost in battle on the GPU (hitch bar <= 2 s hidden; frame time).

## Notes
- act1-chapters and env-art-b: M3-ENV-1341 (an FYI and an offer: bake a storm grade per arena if they want one;
  BattleStorm takes it as environment_res).
- audio owns the storm battle music (the Lead's 11-03 item 4).

## Review log
