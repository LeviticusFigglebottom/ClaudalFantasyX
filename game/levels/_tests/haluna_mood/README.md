# Haluna mood test (M1-ENV-01)

The five ◆ shots of [haluna.md §5.1](../../../../docs/kb/art/environments/haluna.md) at the `ch02_noon`
sub-frame, composed from the procedural Haluna kit. The art review is in
[haluna_mood_review.md](../../../../docs/kb/art/environments/haluna_mood_review.md).

| File | Role |
|---|---|
| `haluna_mood.tscn` | The zone: environment, sun, sea, terrain, dresser, the five shot cameras |
| `haluna_mood.gd` (`HalunaMood`) | Sun from elevation/azimuth, `hymn_*` globals, capture determinism (held clock, FXAA) |
| `haluna_layout.json` | **All placement data**: terrain shape, lanes, wall runs, pieces, plants, scatter |
| `haluna_dresser.gd` (`HalunaDresser`) | Builds the zone from the layout: kit .glb + materials + LOD ranges, wall runs, gulls facing the sea |
| `haluna_terrain.gd` (`HalunaTerrain`) | Generated crescent beach, terrace, lagoon, reef, islet, far islands; lane/turf/seagrass masks |
| `weathering_tide.gd` (`WeatheringTide`) | Moves the sea to the tide height and gives it the datum (the sea publishes `hymn_water_level`, which the weathering and ground shaders read); swaps the weathering tier |
| `haluna_shot_camera.gd` (`HalunaShotCamera`) | A Camera3D driven by a `CameraShot` resource (FIXED framing, vFOV, DOF) |
| `haluna_noon_environment.tres` | The `ch02_noon` mood frame: sky, AgX, exposure, LUT (no fog: the frame row has none) |
| `lut_ch02_noon.png` | 32³ grade LUT (Texture3D), from `assets_src/environments/kits/haluna/zone_lut.py` |
| `haluna_water_material.tres` | The colour script's validated `lagoon_clear` look (absorption ×1.5, deep `#0E4A55`), crest foam reduced |
| `haluna_kit_sheet.tscn` / `.gd` / `.json` | Every kit piece in rows, for review (not a registered shot) |

Shots (`tests/screenshots/shots.json`): `haluna_h01_village_from_sea`, `haluna_h02_tidewall_lane`,
`haluna_h03_lintel_gull`, `haluna_h04_dock`, `haluna_h07_chapel_court` (960×540).

## GI choice (SPEC §8.1)

**Shipping choice for Haluna: SDFGI** (as the brief recommends): an open exterior about 600 m across,
with a night variant (`ch02_night`), so a baked LightmapGI would need a bake per lighting state and
VoxelGI cannot cover the extent (a 512-subdivision probe over 500 m is ~1 m cells, too coarse for
lanes 3 m wide). LightmapGI stays the choice for the Shell Shrine interior.

**But the mood-test frames are rendered with SDFGI off** (`sdfgi_enabled = false` in
`haluna_noon_environment.tres`; sky ambient + SSAO instead). Measured on lavapipe:

| Configuration (H07, 960×540) | Result |
|---|---|
| SDFGI 6 cascades, 0.3 m, occlusion, 16 and 40 settle frames | identical frames: shade under the banyan crushed to near black, whitewash grey |
| SDFGI 4 cascades, 0.2 m, no occlusion, 30 frames | the same, plus blotchy GI on the chapel walls |
| SDFGI off, sky ambient 0.65 + SSAO | shade is sky-lit teal-blue (colour-script rule 5), the chapel reads white |

SDFGI here removes the sky contribution from every shaded surface and does not converge back over 40
frames, which breaks rule 5 ("shadows are teal, never neutral black"). Whether that is lavapipe or the
card-based canopy voxelising as a solid lid cannot be told without a GPU. **Request to Rendering:**
re-test `sdfgi_enabled = true` on the GPU runner; if it holds the sky fill, turn it on and re-approve the
five baselines. The frames as committed are also what the Low preset (`gi_mode = off`) shows.

## Tonemap and LUT

AgX (white 12), exposure 0.65 (the `ch02_noon` practical exposure of ADR 0014), then `lut_ch02_noon` through `Environment.adjustment_color_correction`
(saturation ×1.12, S-curve 0.45, teal toe `#0E4A55`, highlight roll-off to `#FFF8EE`, no (0,0,0)
black). The LUT is sampled at the colour itself, so each texel stores the grade of its own centre
(`(i + 0.5) / 32`); `zone_lut.py --identity` writes the neutral table for checking that.

