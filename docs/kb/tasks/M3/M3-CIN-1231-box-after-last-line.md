---
id: M3-CIN-1231
title: "Request (slice-polish, game/cutscene/**): the dialogue box keeps an advanced line up through a scene's silent holds"
role: cinematics
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
act1-chapters' playthrough stills (`tools/act1/cutscene_stills`, `STILLS_EVERY=5`) show the box keeping the
last line on screen after the player has advanced it, while the script runs on with no line: cameras, walks, long
`@wait`s. `CutsceneSequencer._line` returns on `advance_requested` with `overlay.box` still visible, and the box is
dismissed only in `_finish` (M2-UI-202). In a scene that ends with a held image, the advanced line covers the lower
third for the whole hold. Example: `ch04_long_way_round`, where "I will." stays up over C01 and C02, 30 s of the three
walking out to the causeway (the beat's "hold C01 long as the three get small"), and the walkers are under the box
for most of C01. Other Act I scenes with long silent holds after a line: `ch08_cut_rope`,
`ch09_the_road_out`, `ch08_stranger_on_wall`.

Ask: once a line is advanced and the next step isn't a line or a choice, fade the box out (as `_finish` does), and
open it again on the next line. Timed lines (`TAG_TIMED`) and barks keep today's behaviour.

## Acceptance criteria
- [ ] After an advanced line followed by cues only, the box is hidden within its fade time.
- [ ] A unit test in `tests/unit/test_cutscene_*` covers it. act1-chapters re-renders `ch04_long_way_round` and the
  scenes above.

## Review log
