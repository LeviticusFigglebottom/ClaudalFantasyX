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
| Broadleaf trees (M2-ENV-07) | `banyan.py`, `windbreak.py`, `canopy.py` (shared crown helpers); exported as Haluna kit pieces by `assets_src/environments/kits/haluna/trees.py` (job `haluna_kit`); tests `tools/tests/test_broadleaf_trees.py`. See "Broadleaf trees" below. |

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

LODs are authored meshes (`-lodN`). `VegetationPlant` turns them into `visibility_range` LODs, switching at 45 m / 120 m and ending at 400 m by default. The 45 m switch is hard, with a 2 m hysteresis (`lod_margin_m`).

**One LOD at every distance (M1-ENV-08/09).** Each LOD is the `visibility_parent` child of the next LOD in its chain (`<base>-lodN` → `<base>-lodN+1`). Godot draws a child only while its parent is hidden for being too close, so one range check, the parent's begin, decides each switch. The hysteresis sits on that begin margin alone. Before this, each LOD ran its own range check with its own hysteresis state, and Godot's margins widen the range of an instance that was drawn last frame and narrow it for one that wasn't. A plant first seen within 2 m of a switch from a still camera drew no LOD at all (44–47 m in the probe below), and the faded last LOD (no begin hysteresis) left a 118–120 m hole moving in and a 120–122 m double draw moving out. A child's own end is only a loose bound halfway into its parent's span, and it matters only while the parent passes its children through during the parent's own fade.

**Final fade (M1-ENV-03):** only the last LOD fades. It fades out over 400 ± `lod_fade_m` (394–406 m, measured), so a palm doesn't pop off against the sky, and it crossfades in over 120 ± `lod_margin_m` (118–122 m) on top of the opaque LOD1, which stays drawn underneath. `lod_fade_m` 0 turns both fades off, and the 120 m switch then gets the plain hysteresis.

- **Don't fade the inner switches.** Godot's `VISIBILITY_RANGE_FADE_SELF` alpha-blends the whole instance; it isn't a dither. A fade at the 45 m or 120 m switch on its own made opaque trunks translucent (review-sweep-N). The 120 m crossfade is safe because LOD1 stays opaque under it.
- **Check on a renderer:** `godot-render --path . --rendering-driver vulkan -s res://game/levels/_tests/vegetation/lod_sweep_probe.gd` reads back three coloured probe LODs at 40–50, 114–126 and 390–410 m in 0.5 m steps, from a still camera and sweeping in and out. It prints `LOD_SWEEP PASS`; the pre-fix setup failed 16 rows. `tests/unit/test_vegetation_plant.gd` models Godot's range check as measured there and sweeps 0.5–390 m in 0.25 m steps.
- `force_lod` pins one LOD for debugging, and drops the chain.

**Shelter (M1-ENV-03).** `translucency_shadow_floor` (0.35) lets leaves transmit light where the shadow map says occluded, because the occluder is usually the plant's own canopy. Under an eave that made plants glow. `VegetationPlant.shelter` (AUTO by default) casts one ray from 80 % of the plant's height toward the sun after placement. The sun direction is the `hymn_sun_direction` global, read back through `ShaderGlobals`. If the ray hits a collider on `shelter_mask` (physics layers, default 1; put the static world there), the plant counts as sheltered, and the instance uniform `inst_translucency_shelter` = 1 turns the floor off. Set `shelter` to OPEN or SHELTERED to override it. The ray needs collision on the building (the Haluna kit has none yet, so its plants stay at 0 until then).

**Re-probe when the sun moves (M1-ENV-09).** An AUTO plant joins `ShaderGlobals.LISTENERS_GROUP`. When `ShaderGlobals.set_value` or `reset` changes `hymn_sun_direction` by more than `SHELTER_REPROBE_DEG` (0.5°) from the sun the plant last probed, the plant probes again on the next physics frame. Requests within one frame coalesce, so a time-of-day sweep costs one ray per plant per half degree. Write and restore the sun only through `ShaderGlobals` (`set_value`, and `reset(name)` to put back the project.godot default). A direct `RenderingServer.global_shader_parameter_set` leaves ShaderGlobals' copy stale and the plants unaware. `ShaderGlobals.get_value` falls back to the project.godot default for a global nobody has written.

On the GPU (`tools/gpu_bench/eave_glow.tscn`, a roof over a frangipani) the floor's glow under the roof averaged 0.013 linear luminance (p99 0.23, max 0.37). Sheltered, it's gone. Shelter is per plant, so a crown that pokes out past a roof edge loses the floor there too. Godot's automatic LOD generation is off for these files. MultiMesh grass is one LOD per scatter node (use a second node with `saltgrass_*-lod1` for far bands).

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
| hero banyan (`banyan_placeholder`, Haluna kit) | 59,949 | 6,999 | — | 60,000 / 10,000 | 3.4 MB |
| windbreak tree (`windbreak_placeholder`, Haluna kit) | 5,785 | 430 | — | 6,500 / 1,000 | 0.42 MB |

