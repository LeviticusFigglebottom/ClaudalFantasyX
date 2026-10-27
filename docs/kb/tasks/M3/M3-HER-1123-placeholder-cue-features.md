---
id: M3-HER-1123
title: "Cutscene cue features the sequencer doesn't perform yet, two of them in the slice (request to slice-polish)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: qa
---
## Goal
The sequencer warns "is not performed yet (placeholder)" for these cue parameters, and drops them. Two are in the
human's slice: ch02_girl_on_the_beach (`@camera grade=`, `@vfx drift=`) and ch03_the_first_verse (six of them).

## Where (cue parameter: scenes)
  - @vfx drift=: ch01_going_under, ch01_hullgnaw_rises, ch01_low_lights, ch01_scuttlers, ch02_girl_on_the_beach, ch03_the_first_verse, ch04_name_board, ch04_seventh_terrace, ch04_spar_wraith, ch05_lanternfall_boats, ch06_burned_lamp, ch09_strand, ch09_the_ebbing
  - @vfx rate=: ch01_low_lights, ch03_the_first_verse, ch04_name_board, ch04_seventh_terrace, ch04_spar_wraith, ch05_kahre, ch05_lanternfall_boats, ch09_strand, ch09_the_ebbing
  - @camera grade=: ch02_girl_on_the_beach, ch03_the_first_verse, ch04_long_way_round
  - @sfx at=: ch03_the_first_verse, ch04_shell_is_set, ch04_the_ink, ch04_wake_neme, ch08_stranger_on_wall, ch08_wall_falls
  - @vfx motion=: ch03_the_first_verse, ch05_kahre
  - @vfx form=: ch03_the_first_verse

## Acceptance criteria
- [ ] Each parameter is performed, or the scripts stop using it.
- [ ] The M3-HER-1123 row leaves tests/integration/qa_known.json, and test_qa_threads passes without it.

## Review log
