---
id: M3-ENV-05
title: Ch1 the lamp-diver's sea floor: Oruvel Underway, the drowned tower (kit at final quality)
role: environment
status: review
owner_session: "env-art worktree"
depends_on: [M2-ENV-06]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The Lead's env-art standing queue (2026-10-24; the human authorised M3 work in parallel): Ch1 "Lamp-Diver" from
docs/kb/story/beats/act_outline.md, zone `ch01/oruvel_underway`. Rhen's tutorial dive: a drowned tower and the sea floor around it, lit by his lantern, under the underwater look from M2-RND-02 (docs/kb/tech/underwater.md, the M2-ART-02 sign-off and its M2-RND-09 fixes). Salvage, collapsed floors, seagrass and coral growth, Lit Age fragments, the Hullgnaw's ship's ribs as a landmark.

Gameplay placement (spawns, triggers, NPCs, collision tuning) is m2-slice's: hand it over as swap-in notes in
docs/kb/handoffs/live/env-art.md.

## Acceptance criteria
- [x] **Design notes first:** `docs/kb/art/environments/<zone>.md` in the haluna.md format (mood in one line,
      layout and orientation, lighting sub-frame and grade from color_script.md, kit table with dimensions,
      materials against palette.json, composed shot list with lenses), reviewed against the act outline and the
      story bible before any geometry; references in words only (references.md).
      → `docs/kb/art/environments/oruvel_underway.md` (committed 3b154cd6 before any geometry; checked against the
      act outline Ch1, the Ch1 beat sheet act1_ch01.md C1-02–C1-07 and its §7 shot ids and §9 request, bible §3
      Oruvel, decisions_log N-02, the colour script `ch01` row and its underwater notes, tech/underwater.md, M2-ART-02's
      review log and M2-RND-09; revised after the preview, see its Revisions).
- [x] A procedural kit in `assets_src/environments/kits/<zone>/` with its own Blender job, LOD0/LOD1 within
      budgets and chained per vegetation.md "One LOD at every distance", vertex-colour weathering per haluna.md
      §4, materials written by script, PROVENANCE rows, `verify_blender_builds` byte-identical, every file under
      5 MB, no reference images, packs or AI generation.
      → `assets_src/environments/kits/oruvel_underway/` (30 pieces), job `oruvel_underway_kit` (threads pinned at 4;
      the glbs, manifest, maps and materials: 60 files identical), its own import category `oruvel_underway_kit`.
