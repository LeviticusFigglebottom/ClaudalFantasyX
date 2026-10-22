# Procedural Vegetation (M1-ENV-02)

Owner: Environment. Reviewer: Rendering. This covers the coconut palm, frangipani, saltgrass, and beach vine generators, the wind and foliage shaders, and the test scene. Every mesh and texture here is generated from math in the repo (SPEC §2, ADR 0005). No image, mesh, or texture was sampled from anywhere.

| What | Where |
|---|---|
| Generators (Python, numpy) | `assets_src/environments/vegetation/` (`palm.py`, `frangipani.py`, `saltgrass.py`, `beach_vine.py`, `veg_common.py`) |
| Blender entry point | `assets_src/environments/vegetation/build.py` |
| Textures (plain python3) | `assets_src/environments/vegetation/textures.py` |
| Godot import settings | `assets_src/environments/vegetation/import_settings.py` |
| Outputs | `assets/environments/vegetation/*.glb`, `*.png`, `materials/*.tres` |
| Shaders | `game/shaders/vegetation/` (`vegetation_wind.gdshaderinc`, `vegetation_foliage_body.gdshaderinc`, `vegetation_foliage.gdshader`, `vegetation_foliage_low.gdshader`, `vegetation_bark.gdshader`) |
| Runtime helpers | `game/levels/_tests/vegetation/vegetation_plant.gd` (materials + LODs), `vegetation_scatter.gd` (MultiMesh) |
| Test scene | `game/levels/_tests/vegetation/vegetation_test.tscn` (shots `veg_backlit_fronds`, `veg_frangipani_close`, `veg_beach_wide`) |
| Tests | `tools/tests/test_vegetation.py` |

## Rebuilding

```bash
python3 assets_src/environments/vegetation/textures.py                 # all PNGs (~20 s)
~/.cache/hymn/blender-5.0.1+dfsg-5/blender --background --factory-startup \
  --python assets_src/environments/vegetation/build.py -- --all --out-dir assets/environments/vegetation   # ~4 s
python3 assets_src/environments/vegetation/build.py --dry-run --all     # geometry + budgets, no Blender
godot --headless --path . --import                                      # first time only: creates .import files
python3 assets_src/environments/vegetation/import_settings.py && godot --headless --path . --import
```

Both steps are deterministic. A rebuild is byte-identical, which was checked with md5 over every `.glb` and `.png`. Each generator draws all its random choices from `numpy.random.default_rng(SeedSequence([seed, species salt]))` in a fixed order. `import_settings.py` exists because headless imports never run the editor's "detect 3D" pass. Without it the PNGs would import without mipmaps, and each `.glb` would get automatic LODs on top of the authored ones. It sets VRAM compression and mipmaps on, turns normal-map (RGTC) compression off for `*_normal.png`, because B carries the translucency mask, and turns `generate_lods` off.

## Parameters

Every generator has a `VARIANTS` dict (seeded parameters), a `LODS` list (tessellation per LOD), and a `TRI_BUDGET` list.

| Species | Parameters (per variant) | Variants shipped |
|---|---|---|
| Coconut palm | `seed`, `height` (m), `lean_deg`, `curve` (how far the trunk bends back towards vertical, 0..1), `fronds`, `dead` (hanging brown fronds), `nuts` | `a` 12.5 m / 17°, `b` 15.5 m / 9°, `c` 9.5 m / 24° |
| Frangipani | `seed`, `iterations` (L-system depth), `trunk_m`, `internode_m`, `decay` (internode shrink per depth), `spread_deg` (fork angle), `tropism` (upturn), `flower_p`, `leaves` (min, max per rosette), `blooms` (per spray) | `a` 4.0 m dense garden tree (51 tips), `b` 3.3 m open (19 tips) |
| Saltgrass | `seed`, `cards`, `height` (min, max m), `lean_deg` (min, max), `radius` | `saltgrass_a` tall 0.55–0.8 m, `saltgrass_b` short 0.3–0.45 m |
| Beach vine | `seed`, `runners`, `length` (min, max m), `spacing` | one 2–5 m patch |

