---
id: M3-C01-101
title: "Ch1 Oruvel Underway wears env-art's drowned-tower kit, under the sea and the UnderwaterRig"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M3-C01-02, M3-ENV-05, M3-C06-1200]
reviewer: lead
milestone: M3
---
## Goal
Queue item 6, the Ch1–Ch3 polish. The Underway (`ch01/oruvel_underway`) is the first zone of Act I once the M2
switch flips, and it played as grey boxes under a stand-in murk. Env-art's M3-ENV-05 left a swap-in note for this
track (in its task file). Take the kit, the rig and the ch01 frame into the zone.

## Decision: dress the rooms in place
The swap-in note's anchors are the tower's real frame: floors stacked from F9 (−22.4) to F14 (−6.4) inside one
36 × 12 m footprint. The greybox lays those floors side by side at y 0, which has two consequences:
- **The zone map (ui-menus) draws them top-down.** Its POIs are pinned to the greybox x/z.
- **The map reads floors and walls by absolute height** (`zone_map_menu.json` "greybox": a floor tops out at 0.35 m).

Moving the rooms to the tower frame would break the map, so the rooms stay where they are. Instead:
- **Walls on the kit's grid.** Each room's walls move onto the kit's 6 m grid (at most 1 m). No trigger, spawn or
  POI moves; the old tin moves 3 m into the squared alcove.
- **Kit cells.** Each room is a run of the tower's own cells: slabs on the floor, bays and corner piers on the wall
  lines, and the story props on their blocks.
- **Depth by lighting.** Water sits at y 10, so the camera, which orbits about 4.5 m up, stays under the surface.
  Each room is lit as at its real depth (crown 6.4 m, bell-room 9.6 m, galleries 22.4 m), using the kit preview's
  arithmetic: the sun and the ambient are tinted by the rig's transmittance, and the lighting area scales the
  ambient and the in-scatter.

## Acceptance criteria
- [x] `tools/ch01/ch01_underway_dressing.py` (`--check` in the tools suite) generates `oruvel_underway_dressing.json`
  and copies the kit's ch01 frame next to the zone. It places 150 pieces:
  - **Crown:** broken bays, the collapsed slab and the tether line.
  - **Bell-room:** sealed, with the hinge door and the tether's slot.
  - **Galleries:** the four lamp-columns on their blocks, the stair flight and the divers' cord at the lip, the tin
    alcove behind two coral curtains that follow `CoralCurtain`.
  - **Gauge room:** the gauge wheel and its cut hub, and the current shaft.
- [x] `oruvel_underway.tscn` has the lagoon WaterSurface, a Tide at y 10, the Dressing, the `UnderwaterRig` (its halo
  on the zone's shutter lantern, so there is no second lamp), and the low lights as a held GlimmerField below the
  stair. The layout's `underwater.glimmer` opens the glimmer gate.
- [x] `Ch01UnderwayZone`:
  - per-room lighting from the layout's `underwater` block (`room`, `update_room`, `apply_lighting`);
  - `swaps` (`GaugeWheel` → `GaugeWheelCut` on `ch01_cut_gauge_wheel`, live on `EventBus.flag_changed`);
  - the sun follows the kit frame (42° / 105°, `#FFEFE1` at 3.0) before the depth tint.
- [x] The zone is in the five underwater entries of `prewarm_materials.json` (tech/underwater.md).
- [x] Tests: `test_ch01_underway_kit` covers:
  - the greybox is hidden;
  - every slab lies on a floor and every bay or pier on a wall line;
  - the rooms are lit by depth, and every spawn is in a lit room;
  - the cut wheel swaps in.

  The ch01, zone_map, objective, debug_overlay, kit_dressing, underway, undertow_shaders and character_shading
  suites all pass.
- [ ] PC shots `ch01_underway_crown` and `ch01_underway_gallery` (RENDER-REQUEST in the slice-polish live log), then
  a placement pass on what they show.

## Not yet (next passes)
- **The seafloor terrace and the canyon lip** around the galleries (`seafloor_*`, `sand_drift`, the dead ship) and
  the breach. These wait for the first render.
- **The bell-room's air pocket**, a second WaterSurface (U03). It needs Rendering.
- **The hull keels over the crown (U01).** The water had to go up to y 10 for the camera, so the keels would hang
  in the camera's path.
- **Real per-area lighting in the rig** (M3-RND-24) replaces the zone's stand-in arithmetic.

## Review log
