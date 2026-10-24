---
id: M3-ENV-08B
title: "The Seventh Terrace: one hero ship for Ch1's mooring and Ch4's derelict (boardable, sails set and lowered)"
role: environment
status: todo
owner_session: ""
depends_on: [M3-ENV-08, M3-ENV-07]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
Follow-up to M3-ENV-08 (filed by env-art when the Brightwater ferry kit landed without the derelict the party
boards). act1_ch01.md §9: "Build it once": the *Seventh Terrace*, a red-and-black lacquered Pemakar copper coaster
with copper sheathing and a carved stern name-board, is moored at Oruvel in Ch1 (O07, O13) and drifts as the Ch4
derelict (act1_ch04.md C4-11 to C4-14, its §9 request): a boardable main deck, the galley (four bowls on the
table), the hold (copper ingots, a lamp-housing prop), the stern **name-board** (the same hero prop in both
chapters: D06 must match O07), sails **set** (wind-filled, slightly torn) with a **lowered** state for C4-14,
spawn membrane on the rigging for the Spar-Wraith's arena, fenders and boathooks between the hulls (never a
lashing).

## Acceptance criteria
- [ ] Design notes: a section in docs/kb/art/environments/brightwater_ferry.md (or its own sheet) with D01–D08,
      checked against act1_ch01.md §9 and act1_ch04.md §5, §7, §9, and the colour script's `ch04_derelict`
      sub-frame once Rendering adds it.
- [ ] The hull from the Brightwater kit's `bf_common.HullForm` (the same plank vocabulary as the ferry and
      `arena_derelict_deck`), Pemakar lacquer and copper sheathing; LOD chains; materials by script; PROVENANCE;
      `verify_blender_builds` identical.
- [ ] The two states (moored and crewed for Ch1; sails set, then lowered, for Ch4); the name-board a separate
      hero piece.
- [ ] A preview view per chapter on lavapipe; at most one new baseline.

## Notes
- Coordinate with M3-ENV-07 (Oruvel raft-town) for the Ch1 mooring before building.

## Review log