- **Palm.** A curved trunk with a basal flare and leaf-base swelling. Fronds follow a golden-angle spiral, and their age sets elevation (16° young to 96° old), length, droop, and leaflet hang (the V angle). A frond is a rachis tube plus two leaflet wings as alpha cards whose cross-section bends down (3 columns at LOD0). A fibrous sheath "boot" sits at the crown. Coconuts hang in 2–3 bunches. Brief: 8–22 m, leaning seaward 5–25° (lean is +X in the asset, so yaw the instance towards the sea), with dead fronds. These are hanging fronds (2–4 per palm), not a 15% texture share.
- **Frangipani.** A stochastic parametric L-system. The rules are in the docstring of `frangipani.py`: fork in two (p 0.55), fork in three (0.30), or keep growing (0.15). Branches turn upward (tropism), and radii follow the pipe model with each internode tapering into its thickest child. Every tip gets a spiral rosette of 12–25 leaf cards, and most tips get a spray of 5–13 cupped five-petal flower cards on a stalk, plus a crossed bud card. LOD0 also scatters nine fallen flowers on the ground (wind weight 0).
- **Saltgrass.** A clump is a fan of curved alpha cards, each carrying 18–22 painted blades. Normals are bent "up and out of the clump", so a clump shades as one soft mass. Scatter it with `VegetationScatter`.
- **Beach vine.** Runners lie flat on the sand. Two-lobed leaf cards stand on short petioles, and magenta funnel flowers appear at about 6%.

## Adding a species

1. Write `assets_src/environments/vegetation/<species>.py` with `VARIANTS`, `LODS`, `TRI_BUDGET`, and `build(...) -> list[MeshBuilder]`. Name LOD meshes `<name>`, `<name>-lod1`, and so on. Use `veg_common.tube` / `ellipsoid` / `MeshBuilder.add_grid`, and write all four wind channels plus UV2 (see below). One `MeshBuilder.material(name)` per material slot.
2. If it needs a texture, add an atlas layout to `veg_common.py` and a painter to `textures.py` (`BUILDERS`). Keep textures 1K maximum, sRGB albedo with the cut-out in A, and normal XY in RG with translucency in B. Stay inside the albedo floor/ceiling (`#1D1916`–`#EBE7DF`).
3. Register the target in `build.py::targets()`. The unit test picks it up automatically for budgets, determinism, and committed-file checks.
4. Make `assets/environments/vegetation/materials/<slot>.tres` (a ShaderMaterial on `vegetation_foliage.gdshader` or `vegetation_bark.gdshader`). **The primary-sway uniforms (`wind_response`, `plant_height_m`, `sway_lean`, `sway_amplitude`, `sway_frequency_hz`, `gust_contrast`) must be identical on every material of one plant**, or trunk and crown will separate in the wind.
5. Run the build, run `import_settings.py`, and re-import. Append PROVENANCE rows (append only).

## Wind conventions (vertex colour + UV2)

The art README's packing rule for stone is "R moss, G salt, B wet, A erosion". Vegetation uses the same RGBA-weights idea with its own meaning:

| Channel | Meaning | Range | Palm | Frangipani | Saltgrass |
|---|---|---|---|---|---|
| `COLOR.r` | **primary sway**: whole-plant bend downwind about the root, length-preserving | 0 root .. 1 most bent | trunk `t^1.6`, crown and fronds 1 | `(z/H)^1.6` | `h^1.5` |
| `COLOR.g` | **secondary bend**: each frond, branch, or blade bobs on its own phase | 0 base .. 1 tip | `(s/L)^1.5` along each frond | continuous along each limb (0 at the trunk top, ≤ 0.35), leaves `0.25 + 0.75·t` | `h` |
| `COLOR.b` | **element phase** | 0..1 random | per frond | per limb (shared so forks never tear), per leaf | per card |
| `COLOR.a` | **flutter**: fast, small, along the normal | 0 rib .. 1 edge | 0 at the rachis, 1 at leaflet tips | leaf edges and tips | `h` |
| `UV2.x` | baked occlusion | 1 open .. 0 deep | inner and young fronds darker | rosettes lower in the crown darker | base of the clump |
| `UV2.y` | tint variation (foliage) / height fraction (bark) | 0..1 | per frond / trunk height | per leaf, near 0 on petals / height | per card |

