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
| assets/audio/music/hush_theme_v2.ogg | assets_src/music/hush_theme_v2.py + tools/audio/synth/ | python3 assets_src/music/hush_theme_v2.py | Audio Director | 2026-10-22 | original |
| assets/audio/music/battle_standard.ogg | assets_src/music/battle_standard.py + tools/audio/synth/ | python3 assets_src/music/battle_standard.py | Audio Director | 2026-10-22 | original |
| assets/audio/music/battle_standard.loop.json | assets_src/music/battle_standard.py + tools/audio/synth/looping.py | python3 assets_src/music/battle_standard.py | Audio Director | 2026-10-22 | original |
| assets/audio/music/temple_trial.ogg | assets_src/music/temple_trial.py + tools/audio/synth/ | python3 assets_src/music/temple_trial.py | Audio Director | 2026-10-22 | original |
| assets/audio/music/temple_trial.loop.json | assets_src/music/temple_trial.py + tools/audio/synth/looping.py | python3 assets_src/music/temple_trial.py | Audio Director | 2026-10-22 | original |