- [x] An Environment-owned preview scene with composed views of the design notes' key shots, viewed on lavapipe
      and iterated to final quality (pillar 2, the palette, the colour script). Register at most the two most
      telling shots as screenshot baselines (the repo's binary budget).
      → `game/levels/_tests/oruvel_underway_kit/` (7 views, on the existing `UnderwaterRig`); baselines
      `ou_u04_lamp_gallery`, `ou_u12_terrace`.
- [x] Tests for anything with runtime code; a swap-in note for m2-slice.
      → `tools/tests/test_oruvel_underway_kit.py` (18), `tests/unit/test_oruvel_underway_preview.gd` (6); swap-in
      note below (this task file; docs/kb/handoffs/live/env-art.md is the Lead's to merge).

## Notes
- **Kit** (generators import the Haluna kit's `kit_common.py` read-only, as Brine Shoals does; no Haluna file edited):
  - Sea floor: `seafloor_patch_a/b` (12 m cells, edges at y 0, any yaw), `seafloor_edge` (the podium's broken lip
    and a 14 m face, periodic so a row joins), `seafloor_far` (492 m apron, 132 m hole, the canyon floor south),
    `sand_drift` (the tongue through the breach).
  - Tower: `tower_bay`, `tower_bay_solid`, `tower_bay_broken` (6 × 3.2 m; ceramic cladding in a sill and a spandrel
    band, half fallen), `tower_pier`, `floor_slab` (coffered, silt drifts with natural contours),
    `floor_slab_broken` (one part hanging 24° on its rebar: a tether drop), `bell_room` (dry walls above the air
    line, calcite tide-ring and drips), `current_shaft` (one storey, stacks; weed streaming up), `stair_flight`.
  - Lit Age and salvage: `lamp_column` (fluted ceramic, empty brass housing, two dark shards, nothing lit),
    `lamp_column_fallen`, `lit_fragments`, `gauge_wheel` and `gauge_wheel_cut` (same seed; the rim gone, bright cut
    faces), `hinge_door` (a bay with the door on three hinges, the top one cut), `pipe_run`.
  - Growth: `coral_head_a/b` (lobed boulder, a dozen branching thickets a third to a half bleached, plates, fans,
    sponges), `seagrass_patch` (240 blades), `coral_curtain`. Story: `divers_cord` (~100 knots, a quarter new),
    `tether_line`, `wreck_ribs` (the dead ship: Hullgnaw's kind of rib-timbers), `hull_keels` (Oruvel from below; a
    stand-in until the raft-town kit), `diver_lantern` (a stand-in for Character's lantern, preview only).
  - Maps (`ou_textures.py`): `silt`, `coral`. 25 materials (`ou_materials.py`): the weathering stack with growth as
    the algae and barnacle (coralline) layers over the whole depth range; moss and salt off; only `ou_flame` emits.
- **Triangles, LOD0 / LOD1:** bell_room 1956/60; coral_curtain 4462/4; coral_head_a 8302/60; coral_head_b 8327/60;
  current_shaft 3404/96; diver_lantern 612/36; divers_cord 4464/30; floor_slab 2016/12; floor_slab_broken 2756/12;
  gauge_wheel 4608/132; gauge_wheel_cut 1994/36; hinge_door 1488/36; hull_keels 1778/90; lamp_column 3727/54;
  lamp_column_fallen 4147/54; lit_fragments 1212/32; pipe_run 1592/16; sand_drift 1728/70; seafloor_edge 2046/48;
  seafloor_far 1892/380; seafloor_patch_a 1200/32; seafloor_patch_b 1200/32; seagrass_patch 2400/96;
  stair_flight 2560/36; tether_line 444/18; tower_bay 1279/48; tower_bay_broken 1594/36; tower_bay_solid 888/12;
  tower_pier 192/12; wreck_ribs 5236/286. Budgets in each module's `TRI_BUDGET` (checked by build.py and the tests).
  Kit on disk: 5.9 MB in 60 files, largest 0.4 MB.
- **Shots (lavapipe, 960 × 540), my read:**
  - `ou_u04_lamp_gallery` (baseline): the strongest interior. Two rows of dead lamp-columns receding into the dark,
    the lantern's warm pool on the nearest column and floor, the windows and the breach's light cool teal, coral
    curtains in the left bays. The bright teal sun patches on the near floor pull the eye a little.
  - `ou_u12_terrace` (baseline): the tower rising pale out of the meadow, its storeys banded in surviving ceramic,
    the breach a dark mouth with columns inside, the ribs at the left, seagrass near, a half-bleached coral head and
    the lantern's pool at the lower right. The coral head reads as a lumpy mass more than as brain coral.
  - U06 low lights (the cord across the frame, held motes, ~2–3% of the frame, sinking into the stairwell: the
    frame I would show first for story, but it is orange-hazed), U07 gauge wheel (brass and verdigris in the
    lantern's light), U01 drop (broken crown walls, a hull across the Snell window, the tether), U13 ribs, U14 kit
    row: viewed, not registered.
  - Both baselines capture byte-identically twice in a row (compare.py rmse 0.00000).
- **Grade:** `oruvel_underway_ch01_environment.tres` (exposure 0.65, saturation ×1.12, SSAO, SDFGI off, volumetric
  fog authored at density 0 so the rig adds only its shafts and never writes the shared .tres). The preview rig
  adds two stand-ins per shot (downwelling tint, area light scale), filed as **M3-RND-24**, and opens the glimmer
  gate at the colour script's `ch01` 1.5 for the held motes.
- **Changes found in the preview** (recorded in the notes' Revisions): the tower is 36 × 12 m and the ground cells
  12 m (no silt inside the tower or the stairwell); the breach is one bay; the cladding runs in two bands per storey;
  the downwelling tint (the first captures read as a sunlit beach); the deep area keeps a little teal.
- **Shared files touched (append-only):** assets/PROVENANCE.md (60 rows), docs/kb/ownership.md (one row),
  tools/dev/blender_builds.json (one job), tests/screenshots/shots.json (two shots), baselines.json (by
  compare.py --update-baselines for the two ids only), docs/kb/tech/asset_import.md (one table row). **Import
  category:** `game/data/import/oruvel_underway_kit.json`, `game/core/import/oruvel_underway_kit_post_import.gd`,
  `KINDS` in `tools/tests/test_post_import.py` and `tests/unit/test_post_import.gd` (the Character + Tools row owns
  these; flagged for their review).
- **Requests filed:** M3-RND-24 (Rendering: downwelling and a per-area light scale on the rig). For Narrative: the
  dead ship's ribs are written as Hullgnaw's kind of rib-timbers (planted, never said); confirm or redirect.
  For the colour script: the dive's sun is 08:45, 42° / 105° (the `ch01` row is the 10:30 raft-town).

## Swap-in note for m2-slice (`game/levels/ch01/oruvel_underway/`)
- **Scene path to copy from:** `game/levels/_tests/oruvel_underway_kit/oruvel_underway_preview.tscn` (do not
  reference it from shipped files: `_tests` is excluded from release). Copy its `WorldEnvironment` (the `.tres`),
  `Sun` (42° / 105°, `#FFEFE1` at 3.0, shadows on), `Water` (Haluna's lagoon material and `lagoon_waves.tres`),
  `Tide` (water 0, datum 0), `Underwater` (`UnderwaterRig`, `water` → Water, `lantern_target` → Rhen's lamp node)
  and a `HalunaDresser` with a copy of `oruvel_underway_layout.json` (generated by `ou_preview_layout.py`; drop the
  `kit_row()` pieces at z −40..−47, the review row, and the `diver_lantern`). Add the zone to the five underwater
  entries of `prewarm_materials.json` (tech/underwater.md "Using it in a zone").
- **Anchors (world metres, sea surface y 0, north −Z):** tower x −18..18, z −6..6. Floors F9 −22.4 (the gallery,
  6.4 m tall) to F14 −6.4 (the crown). `Drop` spawn: on the crown floor near (−9, −6.4, 3.6), the tether at
  (−9.9, −5.85, 5.2). Bell-room: (−15, −9.6, −3) on F13 (door on +Z; the air pocket is 0.7 m under its ceiling at
  y −7.1 and needs its own `WaterSurface`, see beat sheet U03). Collapsed floors (tether drops): the slot in the
  broken slabs at (3, F11..F13, 3) and the crown floor at (−3, −6.4, 3). Gallery: x −12..18, lamp-columns at
  z ±3, x −9 … 15; coral curtains at (−3, F9, −5.55) (the old diver's tin goes behind this one) and (9, F9, 5.55).
  Breach onto the terrace: the east wall's south bay, x 18, z 0..6, F9–F10; sand tongue from x 21 into the gallery.
  Stair lip: x −12.15, z 3 (flight runs −X down to −25.6), the divers' cord at x −12.3 across z 1.8..4.2 (0.9 m
  up); the low lights: a held `GlimmerField` at (−15.3, −24.8, 3), extents 2.2 × 2.0 × 2.2, multiplier 0.45.
  Gauge room: door at (−12, F9, −3) facing +X (the gallery); wheel at (−15.4, F9, −3.9) facing ±Z (swap
  `gauge_wheel` → `gauge_wheel_cut` on `ch01_cut_gauge_wheel`); the current shaft stacks at (−16.35, F9…F14, −1.5)
  to the crown. Terrace: silt datum −22.6, the dead ship at (30, 18) yaw −24.4, the meadow east of x 24, the lip
  over the canyon at z ≈ 62.
- **Collision:** the kit exports no `-col` proxies yet. Walkable: the slabs' tops (y = their floor), the stair
  treads, the terrace cells (their height functions are in `ou_ground.py`: `seafloor_height`, `edge_height`), the
  sand tongue. Block: every bay, pier and the shaft staves; the stairwell and the canyon lip are drops (gate them;
  "nobody goes below the ninth floor"). Trimesh from LOD0 is fine for the slabs and walls; the reef pieces, seagrass,
  cord and curtain should not collide (the curtain is a shutter reveal, not a wall).
- **Lighting the zone needs (until M3-RND-24):** per area, the ambient and the rig's in-scatter scale (open 0.65 /
  1.0, interior 0.22 / 0.33, deep 0.14 / 0.2) and the downwelling tint of the sun and ambient for the depth
  (`OruvelUnderwayPreview.apply_lighting` shows the arithmetic). The dive opens `hymn_glimmer` at
  (0.2122, 0.5647, 0.6939, 1.5) so the held motes draw.

## Review log
