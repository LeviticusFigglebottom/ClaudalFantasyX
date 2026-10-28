---
id: M3-C09-06
title: "Ch9 music cues and SFX (the Ebbing)"
role: audio
status: review
reviewer: cinematics
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
depends_on: [M3-C09-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch9's scripts (M3-C09-02, `game/data/dialogue/ch09/`) name these cues and sounds. Most don't exist yet, so the chapter plays nearly silent. The brief is act1_ch09.md §6.

## Acceptance criteria
- [x] **Music:**
  - `corrow_night`: the night bed (B01, B03), and its stripped form for B08;
  - `the_ebbing`: the three-part cutscene score, **Act I's centrepiece and an M3 final**. Hummed, never sung with words. The line falls in every phrase, the last chord sinks rather than resolves, and it must not rise. It is an original melody, not the Hush. It plays muffled through stone for B06's cutaway, which is one shot inside the same scene;
  - `dawn_road`: B09.
  - `hush_first_verse` (the piano coda) is reused at B10. It plays its stand-in today.
- [x] **SFX:** `staff_bell_shells` (pitched in the cue's key), `raft_pole`, `harbour_lap`, `shingle_kneel`.
- [x] **The held input pauses the dance, not the music.** The scene's time stops while the player lets go (`CutsceneHoldGate`). Decide how `the_ebbing` breathes through a pause: hold on a pad, or loop the movement's bar. Then tell Cinematics, who may add a music marker.

## Notes
- All Ch9 cues delivered (M3-AUD-05, M3-AUD-819, M3-AUD-822): `corrow_night`, `the_ebbing`, `dawn_road`, `hush_first_verse`; the SFX are files under sfx_dir, `staff_bell_shells` in the cue's key.
- **Decided: the held input pauses the dance, not the music.** `the_ebbing` runs on through a pause (a through-composed lament should not stall or loop a bar), and the dance re-syncs on the next movement: music.json `the_ebbing.markers` (cantor 11.75 s, dance 34.25, dance_full 56.75, thinning 79.25, last_chord 96.125; from the source's markers()). Cinematics: wait on these once the sequencer reports markers (M3-AUD-834).
- Checked 2026-10-27 (M3-AUD-833's resolution test and the thread runs): `--filter=_thread` (Ch1-Ch9, 34 tests) passes with no "no music" or "no sound" warning from any scene; the only sequencer warnings are other kwargs' placeholders (`@vfx drift=`, `@camera grade=`, `@sfx at=`).
- The cue ids are in the scripts as `@music` and `@sfx`. `game/data/cutscene/sequencer.json` `music_stand_ins` can map a stand-in until the real files land.

## Review log
