---
id: M3-C04-05
title: Ch4 music cues and SFX (the_long_way_round and brightwater_crossing final)
role: audio
status: todo
owner_session: ""
depends_on: [M3-C04-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch4's scripts (`game/data/dialogue/ch04/`) already call every cue in act1_ch04.md §6. Today each one warns "no music" or "no sound" and plays nothing:
- **Music:** `haluna_night` (exists), `haluna_wake` (diegetic feast), **`the_long_way_round`** (diegetic, an original folk tune sung by a village; M3 final), `hearer_hum`, `ysolde_theme`, `haluna_dawn` (exists), **`brightwater_crossing`** (M3 final), `spar_wraith` (two stems), `name_board_home`. The derelict's `derelict` ambience has no script call yet: give it the ferry zone's music row for the derelict, or ask Cinematics for a cue.
- **SFX:** `wake_lamps_out`, `shell_set`, `neme_humming`, `ink_brush`, `gangplank`, `lookout_call`, `derelict_wheel_turning`, `sails_luff_and_fall`, `name_board_prise`.
- **The song's lyric** is in `ch04_shell_is_set.dlg` (lines `ch04_shell_012` to `_015` and `_021`, tagged `#sung`). Pace them to the tune with `@wait music=<marker>` once the cue exists (SPEC §16 Q4/Q5 for voices: until then a small ensemble of solo instruments carries it).
- Give the two zones their beds: `ch04/haluna_wake` plays `haluna_night`, and `ch04/brightwater_ferry` plays `brightwater_crossing`. end_card.gd names a zone music table (`game/data/audio/music.json` zones), but it isn't on the m2-slice branch: use it if it has landed, and otherwise ask Cinematics for a `@music` at each arrival.

## Acceptance criteria
- [ ] `test_ch04_thread` runs with no "no music" or "no sound" warnings from Ch4's scenes.
- [ ] Every new asset has its PROVENANCE row and source (CLAUDE.md §2).

## Notes

## Review log
