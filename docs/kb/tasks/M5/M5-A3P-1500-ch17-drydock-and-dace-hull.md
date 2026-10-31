---
id: M5-A3P-1500
title: "Ch17 Hollowmere: the dry-dock berths and Dace's hull as Rhen finds it (cabin, engine bay, half-rigged sails)"
role: environment
status: doing
owner_session: "env-art-b (claude/env-art-b)"
depends_on: []
reviewer: environment
milestone: M5
request-from: lead (ADR 0207: Act III in the track's own lane)
---
## Goal
The environment half of [act3_ch17.md](../../story/act3/act3_ch17.md) §9 ("the dry-dock berths and Dace's hull
(unfinished Kite) at `ch17/hollowmere`"). Ch17 re-uses Ch15's zone, which env-art-b already dresses
(`tools/act2/ch15_hollowmere_dressing.py`). The new rooms are the berths, the hull's deck, its cabin (the ledger, B05)
and its engine bay (the first lamp, B10).

## The reading (env-art-b's default; the story track may overrule it in review)
The art doc (`docs/kb/art/environments/hollowmere.md`) has the hull as a bare frame, "nothing on it finished". The
Ch17 sheet asks for a cabin, an engine room, a Lit Age brass keel and sails "cut like a flare-kite", and Ch18's Kite
(`kite.py`, env-art) has a hatch amidships with the ledger chest beside it. One hull serves all three:
- **The stern third, decked:** Dace planked both sides of the stern third and decked it, so he could live aboard. A
  hatch drops to the **cabin** in the hold below, with his bunk, the ledger on a fold-down desk, the **chart wall**
  (Corrow circled) and the **tool rack** (his hooks, the make of Rhen's).
- **The engine bay:** forward of the cabin, the hold opens to the first lift-engine bed, empty: the cradle the Kite's
  `kite_engine` will sit in. This is where B10's first lamp is fitted.
- **The bare bow:** the forward two-thirds stay bare ribs, with the near side's five strakes (Ch15's read is
  unchanged from the arrival).
- **The keel** takes a Lit Age brass shoe (`kit_iskarra_bronze`), and **the mast** is stepped with one kite wing
  half-rigged: two of the five battened panels bent on, the rest furled on the boom. That's Virel's shape, planted,
  not paid (B04).
- **Ch15 and Ch17 show the same piece**: nobody has touched the hull in eleven years, so it isn't a variant.

## The berths
`hm_drydock_berth`: an empty floating berth like Dace's (a pontoon, cradle blocks, shear-legs, a fender post at the
outer corner), placed in a row of four along the dry-dock walk, with Dace's at the end (B03: "the last one"). The
**first berth** (B07) gets the old fender post Tobin sat on, its top worn pale, and the rotted keel of a first hull
in the mud under the water.

## Acceptance criteria
- [x] `dace_hull_frame` is revised in `hollowmere.py`: a decked stern with a hatch and a cabin below (bunk, desk and
      ledger, chart wall, tool rack), an empty engine bed, a brass keel shoe, and the mast with a half-rigged kite
      wing. It stays within budget and is rebuilt with its manifest row.
- [x] `hm_drydock_berth` (new) is built and placed four times, the first one with Tobin's post.
- [ ] The zone dressing places them, with walk collision for the hull's deck, hatch ladder and cabin floor, and
      lights for the cabin (one oil lamp) and the engine bed (cold, until B10 lights it).
- [ ] Eye-height renders of the berths at noon, the hull at dusk (H04, H07), the cabin (H05) and the engine bay
      (H09), viewed.
- [ ] PROVENANCE rows; banned-terms clean; tests (`tools/tests/test_hollowmere.py` and the zone's Godot test).

## Requests out
- **act1-chapters / Act III chapters:** the Ch17 marks: the cabin's reading seat, the hatch, the engine bed and the
  first berth's post. The layout is theirs; env-art-b will post the coordinates here when the piece is built.
- **Act III chapters (M5-A3P-1001), the light by beat.** Each beat's `states` row loads its grade by
  `environment_res` (Corrow's dawn row is the precedent):
  - **B06 dusk:** env-art's `res://assets/environments/zones/ch17/ch17_hollowmere_dusk_environment.tres`, with its
    sun row from `ch17_grades.json`.
  - **B08 and B09 night:** env-art-b's `res://game/levels/ch17/hollowmere/hollowmere_night_environment.tres`, with a
    moon for the sun: pitch about -35, colour #8FA6C8, energy 0.3. Viewed at energy 0.3.
  - **B10 morning and B01–B05 day:** the zone's own dawn grade.

## Notes
- 2026-10-30, env-art-b (7fd8e3e5): the hull is revised and rebuilt at 4,648 / 850 triangles (budget raised to 24k / 1.6k).
  Viewed in the zone at eye height from outside, the cabin (desk and open ledger, chart wall with Corrow's red ring,
  tool rack, bunk, daylight through the bulkhead doorway), the engine bay (the empty bed's chocks and bronze ring) and
  the deck (bare ribs forward to the mast, the half-rigged wing overhead). Marks for the Act III chapters, in the
  hull's own frame (x along it, bow +X, y over the water; the zone places it at DACE_AT (78, -24) yaw 30 deg, y -0.9):
  - the hatch: (-3.0, 3.8, 0);
  - the cabin floor: y 1.85, from x -5.1 to -2.0;
  - the reading seat (the stool by the desk, at -0.68): (-2.8, 1.85, -0.23);
  - the engine bed: x -1.6 to 0.4, centre y 2.5;
  - the deck: y 3.8, from x -6.0 to -2.0.
  The walk collision (deck, hatch ramp, cabin floor) comes with the berths' dressing.
- 2026-10-30, env-art-b (07fb3f7f): `hm_drydock_berth` (295 / 126 triangles) and `hm_drydock_berth_first` (837 / 180),
  built with PROVENANCE rows and the kit's import settings. Placed by `ch15_hollowmere_dressing.py` (the zone is Ch15's
  and Ch17's) in a row along Dace's beam, 8.5 m apart: (82.25, -16.64), (86.5, -9.28) and the first at
  (90.75, -1.92), all at yaw 30, the first berth nearest the dock's east end. Tobin's post stands at the first berth's
  outer corner, world (98.7, -2.9), top y 0.85. The rotted keel lies in the shallows off its -X end, around
  (82.1, 3.1). The Ch15 windmill at (76, -10) stood against the row and moves to (66, -14). Viewed along the row from
  the dock's end, and at the post and the keel.
- **Waiting on the Act III chapters:** how the party reaches the row (a gangway from the dock's east end to the first
  berth, and walks between berths). The walk collision for the hull (deck, hatch ramp, cabin floor) and the berths
  follows that layout; env-art-b adds it when the path exists.

- 2026-10-30, env-art-b (8f052ec7): **the dock-master's house** (B07, B11: `fathers_door`, `fathers_table`).
  `hm_dockmaster_house` (4,102 / 368 triangles) is hm_lashed_hulls with the deckhouse furnished: his table and two
  benches, a lamp hook, a shelf of clay jars and a rolled chart, a sleeping mat with a red blanket, and a net on the
  west wall. It replaces HousePlatform1's house, where the greybox's `fathers_door` (28, 0, -16.6) stands. The table's
  centre is world (27.55, y 0, -21.05), for the `fathers_table` mark, with a flickering oil-lamp light 1.6 m over the
  deck. Viewed from inside at the door. Tests: test_ch15_hollowmere_dressing (Ch17 rooms) and Godot
  test_hollowmere_dressing (the light count).

- 2026-10-31, env-art-b (06fb966c): **Ch17's night and the cabin's light.**
  - **The night grade:** `hollowmere_night_environment.tres` is the open sea's Ch15 night (its sky, stars and
    unlamped LUT) with Hollowmere's fog and a little more ambient.
  - **The cabin's light:** an oil-lamp light over Dace's desk, flickering, and its spill up through the open hatch
    (both always on).
  - **Viewed by night:** the cabin is warm on the ledger, the chart wall, the tool rack and the ladder. The deck reads
    by the moonlit water and the hatch's glow.
  - **Tests:** the lamp counts (+2) in test_ch15_hollowmere_dressing and the Godot test_hollowmere_dressing, and a
    night-grade test.

## Review log
