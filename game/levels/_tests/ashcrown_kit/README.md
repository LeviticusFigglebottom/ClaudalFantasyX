# Ashcrown temple kit preview (M3-ENV-09)

The Ashcrown temple kit (`assets/environments/kits/ashcrown/`, generators in
`assets_src/environments/kits/ashcrown/`) composed for the ◆ shots of
[ashcrown.md §5](../../../../docs/kb/art/environments/ashcrown.md), graded to the `ch05_temple` sub-frame
(colour script `ch05`, "temple at 13:00"). Environment owns this folder (docs/kb/ownership.md). It is a kit
preview, not the zone: the zone `game/levels/ch05/ashcrown/` is m2-slice's (swap-in note in
docs/kb/tasks/M3/M3-ENV-09-ashcrown-temple.md). Nothing shipped may reference this folder.

| File | Role |
|---|---|
| `ashcrown_preview.tscn` | Sun (`ch05_temple`: 58° / 225°, `#FFF0DC` 2.8 through the ash veil), the tide datum at the sea (−306.72 in the kit's frame, so no wet line on the crest), a sea stand-in plane, the anvil hall's `HallProbe` (interior ambient), the dresser and the nine shot cameras (`Cameras/A01` … `A07`, `O1`, `O2`) |
| `ashcrown_preview.gd` (`AshcrownPreview`) | Extends `HalunaMood`; places the layout's `borrowed` Pemakar pieces (the plume with `ac_plume_day`, its LOD0 kept up close; the open-hand gate at 1.6×; lamp pillars) and its `lights` (the hall's lamps, the forge trough, two daylight stand-ins, the vent's glow; shadowless, `light_volumetric_fog_energy` 0); `interior` opens the exposure for `ch05_temple_int` |
| `ashcrown_layout.json` | Every placement (HalunaDresser format, explicit heights, no terrain), plus `borrowed` and `lights`. **Generated** by `ac_preview_layout.py`: edit the generator, not the JSON |
| `ashcrown_ch05_environment.tres` | The day frame: an ash-veiled sky (`env_sky_low_sun`), ambient `#8E959C`, AgX at exposure 0.72, distance haze `#8C8882`, the LUT |
| `lut_ch05_ashcrown.png` | 32³ grade LUT from `assets_src/environments/kits/ashcrown/ac_zone_lut.py` |
| `ashcrown_preview_shots.json` | Capture manifest for all nine views (`--manifest=res://game/levels/_tests/ashcrown_kit/ashcrown_preview_shots.json`); A04 and A05 set `interior` |

Registered baselines (tests/screenshots/shots.json): `ashcrown_a01_approach`, `ashcrown_a04_anvil_hall`.

Rebuild after a generator change:

```bash
python3 assets_src/environments/kits/ashcrown/ac_textures.py
blender --background --factory-startup --threads 4 --python assets_src/environments/kits/ashcrown/build.py -- --all \
  --out-dir assets/environments/kits/ashcrown --manifest assets/environments/kits/ashcrown/kit_manifest.json
python3 assets_src/environments/kits/ashcrown/ac_materials.py
python3 assets_src/environments/kits/ashcrown/ac_zone_lut.py
python3 assets_src/environments/kits/ashcrown/ac_preview_layout.py
godot --headless --path . --import && python3 assets_src/environments/kits/ashcrown/ac_import_settings.py
```

The kit's frame is the Pemakar layout's `ashcrown_silhouette` origin (add (0, 306.72, −682) for the Pemakar
town's frame). GI: SDFGI off (sky-colour ambient + SSAO) outside; inside, the `HallProbe` replaces the sky
ambient and two shadowless daylight stand-ins (the sky down the shaft, the court's bounce through the door)
stand in for GI until Rendering decides the hall's GI. The plume is Pemakar's `ash_plume` (its own
`env_ash_plume` shader, this kit's noon parameters); up close its billows show facets (see the task's known
limits).
