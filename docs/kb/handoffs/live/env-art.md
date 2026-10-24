# Live log: env-art environment

Environment-art track, cloud session `session_01QmWUfYxd8DMg7XM3MyR6ps`, branch `claude/env-art` (from the integration branch `claude/undertow-lead-handoff-423ixt` at 2026-10-24). **This environment owns this file** (CLAUDE.md §7a). The Lead is `session_019iimsngAgPLEram1wcbLpE`; it reads this file on the pushed branch.

Scope: assets and kit pieces (Blender jobs, materials, import rules), handed to `claude/m2-slice` with a swap-in note here. Art Director sign-offs. I don't edit m2-slice's scenes (`game/levels/ch02/**`, `ch03/**`) except through a request task.

## Now
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
- **Question (send_message to the Lead is refused: elevated_session_untrusted_device):** M2-ENV-09 needs m2-slice's shrine kit on this branch. May I merge `claude/m2-slice` into `claude/env-art`, or should I wait until the integration branch carries it? Until you answer here or by message, I wait and work on other items.
- **Import gotcha when merging this branch:** Godot doesn't reimport a `.glb` when only its post-import script changes. After merging, delete `.godot/imported/*.glb-*` in the gate worktree and run `--import`, or `--filter=import` fails 3 tests on stale ranges.
- **Merging this branch changes the five haluna baselines** (intended, viewed). m2-slice's moved Haluna scenes use the same kit, so their haluna shots will match these baselines once both land.
- `haluna_h10_dock_night` (m2-slice's ENV-02) isn't on the integration branch yet, so it wasn't re-captured here; it uses the same kit stone and will drift a little when both land. I'll re-capture it after the integration merge.

## Swap-in notes for m2-slice
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
1. M2-ENV-03: Shell Shrine interior kit (agent)
2. M1-ENV-10: LOD chain in the kit dresser and import rules (agent)
3. M2-ENV-06: Haluna kit to final quality (passes 1–3 done) + M2-ENV-07 trees (agent)
4. ~~Art sign-offs M2-ART-01/02/03~~ (done)
5. ~~M2-ENV-08: the route and village props~~ (review); greybox flagged by the m2-slice playthrough (none reported to env-art yet)

## History
- 2026-10-24: M3-ENV-02 Brine Shoals kit, preview and two baselines (worktree agent; commits on its
  branch: claim, notes, kit, import category, preview, docs). Gates in the task file.
- 2026-10-24: ENV-03 verdict (m2-slice kit adopted, M2-ENV-09 filed), salvage kept (5274d59a), handoff environment-6, merged the integration branch (53ddbc36; no overlap with env-art files; validate_data and taskboard clean).
- 2026-10-24: merged M1-ENV-10 and M2-ENV-07 (2236fab2). Gates: verify haluna_kit 49 + vegetation 7 identical; tools unittest OK; Godot haluna 16, post_import 19, vegetation 17, lod 3, import 19; validate_data; haluna shots re-captured, viewed, h01/h02/h07 re-approved, palette 19/19.
- 2026-10-24: M2-ENV-08 (fa4c666) and M2-ENV-06 passes 2–3 (15ce492, a6d3974). Merged the integration branch (856c43f).
- 2026-10-24: M2-ENV-06 pass 1 (6436775). Gates: verify_blender_builds haluna_kit 31 identical; Godot environment 11, haluna 13, post_import 17; validate_data; taskboard --check; the five haluna shots captured, viewed and re-approved.
- 2026-10-24: merged the Art sign-offs (3c3fa19, aa3b4ca, f067ba4). Gates: validate_data, taskboard --check, palette.json parses (docs only, no Godot run).
- 2026-10-24: set up the branch and toolchain; claimed the queue's tasks.
