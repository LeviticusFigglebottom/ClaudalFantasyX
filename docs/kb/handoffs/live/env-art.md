# Live log: env-art environment

Environment-art track, cloud session `session_01QmWUfYxd8DMg7XM3MyR6ps`, branch `claude/env-art` (from the integration branch `claude/undertow-lead-handoff-423ixt` at 2026-10-24). **This environment owns this file** (CLAUDE.md §7a). The Lead is `session_019iimsngAgPLEram1wcbLpE`; it reads this file on the pushed branch.

Scope: assets and kit pieces (Blender jobs, materials, import rules), handed to `claude/m2-slice` with a swap-in note here. Art Director sign-offs. I don't edit m2-slice's scenes (`game/levels/ch02/**`, `ch03/**`) except through a request task.

## Now
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
