---
id: M3-CIN-1220
title: Act I cutscene walks stay on the floor (the quality bar on the kit zones): waypoints, marks, off-screen places
role: cinematics
status: review
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M3-CIN-1221]
milestone: M3
request-from: ""
---
## Goal
The sequencer's `@mark` walks an actor to a mark in a straight line with its height lerped. On the kit zones' heights
(ADR 0200) and on the greybox zones' houses, tables and rails, 66 Act I walks leave the floor or pass through
something (a rail on the mole, the Fisher Stair walked as a slope through the air, Pemakar's harbour to its crown,
the galleries' platforms, Tamsule's decks over the water). `tests/integration/test_act1_cutscene_walks.gd` replays
the Act I chapter threads and checks every seen walk from where the actor really stands; the walks still to fix are
in `tests/integration/act1_cutscene_walks_known.json` (the test fails on any other, and on a listed one that's clean).

## Fixes, by kind
- **A path:** `via=` marks round the obstacle or down the stair (needs M3-CIN-1221's sequencer patch).
- **A mark in the wrong place:** move it.
- **A walk nobody should see** (from one end of a zone to the other between beats): the zone's states / variants /
  `stand` put the actor at the start before the scene, or the script fades.

## Progress (act1-chapters, 2026-10-27)
- Everything that a mark, a collider or a flow step can fix is fixed: 33 left of 66, and every one of them is a path
  (`via=`). They are written: `docs/kb/tech/act1_walk_vias.patch` (`via=` on 36 cues in 19 `.dlg` files, and their compiled
  JSON) applies on top of M3-CIN-1221's `cutscene_mark_via.patch`. With both applied, the audit sees one walk left,
  `ch08_wall_falls` `figure_gone` (the stranger walks off the broken wall into the dark: `exempt`, by design).
- When M3-CIN-1221 lands: apply `act1_walk_vias.patch`, run `--filter=act1_cutscene_walks` (it then asks for every
  listed walk to come off the list) and empty `known`.
- Coilspire: the shell and the tiers collide from LOD1 with their doorways from LOD0 (ZoneKitDressing
  `collide_lod0_in`: LOD1 triangles clipped out of the boxes, LOD0's clipped in); `test_ch08_coilspire_walkable` walks
  the hall door, the hut door, the gallery door and all five flights. Corrow's wall boxes overlap at the arc's joints
  (a 4 cm crack swallowed a walk on Ch9's road). Ch9: a path down Pell's rocks (`RocksDown`). Ch5: the scene changes
  stand the walker near the scene first (`place_actor` steps in ch05.json); Ashcrown's chamber door is open.

## Done (act1-chapters, 2026-10-28)
- M3-CIN-1221 landed in b2d39f8cc. `act1_walk_vias.patch`'s 36 `via=` cues are applied (the .dlg hunks; the compiled
  JSON from dlgc; ch08_beacon_opened keeps its 0.6 s hold after Toma's run). 28 of the 30 known walks came clean.
- The last two (ch04_long_way_round's causeway) started from the dock on the old greybox: the dawn now stands Asha
  at her shell, Toma by the wall and Neme beside them (`dawn_neme`) before the scene, Ysolde (the night's stranger)
  is hidden at dawn, Asha's via no longer starts at `dock_shore`, C01 looks down the path from behind the three and
  the holds fit the 36 s walk (C01 14 s, C02 18 s; the scene no longer runs on in black). Known list: empty.

## Acceptance criteria
- [x] The known list is empty; the test stays in the suite.

## Review log
