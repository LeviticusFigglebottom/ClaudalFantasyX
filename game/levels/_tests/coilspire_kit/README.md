# Coilspire temple kit preview (M3-ENV-10)

The Coilspire temple kit (`assets/environments/kits/coilspire/`, generators in
`assets_src/environments/kits/coilspire/`) composed for the ◆ views of
[coilspire.md §4](../../../../docs/kb/art/environments/coilspire.md), in the Corrow preview's world frame: the
temple stands exactly where Corrow's skyline piece `coilspire_headland` stands. Environment owns this folder
(docs/kb/ownership.md). It is a kit preview, not the zone: the zone `game/levels/ch08/coilspire/` is m2-slice's
(swap-in note in docs/kb/tasks/M3/M3-ENV-10-coilspire-temple.md). Nothing shipped may reference this folder.

| File | Role |
|---|---|
| `coilspire_preview.tscn` | Sun (light-and-sky mode for `env_sky_low_sun`), the storm sky, Corrow's storm-grey sea and swell, tide, two dressers (`Dresser`: this kit; `Backdrop`: Corrow's kit) and the eight view cameras (`Cameras/K01` … `K08`) |
| `coilspire_preview.gd` (`CoilspirePreview`) | Extends `HalunaMood`: `phase` &"storm" (`ch08` outside) and &"interior" (`ch08_coilspire_int`: `interior_environment`); the beacon, braziers, keeping flame and grate lights from the layout (shadowless, `light_volumetric_fog_energy = 0`) |
| `coilspire_layout.json` | This kit's placements (HalunaDresser format, explicit heights), plus `fire_lights` and `hearth_lights`; the trial's fittings carry a `tag` (tier, kind, spire angle). **Generated** by `cs_preview_layout.py` |
| `coilspire_backdrop.json` | Corrow's kit as Corrow's preview places it (wall, stair, town, far ground), without its far headland. **Generated** by `cs_preview_layout.py` from `cw_preview_layout` (read-only) |
| `coilspire_ch08_environment.tres` | The `ch08` frame: Corrow's storm sky and fill, AgX at 0.80, Corrow's `lut_ch08_storm` |
| `coilspire_int_environment.tres` | The `ch08_coilspire_int` frame: the same sky at 0.45 through the openings, ambient `#5A7E78` at 2.0, exposure 1.5, `lut_ch08_coilspire_int` |
| `lut_ch08_coilspire_int.png` | 32³ grade LUT from `assets_src/environments/kits/coilspire/cs_zone_lut.py` |
| `coilspire_preview_shots.json` | Capture manifest for all eight views (`--manifest=res://game/levels/_tests/coilspire_kit/coilspire_preview_shots.json`) |

Registered baselines (tests/screenshots/shots.json): `coilspire_k01_headland_path` and `coilspire_k03_well`.

Rebuild after a generator change:

```bash
blender --background --factory-startup --threads 4 --python assets_src/environments/kits/coilspire/build.py -- --all \
  --out-dir assets/environments/kits/coilspire --manifest assets/environments/kits/coilspire/kit_manifest.json
python3 assets_src/environments/kits/coilspire/cs_materials.py
python3 assets_src/environments/kits/coilspire/cs_zone_lut.py
python3 assets_src/environments/kits/coilspire/cs_preview_layout.py
godot --headless --path . --import && python3 assets_src/environments/kits/coilspire/cs_import_settings.py
```

GI: as Corrow, SDFGI off (sky-colour ambient + SSAO); the interior is lit by its ambient fill and the braziers,
so on lavapipe the slits' light shafts barely read (GPU tiers: LightmapGI per trial state, coilspire.md §0). The
volumetric haze is off on lavapipe (the rig still sets the colour script's density).
