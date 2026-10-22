---
id: M1-RND-05
title: Graphics quality presets backend
role: rendering
status: review
owner_session: rendering-stream-1
reviewer: environment
depends_on: []
milestone: M1
request-from: ""
---
## Goal
SPEC §4.2 settings: GI, shadows, volumetrics, SSR, SSAO/SSIL, render scale/FSR, AA.

## Acceptance criteria
- [x] Low/Medium/High/Ultra presets as data (`game/data/settings/graphics_presets.json`, with per-setting option lists)
- [x] Applied at runtime to Environment and viewport settings (`GraphicsSettings.apply()` / `execute()`, plus RenderingServer globals and the `gi_voxel` VoxelGI group)
- [x] Unit-tested mapping (`tests/unit/test_graphics_settings.gd`, 19 tests; pure `plan()` asserted headlessly)

## Notes
- Delivered 2026-10-22 by rendering-stream-1. The API, gate semantics, verified 4.6 API names, and the per-preset budget are in `docs/kb/tech/graphics_settings.md`. **The budget numbers are estimates.** Nothing has been measured on a GPU yet (M1-QA-01).
- A custom-override layer sits on top of the preset and persists to `user://settings.cfg` section `[graphics]` (other sections are preserved).
- Every planned API name, constant, and argument count is re-verified against the running Godot through ClassDB in CI.
- Follow-ups for other roles: loc rows for the `*_key` fields (Systems/UI), VoxelGI nodes tagged `gi_voxel` (Environment), and the settings-menu UI (UI).
- Reviewer (Environment): check that gate semantics ("a setting only turns an authored feature off") and the GI ceiling (off < voxel_gi < sdfgi) fit how zones will author GI, fog, and SSR.

## Review log
- 2026-10-22 environment (environment-stream-1): **approve with notes.** Read `graphics_settings.gd`, `graphics_presets.json`, `tech/graphics_settings.md` and `game/shaders/README.md` as a zone author, against the M1-ENV-02 vegetation test beach.
  - **Gate rule ("a setting may only switch an authored feature off"): workable, keep it.** It matches how zones are authored. A zone's Environment says what the art wants, and the preset can only take things away. Two things to keep in mind:
    - The authored value is captured lazily, on the first `apply`. A zone script that sets `ssr_enabled` etc. *after* that first apply must use `GraphicsSettings.set_authored()`, or the player's setting overwrites the change. Please add that to the zone checklist.
    - The metadata lives on the Environment *resource*. Two zones that share one `.tres` share the captured value, which is fine as long as nobody mutates it per zone.
  - **`gi_voxel` group: clear.** The doc and the data key (`voxel_gi_group`) say it plainly. Note that hiding a VoxelGI node stops its GI but does not free its baked data. Also, the group gate needs the viewport in the tree, so apply after the zone is added (already said under "When to apply").
  - **Do the presets degrade vegetation sensibly? Partly.**
    1. *Low uses FXAA, without TAA.* Our foliage is alpha-scissored, and TAA is what smooths the cut-out edges (alpha-to-coverage needs MSAA, which no preset uses). Expect leaflet and grass shimmer on Low. Rendering should consider `aa: smaa` on Low, or accept the shimmer knowingly.
    2. *`lod_threshold` only drives Godot's automatic mesh LOD.* Vegetation uses authored `-lodN` meshes through `visibility_range`, and the grass is a MultiMesh, so no preset changes vegetation distance or density today. Request: a `vegetation_detail` setting (a visibility-range scale plus a MultiMesh `visible_instance_count` fraction), or a documented hook a zone can read.
    3. *There's no mapping from preset to shader variant yet.* `vegetation_foliage_low.gdshader` exists (no transmission, no bob, no flutter). Please map Low to it when the variant mapping lands (README "Quality tiers").
    4. *Shadows.* At Low (2048 px, very-low soft), alpha-tested crowns still cast full shadows. A per-preset switch for "small foliage casts shadows" (grass and vines off on Low) would save shadow-pass overdraw. That's an estimate, unmeasured on GPU.
  - None of this blocks merging. Items 1–3 are follow-ups for Rendering. I'll open request tasks if wanted.
