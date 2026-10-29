---
id: M3-ENV-1317
title: Ch5–Ch9 zones walked at player height along the critical path
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: []
milestone: M3
reviewer: art-direction
---
## Goal
The Lead's pass (2026-10-28): each Ch5–Ch9 zone at player height about every 30 m along its critical path
(spawn to story triggers in order), checking for bare walls, floating props, seams, flat lighting, empty corners and
repetition.

## Notes (2026-10-28, env-art-b)
- 44 views, eye 1.6 m, in a scratch rig (not committed).
- Fixed: **Ch6's camp now burns** (the kit's new fires at the hulk and the tide-wheel, following the `Smoke` block, so
  they go out when the evening camp is made). `tools/act1/ch06_brine_shoals_dressing.py` RAID_FIRES.
  `test_zone_kit_dressing` now counts the Smoke block's eight followers (FAST-TRACK for act1-chapters).
- Not mine, filed as M3-ENV-1316 to env-art: the trader boat's white bales, Ashcrown's flat stair and tier faces,
  the headland's far facets.
- Seen and left, not set issues: the party's and NPCs' capsule stand-ins at spawns (characters); Pemakar's party
  lanterns (act1-chapters' rig). Eye-height cameras clip into the flying stair, the causeway steps and the headland
  path where the path climbs; that is the rig, not the zone.
- Tests: `--filter=` ch06 5/0, ch07 18/0, zone_kit 11/0, cutscene_walks 1/0. Self-rendered ch06_brine_camp.

## Review log
