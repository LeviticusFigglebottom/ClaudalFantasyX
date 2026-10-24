# Oruvel raft-town kit preview (M3-ENV-07)

The Oruvel raft-town kit (`assets/environments/kits/oruvel/`, generators in `assets_src/environments/kits/oruvel/`)
composed for the ◆ shots of [oruvel.md §4](../../../../docs/kb/art/environments/oruvel.md), graded to the colour
script's `ch01` (10:30). Environment owns this folder (docs/kb/ownership.md). It is a kit preview, not the zone: the
zone `game/levels/ch01/oruvel/` is m2-slice's (swap-in note in docs/kb/tasks/M3/M3-ENV-07-oruvel-raft-town.md).
Nothing shipped may reference this folder (tools/tests/test_release_excludes_tests.py).

| File | Role |
|---|---|
| `oruvel_preview.tscn` | The HalunaMood rig at `ch01` (sun 58° / 120°, `#FFEFE1` at 3.0), the sea, the tide, the two dressers and the eight shot cameras (`Cameras/O01` … `O20`). **Generated** |
| `oruvel_layout.json` | Every placement (HalunaDresser format, explicit heights, no terrain), the shots (eye, target, lens) and the swap-in anchors. **Generated** |
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
python3 assets_src/environments/kits/oruvel/ov_preview_layout.py
godot --headless --path . --import && python3 assets_src/environments/kits/oruvel/ov_import_settings.py
```

GI: as Haluna, SDFGI off (sky-colour ambient + SSAO). The colour script's volumetric haze (0.004) is off in the
preview on lavapipe (it doubles the capture time); the depth fog stands in for it.
