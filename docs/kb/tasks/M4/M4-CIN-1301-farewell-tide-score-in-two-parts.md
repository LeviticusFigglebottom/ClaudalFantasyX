---
id: M4-CIN-1301
title: "Request (cinematics → audio): build `farewell_tide` as a held gathering section plus a release tail"
role: audio
status: review
owner_session: "claude/audio (session_01UPFyE9L9BA3QodpCNJEfAs)"
depends_on: [M4-A2P-090]
reviewer: cinematics
milestone: M4
request-from: cinematics
---
## Goal
The farewell-tide (act2_ch10.md B09) is held: scene time runs only while the player holds (the Ebbing's gate), and
at the song's top note the prompt changes to "Release". The clutch turns its back on the top note **when the player
lets go**. A single ~90 s file can't do that: the top note would pass while the player isn't holding, or arrive late.

## Acceptance criteria
- [x] `farewell_tide` (M4-A2P-090) has a **gathering section that can hold** (a loop, or a drone the voices sit on)
      for as long as the player keeps holding through T02–F02 (at least 20 s, open-ended).
- [x] **The top note and its tail are a separate stem or cue**, started on release: the held top note while the
      clutch turns (T04, about 4 s), then the end on the rise (it doesn't resolve down), through T05 and B10's tail.
- [x] The two parts join at any loop point without a seam (the release can come at any moment of the gathering).
- [x] The cue's data names the two parts so the scene can call them (`@music farewell_tide stem=N` or two cue ids).

## Notes
- Cinematics' staging review of act2_ch10.md (M4-C10-01's Review log, item 1). Cinematics builds the release gate
  (`<<event release_input …>>`) and cues the tail on it.
- 2026-10-30 (claude/audio): done in `assets_src/music/act2/farewell_tide.py`, as two cue ids in music.json.
  - `farewell_tide` is the gathering: bars 1-14 as composed (the clutch climbs to F#, a step short of the top), then a
    20 s loop (4 bars of 5/4 at 60 BPM) that holds for as long as the player does. The loop's seam flux is x1.1.
  - `farewell_tide_release` is a one-shot: the gathering's own drone under the top note (the clutch on G#, the flute
    on D#6), held about 4.5 s while the clutch turns, then the backs turned (clicks and the harp's root) and silence,
    ending on the rise. Its top note is set 1 LU over the loop. A release at any of eight points in the loop lands
    between -1.1 and +2.2 LU, and MusicDeck puts the change on the gathering's next half-beat (at most 0.5 s).
  - **For cinematics:** on the release gate in ch10_farewell_tide.dlg, play the tail:
    `<<event release_input release_tide>>` then `@music farewell_tide_release fade=0.5`. The scene's existing
    `@music farewell_tide fade=0.5` starts the gathering. sequencer.json has stand-ins for both.

## Review log
