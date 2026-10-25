# Brine Shoals kit preview (M3-ENV-02)

The Brine Shoals kit (`assets/environments/kits/brine_shoals/`, generators in
`assets_src/environments/kits/brine_shoals/`) composed for the ◆ shots of
[brine_shoals.md §4](../../../../docs/kb/art/environments/brine_shoals.md), graded to the colour script's `ch06`.
Environment owns this folder (docs/kb/ownership.md). It is a kit preview, not the zone: the zone
`game/levels/ch06/brine_shoals/` is m2-slice's (swap-in notes in docs/kb/handoffs/live/env-art.md).

| File | Role |
|---|---|
| `brine_shoals_preview.tscn` | Sun, sky, water, tide, the dresser and the eight shot cameras (`Cameras/B01` … `B11`) |
| `brine_shoals_preview.gd` (`BrineShoalsPreview`) | Extends `HalunaMood`: `phase` &"raid" (`ch06`) or &"after" (`ch06_after`); fire lights from the layout |
| `brine_shoals_layout.json` | Every placement (HalunaDresser format, explicit heights, no terrain). **Generated** by `bs_preview_layout.py`: edit the generator, not the JSON |
| `brine_shoals_ch06_environment.tres` | The `ch06` frame: hazed sky, cool `#A8B8B0` fill, depth and volumetric haze, AgX at exposure 0.70, the LUT |
| `lut_ch06_smoke.png` | 32³ grade LUT from `assets_src/environments/kits/brine_shoals/bs_zone_lut.py` |
| `brine_shoals_water_material.tres` | The colour script's validated `silted_flats` look; foam, detail normals and SSS off (the channel is still) |
| `brine_shoals_preview_shots.json` | Capture manifest for all eight views (`--manifest=res://game/levels/_tests/brine_shoals_kit/brine_shoals_preview_shots.json`) |

Registered baselines (tests/screenshots/shots.json): `brine_b01_arrival` and `brine_b05_barge_channel`.

Rebuild after a generator change:

```bash
python3 assets_src/environments/kits/brine_shoals/bs_textures.py
blender --background --factory-startup --python assets_src/environments/kits/brine_shoals/build.py -- --all \
  --out-dir assets/environments/kits/brine_shoals --manifest assets/environments/kits/brine_shoals/kit_manifest.json
python3 assets_src/environments/kits/brine_shoals/bs_materials.py
python3 assets_src/environments/kits/brine_shoals/bs_zone_lut.py
python3 assets_src/environments/kits/brine_shoals/bs_preview_layout.py
godot --headless --path . --import && python3 assets_src/environments/kits/brine_shoals/bs_import_settings.py
```

GI: as Haluna, the frames are rendered with SDFGI off (sky-colour ambient + SSAO); SDFGI on lavapipe loses
the fill (haluna_mood README). The smoke is `game/shaders/environment/env_smoke_plume.gdshader`, a simple
in-repo stand-in; the volumetric column is requested of Rendering (M3-RND-21).
