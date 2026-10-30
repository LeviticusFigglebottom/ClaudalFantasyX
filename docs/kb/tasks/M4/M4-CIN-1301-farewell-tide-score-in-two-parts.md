---
id: M4-CIN-1301
title: "Request (cinematics → audio): build `farewell_tide` as a held gathering section plus a release tail"
role: audio
status: todo
owner_session: ""
depends_on: [M4-A2P-090]
milestone: M4
request-from: cinematics
---
## Goal
The farewell-tide (act2_ch10.md B09) is held: scene time runs only while the player holds (the Ebbing's gate), and
at the song's top note the prompt changes to "Release". The clutch turns its back on the top note **when the player
lets go**. A single ~90 s file can't do that: the top note would pass while the player isn't holding, or arrive late.

## Acceptance criteria
- [ ] `farewell_tide` (M4-A2P-090) has a **gathering section that can hold** (a loop, or a drone the voices sit on)
      for as long as the player keeps holding through T02–F02 (at least 20 s, open-ended).
- [ ] **The top note and its tail are a separate stem or cue**, started on release: the held top note while the
      clutch turns (T04, about 4 s), then the end on the rise (it doesn't resolve down), through T05 and B10's tail.
- [ ] The two parts join at any loop point without a seam (the release can come at any moment of the gathering).
- [ ] The cue's data names the two parts so the scene can call them (`@music farewell_tide stem=N` or two cue ids).

## Notes
- Cinematics' staging review of act2_ch10.md (M4-C10-01's Review log, item 1). Cinematics builds the release gate
  (`<<event release_input …>>`) and cues the tail on it.

## Review log
