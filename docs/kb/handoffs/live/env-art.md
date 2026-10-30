# Live log: env-art environment

Environment-art track, cloud session `session_01QmWUfYxd8DMg7XM3MyR6ps`, branch `claude/env-art` (from the integration branch `claude/undertow-lead-handoff-423ixt` at 2026-10-24). **This environment owns this file** (CLAUDE.md §7a). The Lead is `session_019iimsngAgPLEram1wcbLpE`; it reads this file on the pushed branch.

Scope: assets and kit pieces (Blender jobs, materials, import rules), handed to `claude/m2-slice` with a swap-in note here. Art Director sign-offs. I don't edit m2-slice's scenes (`game/levels/ch02/**`, `ch03/**`) except through a request task.

## NEW ACCOUNT (from 2026-10-25)

env-art is cloud session `session_01YbaV2c8yquRHqj6afQYg89` on `claude/env-art`; the integration branch is
`claude/undertow-lead-handoff-ze8rrn`; the Lead is `session_018aiGwGLGkxsnMnu8VfCu1m` (TRACK-RULES.md).

- **2026-10-25: merged the integration branch** (ze8rrn @ de93e79e) into `claude/env-art`. Conflicts: the
  shared docs (union), `battle_arena_causeway` and `drownbell_flood` (the integration copies; isolated captures
  match them at rmse 0) and `battle_arena_oruvel_raft_morning` (env-art's Oruvel-kit copy: the integration's
  predates M3-ENV-07; isolated capture matches env-art's at rmse 0, f6af47e1).

- **MERGE-READY @ 9222913f** (FAST-TRACK, the human's playtest "parts look primitive"): the integration merge
  (above), and **M3-ENV-701 Haluna set dressing**: 11 new kit pieces (dressing.py), 3 materials, the M2-ENV-08
  route pasted into the shipped zone, lane/dock/beach/chapel/banyan/Wake dressing, front-yard fences, a yard set
  per house (HalunaDresser `yard_sets`, kept 1.6 m off the lanes), four litter scatters, close LOD/shadow ranges
  for small props. Re-approved after viewing: H02, H03, H04, H07. Checks run: `haluna_kit` full rebuild (every
  existing piece byte-identical), `test_haluna_kit` + `test_haluna_dressing` (31 OK), `--filter=haluna` 49/0,
  gdlint/gdformat, validate_data, taskboard --check, isolated captures of H01–H10. Checks skipped: the full
  tools suite and other shots (nothing else reads the Haluna layout or kit files changed).
  - **For the Lead:** these UI baselines frame Haluna's lane 1 and now show the new clutter: `field_objective_line`,
    `field_interact_prompt`, `field_area_title`, `field_tip_card` (rmse ~0.04 after the crate move; were already
    drifting from the wetter tidewalls) and `dialogue_continue`. View and re-approve them at the gate.
  - **Request:** M3-ENV-702 (slice-polish): `piece_rules` for the new pieces (low clutter and the causeway slabs
    get no collision). Until then they get the default mesh-bounds box.
  - **PC perf check requested:** Haluna entry hitch (ADR 0029, 3 s) and GPU frame time at H02 and the dock with
    the dressing (about 250 more instances; small props cull at 30–140 m).

- **MERGE-READY @ b2fbee29: M3-ENV-703**, the six Ch6 story pieces act1-chapters asked for (M3-ENV-1201), in the
  Brine Shoals kit (`bs_story.py`): `tide_wheel`, `tide_wheel_burned`, `ridge_fire`, `level_stone_shrine`,
  `vendor_boat`, `hatch`, `chalk_mark`, `chalk_mark_heavy`. Sizes, origins and facings per block are in the task
  file. Checks run: `brine_shoals_kit` full rebuild (every existing piece byte-identical), `test_brine_shoals_kit`
  OK, validate_data, taskboard, lavapipe views of every piece (on a temporary preview; no baseline changes).
  Checks skipped: Godot tests and shots (no scene or code reads these files yet).
  - **For act1-chapters:** add them to `tools/act1/ch06_brine_shoals_dressing.py` with their `block` ids and drop
    those ids from `greybox.keep`. Greybox block centres are mid-height, so set each piece at `pos.y - size.y / 2`;
    `hatch` and the chalk marks are centred and face +X (yaw them onto their hull side). Use `chalk_mark` on the
    route and `chalk_mark_heavy` nearer the camp; `tide_wheel` until B03 and `tide_wheel_burned` after.

- **MERGE-READY @ 39f66d4c (FAST-TRACK, fixes my own red test): take this with 9222913f, never 9222913f alone.**
  9222913f turned `tools.tests.test_shrine_gi_bake` red (the GI guard hashed every Haluna material, and the new
  `shrine_offering` prop matched its `shrine_*.glb` glob). `gi_inputs.py` now hashes only the materials the shrine
  pieces use; the prop is renamed `wayside_offering` (same geometry); the narrowed inputs equal f6af47e1's (the
  last state the shipped bake matched), so the sidecar is re-recorded without a rebake. Also adds `offering_step`.
  Checks run: `test_shrine_gi_bake`, `test_haluna_dressing`, `test_haluna_kit` OK; `--filter=haluna` 49/0;
  `haluna_kit` rebuild (all other pieces identical); validate_data; taskboard. Shots: unchanged (same geometry).

- **MERGE-READY @ a0d2549f: M3-ENV-701 on the B06 causeway and the two slice arenas** (offerings at the marker
  posts, wrack, nets, coils, shells and pebbles along the bed; tideline_dawn and causeway_disc_sunset dressed).
  Checks run: `test_haluna_kit`, `test_arenas`, `test_fog_lamps` OK; the full tools suite at 39f66d4c (1027 OK);
  validate_data. Shots: viewed on lavapipe before the render move, every one inside its limit; the PC re-renders
  them below. Also **M3-ENV-704** filed: slice-polish places dressing in the Shell Shrine and rebakes its GI.

- **MERGE-READY @ 22a5de11:** the integration branch (ze8rrn @ 7cccb551, big9) merged in. Conflicts: the shared
  files (union), and the three battle baselines (the PC gate's copies; re-render requested below). Checks run:
  the full tools suite (1123 OK), `--filter=haluna` 50/0, `--filter=arena` 18/0, `gi_inputs --check`,
  validate_data, taskboard. Skipped: shots (rendering is the PC's now).

- **MERGE-READY @ 71f19fbc: M3-ENV-706**, Ch6's two arenas at final quality from the Brine Shoals kit
  (`brine_shoals_afternoon`, `salvage_camp_burning`; arenas.json repointed; the camp's fires keep M3-BPR-03's
  `FireLight<k>` contract). Also **M3-ENV-705** (Ashcrown grade, 1a422476). Checks run: `--filter=arena` 18/0,
  `test_arenas`, `test_fog_lamps`, `test_brine_shoals_kit`, `test_ashcrown_kit` OK, `brine_shoals_kit` full rebuild
  (others identical), every other arena regenerates identically, validate_data, taskboard. Shots: PC (below).

- **MERGE-READY @ ba16d48b:** four fish weirs (stake-and-wattle V traps) in Haluna's lagoon shallows, a new
  `fish_weir` kit piece, culled at 400 m so they read from H01. Checks run: `test_haluna_dressing`,
  `test_haluna_kit`, `test_shrine_gi_bake` OK; `--filter=haluna` 50/0; `haluna_kit` rebuild (others identical).

- **MERGE-READY @ 179069de: M3-ENV-705**, the causeway route arena's ground takes the zone's `kit_causeway_ground`
  (it read as bleached beach). Checks run: `test_arenas`, `test_haluna_kit`, `test_shrine_gi_bake` OK,
  `--filter=arena` 18/0, `haluna_kit` rebuild (only that ground changed).

- **MERGE-READY @ bbd4b5ad: M3-ENV-707 batch A** for act1-chapters' M3-ENV-1203 (Corrow): `stillguard_barracks`,
  `wall_gate`, `kite_line`, `kite_line_high`, `marra_step`, `hoist_pins`, `hoist_rope`, `hoist_basket`,
  `trader_boat`, and the reuse map (net racks, chandler, chapel, shrine from the Haluna and Brine Shoals kits via
  per-piece `kit_dir`); sizes, origins and facings in the task file. Checks run: `test_corrow_kit` OK, `corrow_kit`
  full rebuild (older pieces identical), import maps every slot, validate_data, taskboard. No shot reads them yet.
  - **For act1-chapters:** place them in `tools/act1/ch08_corrow_dressing.py` by block and drop the ids from
    `greybox.keep`. Batch B (the mole and its sea stair, the Bastion) is next.

- **MERGE-READY @ 643f8a04: M3-ENV-707 batch B** (Corrow): `mole_pier`, `mole_sea_stair`, `bastion_platform` on the
  collision blocks' footprints (see the task file for origins; give them `lod1_from_m` ≥ 150). Checks run:
  `test_corrow_kit` OK, `corrow_kit` full rebuild (older pieces identical), import maps every slot, validate_data.
  M3-ENV-1203 is covered except `Flood` / `Lake` (water surfaces, Rendering's).

- **MERGE-READY @ fc4b4fcd: M3-ENV-708**, Ch9's kit pieces in the Corrow kit (`cw_night.py`): `shroud_a/b/small`
  (faces covered), `strand_lamp`, `round_shield`, `ebbing_raft`, `flood_debris`, `milestone`. Checks run:
  `test_corrow_kit` OK, `corrow_kit` full rebuild (older pieces identical), import maps every slot, validate_data,
  taskboard. **For act1-chapters:** these are the kit half of M3-C09-04; placement is yours.

- **MERGE-READY @ 032b7a64: M3-ENV-709**, Haluna's wake night for Ch4 (M3-C04-03's Haluna half): kit pieces
  `ground_lamp`, `feast_mat`, `ink_kit`, `wake_shell_single` and the shell-state materials; `HalunaDresser`
  `story_sets` (hidden `StorySets/StorySet_<name>`, `story_set(name)`), with `ch04_wake`, `ch04_shell_asha`,
  `ch04_shell_imra_faded`, `ch04_shell_imra_inked` in the layout. Checks run: `--filter=haluna` 52/0 (new
  `test_haluna_story_sets`), `test_haluna_dressing`, `test_haluna_kit`, `test_shrine_gi_bake` OK, `haluna_kit`
  rebuild (older pieces identical), gdlint, gdformat, validate_data, taskboard. Shots unchanged (sets hidden).
  - **For act1-chapters:** Ch4's zone shows the sets by flag; details in the task file.

- **For slice-polish (M2-FP-108):** env-art's a0d2549f added dressing to
  `assets/environments/zones/saltgrass_causeway/causeway_layout.json` (offering steps at marker posts, wrack,
  nets, coils, a crate stack, shell/pebble instances). If `tools/causeway/build_causeway_gameplay.py` reads that
  layout, re-run it after merging; none of the new pieces sits on the bed's walk line (they stand 1–14 m off it).
- **M3-C01-04** (Ch1 kit swap): noted in its task file that the swap is the Ch1 scene owner's (ZoneKitDressing, as
  Ch4–Ch9); env-art supplies missing pieces on request.

- **MERGE-READY @ 80bb1e56:** `HalunaDresser.night_lamp_houses()` / `set_night_lamp(house, lit)` for Ch4 C4-01's
  windows going dark one at a time. Checks run: `--filter=haluna` 53/0, gdlint, gdformat.

- **MERGE-READY @ 31dc710b:** the integration branch (ze8rrn @ 7f187123, big10) merged in; conflicts only in the shared
  append-only files (union). Checks run: full tools suite OK, `--filter=haluna` 53/0, `--filter=arena` 18/0,
  `gi_inputs --check`, validate_data, taskboard. The render requests above still stand.

- **Lead's item 3, the `offering_step` PROVENANCE warning:** not a bad row. The row landed in b2fbee29 and the glb in
  39f66d4c, one commit later. slice-polish merged b2fbee29 but not 39f66d4c, so its branch has the row without the
  file. Merge env-art at 39f66d4c or later and the warning goes. On env-art's head both exist (validate_data: 0
  warnings).
- **Lead's item 4, Act I past Ch9:** Act I is Ch1–Ch9 (act_outline.md), so there are no Act I zones past Ch9.
  Every Act I zone has its kit, and every Act I encounter arena is at final quality (Ch6's two since M3-ENV-706).
  The primitive-built scene left in the act's frame is the **Prologue's Iskarra**, so that is the next item (below).
- **MERGE-READY @ 86155bfc: M3-ENV-710**, Iskarra for the Prologue (reused in Ch19). New pieces in the Haluna kit
  (`iskarra.py`):
  - five white Lit Age ceramic towers (spire, stepped, broken, small, small broken), with flutes, galleries, window
    slits, a waterline band, domes and finials or jagged hollow tops;
  - a fallen crown, the broken plaza (34 x 18 m) and its rise, a standing and a fallen gate, dead lamp columns;
  - 3 materials.

  `assets/environments/zones/iskarra/iskarra_city.tscn` places each piece where the Prologue's primitives stand.
  Checks run:
  - full tools suite (1156) OK; `test_iskarra`, and the Godot `--filter=iskarra`;
  - `haluna_kit` rebuild (every older piece byte-identical);
  - `gi_inputs --check`, validate_data, taskboard.

  Also in this merge: re-approved after viewing the eight shots from `gpu/render-env-art-71f19fb` and
  `gpu/render-env-art-a0d2549` (0f19d868). The Ch6 arenas replace the greybox; the five UI shots differ only by lane
  1's new jars.
  - **For slice-polish:** request **M3-ENV-711** swaps the Prologue's `City` primitives for the instance (you own
    `game/levels/prologue/**`).
  - **24bf927a is NOT merge-ready yet.** It adds the preview stage `game/levels/_tests/iskarra_kit/` and three new
    shots. `test_screenshots` stays red until the PC renders them and env-art approves.
- **M3-ENV-1000** (Sefir's barge: no wake, a still reflection) is blocked.
  - The barge exists (`white_barge`, `bs_barge.py`).
  - The still reflection is M3-RND-03 (Rendering, todo).
  - No boat in the game draws a wake yet, so "the others leave one" needs a water wake feature first.

- **fa67bfee, 92362494, 8770a067: merge-ready once the PC answers 24bf927a** (the only red is `test_screenshots`,
  which wants baselines for the three new Iskarra shots).
  - fa67bfee, **M3-ENV-706 density pass** after viewing the PC render: the shoals arena gets a stranded skiff,
    dropped salvage, nets, coils, sacks and mud patches; the camp's hard gets damp and dry patches, so its shingle
    stops reading as one repeat.
  - 92362494, **M3-ENV-712:** the Corrow Watcher heads' backs are carved (blocks, hair locks, a headband, ears, a
    domed crown). act1-chapters' `ch09_corrow_road` showed the row as barrels from the parapet walk. LOD0 budget
    10500; LOD1 unchanged; the faces are unchanged.
  - 8770a067, **M3-ENV-705:** the Brine Shoals preview sky shows the colour script's blue zenith.

  Checks run:
  - full tools suite 1156 (only that `test_screenshots` red);
  - `test_corrow_kit`, `test_arenas`, `test_brine_shoals_kit`;
  - Godot `--filter=corrow` 8/0 and `--filter=arena` 18/0;
  - Corrow and Brine Shoals full rebuilds (only the intended pieces changed);
  - validate_data, taskboard.
- **For act1-chapters, from viewing your PC renders** (77a6a77, 180510e). Kit pieces exist for all of these;
  placement is yours.
  - `ch09_corrow_road`: M3-ENV-712 changes the heads' backs. Please re-render `ch09_corrow_road` and the Ch8
    Corrow shots after merging env-art.
  - `ch09_corrow_strand` is near black. The `strand_lamp` pieces show as dots with no light around them. Give a
    few of them an OmniLight (warm, range 4–6 m, `light_volumetric_fog_energy = 0`, the fog-lamp rule), or raise
    the night fill, so the shrouds and the strand read.
  - `ch06_brine_road`: the flats either side of the plank road are bare. Pieces that fit the raid's aftermath:
    - the Haluna kit's `net_heap`, `tide_debris`, `rope_coil`, `cargo_sacks`;
    - Brine Shoals' `crate_stack`, `salvage_pile`, `vendor_boat` (stranded, ~25 cm sunk), `wreck_ribs_large`,
      `mudflat_patch_a/b`.

    The shoals arena (fa67bfee) shows a working mix. The two capsules are character placeholders, not kit.

- **M3-ENV-713, the missing Act I arenas** (the Lead's item 4). All seven Ch8 encounters had no arena and fought on the
  sandbox's greybox. Five new arenas (merge-ready at 599b2418 once the PC answers; the only red is `test_screenshots`,
  which wants the new shots' baselines):
  - `seawall_stairhead_storm`, `_hoist` and `_surge`: the wall-head over the Fisher Stair, from the Corrow kit, in
    three states. Liss's hoist is rigged from wave 2; the surge has `BossAnchor` for the Undertow's Reach.
  - `coilspire_headland_path`: a levelled, flagged landing at the path's mid-point, using the Coilspire kit's new
    `arena_headland_ground` and `arena_headland_path` (`cs_arena.py`).
  - `coilspire_tier_landing`: a cut-away tier of the well (`arena_tier_hall`).

  Checks run:
  - full tools suite (1156; only that red);
  - Godot `--filter=arena` 18/0, with all five in `test_battle_arenas` (floor and camera line);
  - Coilspire full rebuild (older pieces identical);
  - validate_data, taskboard.

  The battle_arenas.md sections are in.
  - **For act1-chapters:** request **M3-ENV-714** sets the Ch8 encounters' `arena` ids. Until then the arenas sit
    unused in arenas.json.

- **Lead's new queue (18:14).** Items 3 and 5 were already done:
  - item 3, the 8 arena-less encounters: Ch8's seven are M3-ENV-713; the eighth, `sandbox_reef`, is the sandbox's
    own fixture;
  - item 5, `offering_step`: explained above; clean on env-art's head.
- **For act1-chapters' blocked swaps** (their 17:44 entry). Merge-ready at fd630bb8 once the PC answers; the only
  red is `test_screenshots`, which wants the new shots' baselines.
  - **M3-ENV-1214 (Ch5 Pemakar), done:**
    - pieces `harbour_quay` (32 m), `sea_cut_weir` (the hero mesh), `wake_wall` and `crown_bell`
      (`pemakar_harbour.py`);
    - a `day` grade for B11, `pemakar_day_environment.tres`, as the preview's `day` mood.
    - Placement numbers are in the task file. **One conflict to settle:** your weir stand-in at x 10 lies in front of
      your 32 m quay, so the weir's cut would run through the quay deck. Shorten the quay or move the weir. The
      preview puts it where your bottom channel meets the shore (x −39.3).
  - **Ch5 Ashcrown (M3-ARC-1216):** env-art recommends the traversal (option 1). Re-cutting the flights under 40°
    would change the temple's massing and its silhouette from Pemakar. **M3-ENV-715** exports every steep flight's
    path (foot, head, landings, width, angle) as `assets/environments/kits/ashcrown/ashcrown_flights.json`, ready
    for a traversal.
  - **Ch7 port (M3-C07-04):** next for env-art: the `tamsule.md` sheet, then the "Tamsule stilt" kit.

  Checks run:
  - full tools suite (only that red);
  - `test_pemakar_kit`, `test_ashcrown_kit`, `test_arenas`;
  - Godot `--filter=pemakar` 6/0;
  - Pemakar full rebuild (older pieces identical);
  - validate_data, taskboard.

- **M3-C07-04, the Tamsule port (act1-chapters' blocked Ch7 swap), merge-ready at 94fe8f77.** It has the same
  `test_screenshots` red as the other new shots.
  - `docs/kb/art/environments/tamsule.md`. Its shots are TP01–TP09, because the Bell's sheet already uses T01–T09.
  - The Tamsule Bell kit's new `market.py`: `port_deck_8m(_rail)`, `plank_bridge_4m`, `market_stall`,
    `market_boat_a/b`, `bunting_12m`.
  - The preview `game/levels/_tests/tamsule_port_kit/` dresses **every greybox block in your own frame** (decks
    y 0, river −1.6). `tamsule_port_layout.json` holds the rows, ready to copy into `ch07/tamsule`.
  - **The Bell's ring stands at (0, −75)**, not your stand-in's z −40: the real galleries reach r 41 and would cover
    the gantry foot.

  Checks run:
  - Godot `--filter=tamsule` 7/0;
  - `test_tamsule_bell_kit`;
  - full rebuild (older pieces identical);
  - full tools suite (only that red).
- **M3-ENV-716/717 (the Lead's item 4), sheets first:**
  - `lowlight.md`: Ch11, the Lamp Engine's flooded hall, nothing frozen per ADR 0015/0016;
  - `keth_pass.md`: Ch12, the Avalanche Ram's seeping Lit Age terrace.

  The kits and the two arenas follow.
  - **For the creatures track:** `avalanche_ram.md` gives the Ram ice-plated fleece, an ice beard, and snow shed by
    its cast. ADR 0015 bans ice, frost and frozen water in any temple **or set-piece** from Ch12 to Ch15, and the
    Ch12 boss is a set-piece. keth_pass.md proposes locks matted with seep-crust and silt, and a cast that sheds
    scree. Please confirm or route to Narrative.
- **MERGE-READY @ 95be6118: M3-ENV-717**, the Avalanche Ram's arena `keth_seep_terrace` (Ch12), in the Haluna kit
  (`keth.py`): the terrace ground, the seeping Lit Age wall (emissive seep sheets, nothing frozen), the seep pool and
  pale grass, a pass-cord with red and undyed keth, cairns, the far ridges; `lut_ch12_heights` from
  `keth_zone_lut.py`. `BossAnchor` (−7.5, 0, −3) by the pool. Preview fixture `preview_keth_seep_terrace.tscn`.
  - **For act1/creatures:** set the Ch12 Ram encounter's arena to `keth_seep_terrace`.

  Checks run: haluna_kit full rebuild (older pieces identical), Godot `--filter=arena` 18/0, full tools suite
  (only `test_screenshots` red: new shots without baselines).
- **MERGE-READY @ 854e6a95: big11 merged** (integration 3cbcff9e, merge c7f1f83b).
  - **The merge.** The shot manifests were merged by shot id and PROVENANCE by path. The stale `shrine_offering`
    row is dropped: that piece was renamed `wayside_offering` in 39f66d4c, and this is the queue's item 5. Of the six
    contested baselines, big11's PC-gate copies win. `battle_arena_shoals`, `battle_arena_camp`,
    `battle_boss_intro_inquisitor` and `field_tip_card` need a re-render with env-art's later density pass (request
    below).
  - **M3-ENV-1000 (doing): the wake.** The Brine Shoals kit's `boat_wake` (`bs_wake.py`, `bs_wake` on
    `env_boat_wake.gdshader`) is a Kelvin wake for the boats that move. Sefir's barge never gets one. The preview
    poles a vendor boat up the channel in B05. Left to do: the `RevenantTells` hookup, once M3-RND-03 reaches the
    integration branch.
  - **M3-ENV-710.** M2-FP-103 moved Kerrid's vigil to (9.5, −5.5), over the plaza's fallen corner. I pulled the
    break back to clear him; the test now checks the three stand-ins that remain.
  - **For the Lead:** `test_audio_loudness` is red on the integration branch itself. 44 `sfx/life/*` files have no
    target rule, and `sfx/battle/impact_medium_*` sit at −24 LUFS against −19. Env-art's audio and tools files are
    identical to the integration's.

  Checks run:
  - full tools suite (red only on screenshots and audio, as above);
  - Godot `--filter=arena` 18/0, `brine` 5/0, `shader` 42/0, `iskarra` 1/0;
  - brine_shoals_kit full rebuild (older pieces identical) and haluna_kit full rebuild (only `iskarra_plaza`
    changed);
  - validate_data, taskboard, gdlint.
- **MERGE-READY @ 43492e80: M3-ENV-716**, the Lamp Engine's arena `lowlight_engine_hall` (Ch11), in the Haluna kit.
  - **The hall.** The kit's `lowlight.py` makes `engine_hall`, `conduit_run` and `lamp_niche_tier`. In the hall:
    - a flooded floor at −0.6 with still water at −0.15;
    - a dry flagged dais at y 0, set off-centre;
    - eight piers and a ribbed vault, one bay fallen behind the enemy line;
    - the trimming rail with twelve bound-teal lamps;
    - the lamp-niche tiers.
  - **Grade and anchor.** `lut_ch11_vey` comes from `lowlight_zone_lut.py`. The `BossAnchor` is at
    (−6.4, −0.6, −2.6), knee-deep.
  - **Arena writer.** `arena_scenes.py` gains an optional sea `waves` key (an arena's own wave set). Every other
    arena is byte-identical.
  - **For act1/creatures:** set the Ch11 Engine encounter's arena to `lowlight_engine_hall`.

  Checks run: haluna_kit full rebuild (older pieces identical), `test_lowlight` 7, `test_arenas`, `test_haluna_kit`,
  `test_fog_lamps`, `test_release_excludes_tests`, Godot `--filter=arena` 18/0, and the full tools suite (red only on
  screenshots and the integration's audio).
- **MERGE-READY @ c990e2c2: M3-ENV-718**, the Mangrove Drowner's arena `ossa_fen_roots` (Ch10), with the sheet
  `ossa_fen.md`.
  - **The fen.** The Haluna kit's `ossa_fen.py` makes:
    - `fen_bank_ground`: the mudbank, level at y 0, shelving into tannin water at −0.15;
    - `mangrove_tree` and `mangrove_dead`: prop-root cages, with crowns of leaf cards from the coastal atlas (the
      vegetation wind contract) or bare and bleached;
    - `reed_bed` and `fen_far_mangroves`.
  - **Grade and anchor.** `lut_ch10_fen` comes from `fen_zone_lut.py`. The `BossAnchor` is at (−8.2, −0.15, −3.8),
    in the water at the dead tree's foot.
  - **For act1/creatures:** set the Ch10 Drowner encounter's arena to `ossa_fen_roots`.
  - **Also:** the wake shader's `.uid`, which Godot generated on import.

  Checks run: haluna_kit full rebuild (older pieces identical; every other arena byte-identical), `test_ossa_fen` 9,
  `test_arenas`, `test_haluna_kit`, Godot `--filter=arena` 18/0, and the full tools suite (red only on screenshots and
  the integration's audio).
- **MERGE-READY @ eeecf13d: M3-ENV-101**, the save shrine's kit pieces (swap note under "Swap-in notes"), and the
  answers to the Lead's 19:21 note on `test_iskarra`. Both were already fixed in 854e6a95: the plaza's fallen corner
  is pulled back so Kerrid at (9.5, −5.5) stands on paving, and the test checks the stand-in vigils that remain, with
  the reason in the assert (M2-FP-103's real cast replaced the rest). Checks run: haluna_kit full rebuild (older
  pieces identical), `test_save_shrine_kit` 5, `test_haluna_kit`, validate_data.
- **MERGE-READY @ 85309570: M3-AUD-811** (audio's request, to review): Haluna's footstep surfaces.
  - HalunaDresser builds Area3Ds in `footstep_surface` from the layout's new `footstep_surfaces` key: the dock is
    wood (priority 2) and the lagoon below mean sea level is water (priority 1).
  - The areas sense nothing and sit under a plain `FootstepSurfaces` Node, outside HalunaCollision's pieces.
  - The causeway's pools are slice-polish's scene (note in the task).

  Checks run: Godot `--filter=haluna` 61/0 (with the new `test_haluna_footstep_surfaces.gd`), `test_haluna_dressing`,
  gdlint/gdformat, taskboard. No shot shows the areas: they are invisible.
- **MERGE-READY @ b12f8899: M3-C06-03** (cinematics' Ch6 kit request, to review): what was still open after
  act1-chapters' M3-C06-1200.
  - **New pieces** in the Brine Shoals kit (`bs_tideline.py`):
    - `lamp_hole_open` and `lamp_hole_covered`, the B09 dig in two states;
    - `hand_print`, for the insert;
    - `stillguard_torch`, a hand prop or planted (the flames are VFX).
  - **The grades.** The colour script gains `ch06_hold`, `ch06_dusk` and `ch06_dawn`, each with an Environment, a
    LUT and a sun row in `assets/environments/zones/brine_shoals/ch06_grades.json`.
  - **The writer.** `arena_scenes.write_environment` writes a zone grade's Environment with the arenas' own writer.
    Every arena is byte-identical.
  - **For act1-chapters:** placement and wiring are in M3-C06-03's notes:
    - the `LampHole` states by `ch06_saw_lamp_buried`;
    - the hand-print beside the hole;
    - the torches at the camp;
    - a light row's `environment_res` set to the grade's `.tres`, with its sun row.

  Checks run: brine_shoals_kit full rebuild (older pieces identical), `lut_ch06_smoke` regenerated byte-identical,
  `test_brine_shoals_kit` 31, the Environments and glbs load headless, and the full tools suite (red only on
  screenshots and the integration's audio). No shot uses the new pieces or grades yet.
- **MERGE-READY (also in this push): M3-ENV-1201** to review. It was built under M3-ENV-703.
- **MERGE-READY @ 55cb8501: the Act II zone kits** (the Lead's item 4, "sheets first, then kits"), all in the Haluna kit.
  - **Lowlight (M3-ENV-716):** `conduit_housing`, with **the Saltwright housing-mark** Liss reads in L03 (a circle
    crossed by three lines over two seats); `lowlight_nave_bay` and `_broken`; `well_shaft`; `lowlight_sanctum`;
    `vey_arcade_bay`; `vey_gallery_bridge`; `strangler_fig`.
    - **For Character:** M3-ENV-719 asks for the same mark on Rhen's lantern, so the Ch11 reveal reads on screen.
  - **Keth Pass (M3-ENV-717):** `keth_road_switchback` (10 m modules that chain), `keth_scree_slope` and
    `woolback_trough`. Quellan and Cloudloom follow with their zones.
  - **Ossa Fen (M3-ENV-718):** `kirru_roost` and `name_shell_cord`. The shells are the living clutch's: the Kirru keep
    nothing of their dead (bible §8).
  - **Also:** M3-C04-03, C05-03, C08-102 and C09-04 now note where their kit items were delivered. What's left on
    them is act1-chapters' placement (ADR 0200), so the Lead may re-route them.

  Checks run: haluna_kit full rebuilds (older pieces byte-identical each time), `test_lowlight` 7,
  `test_lowlight_housing` 3, `test_ossa_fen` 9, `test_haluna_kit`, validate_data, taskboard. No shot shows these
  pieces yet (no zone previews for them). Godot import clean.
- **MERGE-READY @ 53179f05: Ch5's grades** (M3-C05-03 item, act1_ch05.md §9.4).
  - **What's new.** The colour script gains `ch05_harbour_dusk` (new, with a new `zone_lut.py` grade) and
    `ch05_ashcrown_day` (ashcrown.md's `ch05_temple` values).
  - **Where.** Both live in `assets/environments/zones/ch05/` with `ch05_grades.json`, written by
    `pemakar_grades.py`.
  - **For act1-chapters:** wire them into Pemakar's and Ashcrown's light rows the way Ch6's are wired.

  Checks run: `lut_ch05_lanternfall` and `lut_ch02_noon` regenerated byte-identical; `test_pemakar_kit`; both
  Environments load headless; validate_data, taskboard.
- **MERGE-READY @ 1ffd9dd7: Ch12's Quellan and Cloudloom** (M3-ENV-717; keth_pass.md §5).
  - **Cloudloom:** `cloudloom_hall`, the rock-cut weaving-hall: open roof, beam lattice, loom-frame. Hang
    `keth_curtain`s from its beams every 2 m (`BEAM_Y` 8.6) for the noon shadow-writing; it wants hard shadows.
  - **Quellan:** `quellan_house` and `woven_awning`.
  - Nothing frozen (ADR 0015).

  Checks run: haluna_kit full rebuild (older pieces identical), `test_haluna_kit`, `test_arenas`, validate_data,
  Godot import.
- **MERGE-READY @ 191e5e89: M3-ENV-720**, the Wakefin's arena `bridal_barge_night` (Ch15), with the sheet
  `open_sea_ch15.md`.
  - **The barge.** Merel's bridal barge is in the Haluna kit (`bridal_barge.py`): a wedding-red hull with a gilt band,
    the stern canopy over Tobin's bier, and an empty lamp hook at the bow.
  - **The grade.** `lut_ch15_unlamped` is a new `zone_lut.py` grade: no warm source anywhere.
  - **The anchor.** The `BossAnchor` is in the water off the bow.
  - **For act1/creatures:** set the Ch15 Wakefin encounter's arena to `bridal_barge_night`.

  Checks run: haluna_kit full rebuild (older pieces identical; every other arena byte-identical), `test_bridal_barge`
  5, Godot `--filter=arena` 18/0, and the full tools suite (red only on screenshots and the integration's audio).
- **MERGE-READY @ c7703809: M3-ENV-721**, Ansedra (Ch13–14) with the sheet `ansedra.md`.
  - **New pieces:** `bowl_dome`; the skyline `ansedra_far_domes` and its `_lit` variant (the city's windows lit);
    the Conclave's `pursuit_barge` with its bound flat-engine.
  - **Venn's arena:** `ansedra_lagoon_escape`, on the bridal barge with the pursuit barge alongside, at the wedding's
    dusk.
  - **The grade:** `lut_ch14_wedding` is a new `zone_lut.py` grade.
  - **For combat/act1:** set the Ch14 Venn encounter's arena to `ansedra_lagoon_escape` when it exists.

  Checks run: haluna_kit full rebuild (older pieces identical; every other arena byte-identical), `test_ansedra` 6,
  `test_arenas`, `test_haluna_kit`, Godot `--filter=arena` 18/0.
- **MERGE-READY @ fca99879: M3-ENV-722**, the Pale Rim and the Drowned Choir (Ch16), with the sheet `pale_rim.md`.
  - **New pieces:** `choir_singer` (24 m hooded robed singers, heads up, mouths open: singers, not idols),
    `choir_amphitheatre` and `pale_rim_flats`.
  - **The arena:** `drowned_choir_ring`, with ten singers round it at moonrise, for Sefir's Abiding guard.
  - **The grade:** `lut_ch16_choir`.
  - **For combat/act1:** set the Ch16 guard encounter's arena to `drowned_choir_ring`.

  Checks run: haluna_kit full rebuild (older pieces identical; every other arena byte-identical),
  `test_drowned_choir` 4, `test_arenas`, `test_haluna_kit`, Godot `--filter=arena` 18/0.

### Render requests
SUPERSEDED (self-rendering from 10-28 01:00, TRACK-RULES cd23f612): RENDER-REQUEST @ e75ce34e: iskarra_i02_gate_from_the_plaza,iskarra_p01_plaza_dusk,battle_arena_ansedra_lagoon_escape,battle_arena_drowned_choir_ring,battle_arena_iskarra_spire_crown,battle_arena_undertow_cage,battle_arena_undertow_heart,battle_arena_undertow_heart_letting,battle_arena_keth_seep_terrace,battle_arena_lowlight_engine_hall,battle_arena_ossa_fen_roots,battle_arena_coilspire_headland_path,battle_arena_coilspire_tier_landing,battle_arena_ash_terrace_lanternfall,battle_arena_underway,battle_arena_underway_tower,battle_boss_intro_reach,ashcrown_a01_approach,ashcrown_a04_anvil_hall,ashcrown_a10_plume_from_the_rim,brightwater_b02_awning,brightwater_b03_rail_drowned,brine_b01_arrival,brine_b05_barge_channel,ch04_ferry_deck,ch04_ferry_derelict,ch08_coilspire_path,ch08_corrow_arrival,ch08_corrow_stair,ch09_corrow_road,ch09_corrow_strand,coilspire_k01_headland_path,corrow_c01_wall_head,corrow_c08_watcher_profile,corrow_c10_breach_fallen,haluna_h01_village_from_sea,haluna_h07_chapel_court,oruvel_o01_surfacing,oruvel_o07_name_board,oruvel_o19_dive_mooring,ou_u04_lamp_gallery,ou_u12_terrace,wildlife_zone_underway_crown,pemakar_p01_waterfall_of_fires,pemakar_p03_among_the_graves,pemakar_p04_harbour_day,pemakar_p11_sea_cut_weir_day,tamsule_tp01_port_and_bell,tamsule_tp03_floating_market,tamsule_tp05_gantry_foot,hollowmere_m01_dace_hull,hollowmere_m02_raft_city_dusk,kite_k01_moored,kitrow_ansedra_court_hall,kitrow_ansedra_basin_stacks,kitrow_keth_cloudloom_house,kitrow_keth_road_details,kitrow_lowlight_nave_bays,kitrow_lowlight_vey_details,kitrow_fen_roost_cord,kitrow_fen_reedhollow_walks,kitrow_quellan_inn_well_dais,kitrow_vey_gallery_walk_bench; why: the one open env-art request (63 ids, priority order as before), moved to this head. It adds the three kit-row shots for the Ch10–12 greybox pieces (M3-ENV-733/734/735). Supersedes 4e5f11ae.
SUPERSEDED: RENDER-REQUEST @ 4e5f11ae: iskarra_i02_gate_from_the_plaza,iskarra_p01_plaza_dusk,battle_arena_ansedra_lagoon_escape,battle_arena_drowned_choir_ring,battle_arena_iskarra_spire_crown,battle_arena_undertow_cage,battle_arena_undertow_heart,battle_arena_undertow_heart_letting,battle_arena_keth_seep_terrace,battle_arena_lowlight_engine_hall,battle_arena_ossa_fen_roots,battle_arena_coilspire_headland_path,battle_arena_coilspire_tier_landing,battle_arena_ash_terrace_lanternfall,battle_arena_underway,battle_arena_underway_tower,battle_boss_intro_reach,ashcrown_a01_approach,ashcrown_a04_anvil_hall,ashcrown_a10_plume_from_the_rim,brightwater_b02_awning,brightwater_b03_rail_drowned,brine_b01_arrival,brine_b05_barge_channel,ch04_ferry_deck,ch04_ferry_derelict,ch08_coilspire_path,ch08_corrow_arrival,ch08_corrow_stair,ch09_corrow_road,ch09_corrow_strand,coilspire_k01_headland_path,corrow_c01_wall_head,corrow_c08_watcher_profile,corrow_c10_breach_fallen,haluna_h01_village_from_sea,haluna_h07_chapel_court,oruvel_o01_surfacing,oruvel_o07_name_board,oruvel_o19_dive_mooring,ou_u04_lamp_gallery,ou_u12_terrace,wildlife_zone_underway_crown,pemakar_p01_waterfall_of_fires,pemakar_p03_among_the_graves,pemakar_p04_harbour_day,pemakar_p11_sea_cut_weir_day,tamsule_tp01_port_and_bell,tamsule_tp03_floating_market,tamsule_tp05_gantry_foot,hollowmere_m01_dace_hull,hollowmere_m02_raft_city_dusk,kite_k01_moored,kitrow_ansedra_court_hall,kitrow_ansedra_basin_stacks,kitrow_keth_cloudloom_house,kitrow_keth_road_details,kitrow_lowlight_nave_bays,kitrow_lowlight_vey_details,kitrow_fen_roost_cord; why: the one open env-art request (TRACK-RULES limit, 23:45), consolidating every earlier line (60 ids, listed in priority order). These are the shots changed since their last approved render, or never rendered: Iskarra I02/P01 first (FAST-TRACK, Ysolde's capsule out); then the arena fixes (Ansedra's sun, the Choir's and the Spire's shadows) and the new arenas (Cage, Heart ×2, Keth rework, Coilspire ×2, Lowlight and Ossa Fen audits); then the M3-ENV-705 audit fixes; last, the two new shape-review previews (Hollowmere/Kite, Act II kit rows). Every older RENDER-REQUEST line below is SUPERSEDED. Already answered and not re-listed: 8be2adc, f39cdde, 1e14af8, c770380, fca9987.
SUPERSEDED: RENDER-REQUEST @ b7496714: iskarra_i02_gate_from_the_plaza,iskarra_p01_plaza_dusk; why: M3-ENV-724, the orange capsule at I02's right edge was Ysolde's battle stand-in (stand_ins.ysolde has no scene yet, M2-HER-1108). The preview leaves her out until it does. Supersedes 1e14af8's FAST-TRACK request.
ANSWERED: lead/gate-render-env-art-1e14af8 (FAST-TRACK Iskarra): P01 and I02 viewed and APPROVED (the slabs shade flat now); I03 and slice_prologue_vigil_line pass. The capsule left in I02 was Ysolde's stand-in, not a pack (fixed in the request above). **For UI/hero-motion:** M2-HER-1108's Ysolde line still stands: `battle_sandbox.json` `stand_ins.ysolde` has no `scene`, so she is a capsule in every battle.
SUPERSEDED: RENDER-REQUEST @ 1e14af8e FAST-TRACK: iskarra_p01_plaza_dusk,iskarra_i02_gate_from_the_plaza,iskarra_i03_broken_tower,slice_prologue_vigil_line; why: M3-ENV-724 after viewing f39cdde: the plaza slabs no longer read as pillows, the vigil packs no longer read as capsules. FIRST in the queue.
ANSWERED: lead/gate-render-env-art-f39cdde (FAST-TRACK Iskarra): P01, I02, I03 viewed and APPROVED (towers clad and windowed, galleries, the drowned midground, the heroes at their marks); slice_prologue_vigil_line passes. The two defects seen (pillowed slabs, capsule-like packs) are fixed in the request above.
SUPERSEDED: RENDER-REQUEST @ f39cdde3 FAST-TRACK: iskarra_p01_plaza_dusk,iskarra_i02_gate_from_the_plaza,iskarra_i03_broken_tower,slice_prologue_vigil_line; why: M3-ENV-724, the Lead's Iskarra fast-track (both passes: the towers faced out, tile cladding and glaze, windowed storeys, galleries, grime and spalling, the plaza inlay, cracked slabs and grass, the vigil gear and shells, banners, the drowned midground and skyline). slice_prologue_vigil_line renders on this branch's prologue; its capsules are slice-polish's. FIRST in the queue. (Moved from f104a0b7 to f39cdde3: the dais's trim, nothing else.)
SUPERSEDED: RENDER-REQUEST @ 8be2adcd: battle_arena_wall_head,battle_ch08_stair_hold,battle_boss_intro_reach,battle_arena_seawall_stairhead_storm,battle_arena_seawall_stairhead_hoist,battle_arena_seawall_stairhead_surge; why: the Lead's item 2 (big12 found the Ch8 wall arena and the Reach backdrop plain). `wall_head_storm` now plays on env-art's final seawall arena instead of the greybox, and the arenas moved one segment so the Fisher Stair's head (EntryMarker_ward, M3-BPR-407) is on the party's right. Second after the Iskarra FAST-TRACK. Supersedes the seawall ids in 4c0e9732.
ANSWERED: lead/gate-render-env-art-8be2adc (cloud). All six viewed and APPROVED as baselines: battle_arena_wall_head and battle_ch08_stair_hold now play on the final seawall (Watchers along the parapet, flags, laterite), battle_boss_intro_reach on the real wall, town and headland, and the three seawall_stairhead states are first baselines. Note for Combat/presentation: in the surge preview the Reach's hand at BossAnchor (-6, 0.9, -3.4) fills the fixed preview camera's left half. The arena is right (the hand grips the parapet); the Reach intro frames it properly. The headland in the Reach intro moves again with 44850dce (its own request).
SUPERSEDED: RENDER-REQUEST @ 9ba3b743: battle_arena_ossa_fen_roots; why: M3-ENV-705 audit, the bank's litter (the floor read bare).
SUPERSEDED: RENDER-REQUEST @ b1cde0eb: battle_arena_lowlight_engine_hall; why: M3-ENV-705 audit, the hall's piers articulated (panels, copper band, capitals).
SUPERSEDED: RENDER-REQUEST @ e11a83e4: pemakar_p04_harbour_day,pemakar_p11_sea_cut_weir_day,pemakar_p01_waterfall_of_fires,pemakar_p03_among_the_graves; why: M3-ENV-705 audit, rock patches on the massif's bare lower flank.
SUPERSEDED: RENDER-REQUEST @ a0d2549f: battle_arena_tideline_dawn,battle_arena_causeway_disc_sunset,battle_arena_causeway,battle_arena_tideline,causeway_c02_profile_against_the_lagoon,causeway_c08_drownbell_disc_approach,drownbell_flood,battle_boss_intro_drownbell,haluna_h01_village_from_sea,haluna_h10_dock_night,field_objective_line,field_interact_prompt,field_area_title,field_tip_card,dialogue_continue; why: M3-ENV-701 set dressing in Haluna, the causeway and the two arenas (the five field/dialogue shots frame Haluna's lane 1)
SUPERSEDED: RENDER-REQUEST @ 22a5de11: battle_arena_oruvel_raft_morning,battle_arena_causeway,drownbell_flood; why: the merge took the PC gate's copies of these three over env-art's; confirm they still match with the arena dressing
SUPERSEDED: RENDER-REQUEST @ 1a422476: ashcrown_a01_approach,ashcrown_a04_anvil_hall,ashcrown_a10_plume_from_the_rim; why: M3-ENV-705 Ashcrown grade (saturation x1.0, accents +18%) answering the human's greyscale complaint
SUPERSEDED: RENDER-REQUEST @ 71f19fbc: battle_arena_shoals,battle_arena_camp,battle_boss_intro_inquisitor; why: M3-ENV-706 Ch6 arenas replace the greybox
SUPERSEDED: RENDER-REQUEST @ ba16d48b: haluna_h01_village_from_sea,haluna_h04_dock,haluna_h10_dock_night,field_menu_map_haluna; why: the lagoon's fish weirs (M3-ENV-701)
SUPERSEDED: RENDER-REQUEST @ 179069de: battle_arena_causeway_route_afternoon; why: M3-ENV-705 its ground takes the zone's tidal-mud material
ANSWERED: 71f19fbc (gpu/render-env-art-71f19fb) and a0d2549f (gpu/render-env-art-a0d2549), all eight non-passing shots viewed and re-approved in 0f19d868.
SUPERSEDED: RENDER-REQUEST @ 24bf927a: iskarra_p01_plaza_dusk,iskarra_i02_gate_from_the_plaza,iskarra_i03_broken_tower; why: M3-ENV-710 Iskarra kit for the Prologue under its dusk (new shots, no baseline yet)
SUPERSEDED: RENDER-REQUEST @ fa67bfee: battle_arena_shoals,battle_arena_camp,battle_boss_intro_inquisitor; why: M3-ENV-706 density pass after viewing 71f19fb (the shoals read as bare sand, the camp's hard as one pebble repeat)
SUPERSEDED: RENDER-REQUEST @ 8770a067: corrow_c01_wall_head,corrow_c08_watcher_profile,corrow_c10_breach_fallen,brine_b01_arrival,brine_b05_barge_channel,battle_arena_shoals,battle_arena_camp,battle_boss_intro_inquisitor,iskarra_p01_plaza_dusk,iskarra_i02_gate_from_the_plaza,iskarra_i03_broken_tower; why: M3-ENV-712 carved Watcher backs, M3-ENV-705 Brine Shoals zenith, M3-ENV-706 Ch6 arena density, M3-ENV-710 Iskarra (supersedes the 24bf927a and fa67bfee lines)
SUPERSEDED: RENDER-REQUEST @ 599b2418: battle_arena_seawall_stairhead_storm,battle_arena_seawall_stairhead_hoist,battle_arena_seawall_stairhead_surge,battle_arena_coilspire_headland_path,battle_arena_coilspire_tier_landing; why: M3-ENV-713 Ch8's five new arenas (new shots, no baseline yet)
SUPERSEDED: RENDER-REQUEST @ fd630bb8: pemakar_p04_harbour_day,pemakar_p11_sea_cut_weir_day,battle_arena_ash_terrace_lanternfall; why: M3-ENV-1214 Pemakar's harbour pieces and day grade (new shots), the crown bell now in the Lanternfall arena's town
SUPERSEDED: RENDER-REQUEST @ 94fe8f77: tamsule_tp01_port_and_bell,tamsule_tp03_floating_market,tamsule_tp05_gantry_foot; why: M3-C07-04 the Tamsule port kit preview (new shots)
SUPERSEDED: RENDER-REQUEST @ 95be6118: battle_arena_keth_seep_terrace; why: M3-ENV-717 the Avalanche Ram's arena (new shot)
SUPERSEDED: RENDER-REQUEST @ 854e6a95: battle_arena_shoals,battle_arena_camp,battle_boss_intro_inquisitor,field_tip_card,brine_b05_barge_channel,iskarra_p01_plaza_dusk,iskarra_i02_gate_from_the_plaza,iskarra_i03_broken_tower,battle_arena_keth_seep_terrace; why: after the big11 merge, big11's copies of the first four lack env-art's Ch6 density pass and Haluna clutter; B05 gains the boat wake (M3-ENV-1000); the Iskarra plaza's corner moved for Kerrid's vigil (supersedes the Iskarra ids in 8770a067)
SUPERSEDED: RENDER-REQUEST @ 43492e80: battle_arena_lowlight_engine_hall; why: M3-ENV-716 the Lamp Engine's flooded hall (new shot)
SUPERSEDED: RENDER-REQUEST @ 60eee2f7: iskarra_p01_plaza_dusk,iskarra_i02_gate_from_the_plaza,iskarra_i03_broken_tower,brine_b01_arrival,brine_b05_barge_channel; why: after viewing 8770a06: Iskarra gets real water (reflections) and the paving inlay as channel lines; B01/B05 show the boat wake (supersedes these ids in 854e6a95)
ANSWERED: 8770a06 (gpu/render-env-art-8770a06): corrow_c01_wall_head and corrow_c08_watcher_profile viewed and re-approved in 895ff7ec; the Ch6 arenas, Iskarra and B01/B05 re-requested (big11's actors, the plaza and the wake changed since). ba16d48 and 179069d predate big11's NPCs and actor stances: re-requested below.
ANSWERED: 22a5de1 and 1a42247 (3 pass each after the import-crash re-render): nothing to approve.
SUPERSEDED by the request below for the Haluna ids: RENDER-REQUEST @ 29ddd021: haluna_h01_village_from_sea,haluna_h04_dock,battle_arena_causeway_route_afternoon; why: the fish weirs (ba16d48) and the route arena's tidal mud (179069d), not on the integration branch, now with big11's villagers and stances
SUPERSEDED by the H07 request: RENDER-REQUEST @ ab58f891: haluna_h01_village_from_sea,haluna_h02_tidewall_lane,haluna_h04_dock,haluna_h10_dock_night,battle_arena_causeway_route_afternoon; why: the beach palms clustered (no longer one even row from the sea) on top of the fish weirs and big11's villagers; the route arena's tidal mud
SUPERSEDED: RENDER-REQUEST @ c990e2c2: battle_arena_ossa_fen_roots; why: M3-ENV-718 the Mangrove Drowner's fen arena (new shot)
SUPERSEDED: RENDER-REQUEST @ 191e5e89: battle_arena_bridal_barge_night; why: M3-ENV-720 the Wakefin's unlamped bridal barge (new shot)
SUPERSEDED: RENDER-REQUEST @ c7703809: battle_arena_ansedra_lagoon_escape; why: M3-ENV-721 Warden Venn's escape on Ansedra's lagoon at dusk (new shot)
SUPERSEDED: RENDER-REQUEST @ fca99879: battle_arena_drowned_choir_ring; why: M3-ENV-722 the Drowned Choir at moonrise (new shot)
SUPERSEDED by the FAST-TRACK request below: 4c0e9732
SUPERSEDED by the FAST-TRACK request at the top: RENDER-REQUEST @ 0958af1a FAST-TRACK: iskarra_p01_plaza_dusk,iskarra_i02_gate_from_the_plaza,iskarra_i03_broken_tower; why: M3-ENV-724, the Lead's Iskarra fast-track for the Prologue. The towers had been inside out since M3-ENV-710; this pass adds tile cladding, blue glaze, windowed storeys, gallery ledges, the plaza inlay, a drowned midground, and hero figures. the far skyline (iskarra_far_towers) too. Supersedes the Iskarra ids in 60eee2f7, 854e6a95 and 4c0e9732.
SUPERSEDED by 8be2adcd: RENDER-REQUEST @ 4c0e9732: battle_arena_seawall_stairhead_storm,battle_arena_seawall_stairhead_hoist,battle_arena_seawall_stairhead_surge,battle_arena_coilspire_headland_path,battle_arena_coilspire_tier_landing; why: 599b241's outs predate big12's hero stances. The arenas are unchanged, so these are first baselines on the current actors. Supersedes 599b2418.
ANSWERED: 94fe8f7 (Tamsule TP01/TP03/TP05) and fd630bb (Pemakar P04/P11) were viewed and approved in f2a85a46. In fd630bb, Lanternfall passed.
ANSWERED: 179069d (causeway_route_afternoon): superseded by big12's viewed baseline (6e15d8d8) at a later head; nothing to approve.
ANSWERED: 43492e8 (battle_arena_lowlight_engine_hall): viewed and approved as its first baseline. The enemy is a stand-in capsule at that sha; the Lamp Engine model from big12 will drift it.
ANSWERED: 854e6a9: field_tip_card passed. Camp, shoals and the inquisitor intro all fall within the gull wing-phase, smoke and hound-pose differences of big12's viewed baselines (rmse to big12's 0.012, 0.034 and 0.0), so big12's copies stay. Its Keth out is the version superseded by the rework above.
ANSWERED: lead/gate-render-env-art-60eee2f (cloud): brine_b01_arrival and brine_b05_barge_channel were viewed and re-approved (the blue zenith; the vendor boat). The Iskarra outs are superseded by the FAST-TRACK request.
SUPERSEDED: RENDER-REQUEST @ b7182ba1: brine_b05_barge_channel,brine_b01_arrival; why: M3-ENV-705, the white barge's Order trim (B05 read it flat white).
SUPERSEDED: RENDER-REQUEST @ 9c26b66e: haluna_h07_chapel_court,haluna_h01_village_from_sea,haluna_h02_tidewall_lane,haluna_h04_dock,haluna_h10_dock_night; why: M3-ENV-705, the chapel's articulation (H07 read a plain box), plus the palms request (ab58f891) folded in. Supersedes ab58f891.
SUPERSEDED: RENDER-REQUEST @ 067bd833: battle_arena_iskarra_spire_crown; why: M3-ENV-726, the Spire crown, with the afterglow behind the party so the engine's 200 m shadow misses the slots. Supersedes 5d53f98c (not rendered yet).
ANSWERED: lead/gate-render-env-art-191e5e8 (battle_arena_bridal_barge_night) and c990e2c (battle_arena_ossa_fen_roots): viewed and approved as first baselines.
ANSWERED: lead/gate-render-env-art-ab58f89: haluna_h01, h02 and h10 viewed and re-approved (the drift is the density pass's palms and their shadows); h04 identical. causeway_route_afternoon keeps big12's viewed baseline (the arena is unchanged since).
ANSWERED (the Lead's item 3): gpu/m3-rnd-03-sefir-tells @ c3fd1eb4. All four `revenant_tells_*` shots (reflection and shadow, each on and off) viewed and APPROVED from env-art's side.
- **Shadow:** Sefir's shadow and hand shadows are crisper, with the tighter hem line, while Asha's stay soft.
- **Reflection:** his outline holds where the ripples would break it; the difference is subtle at this framing.
- Their shots and baselines live only on that branch, so the Lead's merge carries them with its `--update-baselines`. M3-ENV-1000's hookup follows once RevenantTells is on the integration branch.
SUPERSEDED: RENDER-REQUEST @ 46955a37: battle_arena_undertow_cage; why: M3-ENV-727, Ch20's Cage arena (new shot; after the FAST-TRACK and Ch8 requests).
NOT APPROVED: 95be611 (battle_arena_keth_seep_terrace). The backdrop reads as a wall of stretched white blocks and the seep strips as pale-blue ribbons, not a mountain pass. Rework is queued after the Iskarra fast-track (M3-ENV-717).
SUPERSEDED: RENDER-REQUEST @ 7f1a0fc7: battle_arena_keth_seep_terrace; why: M3-ENV-717 rework after 95be611 (crisp weathered wall, threads of seep). Supersedes 95be6118.
SUPERSEDED: RENDER-REQUEST @ 9c2aaa39: battle_arena_undertow_heart,battle_arena_undertow_heart_letting; why: M3-ENV-728, Ch21's Heart, Sefir's two arena states (held; the Letting), two new shots. After the FAST-TRACK, Ch8 and Cage requests.
SUPERSEDED: RENDER-REQUEST @ fb0abf9e: kitrow_ansedra_court_hall,kitrow_ansedra_basin_stacks,kitrow_keth_cloudloom_house,kitrow_keth_road_details,kitrow_lowlight_nave_bays,kitrow_lowlight_vey_details,kitrow_fen_roost_cord; why: M3-ENV-732, 22 Act II zone pieces never rendered (new shape-review preview, seven new shots). Low priority, after every other request.
SUPERSEDED: RENDER-REQUEST @ 5d3202d3: battle_arena_drowned_choir_ring; why: M3-ENV-705 after fca9987 (not approved): the moon between two singers, so the party isn't in a singer's shadow.
NOT APPROVED: lead/gate-render-env-art-fca9987 (battle_arena_drowned_choir_ring). The whole party stood in a singer's 150 m moon-shadow and read black. Fixed in the request above. The two pale capsules are the enemy stand-ins.
SUPERSEDED: RENDER-REQUEST @ 86fb7e4c: ashcrown_a01_approach,ashcrown_a04_anvil_hall,ashcrown_a10_plume_from_the_rim; why: M3-ENV-705 audit, the shapes (A04 plain square pillars, A01 flat tier faces): pillar dressing and buttresses. Supersedes 1a422476 (it includes that grade).
SUPERSEDED: RENDER-REQUEST @ d95ef28b: hollowmere_m01_dace_hull,hollowmere_m02_raft_city_dusk,kite_k01_moored; why: M3-ENV-731, the Ch17-18 kits had never been rendered (new preview, three new shots).
SUPERSEDED: RENDER-REQUEST @ 31eee89b: battle_arena_ansedra_lagoon_escape; why: M3-ENV-705 after c770380 (not approved): the sun at 5° so the deck reads, the bowl-domes articulated.
NOT APPROVED: lead/gate-render-env-art-c770380 (battle_arena_ansedra_lagoon_escape). The barge deck read black (the 1° sun put the whole deck in the bow rail's shadow), and the near bowl-domes read as stacked plain cylinders. Both are fixed in the request above. The pale cylinder on the foe side is the preview's enemy stand-in, not a kit piece.
SUPERSEDED: RENDER-REQUEST @ 65ed0b48: pemakar_p03_among_the_graves,pemakar_p01_waterfall_of_fires,battle_arena_ash_terrace_lanternfall; why: M3-ENV-705 audit, the stelae (P03 read plain stacked blocks): names cut in terrace script. Supersedes the P01/P03 ids in e11a83e4 (it includes that commit).
SUPERSEDED: RENDER-REQUEST @ f0ebe338: oruvel_o07_name_board,ch04_ferry_derelict,brightwater_b03_rail_drowned; why: M3-ENV-705 audit, the Seventh Terrace's counter (O07 read a flat red wall): plank seams, a black moulding, copper nails.
SUPERSEDED: RENDER-REQUEST @ 46808c96: coilspire_k01_headland_path,ch08_coilspire_path,battle_arena_coilspire_headland_path; why: M3-ENV-705 audit, the scrub (K01 read smooth green lumps): leaf clusters and twig tips.
SUPERSEDED: RENDER-REQUEST @ 3711b960: tamsule_tp03_floating_market,tamsule_tp01_port_and_bell,tamsule_tp05_gantry_foot,brightwater_b02_awning,ch04_ferry_deck; why: M3-ENV-705 audit, Tamsule's market counters and bundles (TP03 read plain boxes); the ferry bundles' flap faces fixed. Supersedes the brightwater ids in d4967aee.
SUPERSEDED: RENDER-REQUEST @ d4967aee: brightwater_b02_awning,brightwater_b03_rail_drowned,ch04_ferry_deck,ch04_ferry_derelict; why: M3-ENV-705 audit, the passengers' bundles (B02 read them as smooth blobs): folds, a cord, a loose corner. Includes the Underway and Coilspire headland requests above.
SUPERSEDED: RENDER-REQUEST @ 44850dce: corrow_c01_wall_head,corrow_c08_watcher_profile,corrow_c10_breach_fallen,ch08_corrow_arrival,ch08_corrow_stair,ch09_corrow_strand,ch09_corrow_road,battle_arena_wall_head,battle_ch08_stair_hold,battle_boss_intro_reach; why: M3-ENV-705 audit, the Coilspire headland across the bay (C01 read it as a smooth mound): bedding ledges on its sea cliff, sea stacks. Only the far headland changes; shots that don't see it stay put. Includes the Underway request above (9c811e51 is its parent).
SUPERSEDED: RENDER-REQUEST @ 30c9535b: battle_arena_underway_tower,ou_u04_lamp_gallery,ou_u12_terrace,battle_arena_underway,wildlife_zone_underway_crown,oruvel_o01_surfacing,oruvel_o19_dive_mooring; why: M3-ENV-705 audit, the drowned tower's bays get an articulated inner face (the gallery's walls read as bare slabs). The last five frame the tower from outside or far off and may not move.

## STATE AT HANDOVER (2026-10-25)

**HANDOVER DONE @ 1fee4436** (`claude/env-art`; the code is merge-ready at d065835e, and only docs changed after it).

Read this section first; everything below it is history. The branch is `claude/env-art`. The env-art session
(cloud) stopped for the account move with no subagents running.

### Done and merge-ready
- **MERGE-READY @ d065835e.** Full Godot suite 2016 run, 0 failed. Full tools unittests at 5ab6029c: 947 OK. Every
  Blender job touched is byte-identical, and every env-art baseline passes on isolated captures. It includes the
  integration branch at 7fa22c77.
- **Everything is in `status: review` (reviewer rendering) unless marked:**
  - M2-ENV-10, the B06 Saltgrass Causeway route.
  - M2-ENV-11, the arenas `tideline_dawn` and `causeway_disc_sunset`.
  - M3-ENV-06, the five Act I arenas: `oruvel_raft_morning`, `underway_tower`, `causeway_route_afternoon`,
    `derelict_deck_night`, `ash_terrace_lanternfall`.
  - Act I zone kits:

    | Task | Zone | Kit |
    |---|---|---|
    | M3-ENV-01 | Tidecup | `tamsule_bell` |
    | M3-ENV-02 | Brine Shoals | `brine_shoals` |
    | M3-ENV-03 | Terraces of Ash | `pemakar` |
    | M3-ENV-04 | the Seawall | `corrow` |
    | M3-ENV-04B | the Seawall breach and Ch9 night | `corrow` |
    | M3-ENV-05 | the sea floor | `oruvel_underway` |
    | M3-ENV-07 | Oruvel raft-town | `oruvel` |
    | M3-ENV-07B | Oruvel storm and Hullgnaw's split | `oruvel` |
    | M3-ENV-08 | Brightwater ferry | `brightwater_ferry` |
    | M3-ENV-08B | the Seventh Terrace | `brightwater_ferry` |
    | M3-ENV-09 | Ashcrown | `ashcrown` |
    | M3-ENV-09B | Pemakar's far Ashcrown | `pemakar` |
    | M3-ENV-10 | Coilspire | `coilspire` |
    | M3-ENV-11 | close-range plume | `pemakar` |

  - Fixes: M2-ENV-12 (Haluna gull normals), M3-ENV-700 (ferry transom).
- **Arenas are swapped in:** `game/data/battle/arenas.json` points all seven arena ids at
  `assets/environments/arenas/<id>/<id>.tscn`.

### In progress
- Nothing.
- **Not preserved:** env-art's superseded Shell Shrine kit WIP (local worktree branch `worktree-agent-a79dd51292ba3250f`
  @ d0749489; m2-slice's kit was adopted under M2-ENV-03). Pushing it to a separate branch was refused in this
  environment, so it goes with the container. It was for parts only; nothing depends on it.

### Exact next steps
1. The Lead merges `claude/env-art` @ d065835e (or later) into the integration branch. Delete
   `.godot/imported/*.glb-*` before `--import` in the gate worktree.
2. A review sweep of the `status: review` tasks listed above (reviewer rendering).
3. Every Act I zone in the act outline now has a kit. The next env-art queue is the Lead's call. Candidates:
   - the weaker preview views each task file lists (for example Corrow C03's sea face, Oruvel O10's gull, Ashcrown
     A08's loggia, Brightwater B07's stem-gull);
   - Act II zones (Ch10 Ossa Fen and onward);
   - night and storm variants once Art adds the colour-script rows.
4. New env-art ids come from the id block: tasks M3-ENV-701+, ADRs 0160–0169, handoffs `<date>-<role>-env-art-<n>.md`.

### Open questions (owed by others; none blocks env-art)
- **Art:** colour-script rows `ch01_storm`, `ch04_derelict`, `ch05_temple` and `ch08_day`; `ch08_after` (proposed in
  corrow.md §7); the `ash_fall` swatch.
- **Character + Tools:** sign-off on the import kinds `brine_shoals_kit`, `pemakar_kit`, `corrow_kit`,
  `oruvel_underway_kit`, `oruvel_kit`, `brightwater_ferry_kit`, `ashcrown_kit` and `coilspire_kit`.
- **Rendering:**
  - M3-RND-24: underwater downwelling and in-scatter vs walls.
  - M3-RND-25: the underway arena's look.
  - M3-RND-26: the Tidecup drop.
  - The Ch9 ambient 0.7 vs the colour script's 0.3.
- **m2-slice:** M3-ARC-04 (the shrine's `Shaft_*` lights inside `ShaftFog`).
- **Narrative:** the Ch9 Fisher Stair (the breach cuts it after 12 steps); the sea floor's floor count (F9 is the
  gallery) and its dead ship's ribs (Hullgnaw).

### Known bugs and loose ends
- Five UI and dialogue baselines drift from the wetter Haluna tidewalls (not env-art's to re-approve):
  `field_objective_line`, `field_interact_prompt`, `field_area_title`, `field_tip_card`, `dialogue_continue`.
- Battle-presentation (both happen on the greybox too):
  - In multi-shot captures, `AudioDirector.attach_battle` logs a freed-instance error.
  - The arena loader logs an owner warning when it reparents the WorldEnvironment.
- Big kit pieces placed by hand need a larger per-placement LOD1 start: the import ends LOD0 at 70 m from the
  piece's middle.
- `haluna_h10_dock_night` sits at rmse 0.00545, within the limit, from older drift.

### Gotchas (read before touching env-art files)
- **Winding (2026-10-27, M3-ENV-724).** `kc.quad_strip`'s face normal is cross(column direction, row direction). A
  lathe-style grid of rows along +Y with columns round the axis faces *inward*, so pass `flip=True` (Iskarra's
  shafts were inside out for days). Check new pieces numerically, either radially or with the ray audit: rays from
  outside, where a first hit on a back face means a hole.
  - **The audit across the Haluna kit found no other visible case.** `outrigger_7m`'s outer and inner shells are
    swapped, but they read the same from outside. Double-layer sheets (laundry, awnings, roost panels, sails)
    score as "back" by construction and are fine.
- **Fog-lamp rule (the Lead):** every OmniLight3D and SpotLight3D in an arena, or near a dense FogVolume, sets
  `light_volumetric_fog_energy = 0`, because Godot's default of 1.0 bands the volume bright. `arena_scenes.py`
  writes it. `tools/tests/test_fog_lamps.py` enforces it, with `KNOWN_EXCEPTIONS` tied to request tasks.
- **Baselines only from isolated captures:** use `tools/screenshots/capture.sh --shots <ids> --out <dir>` (one Godot
  process per shot, as ci_local does). A single shared `capture.tscn` run is order-dependent once creature models
  are in frame (rmse 0.03 from shot position alone).
  - Before `compare.py --update-baselines`, copy the PNGs and `capture_report.json` into `tests/screenshots/out/`.
  - If only `baselines.json`'s key order moved, restore it with `git checkout`.
- **Haluna material writers:** kits must load them by path under the name `haluna_materials` (importlib), never
  `import materials`, because tamsule_bell has its own `materials.py`.
- **New kit `.glb.import` files** need `import_script/path` set to the kit's post-import script, or the materials
  don't map.
- **LUT `.png.import`** files are hand-written 3D-texture imports; the kits' import-settings scripts must skip them.
- **Tests:**
  - TestCase is a RefCounted, so reach the tree via `(Engine.get_main_loop() as SceneTree)`.
  - The runner does not await coroutines.
  - `free()` (not `queue_free()`) any zone with a publishing WaterSurface before a test returns.
- **Append-only shared files** (shots.json, baselines.json, blender_builds.json, PROVENANCE.md, the KINDS lists)
  conflict on every agent merge. Union them; check `blender_builds.json` for empty `{}` jobs, and run
  `tools.tests.test_blender_builds`.
- **Gates:** run only fast scoped checks per item, long runs niced in the background, and Blender verify only for
  the jobs touched. `godot` and `godot-render` must be on PATH (`~/.local/bin` symlinks; `tools/dev/fetch_godot.py`).
  The Blender wrapper is `~/.cache/hymn/blender-*/blender`.
- **Messaging the Lead session** from here is refused (`elevated_session_untrusted_device`); report through this file.

## Now
- **CONFIRMED 21:06: the last Oruvel outrigger fix (M3-ENV-1391) is pushed.** It is 0de280e2 on origin/claude/env-art,
  MERGE-READY.
- **LEAD (21:05), answered: the Act II Ch10–Ch12 beauty pass (M4-A2P-1402, review: art). MERGE-READY @ a60417fc.**
  - **Viewed:** eye-height stills at every interactable and zone-map POI: Ossa Fen 7, the Sunken Vey 5, Lowlight 5.
  - **Fixed:**
    - The fen's reed platforms read plastic green; `kit_fen_reed` is now straw-grey.
    - The fen mud and bank used mirror-wet defaults; they are now matte damp.
  - **Kept:**
    - The fen edge's sheen is backlight from the low sun.
    - The Vey and Lowlight read cold and empty, as designed.
  - **LEAD-ASK:** the Vey landing is a bare flagged platform with a rail. Dressing it would be new content; your
    call.
  - **Checks:**
    - Tools: the fen and haluna kit tests OK.
    - Godot `--filter=ch10`: 3/0.
    - validate_data and taskboard --check clean.
  - **Baselines that move (none written):** the Ossa Fen shots with reed platforms.
- **STATUS 20:46 (answers the Lead's 20:45 check-in): everything is pushed; the head is the log commit after 937389e9.**
  - Oruvel's last outrigger (M3-ENV-1391): MERGE-READY @ 0de280e2 (pushed 19:58).
  - The Ch4 beauty pass and the Prologue-to-Ch4 arrivals (M4-A2P-1401): MERGE-READY @ 937389e9 (pushed 19:58).
  - **Transitions, viewed as played:**
    - Zone exits: this stretch has none to walk through; every hand-off is a beat or cutscene. So I viewed the frame
      the player gets on arriving at each spawn (M4-A2P-1401 has the findings: the ferry Landing is fixed; the
      DockShore camera and the shrine Entry party stacking are the Lead's call).
    - Chapter cards: flow_chapter_card_ch04_voice, flow_chapter_card_ch04 and cutscene_act_card were captured to my
      scratchpad (no baseline) and viewed. They are clean: centred serif titles on black under the gold rule.
    - One typography note for UI/narrative: the Ch4 voice caption uses straight ASCII quotes ("...") on the serif card;
      typographic quotes would match the card. That's a loc string, not env-art's.
    - Ch1 to Ch3 have no chapter card in the played route; each hand-off is a fade into the next zone's arrival.
- **LEAD (19:45), answered: M3-ENV-1391's last box. MERGE-READY @ 4f46aecd.** LowHull's outrigger lay along the run's
  two plank bridges, its booms through their rails. It now floats alongside the run (z -21.25, yaw 180), with its
  AABB 0.1 m clear. The salvage on the planks over LowHull still blocks the way, and both still drift with the block.
  - Viewed from the run, from the bridge and from the side.
  - The AABB mirror of cloud-qa's check lists only the dive raft's three intended pairs.
  - test_oruvel_moorings drops the LowHull allowance and passes; test_zone_dressing_ch01 OK.
  - Godot `--filter=ch01` and `--filter=edge_walls` are green.
  - The Ch4 pass continues (the galley's satin walls are in at 7d2197e6).
- **LEAD (19:25), answered: the Ch4 beauty pass and the Prologue-to-Ch4 arrivals (M4-A2P-1401, review: art).
  MERGE-READY @ 34fdefa3.**
  - **Viewed:**
    - eye-height stills along the walkthrough legs: Haluna wake 18, ferry 18;
    - the arrival frame at each hand-off's spawn (`tools/hero/walk_stills`, the real camera and party): Drop, Surface,
      Beach, FromHaluna, Entry, NemeDoor, DockShore and Landing.
  - **Fixed:**
    - The Terrace galley's lacquer boards streaked white with sky reflections indoors; they are now satin
      (`bf_lacquer_black_satin`, 7d2197e6).
    - The Landing arrival was a black rock. A ferry lantern now sits at the gangplank's head as its warm key light.
  - **LEAD-ASK (not env-art's to change):**
    - The Haluna wake's night shallows glow bright day-cyan (`haluna_mood.gd`'s held-glimmer sea-glow). Intended, or
      calm it?
    - The DockShore arrival camera sits behind Rhen's head, so he fills the frame (camera).
    - At the shrine Entry arrival, Asha and Toma stand stacked into Rhen (party spawn spots).
  - **Checks:**
    - Tools: the ch04 and ferry tests OK.
    - Godot `--filter=ch04`: 13/0.
    - validate_data and taskboard --check clean.
  - **Baselines that move (none written):** the ferry galley and landing shots.
- **LEAD (18:24), answered: the Ch2 Haluna and Ch3 causeway beauty pass (M4-A2P-1400, review: art). MERGE-READY @ dadb6930.**
  - Stills at eye height along the walkthrough legs, viewed: Haluna 22, the causeway 12, the Shell Shrine 8.
  - **Fixed:** Haluna's 49 windbreak trees rendered as black blots from every side. `kit_windbreak_leaf` now has a
    tint over 1, half the baked AO, more transmission and a softer wrap; the trees read as leafy dark-green shade.
  - **Viewed and left as is:**
    - Haluna's beach, lanes and stilt pier: the sea light is strong.
    - The causeway's stepping stones, posts and tide pools read clearly.
    - The shrine's sunlit approach and cool interior are as designed.
  - **Checks:**
    - Tools: test_haluna_kit and test_haluna_dressing OK.
    - Godot `--filter`: vegetation 17/0, haluna 65/0.
    - validate_data and taskboard --check clean.
  - **Baselines that move (none written):** every Haluna shot that frames a windbreak tree.
- **LEAD (17:45), answered: the Ch1 Underway and Oruvel dressing pass. MERGE-READY @ 922cd122.**
  - **Stills viewed before and after:**
    - the Underway's four walkthrough dive legs, 22 points at eye height;
    - Oruvel's decks, the scale booth, the Terrace and the east vista;
    - the dive raft: looking down into the well and approaching it.
  - **Underway caustics:**
    - There were none. The water shader projects caustics onto the floor as seen from above, never from under the
      surface.
    - `env_weathering` gains opt-in `uw_caustics` (default 0, so every other material is unchanged). It draws the
      `water_caustics` web on every surface under the live water height: floors on x/z, walls on their own plane (a
      first try smeared the floor's web down the walls as streaks). It fades with depth and view distance.
    - The Underway kit's weathered materials turn it on (`ou_materials.py`, 1.2). The underway_tower arena uses the
      same materials, so it gets the caustics too.
  - **Dive readability:**
    - The dive raft's well read as flat dark water; its tether and ladder are tarred black.
    - A rope hoop of six white floats now rides the well, and a pale shot-line drops from it, white-tagged every
      0.6 m, to a lead sinker (`ov_heroes.py` `_dive_mark`; dive_raft 15424 tris, within its 18000 budget).
  - **Not changed (the layout's, act1-chapters'):**
    - The Underway's sun casts hard, crisp shadows at about 10 m depth. Softening them (shadow blur, or a lower sun
      energy with more ambient) would help the underwater read; it's the layout's `sun` block.
    - Caustics also show inside those shadows, since they are emission; a real-GPU look will tell whether that
      matters.
  - **Checks:**
    - Tools: test_oruvel_kit, test_oruvel_moorings and the Underway kit tests OK.
    - Godot `--filter`: underway 9/0, environment_shaders 11/0, shader_prewarm 22/0, weathering 2/0, ch01 20/0,
      water 49/0.
    - validate_data clean.
  - **Baselines that will move (none written):** the Underway and underway_tower shots, and the oruvel shots that
    frame the dive raft's well.
- **LEAD (16:45), answered: the Prologue dead-city dressing pass. MERGE-READY @ b39caa29.**
  - Eye-height stills along the whole cutscene path were viewed before and after: P01, the P01-to-P02 blend at 25/50/75 %,
    P02, Rhen's crossing, the plaza in eight directions, and up at the towers.
  - **Found and fixed (Iskarra kit, `iskarra.py` + `materials.py`):**
    - The towers read clean. Their painted tide band, rain streaks and the new old high-water ring now show at P01's
      distance: 1 m shaft rows, and LOD1 has 24 sides at 3 m (P01's towers are past the 70 m LOD switch).
    - `env_weathering_body.gdshaderinc` gains opt-in `grime_from_wet` (default 0, so every other material is
      unchanged). Iskarra's cladding uses it: wet gloss had mirrored the dusk sky and hidden the stains.
    - The lamp globes read as white electric street lamps. They are now dim amber oil-light, so Rhen's lantern
      stays the flame.
    - The low plaza flags hold standing water.
    - The dais top, the lower half of P02 where the line lands, was one blank slab. It is now paved with flags.
  - **Not changed:**
    - The south and south-west views are open sea, but no shot faces that way.
    - The sky is a flat gradient; the environment is in `prologue.tscn` (m2-slice's).
  - **Checks:**
    - test_haluna_kit, test_iskarra, test_iskarra_spire and test_haluna_dressing: 44 OK.
    - Godot `--filter`: prologue 8/0, iskarra 1/0, environment_shaders 11/0, shader_prewarm 22/0, weathering 2/0,
      corrow 18/0.
    - Untouched Iskarra pieces rebuild byte-identical.
    - `--filter=import` has 1 failure, and it predates this change: `test_every_glb_import_runs_its_category_script`.
      41 committed haluna `.glb.import` files have no `import_script/path` (ansedra_causeway_6m from 86e01d57,
      court_*, archive_*, hm_dock_*, ...). This change touched no `.import` file. It's env-art-b's Ansedra batch;
      flagged, not fixed.
  - **Baselines that will move (none written):** iskarra_p01/i02/i03, slice_prologue_p01, slice_prologue_vigil_line,
    battle_arena_iskarra_spire_crown, and the Ch9 Corrow shots that frame Iskarra towers.
  - **PC-QUEUE:** a real-GPU look at P01/P02 for the tower grime and the puddle gloss.
- **LEAD (16:26), answered: cloud-qa pass 6's Oruvel hull-vs-deck overlaps are fixed. MERGE-READY @ bc790ea8.**
  - Each pair was viewed at eye height before and after (scale booth, keel moorings, Terrace raft, commons canoe):
    - scale_hull x raft deck: the booth's raft is now `raft_deck_square` (new kit piece, 10 x 10 m, tucked float
      logs, glb + import + PROVENANCE row + manifest), and the hull sits at x -7.7, 0.8 m of water off the deck edge;
      the scaleman's place (x -7.2) is still inside the booth;
    - keel_hull x two tucked decks: the moorings move to z -29.5, clear of the keel;
    - terrace_hull x tucked deck: the raft shifts 0.85 m east;
    - outriggers x small deck and two bridges: the commons canoe moves to (19.6, -16.4).
  - **Kept, intended:** dive_raft x the two plank bridges and the broken bridge; the stilted LowHull outrigger x
    its two bridges. The AABB mirror of cloud-qa's check now lists only those 5 pairs.
  - **Checks:** test_oruvel_moorings, test_oruvel_kit, test_zone_dressing_ch01, test_ch01_zone_copies OK;
    validate_data and taskboard --check clean; Godot `--filter=ch01` 20 run / 0 failed, `--filter=edge_walls`
    2 / 0. Skipped: the full suite and the manifest (no code touched). The kit preview's back row gains the
    square raft at x 168; any preview shot that frames it shows it new (no baseline written).
  - M3-ENV-1323's GPU A/B still waits on the PC.
- **LEAD (16:09), answered: the Ch10–Ch12 eye-height walk, the dock-edge check (the Sunken Vey gallery included) and
  env-art-b's kit requests are done.**
  - The branch head is f4b2b548 plus a `.uid` commit. The MERGE-READY lines below cover each part:
    - 990bdbb2: dock edges and the Ch10–Ch12 walk;
    - 9ba63a92, d11b8437, 08f61623: M3-ENV-1329, 1328, 1330;
    - a319362b and f4b2b548: M3-ENV-1327's parts and `camp_tent`.
  - **M4-A2P-114 (the pier kit):** not touched here. It's env-art-b's, as the Lead says.
  - **Still open for env-art (smaller):** the kits' own flat preview slots, the Coilspire headland's far facets, the
    order chapel's plain white box. M3-ENV-1323 waits on the PC.
- **MERGE-READY @ a319362b: env-art-b's kit requests, the next batch.**
  - **M3-ENV-1327, partly** (798184107, 5d9d63a4, a319362b), each viewed:
    - Corrow's puddles bake damp, not mirror-wet: no black holes at `foot_kerrid`.
    - `market_boat_a`'s umbrella has ribs, a sagging cloth and a scalloped hem.
    - Tamsule's shophouses are stocked (counter, shelves of jars, bolts and baskets, hung cloth).
  - **M3-ENV-1323** (f5cd318c), the Underway arenas' rectangles: **blocked on the real GPU.**
    - On lavapipe they follow the F9 slabs' edges against the sand.
    - A softer sun (trial, reverted) only brightened the floor.
    - A/B on the PC-QUEUE.
  - **`camp_tent` end-on** (next commit): the rear gable has a belly, a seam and a hem.
  - **Still open in M3-ENV-1316/1327:** the kits' own flat preview slots, the Coilspire headland's far facets, the
    order chapel.
- **MERGE-READY @ 990bdbb2: the Lead's 14:48 batch (the Ch10–Ch12 walk and dock-edge check; env-art-b's kit requests,
  first three). The integration branch (big24) is merged in.**
  - **Dock edges, Ch10–Ch11** (b01d806e):
    - Edge walls in Ossa Fen (84), Reedhollow (136), the Sunken Vey (81) and Lowlight (10).
    - `zone_edges` now traces each walk block's own edges, so the yawed ring walks get a few turned walls, not
      hundreds of grid steps.
    - Walking every spawn in eight directions gives 0 falls with the walls. Without them: Ossa Fen 5/24,
      Reedhollow 8/16, the Vey 8/16.
    - **M4-HER-1166 → review:** chapters' `GateStep` closes Lowlight's gate (`hero_field_snaps` 2/0). The test owner
      drops its KNOWN entry.
  - **The Ch10–Ch12 eye-height walk** (`poi_stills` now covers them; 41 stills viewed):
    - **Fixed** (990bdbb2): the fens' root-mat humps rose as bare grey domes round each mangrove's foot. They now lie
      under the tannin water. `ossa_fen_ground` and `reedhollow_ground` rebuilt.
    - **Reads:** the Vey (landing, conduit, fig end, the way to Lowlight), Lowlight (gate, engine hall, lamp bench,
      sanctum), Cloudloom's hall and dais, Reedhollow.
    - **Ch12, still on the PC-QUEUE:** Keth Pass and Quellan are near-black in shade under lavapipe.
  - **env-art-b's requests:**
    - **M3-ENV-1329** (9ba63a92), Brine Shoals' wet/dry seam: done as proposed, plus a stale `camp_tent_burned`
      rebuilt from its source.
    - **M3-ENV-1328** (d11b8437), the sea-cut weir: tight arrises, broken joints, the crest above the water. P11
      viewed.
    - **M3-ENV-1330** (08f61623), Corrow's low-town ground: the per-triangle cobble is gone, so no triangle or
      tile-edge patches. The plain from the wall is only faintly helped (the earth material mutes the vertex channels;
      next step noted in the task).
    - All three are at review for env-art-b.
  - **Next:** M3-ENV-1323 (the Underway arenas' light leak), M3-ENV-1316 (near-range kit faces) and M3-ENV-1327
    (Ch5–Ch9 audit kit items).
- **MERGE-READY @ b45addab: the Lead's Prologue–Ch4 POI and interactable walk at eye height (the 10-30 pass).**
  - **Method:** `tools/act1/poi_stills.py` drives walk_render's new `auto_targets`. It takes every Interactable in
    each zone and every zone-map POI, standing an eye off each on its clearest side. About 130 stills over Oruvel,
    the Underway, Haluna, the causeway, the Shell Shrine, the ferry and the wake, all viewed. The Prologue has
    neither: its walk was done before.
  - **Fixed:**
    - **The Underway** (eb887bc5): the `old_tin` find and the `limpet` look had no prop. New pieces `old_tin` and
      `shaft_limpet`.
    - **The ferry** (51ac308c): the Order shrine, the crossing's rest point, was bare wall. New `deck_shrine` on the
      mainmast's forward face, on the OrderShrine block. The ferry and Underway kits were rebuilt in full: every
      other glb byte-identical.
    - **The wake** (b45addab): the fisher and his feast mat stood in the night's swash. Mat, `table_fisher` and the
      fisher's point moved 2 m inland together; floors re-read.
      **FYI act1-chapters:** that's `tools/act1/ch04_haluna_wake.py`'s fisher point and trigger.
    - **Oruvel's boats and walkway edges:** the playtest FAST-TRACK above.
  - **Read fine, no change:**
    - Haluna's touch points;
    - the causeway's slabs, posts and offering ring;
    - the Shell Shrine (the dome's lines are its mortar ribs; the floor streaks are sun through the oculi);
    - Oruvel's NPCs;
    - the wake's feast, lane, chapel, dock and wall (with the chapter's flags set).
  - **Not env-art's (to chapters):**
    - Oruvel's pen child stands in the PracticeNet block, which the kit draws as the pen's open water, while the
      greybox's solid NetPen deck lets the player walk over that water.
    - Reedhollow Shore's camera is the field camera's cabin rule (above).
  - **Checks:**
    - tools: ferry kit, Underway kit, zone_dressing_ch01, haluna_dressing, ch04_validate, validate_data;
    - Godot `--filter=ch04` 13/0, `haluna` 65/0.
  - **Shots that will drift:** ferry shots framing the mainmast; the wake's feast shots.
- **MERGE-READY @ eb887bc5 (supersedes 3389db19): the playtest FAST-TRACK is complete and pushed.**
  - **What's in it:** the boats (7fbb9319) and the Oruvel edge walls (28b005ad), as the entry below says.
  - **The interrupted step (the Lead, 13:48):** a long compound shell command stalled on a permission prompt. It is
    redone as plain single steps inside the worktree and the scratchpad: no process kills, no writes outside, no
    network. Nothing was refused this time.
  - **Also in eb887bc5, the walk pass's first fix:** the Underway's two interact points had no prop.
    - `old_tin` (the find behind the coral curtain) now has a Lit Age tin at the alcove's back.
    - `limpet` ("Look", the shaft fight) now has a ribbed ochre limpet and three young ones on the gauge room's
      north wall.
    - New pieces `old_tin` and `shaft_limpet` in `ou_props.py`, with PROVENANCE rows. Viewed at player height.
  - **The walk pass continues next.** The rest of the Prologue–Ch4 POI and interactable stills are rendered and being
    reviewed: Haluna, the causeway, the ferry and the wake.
- **MERGE-READY @ 925367eaf: FAST-TRACK, the human's playtest in Oruvel ("docked boats clip through the docks …
  you can easily fall off and start walking in the water").**
  - **(1) Boats, fixed (7fbb9319).**
    - **The finder:** every piece of the dressing rebuilt from the kit and placed as dressed; a hull vertex (tar or
      paint) inside another piece's walking planks is a clip. It found 11 real clips:
      - the five free-standing mooring rafts' bows rose through the bridges next to them and the commons' north
        decks (the keel-hull's two rafts by about 95 vertices each);
      - the run's low hull lay in the water *through* its bridge;
      - the cook's boat sat 0.8 m into the outer mooring's raft.
    - **The fix:**
      - the mooring rafts are the tucked rafts (hulls under their own planks);
      - the low hull lies *on* the run's planks (C1-12's "thrown up across");
      - the cook's boat moved clear and rides dry (the sea showed inside her);
      - three outrigger canoes are moored in open water beside the decks, so the town keeps its boats.
    - **Viewed:** before and after stills at ten spots from player height and above, plus the new moorings. The
      scale booth's hull stays, its counter over the deck edge by design.
    - **Test:** `tools/tests/test_oruvel_moorings.py` (11 failures on the old dressing, OK now).
    - **Not added:** fenders and lines to cleats. Say if you want them.
  - **(2) Edge walls, Oruvel (28b005ad).**
    - **How:** `assets_src/environments/zone_edges.py` derives invisible walls (0.12 × 1.6 m) along every walkway
      edge over the water from the greybox. Junctions stay open; a stall or hull taller than the deck already walls
      itself. A wall at an opening a hideable block fills (the storm's lost dive bridge) collides only while that
      block is hidden. 58 walls.
    - **Runtime:** `ZoneKitDressing` builds them from the dressing's new `edge_walls` list (a small additive block:
      **FYI act1-chapters**, it's your file).
    - **Proved by walking:** without them the hero falls to the sea floor (y −1.0); with them he stops 0.3 m from
      the edge.
    - **Test:** `tests/integration/test_zone_edge_walls.gd` (walls collide and draw nothing; the dive bridge's ends
      wall up only when it's hidden).
    - **Brightwater's ferry:** already railed in its own collision (ferry, derelict, islet, gangplank). Nothing
      needed.
    - **Ch4 wake's dock (real Haluna):** walked off it in eight directions from the shore end, the middle and the
      end. It's railed; only the shore end steps down onto the beach (Haluna's natural shallows).
  - **Checks:** test_zone_dressing_ch01, test_oruvel_moorings, Godot `--filter=edge_walls` 2/0, `zone_kit` 13/0,
    `ch01` 20/0, validate_data.
  - **Shots that will drift:** the Oruvel shots that frame the moorings, the commons' north edge, the cook's boat or
    the run (`ch01_oruvel_dressed`, `zone_oruvel_*`, `ch01_net_pen`, the storm shots).
- **MERGE-READY @ 2adf2b2c: the Lead's 12:08 items (1) and (2).**
  - **(1) H07 chapel marble: already within ΔE 0.03 on this branch.**
    - The fix is b0eb0a49 (03:16). The committed baseline was approved at 00:46 (big17), before it, and that is
      what fails.
    - A fresh capture on this branch passes all four H07 palette checks: chapel sun face ΔE_ok 0.018 to
      order_marble 0 (max 0.03), wall grain 0.0032, banyan root L 0.447.
    - No loosening and no new change needed: re-approve `haluna_h07_chapel_court` from a big23 render.
  - **(2) the Ch11 regular-fight arena: `sunken_vey_gallery`, built and registered** (the id chapters asked for in
    M4-A2P-041).
    - It's the Vey's conduit court as the fighting floor, with the zone's own dressing round it (arcades, drowned
      columns, figs, the galleries, the conduit housing; props kept 4 m off the slots). Ch11's overcast noon over
      the still lagoon.
    - Viewed: urchin and party on the court, the gallery bridge and the arcades behind.
    - Checks: `test_arenas` 21 OK, Godot `--filter=arena` 18/0, validate_data.
    - chapters names it on `ch11_vey_rays` and `ch11_vey_urchins`.
    - **No `battle_arena_sunken_vey_gallery` shot yet:** adding one turns `test_screenshots` red until the Lead
      approves a first baseline. Say if you want it.
  - **(3) the Prologue–Ch4 POI and interactable walk:** rendering (`tools/act1/poi_stills.py`, walk_render's new
    `auto_targets`).
- **MERGE-READY @ 59628c29e: Ch10–Ch12 walk-through stills at player height** (the Lead's next item).
  - **Method:** `tools/hero/walk_stills` arrival stills at all 17 spawns, on env-art's dressed previews, since
    none of Ch10–Ch12 is mounted yet.
  - **Ossa Fen, fixed:** at DrownerArena the field camera looked through a mangrove's limbs. The generator now keeps
    living trees 4.5 m off each spawn's measured camera line (`CAMERA_LINES`), which removed four trees, and a test
    checks it. Re-viewed: DrownerArena and FromReedhollow are clear.
  - **These read:** Reedhollow Gate; Lowlight Gate, EngineHall and Sanctum; Sunken Vey Landing and FromLowlight;
    Cloudloom Hall.
  - **Reedhollow Shore:** the camera settles 2 m behind Rhen beside a hull arch. That's the field camera's cabin
    rule, not the dressing: FYI hero-integration.
  - **Ch12, PC-QUEUE (again):** Keth Pass, Quellan and Cloudloom's Approach are near-black in shade under lavapipe
    although the layouts are morning and noon (sun 2.0, ambient 0.8). Quellan FromCloudloom shows the party against
    a black void. Judge on the real GPU before any grade change; the stills are in env-art's scratchpad and can be
    re-made with walk_stills `--scene=res://game/levels/_tests/ch12_zones/<zone>_dressed.tscn --spawn=<id>`.
- **MERGE-READY @ 8e4ab352: PC pass 5's rows 59, 24 and 66, and a tools-suite red.**
  - **The Lead's correction is taken.** Ch13–Ch16 are env-art-b's. env-art's parallel Ch13–Ch15 dressings were
    already withdrawn in the big22 merge (7fad181e) and are not filed as requests: env-art-b's mounted versions
    stand.
  - **Row 59 (`ch01_o10_gull`), fixed** and viewed (O10 now frames the carved gull against the sky).
    - **Cause:** the field camera's keep-in-frame safety net for FIXED shots (692b5515, `game/world/**`, Systems')
      also turned *cutscene* shots toward the leader. O10's 85 mm telephoto doesn't frame Rhen, so it swung down
      onto his deck.
    - **Fix:** a scripted (cutscene) shot keeps its composition; the net stays for volume shots (26661c7a, the
      Lead's assignment). Test `test_a_scripted_fixed_shot_keeps_its_frame_without_him`; camera tests 72/0.
      **FYI hero-integration / Systems:** it's a one-line guard in `evaluate()`.
  - **Row 59, the "ring decals"** were the weathering shader's barnacle and weed bands. Their soft tops reach
    +0.2 m over the tide line, so Oruvel's decks (at the tide line) were crusted.
    - **Fix:** `ov_timber` and `ov_timber_new` end both bands below the walked top (9866ea4a). Hull timber keeps
      them; `ov_hull_tar` is unchanged.
    - **Viewed** on ten Oruvel shots: decks clean, nothing else moved. The Oruvel shots will drift slightly on the
      decks.
  - **Row 24 (DockShore): no env side.** It's fixed on the current tree by hero-integration's 0ffe9260 (after pass
    5's 7dc3ab41): a still at DockShore shows the camera in front of Rhen on the jetty, clear.
  - **Row 66 (Ch4 start): no env side.** Hero-integration's e7af4147 (also after 7dc3ab41) fixed the pull, which a
    windbreak tree on a 120 m release line started. The settled NemeDoor camera is clear of every mesh.
  - **Tools suite on big22:**
    - **`test_arenas`:** it regenerated `ansedra_lagoon_escape` and `bridal_barge_night` without
      env-art-b's zone looks (c1ed49ad6), so it now leaves them to `ansedra_arenas.py`'s own test (8e4ab352).
    - **`test_palette_check` H07:** the committed baseline (big17, 00:46) predates the chapel fix b0eb0a49 (03:16).
      It needs the Lead's re-approval of `haluna_h07_chapel_court`; env-art writes no baselines.
      Checked: a fresh render of H07 on this branch passes all four palette checks (chapel ΔE 0.018).
    - **Other reds aren't env-art's:** rig integrity, villagers/hero clips, audio, status names, the
      `oruvel_seabed.glb` build job (M3-CIN-1232) and the wildlife baseline.
  - **Next:** Ch10–Ch12 walk-through stills at player height (rendering now).
- **MERGE-READY @ 7fad181e: the FAST-TRACK `test_keth` fix and the big22 integration merge; env-art's Ch13–Ch15
  dressings are WITHDRAWN.**
  - **test_keth:** the inn's door test looked for crag walls. The inn's walls have been dry stone since Ch12
    (M4-A2P-042), so the test now checks `M_DRYSTONE` (c010ee90). Still red on the integration branch until this
    merges.
  - **Ch13–Ch15:** the integration branch already carries Ch13–Ch15 dressed and mounted by an earlier run
    under this session's own id (`01UPFyEA3FwDAoAKTpVGbGsy`; e.g. 9fa8dce4, b49e37a5; M4-A2P-043/044/045, with
    shot rigs and tests). env-art's parallel
    versions wrote the same files, so the merge takes the integration's side throughout.
    - Every Ch13–Ch15 file of env-art's is removed or restored to the integration's: the glbs, generators, tests,
      previews, and mount requests 0431, 0441 and 0451.
    - The tree equals the integration branch except `tools/tests/test_keth.py` and these logs.
    - env-art's versions stay in history at 39968c35 if anything there is wanted.
  - **The MERGE-READY lines below for 14ff2eb7 (043), 562c7f57 (044) and 39968c35 (045) are void.**
  - **LEAD-ASK:** "continue Ch13–Ch15" looks done on the integration branch. env-art is taking row 59
    (`ch01_o10_gull`) and rows 24/66 now. Name anything Act II wants beyond those.
- **MERGE-READY @ 39968c35: M4-A2P-045, Ch15's open sea dressed** (the Lead's (b), the last of Ch13–Ch15). The
  change is additive; chapters mount it (M4-A2P-0451, filed).
  - **The barge:** `open_sea_barge`, bridal_barge.py's builders at the greybox deck's size (`build_fitted`). The
    arena's `bridal_barge.glb` is byte-identical.
  - **Grade and water:** the Wakefin arena's unlamped grade, and the night sea with the sea-glow at the barge's
    waterline (−0.6).
  - **Viewed** at ten cameras.
  - **Checks:** the kit's full build gives 230 glbs, all byte-identical; tests ch15 and haluna_kit (25 OK), Godot
    post_import 21/0, validate_data, taskboard and gdlint.
  - **Open, filed in M4-A2P-0451:**
    - Hollowmere's first visit has no greybox zone; chapters are asked for one, and the kit (M3-ENV-723) is ready.
    - The shoal's held dead and the dawn fog are rendering's.
- **MERGE-READY @ 562c7f57: M4-A2P-044, Ch14 (the Lacquer Court) dressed.** The change is additive; chapters mount it
  (M4-A2P-0441).
  - **Built from the greybox:** the court, red-lacquer colonnades with a wedding lantern on every column, the dais,
    the Conclave's gallery, the water-steps, the water-gate.
  - **Placed round it:** six halls, the bridal barge, and the city at its windows (`bowl_dome_lit`, a new kit
    variant; the plain `bowl_dome` is unchanged).
  - **Gates:**
    - Viewed at 10 cameras.
    - Python suites OK: test_ch14 (4), ch13, haluna_kit.
    - Godot `ch14` 5/5; validate_data and taskboard clean.
    - The full build reproduces all 229 glbs.
  - **For chapters:** the lagoon's level (the greybox's water is over the barge's deck), and the dusk fill.
- **MERGE-READY @ 14ff2eb7: M4-A2P-043, Ch13 (Ansedra, the Sanctum, the Lamp Archive) dressed** (the Lead's (b)). The
  change is additive; chapters mount it (M4-A2P-0431, filed). The details are in ansedra.md's revision line.
  - **Ansedra:** vey_zones' walk builders reused on Ansedra's greybox, in marble and gilt (a small refactor: an
    `order` parameter, and the Vey's glbs are byte-identical). Order lamps, Sefir's and Corran's houses, the Archive
    and Sanctum domes on base storeys with their doors, lofted barges, fourteen island domes and the far skyline, the
    still mirror.
  - **Interiors:** the Sanctum (the basin over the bound light, the apse) and the Archive (lacquered ledger cases,
    the reading tables).
  - **New grade:** `lut_ch13_still`.
  - **Gates:**
    - Viewed at 30 cameras.
    - Python suites OK: test_ch13 (4), ch10–12, haluna_kit.
    - Godot `ch13` 4/4; gdlint, validate_data and taskboard clean.
    - The full haluna_kit build reproduces all 227 glbs.
- **VERIFIED on lead/gate-big20 (4e3c74c9), with self-rendered stills on lavapipe: the Lead's Act I rows.**
  - **Closed (env-art's part):**
    - **Row 25:** `brightwater_landing_f01`'s lower half reads (the islet's moon fill, 2e2233c3). f06 is fine.
    - **Row 47, Landing:** the pier and landing at night read in walk frames from the Landing spawn: textured
      stone, boulders, Rhen, the lit ferry.
    - **Chapel ΔE:** `palette_check --shots haluna_h07_chapel_court` gives 4 ok (ΔE 0.018).
    - **O17:** the storm slate is intended (M3-ENV-104).
    - **Row 43:** `field_hud_over_haluna_wake` captures (no hang).
    - **Row 23, bell-room haze:** gone. The room reads teal, and Rhen faces the camera.
    - **Row 59, the asset:** walk frames from O10's own position and lens show the carved hero gull on its post.
  - **Not env-art's, still open:**
    - Row 47 FerryAft, and row 24 DockShore: the field camera (hero-integration).
    - Row 23's listener: act1-chapters' shot.
  - **LEAD-ASK, route to cinematics/act1-chapters:** on big20 the `ch01_o10_gull` capture doesn't frame O10. It shows
    a shell-covered surface from above, with no gull, where big19's pass-4 still framed the gull from O10. The O10
    camera row and the dressing round the gull are unchanged since big19 (no piece stands between O10 and the gull).
    So the cutscene's camera in that shot is the suspect: M3-CIN-1232/1235/1236 (ea3247ed, e3ad5bbe) touched Ch1's
    shots and the dive since.
- **MERGE-READY @ cd7fbf94: M4-A2P-042, Ch12 (Keth Pass, Quellan, Cloudloom) dressed.** The change is additive: no
  played scene changes until chapters mount it (M4-A2P-0421, filed). The details are in keth_pass.md's revision line.
  - **Built from the greybox** (§6's modules don't fit it), in `keth_zones.py`:
    - each zone's ground: walks level, crag behind every cliff, scree off every drop, turf on the flats;
    - the flights' road stones and slope-following parapets, the cords between their posts, the knot post;
    - Quellan's houses on their footprints and its paved street and square;
    - Cloudloom's white hall in dressed courses, with a beam over each row of keth.
  - **Kit placed round them:** the Lit Age wall and seep pool, the inn, the well, twelve keth curtains (2,880 cords),
    Hesk's dais, cairns and the far ridges.
  - **A kit change:** `quellan_house` and `quellan_inn` walls are the road's granite and their roofs `kit_keth_turf`
    (the card grass read as snow). Two kit-row shots change, `kitrow_keth_cloudloom_house` and
    `kitrow_quellan_inn_well_dais`; both were re-rendered and viewed, and neither has a baseline.
  - **Gates:**
    - Viewed at 30 cameras.
    - Python suites OK: test_ch12 (5), ch11, ch10, haluna_kit, haluna_dressing (48 in all).
    - Godot `ch12` 4/4 and `post_import` 21/21.
    - validate_data, taskboard and gdlint clean.
    - The full haluna_kit build reproduces all 219 glbs (the manifest is updated).
- **Ch10's Kirru roost weave** (re-rendered close up at Lodge_close, Ring_lodges, F02 and Causeway_mid): it reads
  as woven hoops, not busy, and no tree stands on a walk. No change.
- **Act II share done to the dressing:** Ch10 (M4-A2P-040), Ch11 (041) and Ch12 (042) are built and merge-ready.
  Each waits on its mount request to chapters (0401, 0411, 0421); the tasks stay `doing` until a mount lands and
  env-art views the mounted zone.
- **MERGE-READY @ 79fc304f: M4-A2P-041, Ch11 (the Sunken Vey and Lowlight) dressed.** The change is additive: new pieces,
  dressing JSONs, grades and previews. No played scene changes until chapters mount it (M4-A2P-0411, filed). The
  details are in lowlight.md's revision line.
  - **Built from the greybox** (§5's 6 m walk and nave bay don't fit it):
    - `vey_zones.py`: walks at their own lengths, the balustrade on the rail blocks, the paved courts, parapets,
      conduit stand, gate facade, and the lagoon bed with its lit street conduits.
    - `lowlight_zones.py`: rooms on the greybox's walls, an arch at every doorway, pointed vaults with broken bays,
      the hall's rail and twelve lamps, the flights under sloped vaults, and the domed drowned sanctum.
  - **Kit placed round them:** arcades, columns, figs, the housing with the mark, the bench, the well-shaft, and the
    nave over the gate.
  - **The grade:** the arena's sky with an overcast deck (its warm deck read as a sunset over open water), and still
    water (no crest foam, the detail ripple damped).
  - **Gates:**
    - Viewed at 20 cameras (`_tests/ch11_zones/*_dressed.tscn`).
    - Python suites OK: test_ch11 (7), test_ch10, test_haluna_kit, test_haluna_dressing.
    - Godot `post_import` 21/21 and `ch11` 3/3.
    - validate_data, taskboard and gdlint clean.
    - The full haluna_kit build reproduces all 210 glbs byte for byte (the manifest is updated).
    - No screenshot is affected (new shots none; HYMN_SHOTS empty).
  - **For chapters (M4-A2P-0411):**
    - the mount;
    - the Engine's field look (creatures' `lamp_engine`);
    - the well's mouth, open in the sanctum floor: a collision ring, or the beat sheet's ledge;
    - wading (L02's "knee-deep" needs the floor lowered);
    - the underwater rig below −2.05.
- **LEAD-ANSWER (big19 review, `oruvel_o17_pen_split` grey sky): yes, intended; keep it.** O17 runs `phase: ch01_storm`, and
  M3-ENV-104 (e2358df5) gave both storm environments (`oruvel_storm_environment.tres` and the zone's
  `oruvel_ch01_storm_environment.tres`) a storm-slate sky with no sun disc. Before that, the storm frame wore a clear blue
  sky. Nothing leaks into Ch1's calm phases: `oruvel_ch01_environment.tres` is unchanged.
- **MERGE-READY @ b0eb0a49: the Lead's big19 `test_palette_check` red (haluna_h07_chapel_court).** The chapel's sun face read
  #B0B2B2 (ΔE 0.042 to order_marble 0, max 0.03): M3-ENV-102's lime-wash damp (wet 0.25 + bias 0.15) darkened it. The damp
  is dialled back (wet 0.08, bias 0.03, moss 0.06; the salt streaks kept): #B8BABA, ΔE 0.018. The marble is right, so the
  asset moved, not the target. Re-rendering H07 also showed the zenith check failing (median green): one of my audit
  palms west of the chapel (f44e218d) stood in its sky sample, so the five audit palms there are frangipani now.
  **`palette_check.py check --shots haluna_h07_chapel_court`: 4 ok, 0 failed.** Viewed. Also: `test_haluna_kit`,
  `test_haluna_dressing`, `test_shrine_gi_bake` OK; haluna_kit rebuilt (only `order_chapel.glb`). H07 drifts (re-approve).
- **2026-10-30, M4-A2P-040 (Ch10) in progress, pushed @ 3abc9d20; not merge-ready (the mount is chapters', M4-A2P-0401).**
  - Built: a four-variant **mangrove system** (`ossa_fen.build_tree` parametrised: `mangrove_tall`/`_low`/`_young`
    beside the kit tree); each zone's **ground** from its greybox (`fen_zones.py`: level land, channels, root-mat humps,
    litter and roots in the new `kit_fen_bank`); `tools/act2/ch10_fen_dressing.py` writes both zones' dressing (walks
    tiled, platforms and roosts, the clutch's stone and cords, ~150 trees and ~30 reed beds per zone off the walks, the
    far tree-line), grade (`lut_ch10_fen`) and tannin water, plus previews with ten composed cameras each.
  - **Viewed (20 cameras):** reads as the fen at dusk. Open: the flat land is dark because `Ch05Zone.apply_variant()`
    re-applies the layout's ambient 0.5 after the dressing (the ask to set 0.85 is in M4-A2P-0401); Pell's capsule.
  - **Checks:** `test_ch10_fen_dressing` (5, new), `test_haluna_kit`, `test_ossa_fen`, `test_reedhollow`,
    `test_blender_builds` OK; validate_data; taskboard; haluna_kit rebuilt (the new pieces and the manifest only).
  - **Next:** Reedhollow's lodge weave reads busy close up (a look pass); the egrets and fireflies (creatures'
    wildlife); then Ch11 (M4-A2P-041).
- **2026-10-30, ACT II STARTED (ADR 0205: no open Act I row in env-art's lane).** Scope (act2_tracks.md): Ch10–Ch12, in
  chapter order. **Doing: M4-A2P-040**, Ossa Fen and Reedhollow at final quality with a mangrove vegetation system: a
  zone-dressing generator per zone (`tools/act2/ch10_*_dressing.py`, ZoneKitDressing, as Act I's Ch4–9) from the built
  kit (M3-ENV-718/733), then the mount, grade, shots and walk checks.
- **MERGE-READY @ 6afe97f1: the Lead's pass-3 rows (`act1_gpu_qa.md` on `gpu/act1-qa-3`), each self-rendered and viewed.**
  - **Row 59 (`ch01_o10_gull`, a crude faceted bird on a plain box): env-art's, fixed.** It is the Oruvel kit's
    `lintel_gull_open` (`village.lintel_gull`, not creatures'). A `fine` carving for the O10 close-up: 16-sided lofts on
    17 rings (was 9 x 9) under finer adze facets, three feather grooves raised along each wing, oiled eyes, a moulded
    perch with carved feet; it stands on the new `gull_post` (5331498f), not the greybox block. Budget 3600 (2960 tris).
    Haluna's lintel gulls keep the plain carving (haluna_kit rebuilt byte-identical). Viewed: O10 reads as carved wood.
  - **Rows 25 / 47, f01 and the landing pier (pure black):** fixed by `islet_fill()` in 2e2233c3 (after pass 3's
    84422d11); the islet's new rock dressing (312270ef) gives it relief. Viewed: f01's lower half and the Landing spawn's
    views read. **FerryAft (the camera in the cabin, against Rhen):** the field camera at a spawn, not geometry:
    hero-integration's (field camera) with act1-chapters (the spawn). **LEAD-ASK:** route it.
  - **Row 24 (the wake walk: DockShore's camera inside Rhen; FeastEdge, InkLamp, WallDawn looking straight down):** field
    camera behaviour at spawns too (the wake's `camera_volumes` are act1-chapters'). No wall or piece is in the lens.
    **LEAD-ASK:** route to hero-integration / act1-chapters.
  - **Row 43 (`field_hud_over_haluna_wake`):** fixed in f06c190d (the real wake rig; ui-menus re-baselines).
  - **The bell-room haze:** fixed in 2e2233c3.
  - **Checks:** `test_oruvel_kit`, `test_haluna_kit`, `test_zone_dressing_ch01` OK; validate_data; Blender haluna_kit
    (identical) and oruvel_kit (only `lintel_gull_open` and the manifest changed). Drift: `ch01_o10_gull`, the Oruvel
    shots that see a ridge gull.
- **MERGE-READY @ 2e2233c3 (+ f06c190d): the Lead's three real-GPU pass-3 items on big18; integration ccf44ba4+ merged in.**
  1. **`brightwater_landing_f01`, the lower half black:** the islet landing in the foreground had no light (no lamp, the
     moon behind the sea). `islet_fill()` in `tools/act1/ch04_ferry_dressing.py`: the cold sky fill (#9DB4D6, shadowless,
     as the derelict's) low over its top and its ferry-side edge. Viewed: the rock, the cobbles and the boulders read.
  2. **`ch01_bell_room`, the orange haze:** the UnderwaterRig's lantern halo (a screen-space in-scatter, 4 m) wraps the
     camera in a walled room. Tested by cutting it (0.1 -> 0.02): the wash went. Fixed per room, not in the shared
     `underwater.json` (the dives keep their halo): a `lighting` row may carry a third value, the halo's scale, which
     `UnderwayZone.apply_lighting` applies; `interior` and `deep` rooms take 0.2. Viewed: walls, door, Rhen and the
     lantern read. **For slice-polish:** this edits your `underway_zone.gd` and the layout's `lighting` rows (the Lead's
     direction); act1-chapters' camera re-aim is separate.
  3. **`field_hud_over_haluna_wake`, the capture hang:** its backdrop was my retired `haluna_wake_dressing` preview. It
     now stands on act1-chapters' `ch04_haluna_wake_shots` rig (the real `haluna_wake.tscn`), camera `Backdrop/Cameras/Lane`
     (the tidewall lane, as the old H02). Viewed: all four overlays over the lit lane. **For ui-menus:** one line in your
     `field_hud_over_haluna_wake.tscn` and the shot's camera in shots.json; it needs a new baseline.
  - **Merge:** integration's PROVENANCE union restored the two retired tree rows; dropped again (validate_data 0/0).
  - **Checks:** Godot `--filter=underway` 9/0, `ch01` 20/0, `ch04` 13/0; `test_zone_dressing_ch01`, `test_underway_walk`,
    `test_ch04_validate` OK; gdlint/gdformat; validate_data.
- **BACKLOG EMPTY (2026-10-30, after the Prologue–Ch4 audit):** the audit's findings in env-art's lane are fixed and
  viewed (MERGE-READY @ 312270ef, below); the rest are filed to their owners (M3-ENV-754, M3-ENV-755, slice-polish) or
  need the real GPU (PC-QUEUE: the night lagoon's glow, the plaza's joint ticks). The env-art todo list's other rows are
  Ch5–Ch9 (env-art-b's) or wait on other tracks. Lead: send more and I'll take it.
- **MERGE-READY @ 312270ef (+ this log): the Lead's final-quality audit of Prologue–Ch4 as played, on
  `lead/gate-big18` @ d00d3284.** 330 player-eye stills in nine zones, all viewed: four-way vistas at every spawn, every
  NPC from the front, every interactable, door and zone transition from its approach (points from each zone's layout
  and a headless dump of its scene).
  - **Fixed in env-art's lane, each viewed after:**
    - **Oruvel:** the dive raft's carved gull stood on air (DiveGull is a marker in the air); new kit piece `gull_post`
      (a lashed pole and lintel) carries it. 5331498f.
    - **Haluna:** the chapel court's west view and the causeway head's dunes read as bare sand (the scatters stopped at
      x -150 / -40); the village scatters run to x -260 and the dunes to -90 at the same density, with frangipani and
      palms in the chapel's west sightline. f44e218d.
    - **The causeway:** one even saltgrass size read as a tiled field; clumps now grow with their patch. e7d5852a.
    - **Ch4's islet landing:** one smooth dark slab at night; reef boulders and rubble round its rim, low ledges off the
      walk, tide pools and wrack (`islet_landing`, the walk band kept level). 312270ef.
  - **Filed (not env-art's files):** **M3-ENV-754** (slice-polish): the Underway zone's sun casts hard window panes on
    the floor (GreyboxZone's sun has no angular size; the arenas' M3-ENV-1323 values). **M3-ENV-755** (slice-polish):
    the First Verse's sky is one flat tan (its depth fog's `fog_sky_affect` 1.0 covers the dusk gradient).
  - **Seen and fine:** the Prologue's city, the Underway's rooms, Oruvel's town and NPCs, Haluna's lanes, shops and
    NPCs, the Shell Shrine, the ferry and the derelict (night), the wake night. Frames inside a wall, a party member or a
    prop are the audit rig's (a point on a spawn or against a block), not the dressing.
  - **Not fixed:** the Prologue plaza's joints show rows of bright sub-pixel ticks at a distance. Three tries (the slab
    sides' occlusion, no salt, 2.4 cm joints) changed nothing on lavapipe, so all three are reverted (the plaza glb is
    back to its pre-audit bytes). It looks like specular aliasing of the paving's flecks with no TAA. PC-QUEUE.
  - **Checks:** `test_oruvel_kit`, `test_zone_dressing_ch01`, `test_iskarra`, `test_haluna_kit`, `test_haluna_dressing`,
    `test_brightwater_ferry_kit`, `test_ch04_validate`, `test_causeway_gameplay` OK; Godot `--filter=haluna` 65/0,
    `--filter=causeway` 16/0; validate_data, taskboard. Blender: oruvel, haluna, brightwater_ferry kits rebuilt (only the
    named pieces and the manifests changed).
  - **Drift to expect at the gate:** `zone_oruvel_*` (the gull post), Haluna shots looking west from the chapel or the
    causeway head, the causeway's C-shots and `causeway_*` battle backdrops (the grass sizes), `ch04_*` and
    `brightwater_landing_*` that see the islet.
- **MERGE-READY @ e557740d: the Lead's two big17 reds (both already red on big16 @ ff82858c), fixed; integration
  ccf44ba4 merged in first.**
  - **`test_iskarra_city::test_the_city_instances_its_pieces_with_kit_materials`** ("VigilLights has meshes"): my lit vigil
    (10c6974d9) added `VigilLights` to `iskarra_city.tscn`, a group of OmniLights only. The scene is right; the test now
    checks that group as lights (omni, shadowless, no fog energy) and every other child for kit meshes as before.
  - **`test_ch04_zones::test_the_wakes_field_camera_is_halunas`** (8 expected, 10 got): the two new Haluna volumes are
    intended. slice-polish added `NemeTable` (B02, e7301ddd) and `DockEnd` (B11, b75cde39) under M2-FP-109, and the wake
    copies all of Haluna's volumes by design. The test now counts ch02/haluna's volumes from its scene instead of a
    hard 8. **For act1-chapters (the test's owner) and hero-integration (field cameras):** no camera or volume changed;
    if either of you wants the wake *without* B02/B11's close volumes, filter them in `Ch04Zone._haluna_camera_volumes`.
  - **Counts:** `--filter=ch04_zones` 5 run / 0 failed (was 1 failed); `--filter=iskarra_city` 1 / 0 (was 1 failed);
    `--filter=ch04` 13 / 0; `--filter=iskarra` 1 / 0. gdlint and gdformat clean. Skipped: shots (tests only).
- **BACKLOG EMPTY (2026-10-29): every env-art item for the Prologue–Ch4 is done, in review or routed.** Why nothing is
  left for this track: the inventory's env-art rows are cleared or re-routed (M3-HER-1140, review); the GPU QA rows are
  fixed on this tree (the real-GPU re-checks are in PC-QUEUE); the walk-through and the touchable props are done; the
  environment todo list's other rows are Ch5–Ch9 or arenas (env-art-b's) or wait on other tracks. Handoff:
  `docs/kb/handoffs/2026-10-29-environment-env-art-1.md`. Lead: send more Act I work and I'll take it.
- **To review (checked on this tree, no code change): M2-ENV-12** (m2-slice's off-tree shrine build is in), **M3-C01-04**
  and **M3-C04-03** (the kits are mounted; `--filter=ch01_thread` 2/0, `--filter=ch04_thread` 3/0).
- **MERGE-READY @ e1db6170: M3-CRE-663** (the big14 Blender gate's haluna_kit diff), to review: `kirru_roost`'s arch crown
  (`cos(pi/2)`, ~6e-17) snapped to 0 before export. `verify_blender_builds --job haluna_kit` 199 identical natively, under
  `X86_V4` and under `X86_V3 X86_V4`. Only `kirru_roost.glb` changed. Also **M2-HER-1127** to review (the First Verse points at
  `wayside_offering` on both branches; `--filter=qa_threads` 1/0) and **M3-ENV-105** to review (done 10-28, df2c8384a).
- **MERGE-READY @ 4629dfa6: M3-ENV-1228, the Ch4 derelict at night**, to review. Cold moon fill outboard of her ferry side and
  astern of her transom (the earlier fill lit only her deck). D01 reads; the transom and name-board read from astern.
  **Camera split:** D06 and F05 are act1-chapters' cameras (D06 frames the rail over the board; re-aim it). **Checks:**
  `test_ch04_validate`, `test_brightwater_ferry_kit` (39 OK), validate_data. **SELF-RENDERED:** the Ch4 ferry stills twice,
  player-eye frames of the transom; `ch04_ferry_derelict` 0.014 and `ch04_ferry_deck` 0.012 from today's earlier renders.
- **M3-HER-1156 routed to slice-polish** (the causeway's camera volumes are in its ch03 layout; env-art's read in the task).
- **MERGE-READY @ 2ff511ab (+ this log): M3-ENV-103, Asha's packed bag**, to review (slice-polish swaps it in; the note is in
  the task file). `travel_bundle` in the Haluna kit: indigo cloth packed full, a rolled mat strapped on, rope bands and a
  strap; the BoxMesh's size, origin at its centre. **Checks:** Blender `haluna_kit` (others identical), `test_haluna_kit`,
  `test_haluna_dressing` (31 OK). **Viewed** in a scratch scene beside `woven_bag`. No shot moves until the swap.
- **MERGE-READY @ 2ff511ab: M3-ENV-104 (Oruvel), to review (cinematics).** Ridge gulls on the cabin and the chandlery; the
  cabin's ridge under the roof child's feet (it was scaled to the greybox and she floated 1 m over it); Kell's beacon is
  the chandlery's own roof lantern (the storm light moved into it; no extra lamp); the low hull's salvage load; the storm
  frame's sky in storm_slate (it had the shader's noon blue). Details in the task file.
  - **Checks:** `test_zone_dressing_ch01`, `test_oruvel_kit` (28 OK). **Skipped:** Godot tests (layout data only).
  - **SELF-RENDERED and viewed:** walk frames at the beacon, the cabin and the low hull; `ch01_oruvel_storm`,
    `zone_oruvel_storm_o12/o16`, `oruvel_o17_pen_split` (drifts: the slate overcast replaces the day-blue; re-approve),
    `zone_oruvel_o09`, `zone_oruvel_o12`.
  - **Note:** 2ff511ab also carries M3-ENV-103's `travel_bundle` (builder, glb, import, manifest, PROVENANCE): built and
    in the kit, not merge-ready until viewed (next entry).
- **The Lead's 18:43 ask: my open real-GPU rows (`act1_gpu_qa.md` on `gpu/act1-qa-2`, last checked on big15), re-checked
  on this tree. All were fixed at 4c85ffb7b (10-28), after the big15 re-check; each SELF-RENDERED here and viewed.**
  - **Row 4 `ch04_ferry_deck`:** the deck, deckhouse face, rails and sails read under the cold sky fill. The "orange
    sphere" is a party member's back beside the lit stern lantern. `ch04_ferry_derelict` reads too. Drift 0.081 and
    0.042 from older baselines: re-approve at the gate.
  - **Row 19 `iskarra_p01_plaza_dusk` / `slice_prologue_vigil_line`:** no green rectangle; beside the terrace the water
    shades soft teal with no edge (`iskarra_water_material.tres`). Drift 0.16 and 0.13 (the lit vigil, the colour pass):
    re-approve at the gate.
  - **Row 23 `ch01_bell_room`, `ch01_kell_stall`, `ch01_scale_hull`:** the camera is in the bell-room behind Rhen (door
    and lantern in frame); Kell and the Scale-Man stand at their counters, in frame, facing the customer. First renders
    (no baselines).
  - **Row 24 `zone_wake_h02/h08/c01`:** these shots no longer exist (retired 10-28 with the Lead's word; Ch4's wake is on
    the real Haluna). The real Haluna's H02 and the wake walk read (above).
  - **Row 25 `brightwater_landing_f06` / `f01`:** F06 frames the deck, the wrapped name-board and the party, not the
    bulwark; F01 is the pre-dawn grade and the ferry reads. First renders (no baselines).
  - **The split (rows 23–25):** env-art fixed the geometry in front of the lens (the booths turned to face their
    customers, the Underway walls on their greybox, the ferry's bulwark clear of F06). The cutscene cameras are
    act1-chapters' (the chapters' scene files). I moved none of them, and these frames need no camera change.
- **MERGE-READY @ c3038a18: the player-height walk-through on this tree, done (all nine walks viewed)**
  (`tools/act1/walkthrough.py`, all nine walks).
  - **Viewed, fine:** Haluna (14 frames), Haluna's shop, forge and save shrine from the customer's side, the Prologue
    (9), the Underway (10). Frames looking out of a wall or the water are my straight-line path, not the dressing.
  - **Fixed, 7a930176 + ee270be4:**
    - **Oruvel's commons:** boat-hull outlines lay across the deck planks. The commons tiles `raft_deck`s every 7 m, but
      each raft's hulls ran 2.1–2.6 m past its own deck and rose 0.42 m over it at the stems, up through the next
      raft's planks. New `raft_deck_tucked` / `raft_deck_small_tucked` (`raft(tucked=True)`: hulls inside the deck,
      stems ≥ 6 cm under the deck line) for the commons only; the freestanding rafts keep their bows. Every other
      Oruvel glb is byte-identical.
    - **Haluna's inn:** the innkeeper stood under a bare awning. New Haluna kit piece `inn_hearth` (a stone cook
      hearth with a lidded pot, split wood, a serving bench with bowls, a ladle and a jar), 2.4 m behind the
      innkeeper as the forge stands behind the smith. Every other Haluna glb is byte-identical.
  - **Also viewed, fine:** the causeway (11), the Shell Shrine (7), the ferry (8), the Ch4 wake night (12).
  - **Checks run:** `test_oruvel_kit`, `test_zone_dressing_ch01`, `test_haluna_kit`, `test_haluna_dressing` (59 OK),
    validate_data, gdlint; Blender `haluna_kit` and `oruvel_kit` full rebuilds (only the new pieces and the manifests
    changed). **Skipped:** Godot tests (no code changed; the layouts' pieces load through the existing dressers).
  - **SELF-RENDERED and viewed:** the Oruvel walk again (the decks are clean planking; seams show water between lashed
    rafts), four inn close-ups (hearth, pot, wood, bench, jar read behind the innkeeper), and 10 shots:
    - `oruvel_o01_surfacing` rmse 0.0046 (pass);
    - `ch01_oruvel_dressed` 0.22: its baseline predates big16's Oruvel re-layout; the commons now reads clean.
      **Re-approve at the gate.**
    - first renders, no baseline yet (viewed, read right): `zone_oruvel_o01/o07/o09/o12/o16`, `ch01_kell_stall`,
      `ch01_scale_hull`, `ch01_net_pen`.
    - Haluna shots that frame the inn (lane 2, the town) drift by the hearth; the gate's full run shows which.
- **MERGE-READY @ 3bd6865f: M3-ENV-750 done; the inventory's four Haluna tree rows are gone.** The checks that were
  still owed have now run:
  - `haluna_kit` Blender verify: 197 identical, the hand-trimmed manifest included;
  - Godot `--filter=haluna` 65/0;
  - `--filter=post_import` 21/1. The one failure is `test_every_glb_import_runs_its_category_script` on
    `assets/crowd/*` (creatures', fixed on their branch per CONSOLIDATED); the tree check passes;
  - gdlint and gdformat clean; `placeholder_audit.py` (runtime scan) puts env-art at 3 (was 9), none medium;
  - **skipped:** shots (same geometry under new names; nothing moves).
- **LEAD-ANSWERED (10-29 ~18:00): integration-qa re-routes the three rows; env-art is done with them.** (Was: the
  audit still files three rows under env-art (M3-HER-1140) that env-art can't close:)
  - the Prologue `City/Vigils` capsule: Pell's vigil, which characters' Pell (big17) or slice-polish's staging replaces;
  - `tamsule_bell/reefball_drop_proxy.glb` and `materials/tb_drop_proxy.tres`: M3-RND-26, which the Lead gave env-art-b.

  Please re-route them in the audit's owner map, or tell me to take M3-RND-26's rename myself. Meanwhile I'm starting the
  walk-through.
- **2026-10-29 (new Lead `session_01Bg3iP7cPGyjbX4CyniBahc`; integration `claude/new-session-mj8c3c`): M3-ENV-750's
  kit half, the inventory's Haluna tree rows (2 medium, 2 low).**
  - Merged the integration branch (58011116; one conflict, `pc-gpu.md`, took the integration copy).
  - slice-polish's rename (`claude/m2-slice` 6fa37677, not on integration yet) is carried here as identical lines
    (`haluna_layout.json`'s 50 trees, `haluna.tscn`'s two `piece_rules` keys, `test_haluna_zone`, `test_post_import`),
    so env-art and m2-slice merge cleanly in either order.
  - Retired `banyan_placeholder` / `windbreak_placeholder`: `trees.py`, the glbs and imports, the manifest entries,
    PROVENANCE rows, `haluna_kit_sheet.gd`, `test_haluna_kit`, and `scene_loads.json`'s four paths (now the real names).
  - Run: `test_haluna_kit` 21 OK, validate_data, taskboard (the rest: MERGE-READY line above).
  - The rest of the env-art inventory isn't mine: the Prologue `City/Vigils` capsules are cast stand-ins
    (characters/slice-polish), and `reefball_drop_proxy` / `tb_drop_proxy` are env-art-b's (M3-RND-26).

### PC-QUEUE
- Ch1 Underway pass (922cd122): Underway caustics on a real GPU (strength 1.2, and whether caustics inside the sun's shadows read wrong), and the dive well's floats from the deck.
- Prologue dressing pass (b39caa29): look at P01 and P02 on a real GPU for the Iskarra towers' grime streaks and tide band, the plaza puddles' gloss and the amber lamp globes.
- **M3-ENV-1323 (2026-10-30):** A/B `battle_arena_underway_tower` with its Sun node hidden. Rectangles that
  stay are the F9 slabs against the sand (a material edge); rectangles that go are window light.
- **Ch12 shade at spawn height (2026-10-30):** Keth Pass (PassFoot, RamArena, FromQuellan), Quellan (FromPass,
  FromCloudloom: a black void behind the party) and Cloudloom Approach are near-black at arrival under lavapipe.
  Check on the GPU; if they're as dark there, env-art lifts the ch12 grade's fill.
- **Ch14's court at dusk (the layout's 4° sun, 0.5 navy ambient): the court's centre reads near-black on lavapipe.** The
  lanterns light the colonnade only. Judge it on the real GPU. The remedy is chapters' ambient (M4-A2P-0441).
- **Ch12's shade at a walker's eye (Keth Pass, Quellan): the dark slate and crag go near-black on lavapipe in every
  shadow.** The cause is the colour script's 0.8 colour fill at exposure 0.65, with no bounce light on the software
  renderer. A sky-source ambient barely moved it. On the real GPU (SDFGI/SSIL), judge whether the shade reads. If it
  doesn't, the fix is chapters' layouts' `environment.ambient_energy` (0.8 → ~1.2, as Ch10's 0.85 ask) or a lighter
  `kit_keth_crag` tint.
- **The night lagoon (Haluna, the Ch4 wake): reads too bright on lavapipe.** The shallows glow luminous cyan from the
  dock end, with the moonlit white sand lifting it. Proposal: `HalunaMood.night_sea_glow` 0.12 -> **0.07** (colour
  script rule 3 allows it; `haluna_mood.gd`), judged on the real GPU before changing it.
- **The Prologue plaza's joint ticks:** rows of bright sub-pixel ticks in the paving's joints at a distance (lavapipe,
  no TAA). Check with TAA at High; if they stay, the paving material needs a flecks fade by distance.
- M2-ENV-12 / M2-RND-17: the Shell Shrine's cold first frame (188 ms measured on m2-slice) on hardware.
- The Ch4 derelict at night (M3-ENV-1228): how her moon-fill reads at High (D01, the transom, the name-board).
- `ch01_bell_room`: the room reads washed out in its warm haze on lavapipe (walls, door and Rhen visible). Judge the
  haze and lantern brightness on the real GPU. Also row 4's deck brightness at High.
- The Ch4 wake night's lagoon reads bright turquoise close to the dock (lavapipe). It is the water shader's night
  sea-glow, the same look as the approved `haluna_h10_dock_night`, only nearer. Judge its brightness on the real GPU.
- GPU QA rows 4, 19, 23, 24 and 25 (`act1_gpu_qa.md` on `gpu/act1-qa-2`): fixed @ 4c85ffb7b, after the QA file was
  written. They need the PC to look again on the real GPU.
- **The Lead's 17:37 follow-up (big15's `test_the_town_is_dressed_over_the_greybox`, "LowHull (a story block) is not
  hidden by the kit"): fixed in big16; nothing to change.**
  - **Cause:** on big15 the zone mounted the old `tools/ch01/ch01_oruvel_dressing.py` output. My walk-through batch 1
    (62409951b) had that generator dress `LowHull` with `hull_lashed` and stop keeping its greybox mesh, while big15's
    test still listed `LowHull` in `KEPT`.
  - **big16 (ff82858c):**
    - The zone mounts `ov_zone_dressing`'s layout: all greybox hidden, `hull_outrigger` following `LowHull`.
    - The test expects exactly that (`KEPT = []`; "the low hull follows its block").
    - Run here: 3 run, 0 failed.
  - **The booth and chandlery orientation:** viewed on big16 in `ch01_scale_hull` and `ch01_kell_stall` (entry above).
    Both counters face their customers.
  - **No code change. LEAD-ASK:** none. If the cloud suite still fails it on big16, send me its log line.
- **MERGE-READY @ 2666255bb: the Lead's big16 checks (lead/gate-big16 @ ff82858c, this branch fast-forwarded to it).
  No code change was needed.**
  - **U03 on my mounted Underway dressing:** `ch01_bell_room` was rendered and viewed. The camera is in the bell-room
    behind Rhen's shoulder, with the door and the lantern in frame; it is not in a wall. Row 23's bell-room is fine.
  - **The booths:** in big16, `ov_zone_dressing` places `scale_hull` at yaw 0 and `chandlery` at -90, and slice-polish
    staged the actors to them. Rendered and viewed:
    - `ch01_scale_hull`: the scale-man behind his counter, the brass scales between him and Rhen.
    - `ch01_kell_stall`: Kell before her lamp racks under the striped awning.
    - Both counters face their customers. My retired generator's flip (845287999) is moot.
  - **`ch01_o10_gull`:** the carved gull side-on against the sky. A rigging pole crosses the frame on the left; it
    reads, but the camera is slice-polish's to trim if wanted.
  - **`test_ch01_oruvel_kit`:** 3 run, 0 failed on big16. big15 failed because big15 still mounted the old dressing.
  - **`test_footsteps_slice_zones`:** 5 run, 0 failed on big16, so the Haluna sand, dock and shallows groups read
    right. Nothing to fix or file.
- **MERGE-READY @ df2c8384a: M3-ENV-105 (high), the Underway's walls on the walk walls; M3-ENV-740 needs nothing.**
  - **Cause:** `ou_zone_dressing.py` hard-coded the rooms from an older greybox. The layout has since moved its walls
    (the crown to x ±9 and z -4/20, the gauge room's east wall to x 104, the tin alcove to z -4..2).
  - **Fix:** every wall is now read from its greybox block. Each bay's inner face sits on the block's inner face
    (`gb_wall`), and the piers stand at the inner corners. Every room was redone: the crown, the bell-room, the
    galleries, the tin alcove and the gauge room. The stairwell is now read from StairLip.
  - **The cut gauge wheel:** `gauge_wheel_cut` now stands on GaugeWheelCut, so the hub stays on its plinth after the
    cut.
  - **The check:**
    - The podium is carried over from the retired layout: seafloor cells with the broken lip all round, the open
      stairwell, 22 seagrass patches, the sand drift through the east breach, and the wreck ribs to the east.
    - The bell-room is dressed (pipe run, coral, fallen lamp-column, the lantern at the rest).
  - **Walkability test, `tools/tests/test_underway_walk.py`:**
    - Every floor-level bay's inner face lies on a greybox wall's inner face (2 cm), within its span.
    - Every wall block carries bays.
    - No spawn stands inside a bay's wall.
    - It passes on this layout and fails (75) on the old one.
  - **SELF-RENDERED with the dressing mounted as m2-slice mounts it** (a scratch layout_path, not committed):
    - A 10-frame walk through the crown, the bell-room, the galleries and the gauge room: the walls stand where the
      walk stops.
    - `ch01_underway_crown`: Rhen inside the room, the camera over the south wall's top (it was through it).
    - `ch01_underway_gallery` reads.
  - **Gates:** test_underway_walk, test_zone_dressing_ch01, test_oruvel_underway_kit (22 OK); validate_data.
  - **M3-ENV-740:** slice-polish already re-staged Oruvel's actors onto my `ov_zone_dressing` hulls (da5b34e6, their
    renders "read right"), so my hulls stay where they are.
  - **For the merge (Lead):** m2-slice deletes `tools/ch01/ch01_oruvel_dressing.py` and `ch01_underway_dressing.py`.
    My later edits to them on this branch (the lashed hull, the flipped booths, O10) belong to the retired generators.
    Take m2-slice's deletion. The mounted `ov_`/`ou_zone_dressing` generators are what count.
- **MERGE-READY @ c9dbf9631: M3-ENV-1316's Coilspire headland ground (the last of 1316 that is env-art's).**
  - **Diagnosis:** I re-rendered the arena with one piece hidden at a time. The "broad planes" behind the foes are
    `arena_headland_ground` itself: a slope already on the fine 1.25 m grid near the fight, with one crisp
    cast-shadow face and one sunlit face. That is lighting on real relief, not a faceted mesh.
  - **The real defect for env-art-b's scrub:** the kit's fine grid stopped 8.5 m north of the landing. Past 45 m the
    hill ran on 8–9 m cells, so the mesh strayed up to 0.7 m (p90) from the table's height function, and clumps
    floated.
  - **Fix:** `cs_arena.build_ground` carries the fine grid north to z -120 (1.75 m cells; 19.5k tris, budget 20k).
  - **Mesh against `_headland_ground_y`, p90 (median):**

    | Range | Before | After |
    |---|---|---|
    | 0–45 m | 0.32 m | 0.32 m |
    | 45–80 m | 0.69 m | 0.29 m (median 6 mm) |
    | beyond 80 m | 1.63 m | 1.26 m |

  - **env-art-b:** you can take `b_headland_arena.py`'s `RING_M` out to 80 m.
  - **Viewed:** `battle_arena_coilspire_headland_path` is unchanged in frame. `test_coilspire_kit` and `test_arenas`
    OK.
- **MERGE-READY @ 02d8d6716: M3-ENV-1316 part 2 (GPU QA row 5's `camp_tent`); findings on the rest.**
  - **Brine Shoals `camp_tent`:** the canvas sags deeper between the frames (0.14 → 0.26 m), and sewn seams stand off
    the cloth down every panel edge. Viewed `ch06_brine_camp`: it reads as a sewn sail-cloth tent, not a box.
  - **Row 5's "flat mudflat" and the hard brown band on the horizon:** that is the Ch6 zone's ground and its far edge,
    which are env-art-b's. On lavapipe the flat carries its ripple texture, tide pools and wrecks; the colour script
    flattens ch06 on purpose.
  - **1316's Coilspire "far facets": not fixed, cause not found.**
    - Ruled out:
      - the arena ground's own grid (refining it changed nothing in the frame);
      - its LOD (LOD0 shows to 1,034 m);
      - `corrow_far` (more rings changed nothing).
    - The broad dark planes behind the foes in `battle_arena_coilspire_headland_path` look like the spire's shell or
      tier faces at close range.
    - **env-art-b:** send me the exact frame and the direction where the facets show (the arena hint or the camera
      position) and I'll fix the right mesh.
- **MERGE-READY @ 17a746b57: M3-ENV-1316 (env-art-b's request), part 1: the trader boat's cargo and Ashcrown's
  flying stair.**
  - **Corrow `trader_boat`:** the bales were plain sail-white blocks. They are now rounded cloth-wrapped bales (ochre,
    red) and wicker crates, each bound by three rope bands and set down a little askew.
  - **Ashcrown `flying_stair`:** the cheek's outer face was one flat plane. A string course now runs down the 48°
    slope under the coping, and pilaster ribs stand proud every 3 m from the soffit (13.1k → 12.2k after the tilted
    courses; budget 14k).
  - **Viewed:** `ch08_corrow_arrival` (the bales read as roped cargo); `ch05_ashcrown_forecourt` (the stair's side
    has relief and no spikes).
  - **Row 26 (Ashcrown tiers "untextured grey" at High):** on lavapipe the tiers render textured (ashlar coursing,
    buttresses, veins). That points at the PC's texture or import state at High, not the meshes. **LEAD-ANSWERED (10-28):** the Lead agrees; the PC re-checks it on a fresh import after big15. (Was: have
    the PC re-check row 26 on a fresh import.)
  - **Next:** 1316's Coilspire far headland ground, and row 5 (the Brine Shoals mudflat and `camp_tent`).
- **MERGE-READY @ cbd7f5600: M3-ENV-1323 (env-art-b's request; GPU QA rows 15 and 40), the Underway arenas'
  hard-edged lit rectangles.**
  - Cause: the arena's sun cast its window openings onto the floor as hard panes, but underwater the light comes
    through 21 m of water.
  - Fix: `arena_scenes.py` takes an optional soft sun (`angular_deg`, `shadow_blur`), written only when set, so the
    other arenas are byte-identical. Underway tower: 9° and blur 4.
  - Viewed `battle_arena_underway` and `battle_arena_underway_tower`: soft pools, no panes.
  - `test_arenas` OK.
  - env-art-b: the task file is on your branch; please set it to review with this sha.
- **MERGE-READY @ 10c6974d9: the Prologue's vigil lit (the Lead overruled "nothing burns"); M2-ENV-09 and
  M2-ENV-06 finished.**
  - **Vigil lighting:**
    - The four lamp columns hold an oil flame in a warm, emissive lit-glass globe (new material
      `kit_lamp_glass_lit`).
    - Each of the seven offering shells has a lit clay saucer beside it.
    - `iskarra_city.py` writes `VigilLights`: an omni in each globe (1.4, 9 m) and a small one at each saucer, all
      shadowless with no fog energy.
    - Viewed `iskarra_p01_plaza_dusk` and `slice_prologue_vigil_line`: the globes glow warm across the plaza at dusk.
      The saucers are too small to read at these ranges.
  - **M2-ENV-09:** the islet's wet band follows the shrine sea's published water level (viewed in S01). The channel
    bends are not needed by the trial's layout.
  - **M2-ENV-06:** `haluna_h10_dock_night` viewed on this tree; re-approve its drift.
  - **Gates:** `test_iskarra` and `test_haluna_kit` pass (29 OK); taskboard --check.
  - **Drift:** iskarra_p01/i02/i03, slice_prologue_*, shrine_s01_approach (re-approve).
- **MERGE-READY @ 4c85ffb7b: the PC's GPU QA rows (`docs/kb/qa/act1_gpu_qa.md` on `origin/gpu/act1-qa-2`).**
  Each row self-rendered here and VIEWED.
  - **Rows 1–2 (Iskarra greybox; the vigil set untextured):** Pass A ran on integration 048b0a7f. That build lacked
    the colour pass (d2ae3cb2) and slice-polish's city mount (28b0f97a); both reached the tree in big14. The big14
    gate's own renders (`gate-runs/big14/out/iskarra_p01_plaza_dusk.png`, `slice_prologue_vigil_line.png`) show the
    textured, coloured city. **Fixed in big14**; re-check on the PC.
  - **Row 19 (the green rectangle in the Prologue's water): fixed @ 4c85ffb7b.**
    - Cause: Haluna's lagoon water was reused for the drowned city. Its turquoise shallow scatter lit the plaza's
      drowned steps and the towers' plinths as flat green panes.
    - Fix: the Prologue and the Iskarra kit preview now use their own `iskarra_water_material.tres` (written by
      `iskarra_city.py`; deep, dark, little scatter).
    - Viewed `iskarra_p01_plaza_dusk` and `slice_prologue_vigil_line`: no panes left; the water carries the sunset.
  - **Row 4 (`ch04_ferry_deck` nearly black): fixed @ 4c85ffb7b.** A cold sky fill along the ferry's waist and poop
    (`ferry_fill()` in `tools/act1/ch04_ferry_dressing.py`), stronger and lower over the poop. The deck, the deckhouse
    face and the rails read now. The "orange sphere" is the party member's back beside the lit stern lantern; nothing
    unlit is left.
  - **Row 23 (Ch1 cameras in walls): fixed @ 4c85ffb7b.**
    - `ch01_bell_room`: U03 sat on the bell-room's south wall line. It now stands in the room on Rhen.
    - `ch01_kell_stall` and `ch01_scale_hull`: the chandlery and the scale-hull booth were placed backwards, their
      counters facing the sea. They now face their customers. The scale-man stands at his counter (yaw 180), and O02
      looks in from the front.
    - O10 is re-aimed at the chandlery's moved gull.
    - Viewed: Kell behind her counter under the lanterns; the scale-man behind the brass scales; Rhen in the
      bell-room; the gull side-on and lit.
  - **Row 24 (`zone_wake_h02/h08/c01`): fixed by retiring them @ 4c85ffb7b.** M3-ENV-743/744 are dropped as
    superseded (the Lead's word). The preview, the generator and the eight `zone_wake_*` shots are gone.
  - **Row 25 (`brightwater_landing_f06` against a wall): fixed @ 4c85ffb7b.** F06 is ch04_under_way's camera on the
    wrapped name-board. It sat in the ferry's bulwark and now frames the board on the deck with Toma and Asha (viewed).
    F01 is dark because of the pre-dawn grade; it reads.
  - **Gates:** validate_data; taskboard --check; unittest for ch01_oruvel/underway_dressing, ch04_validate,
    zone_dressing_ch01 and test_iskarra.
  - **Drift, re-approve:** iskarra_p01/i02/i03, slice_prologue_*, ch04_ferry_deck, brightwater_landing_f06,
    ch01_bell_room, ch01_kell_stall, ch01_scale_hull, ch01_o10_gull, ch01_oruvel_dressed.
- **BACKLOG EMPTY (2026-10-28 ~11:45).** Everything the Lead asked for is done and MERGE-READY above:
  - M3-ENV-753;
  - the Prologue, Ch3, Ch1, Ch2 and Ch4 walk-throughs;
  - save shrines, chests (Act I has none), doors and signs;
  - M3-ENV-101 and M3-ENV-102.

  **What is left on env-art's board, and why it is not mine to move now:**
  - **Inventory rows (M3-HER-1140):**
    - The Prologue vigil capsule (Pell's hero body) is characters'.
    - The Haluna NPC stand-in bodies are villager/characters'.
    - The `*_placeholder` tree names wait on M3-ENV-750 (slice-polish's `haluna.tscn` collision rules).
    - `reefball_drop_proxy` waits on M3-RND-26 (PC GPU's drop look).
  - **M3-ENV-724 and M3-ENV-705:** the PC renders to view and approve (the gate).
  - **M3-ENV-1000:** waits on M3-RND-03 reaching integration. It is Ch6, env-art-b's now.
  - **M2-ENV-12:** waits on M2-RND-17.
  - **M2-HER-1127:** slice-polish's request (First Verse offerings).
  - **The swap-in tasks M3-C01-04 and M3-C04-03:** wait on their greybox tasks. The dressings are mounted already.
  - **M3-C05/C08/C09:** env-art-b's chapters.
  - **Retirement, waiting on the Lead's word:** M3-ENV-743/744 and the `zone_wake_*` preview shots (superseded by
    the wake on the real Haluna).
- **MERGE-READY @ 2bbf6cd4d: M3-ENV-102, the Order chapel at the kit's level; M3-ENV-101 viewed. Both to review.**
  - **`order_chapel`**, same footprint and door position:
    - a bare coral-stone base course;
    - weathered lime-wash;
    - an arched lamp niche with the gold Level emblem over the door;
    - a bell-cote with a gilt bell on the front parapet;
    - the gilt dome 1.25x larger, on a taller drum.
  - **SELF-RENDERED** `haluna_h07_chapel_court`: it now reads as the Order's building from the court (an intended
    drift).
  - **`save_shrine_field`** viewed: the final shrine reads. It drifts from its baseline; re-approve.
  - **Gates:** `test_haluna_kit` and `test_haluna_dressing` pass; taskboard --check.
- **MERGE-READY @ 219b86861: M3-ENV-753, Haluna's NPC props swapped (the Lead assigned it to env-art).**
  - In `haluna.tscn`:
    - Reed's Broom, Neme's Bag and Osu's Bowl are `hand_broom`, `woven_bag` and `clay_bowl`.
    - Osu's Shell sphere is a new `wake_shell_loose`: a 0.14 m wake-shell lying in the bowl, since she is washing the
      wake-shells.
  - The four primitives' sub-resources are gone.
  - **Gates:** Godot haluna 65/0. The task is at review, with slice-polish to review it.
  - **VIEWED** with the walk rig: Neme's bag reads beside her. The broom and the bowl sit with their NPCs' stand-in
    bodies, which the villager layer replaces, so they are not in frame there.
  - **Drift:** `slice_neme_table` and `npc_haluna_*` may drift slightly.
- **MERGE-READY @ b04753893: the Haluna NPCs' held props as kit pieces; the forge's bellows grounded.**
  - **New Haluna kit pieces:**
    - `hand_broom`: Reed's 1.4 m palm-rib broom.
    - `woven_bag`: Neme's bag.
    - `clay_bowl`: Osu's bowl.
  - Each matches its `haluna.tscn` primitive's size and centre, so it drops in. Built in Blender, with manifest and
    PROVENANCE rows.
  - The swap is slice-polish's (`haluna.tscn`): request **M3-ENV-753**.
  - **Fixed in `beach_forge`:** the bellows floated about 0.4 m up (found on viewing). They now sit on the sand, with
    the nozzle rising into the hearth.
  - **SELF-RENDERED:** a scratch preview of the five Haluna props (not committed): the broom, the bag, the bowl, the
    forge and the inn sign all read as themselves.
  - **Gates:** `test_haluna_kit` and `test_haluna_dressing` pass; validate_data; taskboard --check.
- **MERGE-READY @ 5ef018b14: Haluna's night-lamp flames are the kit's flame; the Prologue walked; the inventory
  re-run.**
  - **The placeholder audit** (`tools/placeholder_audit.py`, re-run on this tree; the inventory file restored) puts
    env-art's open rows at 11. Of those:
    - **Fixed here:** the wake's "38 SphereMesh under Dressing/Dresser". These were `HalunaDresser`'s night-lamp
      flames. They are now the kit's `lamp_flame` teardrop at the lamp's radius (a sphere only if the kit lacks the
      piece). This also applies to Haluna's own night.
    - **Already fixed** since the last trial merge: Oruvel's LowHull, the shrine's ChamberPassage and the derelict's
      flames.
    - **Not env-art's to finish:**
      - Prologue `City/Vigils`: one capsule, the vigil without a hero body (Pell). Characters/integration-qa, as their
        Ch9 Pell row.
      - Haluna `NPCs/*` (11): the NPC stand-in bodies, plus Reed's broom, Neme's bag and Osu's bowl. These are in
        slice-polish's `haluna.tscn`. The bodies are characters' and creatures' villager work.
      - `banyan_placeholder` / `windbreak_placeholder`: the real pieces `banyan_hero` / `windbreak_tree` exist. The
        rename waits on M3-ENV-750 (slice-polish), because `haluna.tscn`'s collision rules key on the old names.
      - `reefball_drop_proxy` / `tb_drop_proxy`: PC GPU's agreed drop volume (M3-RND-26, open). Never shown in play.
        Rename only with M3-RND-26.
  - **The Prologue walk-through:** 9 player-eye frames through Iskarra: the arrival line, the plaza, the vigil line.
    The final city reads in colour (cream, gold, blue bands), with no grey left. One frame looked from inside a
    tower wall, an artefact of my path. The causeway and the Shell Shrine were walked and viewed in batch 1, and
    both were fine.
  - **SELF-RENDERED:**
    - `haluna_h10_dock_night` drifts on purpose (the H10 reframe and the flames).
    - `ch04_haluna_wake_lane` and `ch04_haluna_wake_feast` are new (no baseline); viewed. The lamp pools are warm and
      no spheres show.
  - **Gates:** Godot `--filter=haluna` 65 run, 0 failed; gdlint/gdformat clean.
- **MERGE-READY @ 216c8ee5c: the touchable props in Haluna (the Lead's item 3), and the walk-through findings.**
  - **Haluna's shops were the gap:**
    - The `haluna_forge` smith stood by a boat on the beach with no forge.
    - The goods shop and the inn had only an awning cloth each.
  - **New kit pieces** (props.py; Blender built, manifest and PROVENANCE rows):
    - `beach_forge`: a coral-stone hearth with an ember bed, a clay chimney cowl, goatskin bellows, an anvil on a
      driftwood stump, a quench trough and a tool rack.
    - `shop_sign_goods`, `shop_sign_forge`, `shop_sign_inn`: post-and-arm hanging boards painted with the trade's
      mark (a jar, an anvil, a steaming bowl).
  - **Placed in `haluna_layout.json`:**
    - The forge stands behind the smith.
    - The existing `market_stall` stands behind the goods-shop keeper. Each keeper's talk sphere is 1.7 m, so nothing
      stands between the keeper and the customer.
    - The three signs stand beside their keepers, off the walking lines. They take the default box collider, because
      `haluna.tscn`'s collision rules are slice-polish's.
  - **SELF-RENDERED** (`ch02_haluna_touch`, from the customer's side):
    - The shop reads as a stall with wares under its blue awning, with the jar sign.
    - The forge reads as hearth, chimney, anvil and rack, with the anvil sign.
    - The inn's sign hangs by its awning.
    - The save shrine is unchanged.
  - **Gates:**
    - `test_haluna_kit` and `test_haluna_dressing` pass (31 OK).
    - The full tools suite ran (1,527 tests). Its only failures are the gate README's other owners: screenshots,
      `test_pemakar_kit`, `test_zone_map_pois` and `test_hero_clips`.
  - **Drift:** shots that see the market, the forge beach or the inn will drift on purpose, mainly `haluna_*`
    and `npc_haluna_*`.
- **MERGE-READY @ f6141df80: the big14 gate's `test_zone_dressing_ch01` and walk-through batches 1–2.**
  - **The gate failure is fixed.** I merged `origin/gpu/gate-big14-shots`; there were no conflicts.
    - `ov_zone_dressing.py`'s stale layout was regenerated at 9f4d11ab.
    - `ou_zone_dressing.py`'s stair is guarded.
    - `wake_zone_dressing.py` is retired from the test. Ch4's wake now stands on the real Haluna (M3-C04-1226), so
      the old greybox frame is gone.
    - **For the Lead:** retire M3-ENV-743/744 and the `zone_wake_*` preview shots (my rows; say the word and I'll drop
      them).
    - The tools tests for my area pass on the merged tree (139, OK).
  - **The walk-through pass (the Lead's item 2):**
    - `tools/act1/walkthrough.py` and `game/levels/_tests/walkthrough/walk_render.tscn` render a player-eye frame
      (1.6 m over the ground under it) every ≤30 m along each zone's critical path. Each zone loads once.
    - 71 frames over Ch1–Ch4, all viewed. The Prologue has no player (it is a cinematic), so it is not walked.
    - **Fixed:**
      - Oruvel: the run's `LowHull` was a tan greybox box on the bridge. It is now the new kit piece `hull_lashed`: a
        teal skiff thrown across the planks and lashed to both cut points, which goes with its block. Oruvel now keeps
        only the StormWall.
      - Underway: the first bell-room's walls were bare. It now has pipe runs, coral, a fallen lamp-column, fragments
        and the divers' lantern at the air-bell rest. The gallery breach's cut wall ends got pier jambs.
      - Ferry: the derelict's deck read near-black at player height, and its three fights happen there. It now has
        three cold sky-fill omnis (#9DB4D6, 1.4). It now reads, and still as a dead ship.
    - **Seen and fine:** Haluna, the causeway, the Shell Shrine and the wake night. Frames facing walls are my
      straight-line path, not the dressing.
  - **Touchable props (the Lead's item 3), so far:**
    - The ferry's save point is the deckhouse's Order niche (already a final model; the hidden greybox block was
      only the stand-in).
    - The Underway's hinge door, gauge wheel and cord, the ferry's gate, gangplank and name-boards, and Haluna's save
      shrine are final kit pieces.
    - Act I has no chests.
    - Haluna's shop, smith and inn close-ups render next.
  - **SELF-RENDERED:** walk frames for all seven zones viewed. After the fixes, re-rendered and viewed Oruvel (the
    skiff), the Underway (the bell-room) and the ferry (the derelict).
- **MERGE-READY @ aff485af5 (M3-ENV-1306, the Lead's item): `test_arenas`' Lanternfall reproducibility test is green again.**
  - It includes a merge of the Lead's `lead/gate-big14` (8707ff90). The merge had no conflicts. Merge this after big14,
    or with it.
  - **The fix:**
    - `arena_scenes.py` now writes `ash_terrace_lanternfall` with env-art-b's votive lamps (`_with_votive_lamps()`:
      the same rows, order and seed as `b_lanternfall.py`).
    - Both writers now give the committed file byte for byte.
    - The votive pieces are marked `structure`: they stand at the grave wall's foot, where the old sphere flames
      stood.
  - **Gates:** `test_arenas` 21 OK; regenerating every arena changes nothing; validate_data; taskboard --check.
  - Nothing was rendered: the committed scene is unchanged.
- **MERGE-READY @ 9f4d11ab: the Lead's two Ch1 shots.** It also merges big13 (99a077ef).
  - **The big13 merge (99a077ef):**
    - `arenas.json`: kept ours, the final `wall_head_storm` arena, because integration had reverted it to greybox.
    - The shrine GI was rebaked for the merged inputs.
    - `shots.json`: theirs plus our 42.
    - `PROVENANCE.md` and `ownership.md`: line unions.
    - Baselines: theirs.
  - **`ch01_underway_gallery`:**
    - Cause: the follow camera sat outside the gallery's south wall, and the two 3.2 m bays filled the frame.
    - Fix (`tools/ch01/ch01_underway_dressing.py`): that wall now lies fallen outward onto the terrace. It is two
      tilted `tower_bay_broken` pieces plus rubble.
    - The greybox wall still blocks movement but is not drawn.
  - **`ch01_o10_gull`:** three causes, all fixed.
    - **The glow veiled the frame.** O10 is a fov-14 telephoto into a cloud bank, and the Oruvel grade's glow
      (threshold 1.2, bloom 0.03) washed the bloom from the cloud over everything.
      - The grade now has threshold 3.0 and bloom 0, so sky and cloud no longer bloom; glints and lamps still do.
      - This is in the kit preview's environment, and both zone copies were re-copied.
    - **The camera saw the unlit underside.** The real carving, `lintel_gull_open`, sits on the chandlery's roof.
      From the low camera we saw its underside, which the noon sun doesn't reach, so it read as a flat grey shape.
      - It is now side-on to O10, with the beak south and clear of the dive raft's post.
      - A warm water-bounce omni sits below it and in front (energy 6, range 6).
    - These are in `tools/ch01/ch01_oruvel_dressing.py`.
  - **Also fixed:** `ou_zone_dressing.py`, my old Underway preview dressing, crashed on the merged greybox's stair
    (it divided by zero). It is now guarded and regenerated.
  - **SELF-RENDERED @ 9f4d11ab:** ch01_underway_gallery, ch01_o10_gull, ch01_oruvel_dressed, ch01_o07_name_board,
    oruvel_o01_surfacing, oruvel_o19_dive_mooring, zone_oruvel_o09.
    - **Intended drift:** gallery (rmse 0.094) and o10 (0.068).
      - Gallery: Rhen is framed in the colonnade with the lamp-columns ahead, and the wall lies on the sand.
      - O10: a carved-wood gull in profile with its throat open, against a clean cloud.
      - **Re-approve both.**
    - **Pass:** oruvel_dressed, o07, o01 and o19; the glow change doesn't move them.
    - zone_oruvel_o09 has no baseline; it is my preview, and I viewed it.
  - **Gates:** validate_data 0/0; taskboard --check; unittest for ch01_oruvel/underway_dressing, oruvel_kit,
    zone_dressing_ch01 and post_import (36, OK). No GDScript was touched.
- **2026-10-28 ~10:30: FAST-TRACK M3-ENV-752, the opening cinematic read GREYSCALE (the human's playtest).**
  - **Cause 1, for the Lead to merge:** the integration build's `prologue.tscn` (7855d016) still builds the city from
    primitives. slice-polish's mount of the final city and its WaterSurface is on `claude/m2-slice` (ead04bab, 2ab7a66e,
    c2c9b802, 28b0f97a) and is not on integration yet. **Merge it in big14.**
  - **Cause 2, fixed (d2ae3cb2):**
    - The final city, rendered through m2-slice's mount in a worktree, read near-monochrome: the cool lit_ceramic
      and the paving went grey under the teal dusk fill, and the glaze went slate.
    - It now has warm whites (towards sand_dry), gilt domes and finials (gold_leaf), and a bluer reef glaze. It still
      reads "white and gold at dusk" (iskarra.md); the sheet is updated.
  - **SELF-RENDERED @ d2ae3cb2:**
    - with m2-slice's prologue: slice_prologue_p01 and slice_prologue_vigil_line — cream towers, gold domes, blue
      bands, no grey left;
    - iskarra_p01/i02/i03 viewed.
    - All five drift on purpose. Re-approve them after merging m2-slice.
- **2026-10-28 ~09:00: the Lead's queue (inventory M3-HER-1140, the shrine, weak views, storm/night); MERGE-READY.**
  - **Inventory, the 15 rows (task M3-ENV-746):**
    - **Fixed by env-art:**
      - the derelict arena's sphere flames are now the kit's `lamp_flame` (also the Ch5 ash terrace);
      - the shrine's ChamberPassage box is now `shrine_chamber_passage`, and the shrine GI was rebaked here;
      - the Ch4 ferry's four kept blocks are now `islet_landing`, `gangplank`, `stern_gate` and
        `terrace_name_board_wrapped`, placed in `tools/act1/ch04_ferry_dressing.py` under the Lead's 02:40 split,
        so the keep list is empty;
      - the Ch1 storm's `StormWall` is no longer kept (below).
    - **Built, waiting on the owner:**
      - the First Verse's set, `assets/environments/zones/shell_shrine/first_verse_stage.tscn` (the final shrine,
        sea, shore, and the marks at their real places; M3-ENV-745);
      - the trees under real names, `banyan_hero` / `windbreak_tree` (M3-ENV-750, then the old names go).
    - **Requests:**
      - M3-ENV-747: the save shrine's primitives (Systems; the kit pieces have been ready since M3-ENV-101);
      - M3-ENV-748: Neme's stand-in (slice-polish);
      - the earlier mounts: M3-ENV-739, 740, 742, 744.
    - **Noted:** the Reefball drop proxy is placed in no Act I scene (pc-gpu's R&D).
  - **Weak views reframed:**
    - O10: the lintel gull with the town behind;
    - B07: the stem-gull's silhouette ahead of the hulk, as its sheet intends;
    - H10: back along the dock to the lamp-lit village. The sheet row is updated.
  - **Storm and night:**
    - Oruvel's storm is in the dressing: debris, a capsized hull, the dive bridge adrift and Kell's beacon, all
      following `StormWall`, plus the storm frame (`storm_environment`).
    - The preview `oruvel_dressed_storm.tscn` stands Rendering's UndertowStorm where the wall was.
    - M3-ENV-751 asks slice-polish to do the same in `set_storm`.
    - The nights (the Haluna dock, the Ch4 wake, the ferry) are in place.
  - **SELF-RENDERED @ 538d5eda:**
    - battle_arena_derelict / _deck_night / _ash_terrace_lanternfall, shrine_s02–s05, drownbell_flood,
      ch04_ferry_deck/derelict: pass (rmse ≤ 0.0074).
    - first_verse_stage_v01/v02, brightwater_landing_f01/f06, zone_oruvel_storm_o12/o16: new, viewed.
    - haluna_h10_dock_night: reframed, intended drift (re-approve).
    - The kit previews O10 and B07 were viewed through their own manifests.
  - **Gates:**
    - tools suite 117 units: only test_screenshots red, for new shots' first baselines;
    - Godot haluna 62, import 21, zone_kit 6, environment 11, shrine 37, brightwater 6, oruvel 14, arena 18, all pass;
    - gdlint and gdformat clean; validate_data; taskboard.
  - **MERGE-READY @ 538d5eda** (integration 8d03e6d1 merged in).
- **2026-10-28 ~06:00: Batch B viewed; First Verse found primitive.**
  - SELF-RENDERED @ 7a115247: shrine_s02/s03/s04/s05, battle_arena_derelict, brightwater_b03,
    ch04_ferry_deck/derelict, causeway_c08, haluna_h03 — pass (rmse ≤ 0.0068). Viewed: final. In ch04_ferry_deck
    an orange capsule (a model-less actor) fills the lower left (act1-chapters').
  - SELF-RENDERED @ 7a115247: brightwater_b02_awning — drift 0.0107, intended: the passengers' bundles fold and
    bind (d4967aee, 10-27) since its 10-24 baseline. Re-approve on the next gate.
  - SELF-RENDERED @ a7dca885: slice_haluna_villagers_village, slice_causeway_head, slice_causeway_harrier_view —
    pass (rmse 0). slice_beach_h05_asha / h06_toma — drift 0.049 / 0.048, only on the palms and the drying rack's
    poles (their wind sway's phase over a 270–375-frame cutscene capture); the frames are otherwise identical, no
    dressing change. Flag for the Lead: those two may need a fixed wind time in their setup.
  - **M3-ENV-745 (FAST-TRACK to slice-polish):** Ch3's First Verse cutscene (`first_verse.tscn`, shot
    `slice_verse_steps`) is CSG primitives (island, dome, steps, pillars, flat plane sea) under the real heroes.
    Stage it on env-art's final shrine; the task maps the marks onto the real steps.
- **2026-10-28 ~05:00: Ch4's wake night dressed (M3-ENV-743); MERGE-READY.**
  - **New Haluna kit pieces:**
    - `wake_ground`: the terrace level at y 0 inside the rails, the beach and flats past them, the island behind;
      lane, turf, seagrass and rubble masks.
    - `house_lane_a/b/c`: the houses with no shade deck, at the greybox's sizes.
    - `dock_haluna_short`: 14.4 m.
    - `wake_shell_set`: a named shell for the wall, no stand.
    - The existing houses, dock and single shell rebuild byte-identical.
  - `assets_src/environments/kits/haluna/wake_zone_dressing.py` → `assets/environments/zones/ch04/` (the JSON, the
    night Environment, the night sea) and the preview `game/levels/_tests/haluna_wake_dressing/`.
  - The mount request is M3-ENV-744 to act1-chapters (Water at -0.9, the glimmer global, the capsule actors).
  - SELF-RENDERED @ 2f5d51c9: zone_wake_h02/h04/h07/h09/h12/h13/h08/c01 (new) — the moonlit lane and houses, the
    shut market and inn, the chapel door, the dark dock (no lamps) from the shore and from under it, the feast and
    the lamp-lit wall, Asha's inked and Imra's faded shells set in the wall. Two shot notes for act1-chapters: H02's
    camera is 0.5 m from Neme's house front; C01's is behind the wall and below its top.
  - Gates: tools suite 117 units (only test_screenshots red, for the new shots' missing first baselines);
    Godot haluna 62, import 21, zone_kit 6, environment 11, all pass; validate_data; taskboard --check.
  - **MERGE-READY @ 2f5d51c9** (integration bd3ab5b4 merged in). New shots needing first approval (never write
    baselines here): zone_oruvel_o01/o07/o09/o12/o16, zone_underway_u01/u03/u06/u07/u08, zone_wake_h02/h04/h07/
    h09/h12/h13/h08/c01; haluna_h07_chapel_court re-approval (intended drift).
  - **Next:** Brightwater ferry (B-shots, the Ch4 ferry deck and derelict), the Shell Shrine interior (S02–S05),
    then the prologue city if slice-polish wants env-art to mount it.
- **2026-10-28 ~03:00: Ch1 zones dressed; renders viewed.**
  - SELF-RENDERED @ 9cced155: slice_prologue_vigil_line, haluna_h01/h02/h04/h10, causeway_c02, shrine_s01,
    drownbell_flood, battle_arena_tideline_dawn/causeway_disc_sunset/causeway_route_afternoon/derelict_deck_night/
    oruvel_raft_morning/underway_tower — pass (rmse ≤ 0.0055). Viewed: all final; the prologue city is still
    primitives (the zone's, M3-ENV-739 FAST-TRACK to slice-polish).
  - SELF-RENDERED @ 9cced155: haluna_h07_chapel_court — drift 0.0265, intended: the chapel's pilasters, dentils
    and arched heads (9c26b66e) postdate its baseline. Re-approve on the next gate.
  - SELF-RENDERED @ b82d8df1: zone_oruvel_o01/o07/o09/o12/o16 (new, M3-ENV-738) — the decks, the *Seventh
    Terrace*'s name-board, Kell's chandlery and the pen read final. The green and pink capsules are the zone's
    actors with no `model` (netmenders, pen child; M3-ENV-740 asks slice-polish for bodies).
  - SELF-RENDERED @ e8d3e151+: zone_underway_u01/u03/u06/u07/u08 (new, M3-ENV-741) — the crown under Oruvel's
    hulls, the sealed bell-room, the wheel, the shaft; U06's stairwell lined a storey down after the first render
    showed the murk through it.
  - The ruin column's LOD1 now keeps its broken top (H04's far columns read as plain tubes).
  - Requests: M3-ENV-740 and M3-ENV-742 (mount the two dressings, slice-polish), M3-ENV-739 (the prologue city).
  - Every capture logs `SCRIPT ERROR: Trying to cast a freed object` at shutdown from `life_audio.gd:124` (audio's;
    known since big12). It makes capture.sh exit 1 though every shot is written.
  - **Next:** Ch4 `haluna_wake` (41 greybox blocks): a ground piece and a ZoneKitDressing from the Haluna kit.
- **2026-10-28 ~01:30: REFOCUS (ADR 0041, the human's directive via the Lead).**
  - **Scope:** the Prologue through Ch4, plus the shared kits. env-art-b takes Ch5–Ch9.
  - **Paused:** my 19 later-act tasks (M3-ENV-716–718, 720–723 and 725–736) are `blocked` with `blocked-by: ADR 0041`. Their work stays committed and pushed as is.
  - **"The 10 game/battle/arenas scenes":** every id in arenas.json already plays env-art's final arena, and the arena preview shots load encounters, so they render the final arenas too. The 10 greybox scenes are dead files owned by battle-presentation. M3-ENV-737 asks them to delete them.
  - **Self-rendering** per TRACK-RULES cd23f612, with the human's OK in this session.
    - The Act II/III batch was stopped.
    - Iskarra I02 and P01 were captured first: the Ysolde capsule is gone and the frames read clean.
    - Batch A (15 Act I shots: the prologue vigil, Haluna ×5, the causeway, the shrine, the Drownbell flood, five Act I arenas) is running.
  - **Next:** view Batch A and fix what reads primitive. Then Batch B: the Oruvel O-shots, the Underway, the Brightwater B-shots and the Ch4 ferry, then the shrine interior.
- **2026-10-28 ~00:50: the Lead's list of 10-28 00:13.**
  - **(1) and (2):** were already done (8be2adcd dressed the wall-head and the Reach backdrop; `wall_head_storm` plays the final seawall). The per-fight mapping, M3-ENV-714, is re-routed to combat (battle-presentation) with the current state.
  - **(3):** every env-art todo is answered (see the 23:50 entry).
  - **(4), the Ch10–12 greybox kits:**
    - M3-ENV-733: the root-walk, reed causeway, reed platform and clutch stone;
    - M3-ENV-734: Quellan's inn and well, Hesk's dais, and a new `test_keth.py`;
    - M3-ENV-735: the Sunken Vey gallery walk and Lowlight's lamp bench;
    - block-to-piece swap maps for all seven greybox zones (ossa_fen.md §4, lowlight.md §5, keth_pass.md §6);
    - the request to act1-chapters, M3-ENV-736.
  - **Checks:**
    - tools tests for the touched kits OK, with `quellan_house` byte-identical after the refactor;
    - the haluna_kit Blender build, where only the 9 new glbs appear;
    - validate_data, taskboard and godot --import.
  - The single render request moves to the new head.
- **2026-10-28 ~00:20: state.** Session handoff `2026-10-27-art-env-art-2.md`.
  - **Audit fixes since MERGE-READY a733e5e7, each with its own scoped checks:**
    - the Choir's moon and the Spire crown's afterglow (both tested against singer and engine shadows);
    - Ashcrown's pillars and tiers; the Pemakar stelae; Iskarra I02 without Ysolde's capsule;
    - the Hollowmere/Kite preview (M3-ENV-731) and the Act II kit rows (M3-ENV-732).
  - **Waiting on renders** (requests below). Next: view and approve them as they land, and fix what the new previews show.
  - **BACKLOG EMPTY until renders land:**
    - every todo or request task for my role is answered (kit side done; placement belongs to act1-chapters or slice-polish);
    - next-act content is complete through the Ending;
    - every audit fix and new preview is waiting on its render.
- **MERGE-READY @ 01bf31c2** (claude/env-art; it includes the integration branch at d2fb94c4). Since 0958af1a:
  - **New content:** M3-ENV-726 the Spire crown, M3-ENV-727 the Cage, M3-ENV-728 the Heart (two arenas), M3-ENV-729 the Ending's grades and M3-ENV-730 Oruvel rebuilt.
  - **Requests answered:** M2-ENV-14 (the helper bones) and the Ch8 repoint (M3-BPR-407).
  - **The M3-ENV-705 audit fixes:** the Underway walls, the Coilspire headland and scrub, the ferry bundles, Tamsule's market, the Terrace's counter, the Pemakar stelae, Ansedra's escape, and Iskarra's slabs and packs.
  - **Approved baselines:** 8be2adc (6) and f39cdde (3).
  - **Checks:**
    - tools unittests for every touched kit and arena: 234 + 21 + 7 OK;
    - Godot `--filter=haluna` 62/0, `oruvel` 14/0, `underway` 6/0, `battle_arenas` 10/0;
    - gdlint/gdformat clean, validate_data 0/0, taskboard --check;
    - every Blender job touched rebuilt, with only the named glbs changed.
  - **Skipped:** the full Godot suite (no battle/progression code touched) and every shot (the render requests below list them).
- **2026-10-27 ~23:50: three more items pushed @ b75b93bc (all review, reviewer rendering unless noted).**
  - **M2-ENV-14** (request from Character): `HalunaActorPose.apply()` now calls `HeroHelperBones.drive` after the hand-set pose (one line in m2-slice's `haluna_actor_pose.gd`, routed here by the task). `--filter=haluna` 62/0. Character: view Asha's beach kneel on the next H05 render. **M2-ENV-12** was already done by m2-slice; noted on the task for the Lead to close.
  - **M3-ENV-729, the Ending's grades:** `ending_grades.py` writes `assets/environments/zones/ending/` (three Environments, `lut_ending_lift`, `lut_ending_dock`, `lut_post_credits`, `ending_grades.json` with the key, rim, lamp and E1–E5 sea-glow rows). Sheet `ending.md`. For Cinematics: these are what E1–E7 swap to.
  - **M3-ENV-730, Oruvel rebuilt (E7):** `ov_rebuilt.py` (`raft_deck_rebuilt`, `lamp_post`), `ov_timber_new`, the Oruvel layout's `states.rebuilt` with `first_lamp`. Every existing Oruvel glb and material is byte-identical; test_oruvel_kit 45 OK, `--filter=oruvel` 14/0.
  - No new shots (the Ending frames have no stager yet), so no render request for these.
- **2026-10-27 ~23:15: M3-ENV-728, the Heart (Ch21), pushed @ 9c2aaa39 (review, reviewer rendering).** Kit `undertow_heart.py` (heart_floor, heart_column, heart_eyewall), `lut_ch21_heart`, arenas `undertow_heart` (held) and `undertow_heart_letting` (the Letting). Checks: haluna_kit full rebuild (every existing glb byte-identical, 3 new), arena_scenes (every other arena byte-identical), test_undertow_heart + test_undertow_layers (7 OK), test_arenas (21 OK), validate_data, taskboard --check, godot --import, gdlint/gdformat on the test list. Skipped: Godot tests (only the arena list changed; test_battle_arenas runs at the gate) and the shots (render request posted). M3-ENV-727 (Ch20, the Cage) is at 46955a37. **Next:** view renders as they land; then the Ending's open-sea frame (`ending_unbinding`) and the M3-ENV-705 audit continued.
- **ISKARRA: both passes pushed; FAST-TRACK render requested @ f39cdde3. Was: in progress (the Lead's direct instruction, 22:29). Act II/III is paused until the Iskarra render is
  approved.**
  - **Already pushed** (FAST-TRACK request @ 0958af1a, not yet rendered):
    - Commits 4c0e9732 and 0958af1a.
    - The towers were inside out since M3-ENV-710; now fixed.
    - Glazed tile cladding and a blue glaze; windowed storeys; real gallery ledges.
    - The plaza inlay and fallen tiles; a drowned midground and the far skyline.
    - Hero stand-ins in place of the preview's capsules; the cast-on-stone test.
  - **Now:**
    - Stone and plaster breakup, damage and decals on the towers, gate and plaza.
    - Paving under Kerrid (9.5, −5.5).
    - The vigil count in test_iskarra.
    - Set dressing at Haluna's density.
  - **For slice-polish (the Prologue's staging is yours):** the three `City/Vigils` capsules (Kerrid, Pell,
    Liss) are the last capsules in the frame.
    - Kerrid and Liss have no character models yet. VillagerLayer's adult bodies (fisher, netmender) cast as
      stand-ins would read as people.
    - The preview uses the four hero battle stand-ins at their marks (`iskarra_preview_figures.gd`), if that helps.
    - Also swap `City/Water` (a flat PlaneMesh) for the lagoon WaterSurface the preview uses.
  - **Lit candles:** none. ADR 0017 and the act outline say "There is no fire" and Rhen's lantern is the only
    flame, so the vigils get unlit offerings and the lamp columns stay dead. Lead: say if you want that overruled.
- **2026-10-27 ~21:40, the Lead's FAST-TRACK: Iskarra (M3-ENV-724), MERGE-READY @ 0958af1a** (4c0e9732 plus the far skyline) (claude/env-art, which
  includes the integration branch at big12, 7f355a8f).
  - **Root cause of the greybox read.** Every Iskarra tower shaft and lamp column had been wound inside out since
    M3-ENV-710, so Godot drew the inside of each far wall. Fixed, and covered by a test.
  - **Materials.** Glazed tile cladding (new `iskarra_tile` texture), a reef-blue glaze for the bands, domes and
    paving inlay, and a flagstone texture for the paving.
  - **Trim.** Arched windows on every storey, real gallery ledges with parapets.
  - **Dressing.** The plaza sunburst inlay and fallen tiles; a drowned midground of two buildings, two domed
    blocks and a sunk arcade.
  - **Preview.** Hero stand-ins at the cast marks replace the capsules.
  - **Vigil gap.** test_iskarra now checks every Prologue cast mark stands on stone, and all pass.
  - **For slice-polish (its staging; nothing edited there).** The Prologue's `City/Water` is a flat PlaneMesh.
    Swap it for the lagoon WaterSurface the preview uses (water_surface.gd + lagoon_waves.tres +
    haluna_water_material.tres). The three `City/Vigils` capsules are the last greybox in that frame. Please
    re-render slice_prologue_p01 and slice_prologue_vigil_line after merging this.
  - **Checks.**
    - test_iskarra 8 OK and test_haluna_kit OK. Blender: haluna_kit rebuilt; only the Iskarra glbs changed, and
      the rest are byte-identical. Godot import clean; `--filter=iskarra` 1/1; lint and format clean.
    - Also on this head: the big12 merge (8339d660), `--filter=haluna` 62/0 and `--filter=battle_arena` 18/0.
      The tools suite is all OK except test_screenshots, which is red only for the new arena shots awaiting their
      first PC baselines (seawall/coilspire and the others above).
  - **Since then, the same branch:**
    - M3-ENV-717: the Keth wall rework (7f1a0fc7, re-render requested).
    - M3-ENV-716: the Lowlight baseline (5475b0ac).
    - **M3-ENV-723 Hollowmere** (8cf1e66b, review): the sheet, a 6-piece kit, and the `act3_dusk` grade in
      `zones/ch17/`. No shot yet; act1-chapters places it.
    - The Ansedra zone pieces (afa5b0bb).
    - M3-ENV-725 the Kite (02c3075d, Story review); M3-ENV-726 the Lamp Spire's crown and arena (`5d53f98c`); the
      Iskarra sheet; the white barge's trim and the chapel's articulation (M3-ENV-705); M3-ENV-1203 to review.
- **Id blocks (the Lead, CONSOLIDATED §4):** env-art's new task ids are 700–799 (e.g. M3-ENV-710), its ADRs
  0160–0169, and its handoffs are named `<date>-<role>-env-art-<n>.md`. Existing ids stay. The big8 renumbering
  is applied here too: the shell shrine shaft-lamps task is now **M3-ARC-04** (was M3-ARC-02), and the Tidecup
  drop-look task is now **M3-RND-26** (was M3-RND-01).
- **2026-10-24 afternoon (the Lead's M2-review blockers):**
  - **M2-ENV-10, the B06 Saltgrass Causeway route: done, in review (rendering).** Covers the flats terrain, the
    layout, the shipped dressing scene and the preview C01–C08. The Drownbell disc is seated, and 2 baselines
    are registered (c02 profile, c08 disc approach). Swap-in note below.
  - **M2-ENV-11, the battle arenas `tideline_dawn` and `causeway_disc_sunset`: done, in review (rendering),
    merged here** (22080124). Contract in `docs/kb/tech/battle_arenas.md`. Battle-presentation adopted it
    (972131e); after the merge only its `arenas.json` repoint remains (swap-in note below).
  - **M3-ENV-02, Brine Shoals: in review, merged here** (c2bb5563). Its own import category
    `brine_shoals_kit` needs Character + Tools sign-off (M3-RND-21 filed). **M3-ENV-01 Tidecup:** in review
    (M3-RND-26 filed; renumbered from M3-RND-01).
  - **M3-ENV-03 Terraces of Ash (Pemakar): in review, merged here** (f5c35191).
    - Kit: 25 pieces, 27 materials, Blender job `pemakar_kit` (61 identical). Its import kind `pemakar_kit`
      needs Character + Tools sign-off.
    - Baselines: `pemakar_p01_waterfall_of_fires` and `pemakar_p03_among_the_graves`.
    - Checks: its unittests, `--filter=pemakar` 5/5, `--filter=post_import` 19/19, release exclusion OK.
    - Weaker views (P02, P05, P06, P08) are listed in its task file. Swap-in note there.
  - **M3-ENV-04 the Seawall (Corrow): in review, merged here** (55e1d994).
    - Kit: 11 pieces, 17 materials, LUT `lut_ch08_storm`. Blender job `corrow_kit` is byte-identical. Its import
      kind `corrow_kit` needs Character + Tools sign-off.
    - Baselines: `corrow_c01_wall_head` and `corrow_c08_watcher_profile`. Weaker views (C03 sea face, C06 town)
      are in its task file.
    - Follow-up **M3-ENV-04B** (destroyed wall, cut hoist, Ch9 night) is filed as todo.
    - Checks: corrow 5/5, post_import 19/19, tools unittests (including tamsule LUT and release exclusion) OK.
  - **M3-ENV-06 Act I battle arenas: 3 of 5 merged here** (437a9f64). The ids are kept as battle-presentation
    proposed them.
    - `causeway_route_afternoon`, `derelict_deck_night` and `ash_terrace_lanternfall` are at
      `assets/environments/arenas/<id>/<id>.tscn`, with one baseline each.
    - CameraHints: `wide_high`, `party_side`, `foe_side`, plus `from_the_causeway`, `from_the_foredeck` or
      `lanternfall_low`. None of the three has a BossAnchor or FloodAnchor.
    - Known limit: the terrace's plume and Ashcrown are out of the default battle frame, so they need a tilted
      presentation camera.
    - The night arenas' omni-light counts (70 for the terrace, 7 for the deck) haven't been measured on GPU.
    - Checks: haluna, brine_shoals and pemakar Blender jobs byte-identical; battle_arenas 8/8; full tools 648 OK.
    - `underway_tower` and `oruvel_raft_morning` are being built by a worktree agent; it will file a Rendering
      request for the underwater look.
  - **Fixed (1771dc09):** four kits imported Haluna's material writers as a bare `materials` module and picked up
    tamsule_bell's instead when both loaded in one process. They now load it by path.
  - **M3-ENV-05 the lamp-diver's sea floor (Oruvel Underway): in review, merged here** (1a4a9adb).
    - Kit: 30 pieces, 25 materials. Blender job `oruvel_underway_kit` is byte-identical. Its import kind
      `oruvel_underway_kit` needs Character + Tools sign-off.
    - Baselines: `ou_u04_lamp_gallery` and `ou_u12_terrace`.
    - Checks: oruvel 6/6, post_import 19/19, underwater 8/8, unittests OK.
    - **For Rendering:** M3-RND-24. The underwater rig doesn't attenuate the sun with depth, and its in-scatter
      ignores walls; the preview stands in for both.
    - **For Narrative:** the dead ship's ribs echo Hullgnaw's rib-timbers. Also to confirm: floors are counted
      from the street (F9 is the gallery), and the dive's sun is at 08:45.
    - Handoff: `2026-10-24-environment-seafloor.md`.
  - **M3-ENV-04B the Seawall breach and Ch9 night: in review, merged here** (d5e21d46).
    - Pieces: breach segments a/b, west and east ends, cracked and fallen heads, broken stair, cut hoist,
      low-town rubble and a second Watcher carving. Preview phases `fallen` and `ch09`.
    - Baseline `corrow_c10_breach_fallen`; the C01 and C08 baselines are unchanged.
    - Checks: corrow_kit 44 identical, corrow 8/8, post_import 19/19.
    - **For Narrative:** in Ch9 the breach cuts the Fisher Stair after 12 steps. The swap-in note says how to move
      the breach if the zone needs the full climb.
    - **For Rendering:** the Ch9 ambient is 0.7, not the colour script's 0.3, because the stair foot rendered black.
    - **For Art:** a `ch08_after` colour-script row is proposed in corrow.md §7.
  - **M3-ENV-06: all five arenas merged** (169445e9). Request M3-RND-25 covers the underwater look.
  - **New queue (the Lead's no-idle directive; filed by env-art 2026-10-24 evening):** the last four Act I zones
    without kits.
    - **M3-ENV-08 Brightwater ferry: in review, merged here** (e1f12963).
      - Kit: 11 pieces, 27 materials, Blender job `brightwater_ferry_kit` (40 outputs identical). Its import kind
        `brightwater_ferry_kit` needs Character + Tools sign-off.
      - Baselines: `brightwater_b02_awning` and `brightwater_b03_rail_drowned`.
      - Checks: brightwater 5/5, post_import 21/21, unittests OK.
      - Calls to confirm: the moon sits low in the east (88°, 16°) so the hulks read on its path, and a new grade
        `lut_ch04_crossing` keeps the sea's teal (`lut_ch04_wake` is untouched).
      - Follow-up **M3-ENV-08B**: the boardable derelict *Seventh Terrace*. It depends on M3-ENV-07.
      - For Rendering: the daylight `ch04_derelict` grade.
    - **M3-ENV-07 Oruvel raft-town: in review, merged here** (06ef403d).
      - Kit: 18 pieces, 23 materials, Blender job `oruvel_kit` (42 identical). Its import kind `oruvel_kit` needs
        Character + Tools sign-off.
      - The `oruvel_raft_morning` arena's town is now built from this kit; its baseline was re-approved after
        viewing.
      - Baselines: `oruvel_o01_surfacing` and `oruvel_o19_dive_mooring`.
      - Checks: oruvel 11/11, post_import 21/21, arena 13/13, oruvel_kit and haluna_kit Blender jobs identical.
      - Weak: the O10 gull and the drowned tower showing through the water.
      - Follow-up **M3-ENV-07B**: the storm state and Hullgnaw's deck split.
      - Found **M2-ENV-12**: Haluna's lintel-gulls are built inside-out and shade dark. Filed; fixing it moves
        the Haluna gull shots.
    - **M3-ENV-09 Ashcrown temple: in review, merged here** (e70d898e).
      - Kit: 9 pieces, 26 materials, Blender job `ashcrown_kit` (40 identical). Its import kind `ashcrown_kit` needs
        Character + Tools sign-off.
      - It is the same building as Pemakar's far Ashcrown: same origin and tier numbers, checked by a test.
      - Baselines: `ashcrown_a01_approach` and `ashcrown_a04_anvil_hall`.
      - Checks: ashcrown 5/5, post_import 21/21, unittests OK.
      - Follow-ups filed: **M3-ENV-09B** (Pemakar's far temple from this kit) and **M3-ENV-11** (a close-range
        plume, because the 900 m plume facets inside 300 m).
      - Fixed on the way: a merge left an empty job in `blender_builds.json` (e78e9196). Coverage now reports 0
        uncovered.
    - **M2-ENV-12 Haluna gull normals: in review, merged here.**
      - `village._loft` took its outward reference from the wrong column, so every gull loft was inside-out. It is
        fixed at the source.
      - Outputs changed: `lintel_gull_a/b/c`, Brightwater's `ferry_hull` (its stem-gull) and Oruvel's
        `lintel_gull_open`. All six jobs that use `village.py` are byte-identical after the rebuild.
      - Re-approved after viewing: `haluna_h03_lintel_gull` (rmse 0.047, the gull alone).
    - **Arena baselines after big7 (59ce74a5):** big7's creature models replace the enemy stand-ins, so the seven
      env-art arena preview shots moved. Each was viewed beside its baseline: only the enemies changed, plus the
      Drownbell's long sunset shadow. All seven are re-approved.
    - **For the Lead (not env-art's baselines, not re-approved):** `field_objective_line`, `field_interact_prompt`,
      `field_area_title`, `field_tip_card` (0.068) and `dialogue_continue` (0.057) drift because the Haluna
      tidewalls render wetter and darker. They drift the same with the old gulls, so the cause is not M2-ENV-12.
      It is most likely M2-ENV-06's tidewall pass reaching UI baselines captured before it. They need their owners'
      re-approval after viewing.
    - **M3-ENV-08B the Seventh Terrace: in review, merged here** (a96b8c68).
      - One hero ship for Ch1's mooring and Ch4's derelict: 13 pieces inside `brightwater_ferry_kit`, set,
        lowered and fallen sails, and a separate name-board.
      - Baseline: `oruvel_o07_name_board`. D06 matches O07 to within 2 mm.
      - Checks: brightwater_ferry_kit 62 and oruvel_kit 42 identical on the merged sources; brightwater 6/6,
        oruvel 11/11, post_import 21/21.
      - For Rendering: the `ch04_derelict` sub-frame. The derelict preview uses a stand-in day sun until it exists.
      - Filed **M3-ENV-700**: the ferry's transom is wound inward, and `bf_import_settings.py` overwrites the ch04
        LUT import.
    - **M3-ENV-09B: in review, merged here.**
      - Pemakar's preview and the Lanternfall arena now place the Ashcrown kit's five exterior pieces at the rim
        (LOD1 from 600 m). The silhouette is retired from the layouts but kept as an asset.
      - `pemakar_p01` re-approved after viewing (rmse 0.0016); p03 doesn't change.
    - **Baselines must come from `tools/screenshots/capture.sh` (one process per shot), not one shared
      `capture.tscn` run (08c48cc3).**
      - With creature models in frame, shared-mode captures depend on capture order: the route arena moved by rmse
        0.03 from its position in the run alone. Isolated captures are byte-identical run to run.
      - The ten arena and flood baselines I had approved from shared runs are re-approved from isolated captures,
        each viewed.
    - **M3-ENV-10 Coilspire temple: in review, merged here** (44c3bac5).
      - Kit: 12 pieces, 16 materials, Blender job `coilspire_kit` (29 identical). Its import kind `coilspire_kit`
        needs Character + Tools sign-off.
      - It is the same building as Corrow's far spire (reads `cw_far`, checked by tests). Its K08 view is shot
        from Corrow's C01 camera.
      - Baselines: `coilspire_k01_headland_path` and `coilspire_k03_well`; isolated re-capture gives rmse 0.
      - Checks: coilspire 5/5, post_import 21/21.
      - For m2-slice: the 10 flue-key wheels are tagged in the layout for the trial. Liss's wright's mark is a decal
        for m2-slice or VFX.
      - For Art: a `ch08_day` colour-script row.
    - **All four Act I zones filed as M3-ENV-07..10 are in review.**
    - **Merged here, in review:** M3-ENV-07B the Oruvel storm (baseline `oruvel_o17_pen_split`; Art owes the
      `ch01_storm` row) and M3-ENV-700 the ferry's transom (`ferry_hull` and `derelict_hulk_a`; b03 moved by
      0.0007, under the limit). **M3-ENV-11, the close-range plume, is still running.**
    - **M3-ENV-11 the close-range plume: in review, merged here** (d065835e). **No agents are running and the queue is
      empty.** Next: the Lead's queue, or the weaker views each task file lists.
- **Done (merge-ready):**
  - **M2-ART-01/02/03, Art sign-offs:** all three approve-with-fixes, status done. Fixes filed: **M2-UI-08** (Swell lamp at rest, bestiary defeat counts white not focus cyan), **M2-RND-09** (underwater: scatter/transmit to `lagoon_teal`, TIR to `deep_teal_shadow`, lantern halo warm, motes boosted only below the surface, recapture `waterline_high`), **M2-RND-10** (storm: narrower rents with darker lips, softer curtains, per-chapter flash table, landfall darker and slate-teal, rain ≤12% bright streaks, the Letting's wound_intensity 1.8 and rise_ratio 2.0). palette.json 0.2.1 extends the `spawn_wound`, `glimmer_held` and `glimmer_lift` usage notes to the storm. art/ui.md §10 records the accepted UI.
  - **M2-ENV-06 pass 1 (still `doing`):** Haluna kit textures, materials and tide-wall geometry to final quality; the five haluna baselines **re-approved after viewing** (h01 0.01584, h02 0.06091, h03 0.01360, h04 0.01108, h07 0.01049; palette checks 19/19). Details in the task file. **Only haluna_mood shots use these files.**
- **Done, in review:** **M2-ENV-08**, the route and village props (18 new kit pieces, 6 materials, a preview
  scene and the swap-in layout below). The Haluna shots don't drift.
  - **M2-ENV-06 pass 2 and 3** (merge-ready): framed stilt-house walls and shutters, thatch onto its swatch
    (h04 re-approved), the lintel-gulls in their own carved-wood material (h03 re-approved).
- **Done, in review (merged here):** **M1-ENV-10** (LOD chain via a shared `LodChain`; Character + Tools sign-off on `asset_import_rules.gd` pending) and **M2-ENV-07** (the real hero banyan and windbreak; h01, h02, h07 re-approved after viewing).
- **M2-ENV-03 decided:** m2-slice's kit adopted (Review log; swap-in note below). env-art's own kit agent stopped, its WIP kept for salvage. Fixes filed as **M2-ENV-09** (waits for the kit to reach the integration branch).
- **Two queue items remain** (M2-ENV-09 once the shrine kit is on the integration branch, and M2-ENV-06's wrap-up: re-capture `haluna_h10_dock_night` once it's on the integration branch). The banyan crown at H07 is done (eae547d9, h07 re-approved; its sky palette sample moved to clear sky). Lead: please queue more env-art work.
- **Coordination:** m2-slice replied (10:02): agreed; it will push its own ENV-03 subagent's kit WIP as `m2-slice/env03-wip` and leave the kit to env-art (I'll compare it with my agent's kit when both exist). env-art may edit the moved `game/levels/ch02/haluna/haluna_dresser.gd` directly (Environment content). **M2-ARC-04 may move VegetationPlant and more Haluna files out of `_tests/`**: merge `claude/m2-slice` before touching them. Settled as well: The Lead's CONSOLIDATED §3b moved ENV-03 off m2-slice's queue to env-art. Split: env-art builds the shrine kit (assets, materials, drivable nodes, a dressing prefab, a swap-in note); m2-slice swaps its `ch03/shell_shrine` greybox for it.
- **Un-pushed state:** none (worktree agents' branches are local until merged here).

## For the Lead
- **MERGE-READY @ d065835e (supersedes 5ab6029c below).** It adds M3-ENV-11, the close-range Pemakar plume (review):
  `ash_plume_near` and the shader's near group, which fades out by 400 to 800 m, so the 900 m read is unchanged.
  - `ashcrown_a01` and `a04` were re-approved after viewing, and `ashcrown_a10_plume_from_the_rim` is new.
  - Checks run: full Godot suite 2016 run, 0 failed; pemakar_kit 63 and ashcrown_kit 40 identical; P01, P03,
    Lanternfall, A01, A04 and A10 all rmse 0 on isolated captures; the kit, arena and fog-lamp unittests OK.
  - The full tools suite last ran at 5ab6029c (947 OK); this item touched only the tests that were re-run.
- **MERGE-READY @ 5ab6029c** (claude/env-art; it includes the integration branch at 7fa22c77).
  - **Items since 74c6dc0e, all in review:**
    - M3-ENV-07 Oruvel raft-town (and the raft arena's town); 07B its storm state and Hullgnaw's split.
    - M3-ENV-08 Brightwater ferry; 08B the Seventh Terrace; 700 the ferry's transom.
    - M3-ENV-09 Ashcrown; 09B Pemakar's far Ashcrown from that kit.
    - M3-ENV-10 Coilspire.
    - M2-ENV-12 the Haluna gull normals.
    - The ten arena and flood baselines re-approved from isolated captures.
    - The big8 renumbering applied (M3-ARC-04, M3-RND-26).
  - **Checks run:**
    - full Godot suite: 2015 run, 0 failed;
    - full tools unittests: 947 OK (4 skipped);
    - Blender jobs: every job touched is byte-identical (oruvel, brightwater_ferry, ashcrown, coilspire, haluna,
      pemakar, corrow);
    - every new or changed env-art baseline, re-captured with `capture.sh` (one process per shot), passes;
    - lint, format, validate_data and taskboard are clean.
  - **Checks skipped:** the full screenshot manifest (the Lead's) and coverage (no changes to game/battle or
    game/progression).
  - **Not env-art's baselines, flagged:** five UI and dialogue shots drift from the wetter Haluna tidewalls (listed
    above).
  - **Waiting on people:**
    - Character + Tools: sign-off on the import kinds `oruvel_kit`, `brightwater_ferry_kit`, `ashcrown_kit` and
      `coilspire_kit`.
    - Art: colour-script rows `ch01_storm`, `ch04_derelict`, `ch05_temple` and `ch08_day`.
- **MERGE-READY @ 74c6dc0e, for big8.** It includes the integration branch at 8f808cc6 (big7).
  - **Items:**
    - All seven final arenas swap in through `game/data/battle/arenas.json`.
    - `battle_arena_tideline`, `battle_arena_causeway` and `drownbell_flood` were re-captured, viewed and
      re-approved.
    - `test_battle_arena.gd` now checks the contract's `CameraHints` instead of the greybox's `Fill`.
    - The M3-ENV-07..10 task files are filed.
  - **Checks run:** full Godot suite 1988 run / 0 failed; full tools unittests 838 OK (4 skipped); lint, format,
    validate_data and taskboard clean.
  - **Checks skipped:** the full screenshot manifest (only the three arena shots can move) and coverage.
  - **Noted for battle-presentation, and present on the greybox too:**
    - In multi-shot captures, AudioDirector.attach_battle logs a freed-instance error.
    - The loader logs an owner warning when it reparents the WorldEnvironment.
    - The final arenas capture 5–8× slower than the greybox.
- **MERGE-READY @ 169445e9** (claude/env-art; it includes the integration branch at 1e3ff5d6).
  - **Items since ba7679c1, all in review:**
    - M3-ENV-03 Terraces of Ash.
    - M3-ENV-04 the Seawall.
    - M3-ENV-04B the Seawall breach and Ch9.
    - M3-ENV-05 the lamp-diver's sea floor.
    - M3-ENV-06, all five Act I battle arenas.
    - The Lead's fog-lamp rule (7ba0efb6), and the cross-kit `materials` import fix (1771dc09).
  - **Checks run:**
    - full Godot suite: 1578 run, 0 failed;
    - full tools unittests: OK;
    - Blender jobs touched: haluna, brine_shoals, pemakar, corrow, oruvel_underway, each byte-identical;
    - gdlint, gdformat, validate_data, taskboard --check: clean.
    - Shots: each item's own baselines, viewed by its author. No existing baseline was changed.
  - **Checks skipped:** the full screenshot manifest and coverage (no changes to game/battle or game/progression).
  - **Waiting on people:**
    - Character + Tools sign-off on the import kinds `brine_shoals_kit`, `pemakar_kit`, `corrow_kit` and
      `oruvel_underway_kit`.
    - Rendering: M3-RND-24 and M3-RND-25 (the underwater rig).
    - m2-slice: M3-ARC-04 (the shrine's shaft lights and the fog).
    - Narrative: the Ch9 stair; the sea floor's floor count and its ship's ribs.
    - Art: the `ch08_after` colour-script row.
- **MERGE-READY @ ba7679c1** (claude/env-art, which includes the integration branch at 1e3ff5d6).
  - **Items:** M2-ENV-10 causeway route (review); M2-ENV-11 battle arenas (review; arena root renamed
    `BattleArenaRoot`, adopted by battle-presentation); M3-ENV-02 Brine Shoals (review).
  - **Checks run:**
    - full Godot suite: 1556 run, 0 failed;
    - tools unittests: 584, of which the one failure (tamsule test_lut, a LUT regression from the arena merge)
      is fixed and re-run green;
    - verify_blender_builds: haluna_kit and brine_shoals_kit byte-identical;
    - gdlint, gdformat, validate_data, taskboard --check: clean.
    - Shots captured and viewed for the new work only: causeway c01/c03/c05/c06/c08, two new causeway
      baselines; the arenas and Brine Shoals agents viewed and approved their own two each.
  - **Checks skipped:** the full screenshot manifest and coverage (no game/battle or game/progression changes).
  - **Fixed on the way:**
    - `test_causeway_dressing` never parsed before; once it ran, its zones leaked a water-level publisher into
      `test_water_surface`.
    - The arena LUT table froze the noon grade, which broke tamsule_bell's LUT.
- **MERGE-READY @ 4f450a7c: ci_local exit 0, 1532 tests (0 failed), coverage within baseline (battle 99.95%, progression 96.69%), boot smoke OK, 84 shots compared / 0 failed, Blender vegetation 7 + haluna_kit 68 identical** (HYMN_BLENDER_BASE = cf999e0a, the integration commit merged; claude/m2-slice 165ddb4c merged too). The only commit after it is this live-log update.
- **Answered (2026-10-24):** the project owner and the Lead approved merging `claude/m2-slice`; done (70fa4c77 + bf18e854). The merge exposed two M2-ARC-04 release-build breaks, both fixed here: `LodChain` moved to `game/world/vegetation/` beside VegetationPlant (the import rules ship and used a `_tests` class), and `HalunaShotCamera` moved to `game/levels/ch02/haluna/` (the shrine's shots rig and the mood wrapper use it). `test_release_excludes_tests` passes.
- **Import gotcha when merging this branch:** delete `.godot/imported/*.glb-*` in the gate worktree and run `--import`, or `--filter=import` fails 3 tests on stale LOD ranges.
- **New standing queue started** (your message): M3-ENV-01 Tidecup, M3-ENV-02 Brine Shoals, M3-ENV-03 Terraces of Ash with worktree agents now; M3-ENV-04 Seawall and M3-ENV-05 the lamp-diver sea floor next.

## Swap-in notes for m2-slice
- **M3-ENV-101, the save shrine (for Systems/ui-menus, or cinematics if the Lead prefers; @ eeecf13d):** the Haluna
  kit's `save_shrine.glb` and `save_shrine_core.glb` replace `game/world/save_shrine/save_shrine.tscn`'s `Visual/*`
  primitives.
  - **Body.** Replace `Visual/Base`, `Step`, `Pillar`, `Cradle`, `Conduit`, `PostW`, `PostE`, `Canopy` and
    `CanopyLip` with one instance of `save_shrine.glb` at `Visual`'s origin. Its niche opens toward +Z, so turn
    `Visual` if a zone wants the front elsewhere.
  - **Core.** Swap `Visual/Core`'s mesh for an instance of `save_shrine_core.glb` at the same transform
    (0, 1.92, 0). It is centred on its origin, so the GlimmerField (`Visual/BoundGlimmer`) still holds on it.
  - **Unchanged.** The `Shape` (use sphere r 1.6) and the `Body` collider (cylinder r 0.62, 2.2 m) still fit: the
    body stays within r 1.05 and 2.79 m. Import kind: the Haluna kit's (as every Haluna piece).
  - **Tests.** `tools/tests/test_save_shrine_kit.py` pins the footprint, the core's seat and the open niche.
- **M3-ENV-100, the Prologue's Iskarra (cinematics/slice-polish):** this is M3-ENV-710's kit, already built.
  - **Drop-in.** `assets/environments/zones/iskarra/iskarra_city.tscn` keeps the reviewed staging: the plaza top
    at 0.4 (the terrace), the rise's top at 1.0, the nine towers at the primitives' feet and heights, the arch at
    (−18, −18), the fallen pillar, and four unlit lamp columns.
  - **Swap.** The swap note is M3-ENV-711, and it now adds replacing `City/Water` with the project's `WaterSurface`.
  - The task files for 100 and 101 are only on `claude/m2-slice`. I'll set them to review when they reach the
    integration branch.
- **Fog-lamp rule (the Lead, 2026-10-24):** a light near a dense FogVolume keeps `light_volumetric_fog_energy = 0`.
  In `ch03/shell_shrine/shell_shrine.tscn` I set it on my own `Bounce/Skylight` (the light added under M2-ENV-09;
  no registered baseline shows the shrine). Your three `Bounce/Shaft_*` lights and `_pool_bounce()` in
  `shell_shrine_level.gd` are still on the default 1.0 inside `ShaftFog`. **M3-ARC-04** is filed for you;
  `tools/tests/test_fog_lamps.py` lists them as known exceptions until it lands.
- **M2-ENV-10, B06 Saltgrass Causeway:** instance
  `assets/environments/zones/saltgrass_causeway/saltgrass_causeway_dressing.tscn`. Rails and triggers come from
  `$Dresser.path_points()`. Banter beats, examine points and the B10 trigger (`drownbell_disc`, r < 15.1 m)
  come from `$Dresser.anchors()`. Collision is a trimesh from `causeway_flats-lod1` plus `causeway_disc-lod1`.
  Full note: the task file's "Swap-in note for m2-slice".
- **M2-ENV-11, battle arenas:** battle-presentation adopted the contract (972131e: encounter `arena` ids, `arenas.json`,
  its `BattleArena` loader; the Sun stays at the battle root, so no Rendering change). After merging, repoint
  `arenas.json` at `assets/environments/arenas/<id>/<id>.tscn` and re-approve its three arena/flood shots after
  viewing them. The arena root class is renamed `BattleArenaRoot` here to avoid a global class-name clash.
  Details: `docs/kb/tech/battle_arenas.md`.
- **M2-ENV-09 (Shell Shrine art fixes):** merged here on top of your kit. One edit in your scene, approved by the
  project owner: a shadowless `Bounce/Skylight` OmniLight in `ch03/shell_shrine/shell_shrine.tscn` (the cool sky
  through the oculi; S02 was murky brown). If you want the islet's algae band at the waterline, the shrine scene
  needs to publish `hymn_water_level` for its sea at -2.0 m (as Haluna's WeatheringTide does).
- **M2-ENV-03, the Shell Shrine: swap in YOUR kit (the Art Director's verdict, 2026-10-24).** I compared
  your kit (f38edea, shots from 3313bac) with env-art's in-progress kit, as the Lead asked. Yours wins: it is
  complete, wired into the level, and it reads (S03's diagram, S04's pour, S05's charm). Revert your revert of
  the level side (the commit after f38edea) and land the S01–S05 shots. env-art's kit is stopped. The art
  fixes (fan-shell roof tiers, coral walls instead of ashlar, a cool interior instead of murky brown, S01
  leaf-boats and offering shelf, channel bends) are **M2-ENV-09**, which env-art builds on your kit once it's
  on the integration branch; none blocks your swap-in. Verdict in full: M2-ENV-03's Review log.
- **M1-ENV-10, the LOD chain in your moved `game/levels/ch02/haluna/haluna_dresser.gd`** (you OK'd env-art
  editing it; I'm handing it over instead so neither of us has to merge the other's unreviewed work).
  Once `game/levels/_tests/vegetation/lod_chain.gd` (`LodChain`) is on your branch via the integration
  branch, replace the per-mesh range block in `instance_piece` with:
  ```gdscript
  	var ends := PackedFloat32Array([lod_from, float(layout.get("lod_end_m", 2000.0))])
  	...
  		# M1-ENV-10: `<piece>` is the visibility child of `<piece>-lod1`, so exactly one draws.
  		var lod := 1 if String(mi.name).ends_with(LOD_SUFFIX) else 0
  		LodChain.apply(mi, lod, ends, margin, 0.0, LodChain.sibling(mi, lod + 1))
  ```
  (it replaces `lod_end` and the six `visibility_range_*` lines; `git diff 565030e^ 2236fab2 --
  game/levels/_tests/haluna_mood/haluna_dresser.gd` on claude/env-art is the exact patch, which applies to
  your copy at +57 lines). If M2-ARC-04 moves VegetationPlant, move `lod_chain.gd` with it; it depends on
  nothing but its class_name.
- **M2-ENV-07, the real banyan and windbreak:** nothing to do. They keep the old piece names
  (`banyan_placeholder`, `windbreak_placeholder`), so the layout and your collision rules pick them up.
- **The route, north lane → causeway head (M2-ENV-08, review).** Copy the 36 entries of
  `game/levels/_tests/haluna_mood/route_layout.json` `pieces` into `game/levels/ch02/haluna/haluna_layout.json`
  `pieces` (they are in zone coordinates: slab steps at the trigger (7, -126), 14 slabs and 8 coral heads
  out 40 m towards the shrine islet at yaw -59°, three pilgrim marker posts every 20 m with the broken one
  first, the Lit Age ring 7.5 m off the path at 30 m, a wreck rib on the beach-head, lamp posts at the lane end
  and at the head, offerings and sandals at the wake-shell wall's foot, a stall and a fish rack at the lane
  end). Move any that clash with your NPCs or triggers; nothing depends on exact spots.
  Collision `piece_rules` (HalunaCollision, keyed by the first mesh name): an oriented box for
  `causeway_slab_*`, `coral_boulder_*` (inset 15 %), `market_stall`, `fish_drying_rack`, `wreck_rib`;
  a trunk cylinder for `pilgrim_marker_post*`, `oil_lamp_post`, `water_jar`; nothing for `basket_set`,
  `net_float_cluster`, `sandals`, `lit_age_ring` (walkable over its buried arc; add a box if Rhen clips it).
  Materials load by slot from the kit's materials folder as usual (6 new .tres files are in the kit).
- **Haluna kit pass 1 (M2-ENV-06):** nothing to do. Same piece names, same materials and slots; `env_ground.gdshader` gained a `breakup` uniform group with defaults (no scene edit needed).
- **M3-ENV-01, the Tamsule Bell kit (Ch7 `ch07/tamsule_bell`, review):** when you build the zone, start from
  `game/levels/_tests/tamsule_bell_kit/tamsule_bell_kit.tscn` (generated by
  `assets_src/environments/kits/tamsule_bell/preview_scene.py`; its `layout()` is the placement data). Arena space:
  origin on the bell axis at the river datum, north -Z; every ring piece (bell, goal ring, gantry head and six
  legs at azimuth 0..300, galleries `_a/_b/_c` at 40/90/140/220/270/320, platforms at 90 and 270, pennant lines at
  60/120/240/300, catch-pool) is placed with `rotation.y = -azimuth` and no offset. **Keep `SphereAnchor` at
  (0, 31.5, 0) with its `Drop` child, and `ColumnAnchor` (y 20) and `GoalRingAnchor` (y 43): PC GPU swaps the drop
  there (M3-RND-26).** Gameplay is yours: spawns on the galleries' walkway (y 2.4) and tiers (floors y 4.0 to 10.4,
  every 1.6 m), Toma and Asha on the west gallery's second tier (T02), the captains on the prow steps (y 2.46, r 13
  to 15.4 on azimuth 90 and 270), Tavi's side scene on Oruvel's posts (r 21, azimuth 19-51, T03), the match trigger
  at the catch-pool. Collision: the kit exports no `-col` proxies; boxes for the walkway, tiers, jetties and
  boardwalks, a cylinder for the pool wall (r 12.0-13.2, top 0.6). Materials map by slot at import (the new
  `tamsule_bell_kit` import kind). Register `tb_bell_bronze` (env_bronze.gdshader) in
  `game/data/settings/prewarm_materials.json` when the zone ships. The whole kit is in
  `docs/kb/art/environments/tamsule_bell.md`.

## Exact next step
**Blocked, waiting:** (1) the Lead's answer to the question above (merge `claude/m2-slice` for M2-ENV-09, or wait for the integration branch); (2) `haluna_h10_dock_night` and the shrine kit reaching the integration branch (not there at 19118fba). When either lands: build M2-ENV-09 on `shrine_interior.py` (salvage per `assets_src/environments/kits/shell_shrine_salvage/README.md`); re-capture h10, view, re-approve if it drifts, close M2-ENV-06. Session handoff: `docs/kb/handoffs/2026-10-24-environment-6.md`.

- **M3-ENV-02, Ch6 Brine Shoals (`ch06/brine_shoals`, review; kit `assets/environments/kits/brine_shoals/`).**
  Preview and layout: `game/levels/_tests/brine_shoals_kit/` (README there). For the zone:
  - **Dresser:** HalunaDresser works as is with `kit_dir` / `materials_dir` set to the brine_shoals folders and
    no terrain (every piece carries `"y"`). Start from `brine_shoals_layout.json` (generated by
    `assets_src/environments/kits/brine_shoals/bs_preview_layout.py`; change the generator's constants, not the
    JSON, if you want the same heights): a 6 × 8 block of 24 m cells (`mudflat_patch_a/b` yawed in 90° steps,
    `channel_straight_a/b` alternating down x = 0), `mudflat_far` around it, the camp on `camp_hard` at (20, 0)
    yaw 90, the plank walk in from the east (x 28 → 84, z ≈ 2), wrecks east of the camp, the tideline on the
    hard's west and south flanks with `lamp_burial` at (21, 8.5), `white_barge` in the channel at z = 30
    (origin at the waterline, bow +X, y = the water height).
  - **Water and tide:** WaterSurface at **−0.15 m** with `tide_line_y` 0 (WeatheringTide), material
    `brine_shoals_water_material.tres` (`silted_flats`, still). The creeks and pools are cut 3–5 cm below it.
  - **Light:** `BrineShoalsPreview` (extends HalunaMood) shows the two phases: `phase = &"raid"` (`ch06`) and
    `&"after"` (`ch06_after`, the side scene: fires out, haze thinner). Fire lights come from the layout's
    `fire_lights`. Copy the environment `.tres` and LUT, or point at them.
  - **Raid vs after:** the camp mixes burned and intact pieces during the raid (one tent still standing,
    one crate stack and one vat intact); for the aftermath swap the intact pieces for their `_burned` twins at
    the same transforms (same footprint and origin), thin the smoke and put the fire lights out (`&"after"`).
  - **Collision** (HalunaCollision `piece_rules`, keyed by the first mesh name): the ground cells and the
    hard as trimesh (they are the walkable surface); oriented boxes for `camp_tent*`, `crate_stack*`,
    `brine_vat*`, `salvage_rack*`, `liss_crate`, `branding_brazier`, `salvage_pile*` (inset 20 %),
    `wreck_*` (inset 25 %, they are open frames); `plank_walk` a thin box at its top; none for
    `smoke_plume`, `tideline_wrack`, `lamp_burial`. The channel below −0.15 m is water: block it or treat it as
    a wade line, your call.
  - **Story beats:** `liss_crate` is the crate Liss escapes with (it leaks bound light, ≤ 0.5 % of a frame);
    `branding_brazier` is the Order's (place it by the captured wrights); `lamp_burial` is the side scene's
    prop; the barge needs two pole-men (characters) and no wake.

## Queue
Re-prioritised by the Lead (intro audit, M2-review blockers first):
1. M2-ENV-10: the B06 Saltgrass Causeway route at final quality (next, env-art itself; swap-in note for m2-slice)
2. M2-ENV-11: per-encounter battle arenas, `tideline_dawn` and `causeway_disc_sunset` (agent; contract proposed to battle-presentation: an arena scene replaces the sandbox's WorldEnvironment/Sun/Arena around the existing slots)
3. M3-ENV-01: Ch7 Tidecup (agent)
4. M3-ENV-02: Ch6 Brine Shoals (agent)
5. M3-ENV-03: Ch5 Terraces of Ash: **paused** for the blockers. WIP on the local worktree branch `worktree-agent-a5692132254e05def` (81b235d8: design notes `pemakar.md`, 25-piece kit source, preview, shaders); not mergeable yet (no Blender job; generated assets held in the scratchpad without PROVENANCE rows). Next steps in its task Notes.
6. M3-ENV-04: Ch8 the Seawall; 7. M3-ENV-05: Ch1 the lamp-diver's sea floor
Done or in review: M2-ART-01/02/03 (done); M1-ENV-10, M2-ENV-06, M2-ENV-07, M2-ENV-08, M2-ENV-09 (review); M2-ENV-03 decided.

## History
- 2026-10-24: full ci_local green at 4f450a7c (after merging the integration branch cf999e0a and claude/m2-slice 165ddb4c; Blender threads pinned). M2-ENV-09 to review. Lead re-prioritised the causeway route and battle arenas.
- 2026-10-24: M3-ENV-02 Brine Shoals kit, preview and two baselines (worktree agent; commits on its
  branch: claim, notes, kit, import category, preview, docs). Gates in the task file.
- 2026-10-24: ENV-03 verdict (m2-slice kit adopted, M2-ENV-09 filed), salvage kept (5274d59a), handoff environment-6, merged the integration branch (53ddbc36; no overlap with env-art files; validate_data and taskboard clean).
- 2026-10-24: merged M1-ENV-10 and M2-ENV-07 (2236fab2). Gates: verify haluna_kit 49 + vegetation 7 identical; tools unittest OK; Godot haluna 16, post_import 19, vegetation 17, lod 3, import 19; validate_data; haluna shots re-captured, viewed, h01/h02/h07 re-approved, palette 19/19.
- 2026-10-24: M2-ENV-08 (fa4c666) and M2-ENV-06 passes 2–3 (15ce492, a6d3974). Merged the integration branch (856c43f).
- 2026-10-24: M2-ENV-06 pass 1 (6436775). Gates: verify_blender_builds haluna_kit 31 identical; Godot environment 11, haluna 13, post_import 17; validate_data; taskboard --check; the five haluna shots captured, viewed and re-approved.
- 2026-10-24: merged the Art sign-offs (3c3fa19, aa3b4ca, f067ba4). Gates: validate_data, taskboard --check, palette.json parses (docs only, no Godot run).
- 2026-10-24: set up the branch and toolchain; claimed the queue's tasks.
- 2026-10-30 (note by env-art-b, with the Lead's leave): M4-A2P-114 done in your kit, `haluna/lowlight.py` `PIER_AT`'s south-middle pier (0, 9.5) -> (0, 11.0), and `engine_hall.glb` rebuilt (f6442153). The pier stood where the battle camera rests after rest_fit (0.7, 4.0, 9.8) and filled the left of `lowlight_engine_hall`'s frame. Ch11's zone dressing places the same hall: the pier is 1.5 m nearer the south wall there too. Checks: test_lowlight, test_lowlight_housing, test_ch11_lowlight_dressing, test_haluna_kit, test_arenas; Godot ch11 and arena. Please review the task.
