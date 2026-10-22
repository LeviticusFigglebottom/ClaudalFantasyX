# Asset Provenance

Every file under `assets/` must have exactly one row here (SPEC §2, §13.6).
`tools/validate_data.py` fails CI on any asset without a row.

Rules:
- `source` is a path under `assets_src/` or `tools/` that regenerates the asset.
- `command` is the exact command that regenerates it from a clean checkout.
- `license` is `original` for agent-authored work. Third-party licenses are allowed ONLY for
  fonts (SIL OFL) and code; any other exception needs an ADR and a flag to the human.

| path | source | command | role | date | license |
|---|---|---|---|---|---|
| assets/audio/music/hush_theme_sketch.ogg | assets_src/music/hush_theme_sketch.py + tools/audio/synth/ | python3 assets_src/music/hush_theme_sketch.py | Audio Director | 2026-10-22 | original |
| assets/audio/sfx/ui_cursor.ogg | assets_src/sfx/ui_sfx.py + tools/audio/synth/ | python3 assets_src/sfx/ui_sfx.py | Audio Director | 2026-10-22 | original |
| assets/audio/sfx/ui_confirm.ogg | assets_src/sfx/ui_sfx.py + tools/audio/synth/ | python3 assets_src/sfx/ui_sfx.py | Audio Director | 2026-10-22 | original |
| assets/audio/sfx/ui_cancel.ogg | assets_src/sfx/ui_sfx.py + tools/audio/synth/ | python3 assets_src/sfx/ui_sfx.py | Audio Director | 2026-10-22 | original |
| assets/audio/sfx/text_blip.ogg | assets_src/sfx/ui_sfx.py + tools/audio/synth/ | python3 assets_src/sfx/ui_sfx.py | Audio Director | 2026-10-22 | original |
| assets/environments/vegetation/beach_vine_albedo.png | assets_src/environments/vegetation/textures.py | python3 assets_src/environments/vegetation/textures.py --only beach_vine | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/beach_vine_normal.png | assets_src/environments/vegetation/textures.py | python3 assets_src/environments/vegetation/textures.py --only beach_vine | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/beach_vine_patch.glb | assets_src/environments/vegetation/build.py + beach_vine.py + veg_common.py | blender --background --factory-startup --python assets_src/environments/vegetation/build.py -- --target beach_vine_patch --out assets/environments/vegetation/beach_vine_patch.glb | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/frangipani_a.glb | assets_src/environments/vegetation/build.py + frangipani.py + veg_common.py | blender --background --factory-startup --python assets_src/environments/vegetation/build.py -- --target frangipani_a --out assets/environments/vegetation/frangipani_a.glb | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/frangipani_b.glb | assets_src/environments/vegetation/build.py + frangipani.py + veg_common.py | blender --background --factory-startup --python assets_src/environments/vegetation/build.py -- --target frangipani_b --out assets/environments/vegetation/frangipani_b.glb | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/frangipani_bark_albedo.png | assets_src/environments/vegetation/textures.py | python3 assets_src/environments/vegetation/textures.py --only frangipani | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/frangipani_bark_normal.png | assets_src/environments/vegetation/textures.py | python3 assets_src/environments/vegetation/textures.py --only frangipani | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/frangipani_leaf_albedo.png | assets_src/environments/vegetation/textures.py | python3 assets_src/environments/vegetation/textures.py --only frangipani | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/frangipani_leaf_normal.png | assets_src/environments/vegetation/textures.py | python3 assets_src/environments/vegetation/textures.py --only frangipani | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/materials/beach_vine.tres | assets/environments/vegetation/materials/beach_vine.tres (hand-authored ShaderMaterial; shader in game/shaders/vegetation/) | none: hand-authored text resource | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/materials/frangipani_bark.tres | assets/environments/vegetation/materials/frangipani_bark.tres (hand-authored ShaderMaterial; shader in game/shaders/vegetation/) | none: hand-authored text resource | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/materials/frangipani_leaf.tres | assets/environments/vegetation/materials/frangipani_leaf.tres (hand-authored ShaderMaterial; shader in game/shaders/vegetation/) | none: hand-authored text resource | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/materials/palm_bark.tres | assets/environments/vegetation/materials/palm_bark.tres (hand-authored ShaderMaterial; shader in game/shaders/vegetation/) | none: hand-authored text resource | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/materials/palm_frond.tres | assets/environments/vegetation/materials/palm_frond.tres (hand-authored ShaderMaterial; shader in game/shaders/vegetation/) | none: hand-authored text resource | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/materials/saltgrass.tres | assets/environments/vegetation/materials/saltgrass.tres (hand-authored ShaderMaterial; shader in game/shaders/vegetation/) | none: hand-authored text resource | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/palm_bark_albedo.png | assets_src/environments/vegetation/textures.py | python3 assets_src/environments/vegetation/textures.py --only palm | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/palm_bark_normal.png | assets_src/environments/vegetation/textures.py | python3 assets_src/environments/vegetation/textures.py --only palm | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/palm_coconut_a.glb | assets_src/environments/vegetation/build.py + palm.py + veg_common.py | blender --background --factory-startup --python assets_src/environments/vegetation/build.py -- --target palm_coconut_a --out assets/environments/vegetation/palm_coconut_a.glb | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/palm_coconut_b.glb | assets_src/environments/vegetation/build.py + palm.py + veg_common.py | blender --background --factory-startup --python assets_src/environments/vegetation/build.py -- --target palm_coconut_b --out assets/environments/vegetation/palm_coconut_b.glb | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/palm_coconut_c.glb | assets_src/environments/vegetation/build.py + palm.py + veg_common.py | blender --background --factory-startup --python assets_src/environments/vegetation/build.py -- --target palm_coconut_c --out assets/environments/vegetation/palm_coconut_c.glb | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/palm_frond_albedo.png | assets_src/environments/vegetation/textures.py | python3 assets_src/environments/vegetation/textures.py --only palm | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/palm_frond_normal.png | assets_src/environments/vegetation/textures.py | python3 assets_src/environments/vegetation/textures.py --only palm | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/saltgrass_albedo.png | assets_src/environments/vegetation/textures.py | python3 assets_src/environments/vegetation/textures.py --only saltgrass | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/saltgrass_clumps.glb | assets_src/environments/vegetation/build.py + saltgrass.py + veg_common.py | blender --background --factory-startup --python assets_src/environments/vegetation/build.py -- --target saltgrass_clumps --out assets/environments/vegetation/saltgrass_clumps.glb | Environment Artist | 2026-10-22 | original |
| assets/environments/vegetation/saltgrass_normal.png | assets_src/environments/vegetation/textures.py | python3 assets_src/environments/vegetation/textures.py --only saltgrass | Environment Artist | 2026-10-22 | original |
