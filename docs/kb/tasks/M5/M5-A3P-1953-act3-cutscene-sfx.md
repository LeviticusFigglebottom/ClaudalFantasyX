---
id: M5-A3P-1953
title: "Act III cutscene sounds: every @sfx the Act III drafts name"
role: audio
status: review
owner_session: "claude/audio (session_01UPFyE9L9BA3QodpCNJEfAs)"
depends_on: []
reviewer: cinematics
milestone: M5
---
## Goal
Every `@sfx` in docs/kb/story/act3/drafts/ that no row played: 17 ids.

## Acceptance criteria
- [x] **13 new sounds** (assets_src/sfx/act3_cutscene_sfx.py, `assets/audio/act3/sfx/`, ADR 0208), each made from its draft line:
  - sea_flat_lap, names_murmured, clutch_hum;
  - velamir_lullaby_hum: one file for both Asha (Ch18) and Imra (E1), the first verse's first two lines on a closed-mouth "m";
  - shell_into_water, engine_hum_stops, rope_slips;
  - kite_settles, kite_engine_strains, kite_touches_floor: the Kite's engine at kite_foley.py's 55 Hz;
  - pell_farewell_tide: the clutch's rising line, sung;
  - match_struck, wind_in_sails.
- [x] **4 alias rows** for the Kite's own foley: kite_engines_stop, sails_fill, rope_creak and hull_meets_water play kite_engine_stop, kite_sail_fill, kite_rope_strain and kite_landing.
- [x] Rows: `game/data/audio/sfx_cutscene_act3.json` (merged by AudioData.sfx_rows).
- [x] Checks: targets.py `act3/sfx/*.ogg` (-24.5 ±4 momentary); determinism; PROVENANCE.

## Notes
- The drafts aren't in game/data yet. When they move there, act1_audio_audit `--act 3` (once it learns Act III) can confirm every id resolves.

## Review log
