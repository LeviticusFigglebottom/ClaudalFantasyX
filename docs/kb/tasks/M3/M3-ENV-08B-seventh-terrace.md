---
id: M3-ENV-08B
title: "The Seventh Terrace: one hero ship for Ch1's mooring and Ch4's derelict (boardable, sails set and lowered)"
role: environment
status: review
owner_session: "env-art"
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
- [x] Design notes: a section in docs/kb/art/environments/brightwater_ferry.md (or its own sheet) with D01–D08,
      checked against act1_ch01.md §9 and act1_ch04.md §5, §7, §9, and the colour script's `ch04_derelict`
      sub-frame once Rendering adds it. (§7, written before geometry; `ch04_derelict` is still missing from the
      colour script, so the Ch4 view uses a **provisional** frame named as such in §7.4: Rendering replaces it.)
- [x] The hull from the Brightwater kit's `bf_common.HullForm` (the same plank vocabulary as the ferry and
      `arena_derelict_deck`), Pemakar lacquer and copper sheathing; LOD chains; materials by script; PROVENANCE;
      `verify_blender_builds` identical. (13 pieces in the `brightwater_ferry_kit` job: `bf_terrace.py`,
      `bf_terrace_rig.py`; 9 new `bf_*` materials; `verify_blender_builds --job brightwater_ferry_kit --job
      oruvel_kit`: 62 and 42 identical.)
- [x] The two states (moored and crewed for Ch1; sails set, then lowered, for Ch4); the name-board a separate
      hero piece. (`terrace_sails_furled` + `terrace_moored`; `terrace_sails_set` + `terrace_membrane` +
      `terrace_derelict`; `terrace_sails_lowered`; `terrace_name_board`; `alongside_gear`.)
- [x] A preview view per chapter on lavapipe; at most one new baseline. (O07 and O21 in the Oruvel preview, D01–D04,
      D06, D09 in the new daylight derelict scene of the Brightwater preview; one baseline: `oruvel_o07_name_board`.)

## Notes
- Coordinate with M3-ENV-07 (Oruvel raft-town) for the Ch1 mooring before building. (Done: oruvel.md §0's outer
  mooring at (−58, 8); the stage raft is the Oruvel kit's `raft_deck_small`.)
- **Why the Brightwater job, not a new one:** the hull *is* `bf_common.HullForm` and its plank, bulwark and deck
  helpers, the slots are the kit's `bf_*` materials and import kind; a separate job would need a second import kind
  and material folder for one ship that shares all of them. Adding modules left every ferry output byte-identical.
- Found while building: the ferry's transom (`bf_common.transom`, M3-ENV-08) is wound against its normals, so it is
  culled seen from astern (no ferry baseline sees it). Not fixed here; a one-line fix for env-art (it moves
  `ferry_hull.glb`).
- Gotcha: `bf_import_settings.py` also patches `lut_ch04_crossing.png.import` with the 2D PNG settings; restore it
  with git after running the script.

### Swap-in note for m2-slice (the Seventh Terrace in both chapters)
All pieces are in `res://assets/environments/kits/brightwater_ferry/` (kit kind `brightwater_ferry_kit`, materials
`.../materials/`). Her frame: bow −Z, origin on the centre line at main-deck level amidships, waterline at y −1.5
(place her origin 1.5 m above the sea). Every piece below is placed at her origin unless stated; constants are in
`assets_src/environments/kits/brightwater_ferry/bf_terrace.py`.
- **Always:** `terrace_hull`, `terrace_galley`, `terrace_hold`, `terrace_rig`; `terrace_wheel` at `WHEEL_AT`
  (0, 2.02, 7.0) in her frame, its own node so the zone can turn it about its local Z ("the wheel turning by
  itself", C4-11).
- **Ch1, `ch01/oruvel`, moored and crewed (C1-09, O07):** her origin at (−58, 1.5, 8), yaw 0 (bow north); add
  `terrace_sails_furled`, `terrace_moored` and `terrace_name_board` at `NAME_BOARD_AT` (0, 0.95, 10.035) in her
  frame (world (−58, 2.45, 18.035)); the Oruvel kit's `raft_deck_small` at (−51.33, 0, 9.4), yaw 0, is the stage
  her lines, fenders and gangplank meet. Placement as built: `game/levels/_tests/oruvel_kit/oruvel_seventh_terrace_layout.json`
  and the stage in `oruvel_layout.json` (copy, do not reference). O07's camera: eye = board + (0.6, −0.25, 9.0),
  target = board, vFOV 16.1 (85 mm).
- **Ch1 O13 (C1-12, casting off):** swap `terrace_sails_furled` + `terrace_moored` for `terrace_sails_set` (under
  full sail, running); the storm grade is the storm variant's (M3-ENV-07B).
- **Ch4, `ch04/brightwater_ferry`, the derelict (C4-11 to C4-14):** her origin 9.24 m to port of the ferry's,
  0.1 m lower (the ferry's waterline is −1.6 in its frame), 1.0 m aft: `bf_terrace.DERELICT_IN_FERRY`; both bow
  north. Add `terrace_sails_set`, `terrace_membrane`, `terrace_derelict`, `terrace_name_board` (as above), and
  **`alongside_gear` at the ferry's origin** (its frame is the ferry's: fenders on her port side, three boathooks
  across to the derelict's cap rail). **No lashing anywhere** (tested: no rope crosses the gap).
- **C4-14, after the Canticle:** hide `terrace_sails_set` and `terrace_membrane`, show `terrace_sails_lowered`;
  remove `terrace_name_board` when Rhen takes it (the hull keeps its two copper brackets). The preview does this
  with `setup.nodes` on dressers `SailsSet` / `SailsLowered` / `NameBoard` (D09).
- **Collision (m2-slice's; the kit exports no `-col` proxies, as the ferry):** walkable boxes in her frame,
  `bf_terrace.WALK`: main deck x ±2.6, top y 0, z −9.4 … 5.2; poop x ±2.1, top y 1.0, z 5.2 … 9.7; hold floor
  x ±1.4, y −1.9, z −5.3 … −1.9 (down the ladder at the main hatch's fore end, hatch x ±0.9, z −4.4 … −2.8). The
  galley's floor is the main deck (door 0.84 m wide in its fore face at z 2.4; inside x ±1.6, z 2.4 … 5.0). Block:
  the bulwarks (cap rail 0.95 m), the galley's walls, the hatch coaming (0.42 m), the poop's breast rails except the
  two ladders at x ±2.15. The gangways (z 0.9 … 1.9, both sides) are open: C4-11's boarding place. The derelict
  layout's `anchors.walk` gives the same boxes in the preview's world frame.
- **The boss arena (C4-13):** the deck round the mainmast (z −0.6) is clear from the hatch's after coaming (z −2.8)
  to the galley's door (z 2.4), the full beam athwart; the fife rail stands 0.7 m forward of the mast.
- **Light:** nothing on her emits but `bf_spawn_wound` (the membrane's seams, faint); the lamp-housing in the hold
  is dead. The Ch4 grade is Rendering's `ch04_derelict` (provisional values in brightwater_ferry.md §7.4).

## Review log
