# Corrow seawall kit preview (M3-ENV-04)

The Corrow seawall kit (`assets/environments/kits/corrow/`, generators in
`assets_src/environments/kits/corrow/`) composed for the ◆ shots of
[corrow.md §4](../../../../docs/kb/art/environments/corrow.md), graded to the colour script's `ch08`.
Environment owns this folder (docs/kb/ownership.md). It is a kit preview, not the zone: the zone
`game/levels/ch08/corrow/` is m2-slice's (swap-in note in docs/kb/tasks/M3/M3-ENV-04-seawall.md).

| File | Role |
|---|---|
| `corrow_preview.tscn` | Sun, Moon (hidden by day), storm sky, the storm-grey bay, tide, the dresser and the nine shot cameras (`Cameras/C01` … `C11`) |
| `corrow_preview.gd` (`CorrowPreview`) | Extends `HalunaMood`: `phase` &"front" (`ch08`), &"surge" (`ch08_surge`: sun behind the front, the sea at +1.8 m over the low town), M3-ENV-04B's &"fallen" (`ch08_after`) and &"ch09" (the night mood); the last two show the layout's `states.fallen` (built on first use, the pieces it replaces hidden); the Coilspire beacon light from the layout |
| `corrow_layout.json` | Every placement (HalunaDresser format, explicit heights, no terrain), plus `states.fallen` (`hide` + `pieces`, read by CorrowPreview only). **Generated** by `cw_preview_layout.py`: edit the generator, not the JSON |
| `corrow_fallen_environment.tres`, `corrow_ch09_environment.tres` | The `ch08_after` overcast and the `ch09` night (stars, a half moon, `lut_ch09_ebbing`) |
| `corrow_ch08_environment.tres` | The `ch08` frame: a slate storm sky (`env_sky_low_sun`: the sun's side breaks warm under the front), the `#5E6E80`-family fill, AgX at exposure 0.80, the LUT |
| `lut_ch08_storm.png`, `lut_ch09_ebbing.png` | 32³ grade LUTs from `assets_src/environments/kits/corrow/cw_zone_lut.py` (`--frame ch09` for the second) |
| `corrow_water_material.tres` | The colour script's validated `storm_grey` look (σ base × 2.25, scatter `#1F7F86`, deep `#0E4A55`) |
| `corrow_preview_shots.json` | Capture manifest for all nine views (`--manifest=res://game/levels/_tests/corrow_kit/corrow_preview_shots.json`) |

Registered baselines (tests/screenshots/shots.json): `corrow_c01_wall_head`, `corrow_c08_watcher_profile` and
(M3-ENV-04B) `corrow_c10_breach_fallen`.

Rebuild after a generator change:

```bash
python3 assets_src/environments/kits/corrow/cw_textures.py
blender --background --factory-startup --threads 4 --python assets_src/environments/kits/corrow/build.py -- --all \
  --out-dir assets/environments/kits/corrow --manifest assets/environments/kits/corrow/kit_manifest.json
python3 assets_src/environments/kits/corrow/cw_materials.py
python3 assets_src/environments/kits/corrow/cw_zone_lut.py && python3 assets_src/environments/kits/corrow/cw_zone_lut.py --frame ch09
python3 assets_src/environments/kits/corrow/cw_preview_layout.py
godot --headless --path . --import && python3 assets_src/environments/kits/corrow/cw_import_settings.py
```

GI: as Haluna and the Brine Shoals, the frames are rendered with SDFGI off (sky-colour ambient + SSAO). The
Sun's `sky_mode` is light-and-sky (0), because `env_sky_low_sun` reads the sun's direction for its warm
break; with light-only the sky turns uniformly tan. The storm wall itself (the Undertow) is Rendering's
`UndertowStorm`, not in this preview; the volumetric spray haze is off on lavapipe (it doubles the capture
time and veils the sky warm), see corrow.md §6.