- **Per-instance phase** = `hymn_hash12(instance origin.xz)` + the `inst_wind_phase` instance uniform. This works for MultiMesh too, because `world_vertex_coords` gives instance-transformed positions.
- **Inputs.** `hymn_wind` (xyz = downwind direction × m/s, w = gust 0..1) and `hymn_wind_time` (s). Nothing reads `TIME`. A gust field (2-octave fBm) travels downwind at wind speed, with an 18 m wavelength, so gusts roll across the grass. The reference wind is 6 m/s, the Haluna trade wind, at which `wind_response` is reached.
- **Captures are deterministic.** `VegetationTestScene` pins `hymn_wind = (-5, 0, -2.4, 0.6)` (onshore) and `hymn_wind_time = 7.4` on enter, and restores the project defaults on exit. `animate_wind = true` lets it run.
- **Screenshot thresholds.** The three `veg_*` shots use `threshold_rmse` 0.018, not 0.008. A full `capture.sh` run is bit-exact (RMSE 0.00000). But the TAA jitter phase depends on the global frame count, so capturing these shots alone or in a different order shifts every alpha-scissored edge, giving RMSE 0.010–0.015. The baselines come from the full-manifest order. Re-approve them if a shot is inserted *before* them in `shots.json`.
- **Verified.** Rendering `dbg_palm_side` at `wind_time` 7.4 and 9.9 changed 14% of pixels (the crowns sway and stay attached to the trunk).

## Shaders and tiers

- `vegetation_foliage.gdshader` (default tier, used by High, Ultra and Medium). Two-sided (`cull_disabled`; Godot flips back-face normals). Alpha scissor with a per-mip coverage boost (`mip_coverage_boost`), so distant cards don't thin out. TAA (the project default) smooths the scissor edge. It also has a **custom `light()`**: wrapped diffuse, GGX specular, and a transmission term (back-light + a forward-scatter lobe, `translucency_focus`, towards the sun). The transmission is attenuated with a floor (`translucency_shadow_floor`), not killed by the shadow map. Godot's built-in BACKLIGHT is multiplied by the full shadow attenuation, so any leaf under another leaf stayed dark: the first "backlit" render was pale and flat. The transmission tint is `col_translucency` for saturated texels and white for pale ones, so petals don't go green. Undersides are paler (`underside_lighten`).
- `vegetation_foliage_low.gdshader` (`HYMN_QUALITY_LOW`). No transmission, no secondary bob, no flutter: primary sway only.
- `vegetation_bark.gdshader`. Tiling albedo and normal, a root-to-top tint over UV2.y, UV2.x occlusion, and the same wind include. Bark has no flutter weight, so one tier serves all.
- **Alpha-to-coverage is not used.** It needs MSAA, and no preset enables MSAA (`graphics_presets.json` uses FXAA, TAA, or FSR2).
- **Not done yet: mapping preset → variant.** `graphics_presets.json` (Rendering) should point the Low preset at `vegetation_foliage_low.gdshader`. Until then, swap `ShaderMaterial.shader` at load. Both variants pass the headless compile check (`vegetation_shader_check.gd`, run by the unit test).

## LODs

LODs are authored meshes (`-lodN`). `VegetationPlant` turns them into `visibility_range` LODs, with ends at 45 m / 120 m / 400 m by default, a 2 m hysteresis margin, and no fade (deterministic captures). `force_lod` pins one LOD for debugging. Godot's automatic LOD generation is off for these files. MultiMesh grass is one LOD per scatter node (use a second node with `saltgrass_*-lod1` for far bands).

