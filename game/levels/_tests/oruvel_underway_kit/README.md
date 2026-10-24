# Oruvel Underway kit preview (M3-ENV-05)

The Oruvel Underway kit (`assets/environments/kits/oruvel_underway/`, generators in
`assets_src/environments/kits/oruvel_underway/`) composed for the ◆ shots of
[oruvel_underway.md §4](../../../../docs/kb/art/environments/oruvel_underway.md), under the underwater look
(M2-RND-02 with M2-RND-09's fixes) at the colour script's `ch01` grade. Environment owns this folder
(docs/kb/ownership.md). It is a kit preview, not the zone: the zone `game/levels/ch01/oruvel_underway/` is
m2-slice's (swap-in note in docs/kb/tasks/M3/M3-ENV-05-lamp-diver-seafloor.md).

| File | Role |
|---|---|
| `oruvel_underway_preview.tscn` | Sun, sky, the lagoon surface, tide, the dresser, the existing `UnderwaterRig`, Rhen's lantern (a stand-in mesh), the held motes down the stairwell, and the seven shot cameras (`Cameras/U01` … `U14`) |
| `oruvel_underway_preview.gd` (`OruvelUnderwayPreview`) | Extends `HalunaMood`: per camera, from the layout's `shots`, hangs the lantern, tints the sun and ambient for the subject's depth (`depth_m`) and sets the lighting area (open, interior, deep); opens the glimmer gate for the held motes |
| `oruvel_underway_layout.json` | Every placement (HalunaDresser format, explicit heights, no terrain) and the per-camera `shots`. **Generated** by `ou_preview_layout.py`: edit the generator, not the JSON |
| `oruvel_underway_ch01_environment.tres` | The `ch01` frame: sky for the Snell window, AgX at exposure 0.65, saturation ×1.12, SSAO, SDFGI off, volumetric fog authored on at density 0 (the rig's shafts only) |
| `oruvel_underway_preview_shots.json` | Capture manifest for all seven views (`--manifest=res://game/levels/_tests/oruvel_underway_kit/oruvel_underway_preview_shots.json`) |

Registered baselines (tests/screenshots/shots.json): see the task file (two at most).

Two stand-ins in the rig, both requested of Rendering (design notes §0):
- **Downwelling.** The rig absorbs light along the camera's ray only, so a floor at 22 m was lit by the full noon
  sun. The preview tints the sun and the ambient by the rig's own transmittance over the subject's depth.
- **Area light level.** The rig lights its in-scatter with the sun and no occlusion; inside the tower the preview
  scales it (and the ambient) per area through a private copy of the rig's data (never the shared cache).

Rebuild after a generator change:

```bash
python3 assets_src/environments/kits/oruvel_underway/ou_textures.py
blender --background --factory-startup --python assets_src/environments/kits/oruvel_underway/build.py -- --all \
  --out-dir assets/environments/kits/oruvel_underway --manifest assets/environments/kits/oruvel_underway/kit_manifest.json
python3 assets_src/environments/kits/oruvel_underway/ou_materials.py
python3 assets_src/environments/kits/oruvel_underway/ou_preview_layout.py
godot --headless --path . --import && python3 assets_src/environments/kits/oruvel_underway/ou_import_settings.py
```