Textures are 1K maximum. The palm frond atlas is 1024², palm bark 512×1024 (tiles every 1.6 m), the frangipani leaf/flower atlas 1024², frangipani bark 512², and saltgrass and beach vine 512². Their PNGs total about 3.5 MB, and no file exceeds 1 MB. Normal maps are **8-bit**, not the 16-bit that ADR 0005 suggests: foliage normals are low-amplitude detail, and 16-bit would roughly double the size for no visible gain. Promote them if a hero needs it.

The test scene holds 6 palms, 2 frangipani, 3 vine patches, and about 1,100 MultiMesh grass clumps. A 960×540 frame takes 1.8–3 s on lavapipe (4 vCPU, shared).

**On the GPU** (RX 9070 XT, 1440p), the whole test scene costs 0.94–0.98 ms (Low) and 1.56–1.60 ms (High) on Wide, and 0.65 / 1.27 ms on Backlit.

**Overdraw budget (M1-ENV-03).** Measured with `gpu_bench --debug-draw=overdraw`, 1080p High, in layers per pixel, calibrated on the single-layer sand plane:

| View | Frame mean | Covered-pixel mean | p95 | p99 | max |
|---|---:|---:|---:|---:|---:|
| Wide | 1.64 | 3.0 | 7.9 | 11.9 | 16.4 |
| Backlit | 0.50 | 2.1 | 3.4 | 4.6 | 8.1 |
| FrangipaniClose | 4.36 | 5.0 | 10.0 | 11.9 | 15.3 |

The budget per view is:
- **Field and wide views:** frame mean ≤ 2.5 layers, p99 ≤ 12.
- **Close-ups:** frame mean ≤ 5, p99 ≤ 14.

The dense layers are the near salt-grass clumps (8–16 layers). Thin those first, or use the `vegetation_detail` MultiMesh fraction, before cutting crown cards.

**Wind flutter and TAA.** `flutter_amplitude_m` 0.02 at 3.5 Hz is the cap for TAA presets. Measured at a fixed 30 fps on Low (M1-RND-15, `docs/kb/qa/gpu/2026-10-23-rnd-15-prewarm.md`), TAA with the wind on departs from the instant 30–40 % more than its static softening: soft blades and faint double edges, with no trails. Raise the flutter only together with a ghosting re-measure (`aa_shimmer --wind` plus `aa_shimmer.py --ghost`).

## Broadleaf trees (M2-ENV-07): the hero banyan and the windbreak tree

Both are grown by vegetation generators in this folder and exported as Haluna kit pieces, so the Haluna dresser places them with no layout or scene change. `assets_src/environments/kits/haluna/trees.py` replaced the old `placeholders.py`. It converts the vegetation frame (+Z up) to the kit's (+Y up) and renames the material slots to kit materials. **The piece names `banyan_placeholder` and `windbreak_placeholder` are kept** because they are the scene contract: `haluna_layout.json`, the zone's collision table in `haluna.tscn`, and `test_haluna_zone.gd` all name them. They are no longer placeholders: they have no PLACEHOLDER extras and no manifest tag. Renaming them is a layout change for the zone's owners.

- **Structure.** Each tree is grown once, with every random draw made in a fixed order (`make_tree`), and then meshed per LOD with no further randomness, so LOD0 and LOD1 are the same tree. Rebuilds are byte-identical (`verify_blender_builds --job haluna_kit`).
- **Hero banyan** (`banyan.py`, variant `hero`, 14 m tall, about 25 m across):
  - The trunk is seven twisted stems fused round a core column, with seven buttress flanges (tall, thin elliptical sections that stand on the sand). Each flange runs on as a half-buried surface root, and more surface roots run out between them.
  - Seven near-horizontal limbs sag and then curl up. Branches rise alternately from each limb to 41 leaf clumps.
  - Each clump is a flattened ellipsoid of twig clusters: branchlets, then a twig per cluster, then 2–4 leaf sprays per cluster (2,682 sprays in all). The underside is sparser and darker, so you look *up into* a crown.
  - It has 23 prop-root strands: one to three twisted strands per pillar, flared at the foot and where they leave the limb. It also has 329 hanging aerial-root strands in braided bunches, and a few long ones reach the ground.
  - **Art direction for H07.** `hero_limbs` fixes two great limbs (asset azimuths 180° and 106°) that reach either side of the chapel court. At yaw 30 in Haluna, the court lies at asset azimuth ~135°. The 180° limb runs low, at about 4.75 m, with three small leaf clumps on it, so it arches across the top of H07. Its root curtains hang between the two prop pillars that bracket the chapel. The `path` capsule is the walk from the lane to the chapel door. The village keeps it clear: no prop root stands in it, and hanging roots over it are cut at 2.4 m (`path_cut_m`).
