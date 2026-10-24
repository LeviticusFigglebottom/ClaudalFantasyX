---
id: M3-C09-06
title: "Ch9 music cues and SFX (the Ebbing)"
role: audio
status: todo
owner_session: ""
depends_on: [M3-C09-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch9's scripts (M3-C09-02, `game/data/dialogue/ch09/`) name these cues and sounds. Most don't exist yet, so the chapter plays nearly silent. The brief is act1_ch09.md §6.

## Acceptance criteria
- [ ] **Music:**
  - `corrow_night`: the night bed (B01, B03), and its stripped form for B08;
  - `the_ebbing`: the three-part cutscene score, **Act I's centrepiece and an M3 final**. Hummed, never sung with words. The line falls in every phrase, the last chord sinks rather than resolves, and it must not rise. It is an original melody, not the Hush. It plays muffled through stone for B06's cutaway, which is one shot inside the same scene;
  - `dawn_road`: B09.
  - `hush_first_verse` (the piano coda) is reused at B10. It plays its stand-in today.
- [ ] **SFX:** `staff_bell_shells` (pitched in the cue's key), `raft_pole`, `harbour_lap`, `shingle_kneel`.
- [ ] **The held input pauses the dance, not the music.** The scene's time stops while the player lets go (`CutsceneHoldGate`). Decide how `the_ebbing` breathes through a pause: hold on a pad, or loop the movement's bar. Then tell Cinematics, who may add a music marker.

## Notes
- The cue ids are in the scripts as `@music` and `@sfx`. `game/data/cutscene/sequencer.json` `music_stand_ins` can map a stand-in until the real files land.

## Review log
