---
id: M3-C04-05
title: Ch4 music cues and SFX (the_long_way_round and brightwater_crossing final)
role: audio
status: review
reviewer: cinematics
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
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
- [x] `test_ch04_thread` runs with no "no music" or "no sound" warnings from Ch4's scenes.
- [x] Every new asset has its PROVENANCE row and source (CLAUDE.md §2).

## Notes
- Every music id above is in music.json and plays as the sequencer finds it (`haluna_wake` and `brightwater_crossing` through M3-AUD-833's stand-ins); every SFX id is a file under sequencer.json's sfx_dir (act1_cutscene_sfx.py, M3-AUD-818). The zone beds are music.json zone rows (M3-AUD-828).
- The song's markers are in music.json (`the_long_way_round.markers`, one per sung line; tools/tests/test_music_markers.py keeps them equal to the source). Pacing the `#sung` lines with `@wait music=` is Cinematics': the sequencer does not report markers yet (it holds for `max=`), which M3-AUD-834 now asks for.
- Checked 2026-10-27 (M3-AUD-833's resolution test and the thread runs): `--filter=_thread` (Ch1-Ch9, 34 tests) passes with no "no music" or "no sound" warning from any scene; the only sequencer warnings are other kwargs' placeholders (`@vfx drift=`, `@camera grade=`, `@sfx at=`).

## Review log
