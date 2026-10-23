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
| `weathering_tide.gd` (`WeatheringTide`) | Writes `tide_line_y` / `water_height_y` to every weathering and ground material and moves the sea; swaps the weathering tier |
| `haluna_shot_camera.gd` (`HalunaShotCamera`) | A Camera3D driven by a `CameraShot` resource (FIXED framing, vFOV, DOF) |
| `haluna_noon_environment.tres` | The `ch02_noon` mood frame: sky, AgX, exposure, fog, LUT |
| `lut_ch02_noon.png` | 32³ grade LUT (Texture3D), from `assets_src/environments/kits/haluna/zone_lut.py` |
| `haluna_water_material.tres` | The lagoon look (validated water.md values; crest foam reduced) |
| `haluna_kit_sheet.tscn` / `.gd` / `.json` | Every kit piece in rows, for review (not a registered shot) |

Shots (`tests/screenshots/shots.json`): `haluna_h01_village_from_sea`, `haluna_h02_tidewall_lane`,
`haluna_h03_lintel_gull`, `haluna_h04_dock`, `haluna_h07_chapel_court` (960×540).

## GI choice (SPEC §8.1)

**Shipping choice for Haluna: SDFGI** (as the brief recommends): an open exterior about 600 m across,
with a night variant (`ch02_night`), so a baked LightmapGI would need a bake per lighting state and
VoxelGI cannot cover the extent (a 512-subdivision probe over 500 m is ~1 m cells, too coarse for
lanes 3 m wide). LightmapGI stays the choice for the Shell Shrine interior.

**But the mood-test frames are rendered with SDFGI off** (`sdfgi_enabled = false` in
`haluna_noon_environment.tres`; sky ambient + SSAO + volumetric fog instead). Measured on lavapipe:

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

AgX (white 12), exposure 0.58, then `lut_ch02_noon` through `Environment.adjustment_color_correction`
(saturation ×1.12, S-curve 0.45, teal toe `#0E4A55`, highlight roll-off to `#FFF8EE`, no (0,0,0)
black). The LUT is sampled at the colour itself, so each texel stores the grade of its own centre
(`(i + 0.5) / 32`); `zone_lut.py --identity` writes the neutral table for checking that.

## Tide

No global tide uniform exists yet (`project.godot` belongs to the Lead). `WeatheringTide` writes the
two uniforms into each registered material instead. Request: a `hymn_tide` vec2 global
(`tide_line_y`, `water_height_y`); the shader reads material uniforms of the same names, so the switch
is a one-line change in `env_weathering_body.gdshaderinc` and `env_ground.gdshader`.