`VegetationPlant` is a runtime stopgap. When M1-ART-02 lands, its material map and LOD setup should move into `game/core/import/vegetation_post_import.gd` unchanged.

## Budgets (triangles; enforced by `build.py` and the unit test)

| Asset | LOD0 | LOD1 | LOD2 | Budget (LOD0/1/2) | .glb size |
|---|---|---|---|---|---|
| palm_coconut_a | 9,624 | 2,788 | 456 | 11,500 / 3,400 / 900 | 0.71 MB |
| palm_coconut_b | 10,392 | 3,040 | 480 | | 0.76 MB |
| palm_coconut_c | 8,280 | 2,364 | 408 | | 0.61 MB |
| frangipani_a | 15,996 | 5,008 | 1,327 | 16,000 / 5,200 / 2,000 | 1.67 MB |
| frangipani_b | 7,934 | 2,260 | 575 | | 0.82 MB |
| saltgrass_a / _b | 84 / 72 | 18 / 16 | — | 120 / 24 | 24 KB (both) |
| beach_vine_patch | 708 | 414 | — | 3,000 / 900 | 0.11 MB |

Textures are 1K maximum. The palm frond atlas is 1024², palm bark 512×1024 (tiles every 1.6 m), the frangipani leaf/flower atlas 1024², frangipani bark 512², and saltgrass and beach vine 512². Their PNGs total about 3.5 MB, and no file exceeds 1 MB. Normal maps are **8-bit**, not the 16-bit that ADR 0005 suggests: foliage normals are low-amplitude detail, and 16-bit would roughly double the size for no visible gain. Promote them if a hero needs it.

The test scene holds 6 palms, 2 frangipani, 3 vine patches, and about 1,100 MultiMesh grass clumps. A 960×540 frame takes 1.8–3 s on lavapipe (4 vCPU, shared). The GPU cost is unmeasured. Expect alpha-tested overdraw in dense crowns to dominate, not triangle count.

## Honest quality assessment

What works:
- **Silhouettes read as the right plants.** At wide and middle distance, the palms read as coconut palms: curved leaning trunks, arching fronds with hanging leaflet curtains, hanging dead fronds, and nuts. Their shadows on the sand (`veg_beach_wide`) look right. Frangipani `a` reads as a flowering Plumeria dome with blunt candelabra branches. The saltgrass reads as tussocky beach grass in drifts.
- **Backlighting.** Since the custom transmission term, a crown seen against the sun glows yellow-green with dark rachises, and the sun disk flares through gaps.
- **Close-ups.** Frangipani leaves (veins, quilting, glossy face, paler underside) and the cream flowers with yolk-yellow throats hold up at about 1 m.

What is weak (about 55–65% of a shipped AAA tropical set):
- **From directly below, the palm crown is too regular.** Fronds radiate like a star, and leaflets are evenly combed. Real crowns are messier: torn leaflets, fronds crossing each other, uneven ages. The geometry has no twisted or broken fronds, and nothing yellowing.
- **The wing cards read as cards** at grazing angles near the crown centre. There are no leaflet-level geometric silhouettes at LOD0.
- **Frangipani bark is too smooth and uniform** (it looks like a grey pipe in shade). The forks have no branch collars. The tips are capped with flat-ish cones. Flowers face only upward-ish, so side views show slivers.
- **Saltgrass is one colour family**, with no seed heads and no ground debris. The clump fans can show their radial structure from above.
- **Not built:** windbreak tree, screw-pine, sea hibiscus, hero banyan, seagrass, mangrove (later tasks). No impostors or billboards for more than 400 m. No wind interaction with characters. No collision meshes. No `PLACEHOLDER` metadata needed: the assets are final-intent, but expect a revision pass.
- **Unverified on GPU:** cost, alpha-scissor shimmer under motion, and the shadow-acne settings. Lavapipe only.
