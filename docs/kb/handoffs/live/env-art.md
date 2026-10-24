# Live log: env-art environment

Environment-art track, cloud session `session_01QmWUfYxd8DMg7XM3MyR6ps`, branch `claude/env-art` (from the integration branch `claude/undertow-lead-handoff-423ixt` at 2026-10-24). **This environment owns this file** (CLAUDE.md §7a). The Lead is `session_019iimsngAgPLEram1wcbLpE`; it reads this file on the pushed branch.

Scope: assets and kit pieces (Blender jobs, materials, import rules), handed to `claude/m2-slice` with a swap-in note here. Art Director sign-offs. I don't edit m2-slice's scenes (`game/levels/ch02/**`, `ch03/**`) except through a request task.

## Now
- **2026-10-24 afternoon (the Lead's M2-review blockers):**
  - **M2-ENV-10, the B06 Saltgrass Causeway route: done, in review (rendering).** Covers the flats terrain, the
    layout, the shipped dressing scene and the preview C01–C08. The Drownbell disc is seated, and 2 baselines
    are registered (c02 profile, c08 disc approach). Swap-in note below.
  - **M2-ENV-11, the battle arenas `tideline_dawn` and `causeway_disc_sunset`: done, in review (rendering),
    merged here** (22080124). Contract in `docs/kb/tech/battle_arenas.md`. Battle-presentation adopted it
    (972131e); after the merge only its `arenas.json` repoint remains (swap-in note below).
  - **M3-ENV-02, Brine Shoals: in review, merged here** (c2bb5563). Its own import category
    `brine_shoals_kit` needs Character + Tools sign-off (M3-RND-21 filed). **M3-ENV-01 Tidecup:** in review
    (M3-RND-01 filed).
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
  - **Running:** M3-ENV-06's last two arenas. Nothing is queued after them.
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
  there (M3-RND-01).** Gameplay is yours: spawns on the galleries' walkway (y 2.4) and tiers (floors y 4.0 to 10.4,
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
