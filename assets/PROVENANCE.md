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
| assets/fonts/source_sans_3/SourceSans3-Regular.otf | Ubuntu package fonts-adobe-sourcesans3 3.052+dfsg-2 (archive.ubuntu.com, pool/universe); upstream Adobe Source Sans 3.052, unmodified | `dpkg-deb -x fonts-adobe-sourcesans3_3.052+dfsg-2_all.deb x`, copy `x/usr/share/fonts/opentype/sourcesans3/SourceSans3-Regular.otf` | UI/UX | 2026-10-22 | SIL OFL 1.1 |
| assets/fonts/source_sans_3/SourceSans3-Medium.otf | Ubuntu package fonts-adobe-sourcesans3 3.052+dfsg-2; upstream Adobe Source Sans 3.052, unmodified | same package, copy `SourceSans3-Medium.otf` | UI/UX | 2026-10-22 | SIL OFL 1.1 |
| assets/fonts/source_sans_3/SourceSans3-Semibold.otf | Ubuntu package fonts-adobe-sourcesans3 3.052+dfsg-2; upstream Adobe Source Sans 3.052, unmodified | same package, copy `SourceSans3-Semibold.otf` | UI/UX | 2026-10-22 | SIL OFL 1.1 |
| assets/fonts/source_sans_3/SourceSans3-Bold.otf | Ubuntu package fonts-adobe-sourcesans3 3.052+dfsg-2; upstream Adobe Source Sans 3.052, unmodified | same package, copy `SourceSans3-Bold.otf` | UI/UX | 2026-10-22 | SIL OFL 1.1 |
| assets/fonts/source_sans_3/SourceSans3-It.otf | Ubuntu package fonts-adobe-sourcesans3 3.052+dfsg-2; upstream Adobe Source Sans 3.052, unmodified | same package, copy `SourceSans3-It.otf` | UI/UX | 2026-10-22 | SIL OFL 1.1 |
| assets/fonts/source_sans_3/OFL.txt | license text from that package's `usr/share/doc/fonts-adobe-sourcesans3/copyright` | copied with the Debian indentation removed | UI/UX | 2026-10-22 | SIL OFL 1.1 |
| assets/fonts/eb_garamond/EBGaramond12-Regular.otf | Ubuntu package fonts-ebgaramond 0.016+git20230418-2 (archive.ubuntu.com, pool/universe); upstream Georg Duffner EB Garamond 0.016, unmodified | `dpkg-deb -x fonts-ebgaramond_0.016+git20230418-2_all.deb x`, copy `x/usr/share/fonts/opentype/ebgaramond/EBGaramond12-Regular.otf` | UI/UX | 2026-10-22 | SIL OFL 1.1 |
| assets/fonts/eb_garamond/EBGaramond12-Italic.otf | Ubuntu package fonts-ebgaramond 0.016+git20230418-2; upstream Georg Duffner EB Garamond 0.016, unmodified | same package, copy `EBGaramond12-Italic.otf` | UI/UX | 2026-10-22 | SIL OFL 1.1 |
| assets/fonts/eb_garamond/OFL.txt | license text from that package's `usr/share/doc/fonts-ebgaramond/copyright` | copied with the Debian indentation removed | UI/UX | 2026-10-22 | SIL OFL 1.1 |
| assets/characters/shader_test/collar_albedo.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/collar_clothmask.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/collar_normal.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/drape_albedo.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/drape_clothmask.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/drape_normal.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/hair_flow.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/hair_strands.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/head_albedo.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/head_skinmask.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/iris_albedo.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/shader_test_bust.glb | assets_src/characters/shader_test/build_shader_test_meshes.py + layout.py | `~/.cache/hymn/blender-5.0.1+dfsg-5/blender --background --factory-startup --python assets_src/characters/shader_test/build_shader_test_meshes.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/shader_test_cloth.glb | assets_src/characters/shader_test/build_shader_test_meshes.py + layout.py | `~/.cache/hymn/blender-5.0.1+dfsg-5/blender --background --factory-startup --python assets_src/characters/shader_test/build_shader_test_meshes.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/skin_pore_detail_normal.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/sleeve_albedo.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/sleeve_bandid.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/sleeve_clothmask.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/sleeve_normal.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
| assets/characters/shader_test/thread_detail_normal.png | assets_src/characters/shader_test/build_shader_test_textures.py + layout.py | `python3 assets_src/characters/shader_test/build_shader_test_textures.py` | Rendering (M1-RND-04 shader test prop) | 2026-10-23 | original |
