---
id: M3-C01-04
title: Ch1 kits swap-in (raft-town, drowned tower) and the Underway's underwater look
role: environment
status: todo
owner_session: ""
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

## Review log