## Tide

M1-ENV-05: the sea (`Water`, `publishes_water_level = true`) publishes the `hymn_water_level` global
every frame (x = the water's world Y now, y = its `tide_line_y` datum; docs/kb/tech/water.md), and
`env_weathering_body.gdshaderinc` and `env_ground.gdshader` read it: there are no per-material tide
uniforms any more. `WeatheringTide` moves the sea to `water_height_y` and gives it `tide_line_y`, so a
flood rig animates one value and every wet line follows. Its tier comes from graphics_presets.json
`presets[].tiers.weathering` (`WeatheringTide.quality_for_preset`). SceneRouter resets the global on
every zone change, and the sea resets it when it leaves the tree.

M1-NIT-02 (review-sweep-L on M1-ENV-05):
- **A sea that doesn't publish.** If `WeatheringTide.water` is set but its `publishes_water_level`
  is off, the tide still moves that sea, warns once at `_ready`, and writes `hymn_water_level`
  itself. The no-sea branch does the same. The shaders therefore never keep 0,0 or the previous
  zone's level.
- **One-frame lag (for the Drownbell flood rig).** The sea publishes in its `_process`, so the wet
  line trails a `water_height_y` change by one frame. Before the sea's first frame it reads the
  cleared 0,0. At tide speed this can't be seen. A flood rig that cuts the water height in one jump
  under a camera cut should make the jump one frame before the cut.

## Vegetation groups (M1-ENV-05)

The dresser tags what `vegetation_detail` drives (graphics_presets.json `vegetation_groups`): plant LOD
meshes join `vegetation_lod` (their authored visibility ranges scale), the saltgrass scatters join
`vegetation_multimesh` and `small_foliage` (density, and shadows off on Low), and plant kinds marked
`"small_foliage": true` in haluna_layout.json (the beach vines) join `small_foliage`. GraphicsSettings
applies them when the zone loads (M1-ARC-15's per-scene hook).

## Sky and palette checks (review-sweep-F)

The sky is `game/shaders/environment/env_sky_cumulus.gdshader`, tuned in the environment's sky material:
`background_energy` 1.5 (the visible sky only; the radiance cubemap that gives the sky fill and the water's
sky reflection keeps `sky_energy` 1.0, so ground, shade and water values are unchanged by it) and
`horizon_curve` 0.14. The depth fog and volumetric fog are gone: they are not in the `ch02_noon` row
(haluna.md §0), and the volumetric fog also hazed the sky (`volumetric_fog_sky_affect` 1), which was most of
the zenith's lost chroma.

**Cost and quality tiers (M1-RND-12).** The clouds read two baked lattices, `cloud_lattice`
(assets/vfx/undertow/undertow_noise3d.png) and `cloud_lattice2` (assets/vfx/sky/cloud_lattice2.png); both are bound
in `haluna_noon_environment.tres`, and an unbound lattice reads 0. The march's quality comes from the graphics preset
(`sky_detail` in graphics_presets.json, applied by GraphicsSettings to the sky material). The sky's
`process_mode` is Incremental, so a moving sun or drifting `cloud_offset_m` re-renders the radiance cubemap over
several frames. Measured on an RX 9070 XT: the clouds cost 0.23 ms at Low 1080p and 0.40 ms at High 1440p (they were
2.4 and 3.7 ms); see docs/kb/qa/gpu/2026-10-23-rnd-12-sky.md.

`tests/screenshots/palette_checks.json` holds the numeric targets the five baselines must meet (zenith on
`sky_zenith_noon` +1, lit tops at `cumulus_lit` +1 L, chromatic blue-lilac undersides, cloud grain, the
chapel on `order_marble` 0, the banyan roots above the toe, planks on `timber_weathered` +1, the red budget).
`tools/tests/test_palette_check.py` runs them against the committed baselines, so a re-approval that drifts
off the palette fails the tool tests. Measure any frame with
`python3 tools/screenshots/palette_check.py coverage <png>` (swatch coverage, red and gold masks) or
`... region <png> --rect x0,y0,x1,y1` (median colour, Oklab L/C/h, grain).

The **SaveShrine** (M1-ENV-04) at (-67, 2.04, 46.6) sits behind the beach palms in H01 and does not read there.

