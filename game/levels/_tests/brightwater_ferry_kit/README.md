# Brightwater ferry kit preview (M3-ENV-08)

The Brightwater ferry kit (`assets/environments/kits/brightwater_ferry/`, generators in
`assets_src/environments/kits/brightwater_ferry/`) composed for the ◆ shots of
[brightwater_ferry.md §4](../../../../docs/kb/art/environments/brightwater_ferry.md), graded to the colour script's
`ch04`. Environment owns this folder (docs/kb/ownership.md). It is a kit preview, not the zone: the zone
`game/levels/ch04/brightwater_ferry/` is m2-slice's (swap-in note in docs/kb/tasks/M3/M3-ENV-08-brightwater-ferry.md).
Nothing shipped may reference this folder.

| File | Role |
|---|---|
| `brightwater_ferry_preview.tscn` | The Moon (the sun hidden), the night sea (`WaterSurface`, an open-sea swell from the ENE), the tide, the dresser and the seven shot cameras (`Cameras/B01` … `B07`) |
| `brightwater_ferry_preview.gd` (`BrightwaterFerryPreview`) | Extends `HalunaMood` in its night mood (the `ch04` values: the Moon `#9DB4D9` at 0.28, a waning crescent low in the east at 16°; sea-glow 0.12; the `night_sea` look) and lights the deck lanterns from the layout's `lamps`, every light with `light_volumetric_fog_energy` = 0 |
| `brightwater_ferry_layout.json` | Every placement (HalunaDresser format, explicit heights, no terrain) plus `lamps`. **Generated** by `bf_preview_layout.py`: edit the generator, not the JSON |
| `brightwater_ferry_ch04_environment.tres` | The `ch04` frame: the navy night sky (`env_sky_night`, `#0B1630` / `#1E2E4E`, stars, the crescent), the `#2A4A6E` fill at 0.2, AgX at exposure 1.10, the kit's `lut_ch04_crossing` |
| `brightwater_ferry_water_material.tres` | The colour script's validated `night_sea` look (σ 2 / 0.5 / 0.42 × 1.0, scatter `#1FA3A6`, deep `#061A2B`) |
| `brightwater_ferry_preview_shots.json` | Capture manifest for all seven views and the six derelict views (`--manifest=res://game/levels/_tests/brightwater_ferry_kit/brightwater_ferry_preview_shots.json`) |
| `brightwater_derelict_preview.tscn` | M3-ENV-08B: the *Seventh Terrace* alongside the ferry by day (HalunaMood's day mood at the **provisional** `ch04_derelict` frame: sun 15° / 100°, `#FFD9B0` at 2.6), four dressers (`Dresser`: both ships and the alongside gear; `SailsSet`: the set sails and the spawn membrane; `SailsLowered`: hidden; `NameBoard`) and six cameras (`D01` … `D04`, `D06`, `D09`; D09's setup shows the lowered state). **Generated** by `bf_preview_layout.py` |
| `brightwater_derelict_*_layout.json` | The four dressers' layouts (generated); the main one carries `anchors` (her origin, the board, the wheel's axle, the walkable boxes) |
| `brightwater_derelict_environment.tres`, `brightwater_derelict_water_material.tres` | The provisional `ch04_derelict` sky (`env_sky_low_sun`, exposure 0.75, no grade) and the open-sea day water, until Rendering adds the sub-frame |

Registered baselines (tests/screenshots/shots.json): `brightwater_b02_awning`, `brightwater_b03_rail_drowned`. The derelict
views are review views (the Seventh Terrace's one baseline is Oruvel's `oruvel_o07_name_board`, the same board).

Rebuild after a generator change:

```bash
blender --background --factory-startup --threads 4 --python assets_src/environments/kits/brightwater_ferry/build.py -- --all \
  --out-dir assets/environments/kits/brightwater_ferry --manifest assets/environments/kits/brightwater_ferry/kit_manifest.json
python3 assets_src/environments/kits/brightwater_ferry/bf_materials.py
python3 assets_src/environments/kits/brightwater_ferry/bf_zone_lut.py
python3 assets_src/environments/kits/brightwater_ferry/bf_preview_layout.py
godot --headless --path . --import && python3 assets_src/environments/kits/brightwater_ferry/bf_import_settings.py
```

GI: as the other kit previews, the frames are rendered with SDFGI off (sky-colour ambient + SSAO). The ship is still
(no rocking: that is the zone's, if wanted); the swell passes through the hull below the deck, where nothing shows.
The volumetric fog (`ch04` 0.008) is off on lavapipe; the rig's lamps already keep it dark for the GPU tiers.
