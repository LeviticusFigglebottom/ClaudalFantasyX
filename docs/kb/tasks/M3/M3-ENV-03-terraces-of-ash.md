---
id: M3-ENV-03
title: Ch5 Terraces of Ash: Pemakar town, the terrace channels and graves, the Lanternfall festival (kit at final quality)
role: environment
status: review
owner_session: worktree-agent-a47682c2eedaa8e26
depends_on: [M2-ENV-06]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The Lead's env-art standing queue (2026-10-24; the human authorised M3 work in parallel): Ch5 "Terraces of Ash" from
docs/kb/story/beats/act_outline.md, zone `ch05/pemakar`. Pemakar, a terraced town on a stair-mountain under an ash-plume: terrace channels among the graves carrying a thousand leaf-boats at Lanternfall (pillar 2: beauty in decline), copper veins in the rock (the temple trial walks a strike down them; Ashcrown temple itself is a later task), a smithy (the side scene), volcanic stone and ash palette (`volcanic_stone`, `laterite`).

Gameplay placement (spawns, triggers, NPCs, collision tuning) is m2-slice's: hand it over as swap-in notes in
docs/kb/handoffs/live/env-art.md.

## Acceptance criteria
- [x] **Design notes first:** `docs/kb/art/environments/<zone>.md` in the haluna.md format (mood in one line,
      layout and orientation, lighting sub-frame and grade from color_script.md, kit table with dimensions,
      materials against palette.json, composed shot list with lenses), reviewed against the act outline and the
      story bible before any geometry; references in words only (references.md).
- [x] A procedural kit in `assets_src/environments/kits/<zone>/` with its own Blender job, LOD0/LOD1 within
      budgets and chained per vegetation.md "One LOD at every distance", vertex-colour weathering per haluna.md
      §4, materials written by script, PROVENANCE rows, `verify_blender_builds` byte-identical, every file under
      5 MB, no reference images, packs or AI generation.
