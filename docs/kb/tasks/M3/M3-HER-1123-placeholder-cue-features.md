---
id: M3-HER-1123
title: "Cutscene cue features the sequencer doesn't perform yet, two of them in the slice (request to slice-polish)"
role: cinematics
status: doing
owner_session: "slice-polish (session_01F3vrUPLtDQMGSRrMHJtpz1)"
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

### 2026-10-28: Act I too (the hero-motion audit, M3-HER-1132)
The same cue features are placeholders in 17 Act I scenes: `@vfx drift=` and `rate=` (ch01_low_lights,
going_under, scuttlers, hullgnaw_rises; ch04_name_board, seventh_terrace, spar_wraith; ch05_lanternfall_boats;
ch06_burned_lamp; ch09_strand, the_ebbing), `@vfx motion=` (ch05_kahre), `@sfx at=` (ch04_wake_neme, shell_is_set,
the_ink; ch08_wall_falls, stranger_on_wall) and `@camera grade=` (ch04_long_way_round). They're implemented once in
the sequencer, so one fix covers the slice and Act I.

## Review log
- 2026-10-28 slice-polish:
  - **Done:** `@vfx drift=`, `rate=` and `motion=` are performed: cues build Rendering's GlimmerField through
    `apply_cue` (CutsceneVfx). `@sfx at=` was done earlier (CutsceneSound).
  - **Left:** `@camera grade=` needs a grade table no one has built, requested as **M3-ENV-106**. `@vfx form=` is
    reserved in glimmer.json (no form shape exists).
  - The qa_known row stays until grade= lands.

