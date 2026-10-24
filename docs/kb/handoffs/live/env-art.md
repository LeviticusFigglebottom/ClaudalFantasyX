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
- **In progress (worktree agents):** M2-ENV-03 (Shell Shrine kit), M1-ENV-10 (LOD chain; running its shot gate), M2-ENV-07 (real banyan and windbreak trees, replacing the two PLACEHOLDER trees).
- **Coordination:** m2-slice's log said an m2-slice subagent had ENV-03. I messaged m2-slice (2026-10-24) proposing the split: env-art builds the kit (assets, materials, drivable nodes, swap-in note); m2-slice keeps the `ch03/shell_shrine` level swap, bakes and level shots. No reply yet. If m2-slice already committed kit work I build on it.
- **Un-pushed state:** none (worktree agents' branches are local until merged here).

## For the Lead
- **Merging this branch changes the five haluna baselines** (intended, viewed). m2-slice's moved Haluna scenes use the same kit, so their haluna shots will match these baselines once both land.
- `haluna_h10_dock_night` (m2-slice's ENV-02) isn't on the integration branch yet, so it wasn't re-captured here; it uses the same kit stone and will drift a little when both land. I'll re-capture it after the integration merge.

## Swap-in notes for m2-slice
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
Merge each worktree agent's branch as it reports (ENV-10, ENV-03, ENV-07), gate it, push. Meanwhile: ENV-06 pass 2 (stilt-house wall frame in village.py, a look at the dock and props), then queue item 5.

## Queue
1. M2-ENV-03: Shell Shrine interior kit (agent)
2. M1-ENV-10: LOD chain in the kit dresser and import rules (agent)
3. M2-ENV-06: Haluna kit to final quality (pass 1 done; pass 2 next) + M2-ENV-07 trees (agent)
4. ~~Art sign-offs M2-ART-01/02/03~~ (done)
5. The slice's one route (village → causeway head) at final quality; greybox flagged by the m2-slice playthrough

## History
- 2026-10-24: M2-ENV-06 pass 1 (6436775). Gates: verify_blender_builds haluna_kit 31 identical; Godot environment 11, haluna 13, post_import 17; validate_data; taskboard --check; the five haluna shots captured, viewed and re-approved.
- 2026-10-24: merged the Art sign-offs (3c3fa19, aa3b4ca, f067ba4). Gates: validate_data, taskboard --check, palette.json parses (docs only, no Godot run).
- 2026-10-24: set up the branch and toolchain; claimed the queue's tasks.