- [x] An Environment-owned preview scene with composed views of the design notes' key shots, viewed on lavapipe
      and iterated to final quality (pillar 2, the palette, the colour script). Register at most the two most
      telling shots as screenshot baselines (the repo's binary budget).
- [x] Tests for anything with runtime code; a swap-in note for m2-slice.

## Notes
- 2026-10-24 (env-art): **PAUSED for the M2-review blockers (Lead), WIP committed.** Done: design notes
  `docs/kb/art/environments/pemakar.md` (committed first); kit source `assets_src/environments/kits/pemakar/`
  (25 pieces in budget: terraces, walls with copper vein, channels/inlets/spills with cross channels, paddy,
  stair, graves, open-hand gate, lamp pillar, leaf-boat, shrine-box, two houses, smithy, massif, Ashcrown
  silhouette, plume; textures, materials, import settings, layout generator writing ~940 boats / 376 lamps /
  5,000 far lights); preview scene `game/levels/_tests/pemakar_kit/` (PemakarKitPreview, dusk/night moods,
  7 cameras, shots manifest); shaders env_ash_plume, env_far_lights, env_sky_pemakar.
  **Not committed:** the generated assets under `assets/environments/kits/pemakar/` (no PROVENANCE rows yet;
  regenerate with build.py via Blender, pemakar_textures.py, pemakar_materials.py, pemakar_import_settings.py,
  then `godot --import`). No Blender job, no tests, no shots registered yet.
  **Next step:** (1) rework P01 as the view from the harbour looking north (sea-glow foreground, town lights,
  mountain far lights, Ashcrown, plume; ~50 mm, camera about (-20, 6, 130)) and update pemakar.md §5 to match;
  (2) plume: darker (fog_disabled, body_darken ~0.2), lumpier silhouette, afterglow rim; (3) far lights spread
  lower and thinner near the crest; (4) render P05-P08 and iterate; (5) add the `pemakar_kit` Blender job to
  tools/dev/blender_builds.json (sources: pemakar/*.py + haluna kit_common.py, village.py, shrine_interior.py),
  commit assets + PROVENANCE rows, Python tests (tools/tests/test_pemakar_kit.py) and a GDScript test for
  PemakarKitPreview; request a `pemakar_kit` import kind from Tools; register at most 2 shots (P01, P03).
  P03 (dusk, among the graves) already reads well on lavapipe.
- 2026-10-24 (env-art, worktree-agent-a47682c2eedaa8e26): **resumed and finished; ready for Rendering review.**
  Merged the paused WIP, then: generated and committed the 25 pieces (`assets/environments/kits/pemakar/`,
  LOD0 + chained LOD1 in budget, kit manifest, 8 maps, 27 script-written materials, 61 PROVENANCE rows, all
  files under 1.1 MB); the `pemakar_kit` Blender job (4 threads, textures and materials steps verified too;
  `verify_blender_builds --job pemakar_kit`: 61 identical); a `pemakar_kit` import kind
  (`game/data/import/pemakar_kit.json` + `game/core/import/pemakar_kit_post_import.gd`, a copy of the Brine
  Shoals kind with the LOD end at 4,000 m for the skyline; every `.glb.import` points at it; Character +
  Tools sign-off noted in ownership.md). Kit fixes found on lavapipe: the massif cut a trench across the
  face behind the town (the tier rings were full circles) and bulged through the treads in front of each
  wall (now a full tier under the kit's treads); Ashcrown carried an unused slot. Preview iterated to final
  (see pemakar.md Revisions): P01 turned round to the harbour view looking north, with the pilgrims' stair,
  the sea road and the boats on the sea; plume fog-free, darker, lumpier, ember vent and a dusk rim; far
  lights thinner toward the crest; fewer stars; graves turned toward the path; lights for P06-P08 and a
  clear P08. Tests: `tools/tests/test_pemakar_kit.py` (19) and `tests/unit/test_pemakar_kit_preview.gd` (5).
  Baselines: `pemakar_p01_waterfall_of_fires` (night) and `pemakar_p03_among_the_graves` (dusk), both
  re-captured identical (rmse 0). Not built: `stair_cascade` (see pemakar.md Revisions). P02 and P05-P07 are
  composed and lit but not registered; P05's flame reads as a white cone at 100 mm and P06's falling sheet
  is faint at night (Rendering may want to look at both).
  **Review request (Rendering):** the two baselines against pemakar.md §0 and §6 (value order: flames > lit
  stone > sea-glow > sky and plume > shadow; volcanic stone neutral-cool; no glimmer on screen), and the
  plume shader (`game/shaders/environment/env_ash_plume.gdshader`: `fog_disabled`, the dusk rim from
  `hymn_sun_direction`).

## Swap-in note for m2-slice (zone `ch05/pemakar`, `game/levels/ch05/pemakar/`, not built yet)
- **Source of placements:** `game/levels/_tests/pemakar_kit/pemakar_preview_layout.json` (generated by
  `assets_src/environments/kits/pemakar/pemakar_layout.py`): explicit transforms for 1,113 pieces, 943 boats,
  388 lamps (`#FFA757`, energy and range per entry), far lights, sea lights and 35 frangipani. Copy the entries
  into the zone layout; do **not** instance or reference the preview scene or `PemakarKitPreview` from shipped
  files (`game/levels/_tests/` is excluded from release, test_release_excludes_tests). The preview script is
  the reference for dressing (slot materials per `materials` override, `LodChain` with LOD1 from 70 m to
  4,000 m, one MultiMesh for the boats, billboard MultiMeshes for the far and sea lights with
  `env_far_lights`); ask Environment to promote a `PemakarDresser` into `game/levels/ch05/pemakar/` if you
  want one. The kit .glbs import with their materials already (pemakar_kit import kind).
- **Anchors (metres; origin at the town's foot at sea level, +X east, -Z north toward the crown):** tier t
  (0-9) has its tread at y = 8.0 + 2.4 t, its tread front on an arc of radius 150 - 7 t about (0, -150), 7 m
  deep, rising 0.14 m to the back. Kinds bottom to top: market, house, house, paddy, cemetery, cemetery,
  paddy, cemetery, cemetery, cemetery. Main stair at x = 0 from (0, 8, 0) to the top tread (0, 29.6, -63);
  open-hand gates at the stair heads of tiers 4, 5, 7, 8, 9 ((0, 17.6, -30.1) ... (0, 29.6, -65.1)). Smithy
  (side scene): (22.8, 8.0, -5.6), yaw 9 deg, open side facing downhill; forge light at its back left.
  Copper vein: a `terrace_wall_copper` module at x of about 14 on every tier (the temple trial's strike path
  down the town), the outcrop on tier 1 at (17.3, 10.45, -13.7). Kerrid's spot (P04, not built): the east
  end of a cemetery tier where the lamps stop, e.g. tier 8 at about (41, 27.2, -64). Sea road along the
  shore at z of about 18, y of about 3; the bottom tier spills to it at (-39.3, 8.0, -5.2). Ashcrown on the
  rim at (0, 306.7, -682); the plume vent at (0, 250, -760).
- **Collision:** the kit exports no `-col` proxies (the import rule would build trimesh bodies if they
  appear; Environment can add them on request). Walk surfaces: the tread and paddy tops, the stair flights
  (12 risers of 0.2 m); retaining walls (2.4 m) are blockers; channel kerbs stand 0.15 m (step-over),
  paddies are knee-deep water behind 0.25 m bunds. Suggested: trimesh from the LOD1 meshes of
  `terrace_tread_4m`, `paddy_tread_4m`, `terrace_wall*`, `stair_flight` (8-400 triangles each), boxes for
  graves, gates, lamp pillars, houses and smithy posts. The massif is not a walk surface inside the town:
  it sits a full tier (3.3 m) under the kit's treads for |x| < 47 m and continues the tier shapes on the
  flanks beyond.

## Review log