- **Windbreak tree** (`windbreak.py`, variant `a`, 8 m tall, 4.2 m across). This is an original thick-leaved coastal evergreen. A short, stout trunk forks at about 1.6 m into three upright leaders. Short ascending branches run all the way up them (a fastigiate habit), so the crown is an upright oval, widest at 42 % of its height (`profile`). It carries 784 sprays of leathery obovate leaves crowded in rosettes. An opaque lumpy core (an inner shell mapped to a leaf mosaic) keeps the crown dense: shrunk to 55 % at LOD0 so the sprays own the silhouette, and 72 % at LOD1 so a row 250 m away still reads as one dark mass.
- **Textures** (`textures.py --only trees`, plain python3, about 20 s):
  - `coastal_tree_leaf_*` is a 1024² atlas (`veg_common.COASTAL_ATLAS`). It holds two banyan sprays (0.8 m cells: forked twigs with 25–35 elliptic, drip-tipped 10–15 cm leaves, pale midribs and laterals, 10 % pale undersides, a few laterite figs), two windbreak sprays (0.62 m: 3–5 shoots with spiral rosettes of obovate leaves), and two opaque tiling leaf mosaics for the cores. Each leaf is painted at its own size, back to front, with a contact shadow on the leaves below. The normal map's B channel holds translucency (banyan 0.55, windbreak 0.32).
  - `banyan_bark_*` is 512×1024 and tiles at 0.7 m round by 1.4 m along. It shows fused root strands (vertical ridges that merge and part, each its own tone), dark crevices, horizontal lenticel dashes, and pale lichen and crust. The painted mean is about #8C8477.
- **Materials** (appended to the kit's `materials.py`): `kit_banyan_bark`, `kit_banyan_root`, `kit_banyan_leaf`, `kit_windbreak_bark`, `kit_windbreak_leaf`. Bark and leaves of one tree share every wind uniform, the secondary bob included, because twigs hand their bob on to the sprays (a unit test checks this). The roots are tinted warmer and a little darker than the trunk (0.84–0.92 gain, warm), so in H07 they read as mid-value brown: neither white sticks nor black poles. The older `kit_canopy_*` materials and the kit's `canopy_cluster` texture are now unused. They are left for the kit owner to delete, because those files are being edited elsewhere.
- **Budgets and why.**
  - The banyan has one instance in the game: the hero tree, seen from 7 m in H07 with the camera inside its crown footprint. LOD0 is 59,949 triangles (budget 60,000): sprays 21.5k (8 triangles each: 2 rows × 2 columns, cupped), hanging roots 17.1k (the H07 feature), limbs, branches and branchlets 8.1k, twigs 5.4k, props 4.0k, trunk, flanges and surface roots 3.9k. The .glb is 3.4 MB, under the 5 MB cap. LOD1 is 6,999 (budget 10,000): 25 % of the sprays at 1.75× size round 41 opaque clump cores, 20 % of the hanging roots, and one strand per prop.
  - There are 49 windbreak instances in rows, about 15–25 of them inside 75 m in a given view. LOD0 is 5,785 (budget 6,500): sprays with 4 triangles each. LOD1 is 430 (budget 1,000): 14 % of the sprays at 1.7× round the core.
  - Textures add 1.9 MB of PNG, and no file exceeds 1 MB.
- **LODs.** Kit pieces carry exactly `<piece>` and `<piece>-lod1`. The Haluna dresser draws LOD1 beyond `lod1_from_m` (75 m) and does not chain them with `visibility_parent` the way `VegetationPlant` does ("One LOD at every distance" above). Every kit piece shares this pre-existing dresser behaviour. A tree first seen from a still camera within the 2 m margin of the switch can draw neither LOD until the camera leaves the margin. The fix belongs in `haluna_dresser.gd`: set `visibility_parent` of `<piece>` to `<piece>-lod1`, with the margin on LOD1's begin only. That file now lives with the zone track, so it is noted for them and not changed here.
- **Honest assessment.** In H07 the banyan reads as a hero tree. The twisted multi-strand prop pillars and the fused, fluted trunk bracket the white chapel, braided root curtains hang from the low limb, and the crown throws dappled shade on the court. Sprays read as individual leaves at 3–5 m. The windbreak rows read as dark, dense, upright ovals in H01 and H07. Weak points:
  - The root strands are 4-sided, and their bands show up close.
  - The fig notes are invisible at game distance.
  - Every windbreak is the same tree, varied only by yaw and scale.
  - The low limb's underside at the top of H07 is plain bark, with no epiphytes or moss.
  - Lavapipe only: the GPU cost is unmeasured.

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
- **Not built:** screw-pine, sea hibiscus, seagrass, mangrove (later tasks). The hero banyan and the windbreak tree were built in M2-ENV-07 (below). No impostors or billboards for more than 400 m. No wind interaction with characters. No collision meshes. **PLACEHOLDER until Art Director sign-off** (M1-ENV-03): `docs/kb/art/environments/vegetation_placeholders.md` lists every asset and moves each to "Signed off" when Art approves it.
- **Unverified on GPU:** cost, alpha-scissor shimmer under motion, and the shadow-acne settings. Lavapipe only.
