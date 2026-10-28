---
id: M3-C08-101
title: "Ch8 music cues and SFX (the Seawall)"
role: audio
status: review
reviewer: cinematics
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
depends_on: [M3-C08-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch8's scripts (M3-C08-02, `game/data/dialogue/ch08/`) name these cues and sounds. Most don't exist yet, so the chapter plays nearly silent. The brief is act1_ch08.md §6.

## Acceptance criteria
- [x] **Music:**
  - `seawall_hold`: B10-B14, three stems that stack across the waves;
  - `undertow_rising`: B07 after the silence, B08, B09;
  - `virel_bound`: a sting of 8 s or less;
  - `virel_summon`: a sting of 6 s or less;
  - `corrow_aftermath`: B18.
  - Three cues play stand-ins today (`game/data/cutscene/sequencer.json` `music_stand_ins`): `corrow_day` uses `corrow_seawall` (M3-AUD-04), `coilspire_flues` uses `temple_trial`, and `undertow_reach` uses `undertows_reach_p1` (M3-AUD-09). Either ship the cue under the script's id or keep the stand-in as the final.
- [x] **Diegetic:**
  - `current_song`: the same melody as Ch1's statement, heard from Rhen's position only (an `@sfx ... at=figure` today);
  - `pell_storm_note`: a voice doing a storm, never sampled weather;
  - `asha_hum_lullaby`: humming, never a verse.
- [x] **SFX:**
  - the beacon and the walls: `beacon_roar`, `coast_bells`, `watchers_pin`, `hoist_block`, `wall_breach`, `hatchet_rope`;
  - the scripts also call `gulls_far`, `shield_dropped`, `gate_bar`, `spire_door`, `hearth_crackle`, `hearth_settle`, `flue_key_free`, `wind_landward`, `kite_torn`, `crowd_on_stair`, `surf_storm`, `reach_rises`, `reach_grips`, `stone_falls`, `rain_easing`.

## Notes
- All Ch8 cues delivered (M3-AUD-819, M3-AUD-822): `seawall_hold` (three stems), `undertow_rising`, `virel_bound`, `virel_summon` (a battle sfx row), `corrow_aftermath`; `current_song`, `pell_storm_note`, `asha_hum_lullaby` and every SFX id under sfx_dir. The stand-ins for `corrow_day`, `coilspire_flues` and `undertow_reach` stay (each points at the real cue's file).
- Stems in a cutscene: the sequencer plays one file, so `seawall_hold` and `undertow_rising` start on their first stem (M3-AUD-833); stacking the waves needs M3-AUD-834.
- Checked 2026-10-27 (M3-AUD-833's resolution test and the thread runs): `--filter=_thread` (Ch1-Ch9, 34 tests) passes with no "no music" or "no sound" warning from any scene; the only sequencer warnings are other kwargs' placeholders (`@vfx drift=`, `@camera grade=`, `@sfx at=`).
- The rule on B15: no music line on "Captain?". The scene sets `@music silence` before the word, and `test_ch08_thread` checks it.

## Review log
