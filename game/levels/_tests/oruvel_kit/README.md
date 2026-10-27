# Oruvel raft-town kit preview (M3-ENV-07)

The Oruvel raft-town kit (`assets/environments/kits/oruvel/`, generators in `assets_src/environments/kits/oruvel/`)
composed for the ◆ shots of [oruvel.md §4](../../../../docs/kb/art/environments/oruvel.md), graded to the colour
script's `ch01` (10:30). Environment owns this folder (docs/kb/ownership.md). It is a kit preview, not the zone: the
zone `game/levels/ch01/oruvel/` is m2-slice's (swap-in note in docs/kb/tasks/M3/M3-ENV-07-oruvel-raft-town.md).
Nothing shipped may reference this folder (tools/tests/test_release_excludes_tests.py).

| File | Role |
|---|---|
| `oruvel_preview.tscn` | The OruvelPreview rig at `ch01` (sun 58° / 120°, `#FFEFE1` at 3.0), the sea, the tide, the three dressers and the shot cameras (`Cameras/O01` … `O22`; the storm views reach 40 km). **Generated** |
| `oruvel_preview.gd` (`OruvelPreview`) | M3-ENV-07B. Extends HalunaMood: `phase` &"day" (the `ch01` frame untouched) or &"ch01_storm" (the stand-in storm frame, the layout's `states.storm`, Kell's beacon, the Seventh Terrace gone, the Undertow at `ch01_arrival` to the south); `pen_split` / `section_transform` pose the net-pen's split by the layout's `rigs.net_pen_split` |
| `oruvel_storm_environment.tres` | M3-ENV-07B. The stand-in `ch01_storm` frame: the sky cleared, ambient 0.5, a cooler spray haze, `lut_ch01_storm` (the kit's, `assets/environments/kits/oruvel/`) |
| `oruvel_layout.json` | Every placement (HalunaDresser format, explicit heights, no terrain), the shots (eye, target, lens), the swap-in anchors, and (M3-ENV-07B) `states.storm`, `rigs.net_pen_split` and `storm_lights`. **Generated** |
| `oruvel_drowned_layout.json` | The Oruvel Underway kit's crown (its preview layout's rows at and above F13), read-only, in the same frame: the drowned tower under the dive raft. **Generated** |
| `oruvel_preview_shots.json` | Capture manifest for all eight views (`--manifest=res://game/levels/_tests/oruvel_kit/oruvel_preview_shots.json`). **Generated** |
| `oruvel_ch01_environment.tres` | The `ch01` frame: the noon cumulus sky, sky ambient 0.6, AgX at exposure 0.65, a light depth haze (`#BFDDE8`), `lut_ch01_raft` (M3-ENV-06's, read-only) |
| `oruvel_water_material.tres` | The colour script's validated `lagoon_clear` look at absorption ×2.0 (scatter `#1FA3A6`, deep `#0E4A55`) |

The four generated files come from `assets_src/environments/kits/oruvel/ov_preview_layout.py`: edit the generator,
not them (`tools/tests/test_oruvel_kit.py` fails when they are stale).

Registered baselines (tests/screenshots/shots.json): see oruvel.md §6.

Rebuild after a generator change:

```bash
blender --background --factory-startup --threads 4 --python assets_src/environments/kits/oruvel/build.py -- --all \
  --out-dir assets/environments/kits/oruvel --manifest assets/environments/kits/oruvel/kit_manifest.json
python3 assets_src/environments/kits/oruvel/ov_materials.py
python3 assets_src/environments/kits/oruvel/ov_zone_lut.py
python3 assets_src/environments/kits/oruvel/ov_preview_layout.py
godot --headless --path . --import && python3 assets_src/environments/kits/oruvel/ov_import_settings.py
```

GI: as Haluna, SDFGI off (sky-colour ambient + SSAO). The colour script's volumetric haze (0.004) is off in the
preview on lavapipe (it doubles the capture time); the depth fog stands in for it.
