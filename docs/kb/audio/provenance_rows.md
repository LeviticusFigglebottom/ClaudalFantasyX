# Provenance rows for M1 audio (for the Lead to merge into assets/PROVENANCE.md)

Every file is synthesized from in-repo code (numpy DSP, encoded with ffmpeg/libvorbis).
No samples, soundfonts, downloads, or generative models were used. The regeneration
command for all of them is `python3 tools/audio/render_all.py`.

| path | source | command | role | date | license |
|---|---|---|---|---|---|
| assets/audio/music/hush_theme_sketch.ogg | assets_src/music/hush_theme_sketch.py + tools/audio/synth/ | python3 assets_src/music/hush_theme_sketch.py | Audio Director | 2026-10-22 | Original, project-owned; no third-party content |
| assets/audio/sfx/ui_cursor.ogg | assets_src/sfx/ui_sfx.py + tools/audio/synth/ | python3 assets_src/sfx/ui_sfx.py | Audio Director | 2026-10-22 | Original, project-owned; no third-party content |
| assets/audio/sfx/ui_confirm.ogg | assets_src/sfx/ui_sfx.py + tools/audio/synth/ | python3 assets_src/sfx/ui_sfx.py | Audio Director | 2026-10-22 | Original, project-owned; no third-party content |
| assets/audio/sfx/ui_cancel.ogg | assets_src/sfx/ui_sfx.py + tools/audio/synth/ | python3 assets_src/sfx/ui_sfx.py | Audio Director | 2026-10-22 | Original, project-owned; no third-party content |
| assets/audio/sfx/text_blip.ogg | assets_src/sfx/ui_sfx.py + tools/audio/synth/ | python3 assets_src/sfx/ui_sfx.py | Audio Director | 2026-10-22 | Original, project-owned; no third-party content |

Tooling note: ffmpeg/libvorbis is used only as the encoder (the system binary
/usr/bin/ffmpeg, which is not vendored). numpy is the only Python dependency
(tools/audio/requirements.txt).
