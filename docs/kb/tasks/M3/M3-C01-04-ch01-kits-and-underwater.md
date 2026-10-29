---
id: M3-C01-04
title: Ch1 kits swap-in (raft-town, drowned tower) and the Underway's underwater look
role: environment
status: review
owner_session: "env-art (claude/env-art, 2026-10-29)"
depends_on: [M3-C01-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch1's two zones are greybox blocks: `game/levels/ch01/oruvel_underway/` and `game/levels/ch01/oruvel/`. Their story data doesn't depend on the blocks. Swap in the kits that act1_ch01.md §9 asks for:
- the drowned-tower kit for the Underway: lamp-columns, bell-rooms, coral curtains, the stairwell with its cord, the gauge-wheel and the shaft;
- the raft-town kit for Oruvel, with its storm rig. The layout's `storm` block names what the rig must hide and show, and the two lashings that free the low hull.

Keep every spawn, trigger and shot id. For the Underway's look, put in an `UnderwaterRig` (docs/kb/tech/underwater.md; with rendering) and drop the stand-in sun, environment and `fog`. Then add the Underway's scene to `prewarm_materials.json`.

## Acceptance criteria
- [ ] Both zones play `tests/integration/test_ch01_thread.gd` unchanged.
- [ ] Every route can be walked with the kit's collision. The greybox has no step-up, and Oruvel's sea is a walkable floor today; replace it with rails.
- [ ] The shots U01–U11 and O01–O18 are composed on the kit (`oruvel.md`, §9 Art 3).

## Notes
- 2026-10-27 (env-art): the swap is a zone-scene change in `game/levels/ch01/**` (slice-polish's), done the way
  act1-chapters swaps Ch4–Ch9: `ZoneKitDressing` (ADR 0200, on `claude/act1-chapters`) with a generated layout from
  the Oruvel and Underway kits' preview layouts. Env-art builds any piece the swap finds missing: file a
  `role: environment` task, as M3-ENV-1201 and M3-ENV-1203 did.

## Checked (env-art, 2026-10-29)
- Both zones mount env-art's kit dressing (`ov_zone_dressing` / `ou_zone_dressing`, ZoneKitDressing, M3-ENV-738/740);
  the Underway carries `UnderwaterRig`. Godot `--filter=ch01_thread` 2 run, 0 failed. Routes walked at player eye on
  10-28 and 10-29 (walls on the greybox's lines, test_underway_walk); Oruvel's commons, gulls, beacon and storm sky
  finished under M3-ENV-104. The U/O shots render on the kit (the gate re-approves their drift).

## Review log
