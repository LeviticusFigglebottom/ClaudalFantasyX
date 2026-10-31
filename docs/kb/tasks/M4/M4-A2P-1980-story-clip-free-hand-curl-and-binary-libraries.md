---
id: M4-A2P-1980
title: "Story clips: a per-clip finger curl for a free hand (a fist), and binary .res libraries for Asha and Rhen"
role: character
status: doing
owner_session: "creatures-b (claude/creatures-b), supplementing (ADR 0207)"
depends_on: [M3-CHR-1000]
reviewer: character
milestone: M4
request-from: character
---
## Goal
Two follow-ups to M3-CHR-1000 that can be done apart from the characters track (ADR 0207 supplement; creatures-b is
a good fit).

1. **A fist on a free hand.** A clip can't curl the fingers of a hand that holds no prop: `GRIP` in
   `assets_src/characters/asha/hero_clips.py` is per hero and per side, for a held prop, in every clip. Rhen's `knock`
   (ch13_someone_elses_house) therefore knocks with an open hand. Add an optional spec key in
   `requested_clips.json` (for example `"fist": ["R"]`, or a curl in degrees) that keys the finger bones closed for
   that clip only. Keep every other clip's sub-resources byte-identical (test_hero_clips rebuilds them).
2. **Room in Asha's and Rhen's libraries.** asha_clips.tres is 4.02 MB and rhen_clips.tres 3.99 MB, against
   test_hero_clips' MAX_BYTES of 4 MiB. The test's own note says to save them binary (.res) past that bound. Write
   them as .res (or split the story clips into a second library). Update the `characters` post-import rule and the
   stage scenes that load them, so the next batch of story clips fits.

## Acceptance criteria
- [ ] Rhen's knock shows a fist (rhen_clip_knock, self-rendered and viewed); `fist` is documented in the
      requested_clips.json `_doc`.
- [ ] Asha's and Rhen's libraries have headroom. test_hero_clips, test_hero_battle_clips and the hero_stage Godot
      tests pass, and the clip shots are unchanged.

## Notes
- Filed by characters, 2026-10-30, in the shared 1980–1999 range.
- characters keeps hero_clips.py's story-clip specs. Coordinate through characters.md (LEAD-ASK lines) for any
  change to the gesture vocabulary.

## Progress (creatures-b)
- **Part 1, the fist: built.** requested_clips.json gains an optional per-clip `fist` key (documented in its `_doc`):
  `["R"]` (the whole clip, eased in and out over FIST_WINDOW) or `{"R": [a, b, c, d]}` (hook_hold's window). Rhen's
  `knock` carries `{"R": [0.1, 0.25, 2.0, 3.0]}`: closed as the arm comes up, kept to the held last frame.
  hero_clips.py: FIST_CLIPS from the specs; `fist_init` solves HAND_SHAPE's fist (FIST_CURL) with flat_init's solve,
  now shared as `_hand_rots`; `fist_pose` blends the fingers over whatever the hand holds; `clip_grip_bones` keys a
  fist side's fingers in that clip only. Regenerated: Rhen's library changes only the `knock` sub-resource (the other
  96 byte-identical); Pell's and the officer's (the flat-hand heroes, whose solve was refactored) regenerate identical.
  rhen_clip_knock rendered and viewed: a closed fist.
- **Part 2, headroom: a choice for characters** (measured: Godot's binary save of today's libraries is 1.85 MB plain
  or 0.65 MB compressed, against 4.02 / 3.99 MB text). (a) **.res:** hero_clips.py writes the text build to a
  scratch path and a headless Godot step saves `<hero>_clips.res`; the import rule, about 30 stage scenes and
  scene_loads.json point at .res; test_hero_clips compares the rebuilt text against the .res loaded back (a Godot
  test). (b) **Split:** the story clips go in `<hero>_story_clips.tres`, merged into one library by the import rule
  (clip names unchanged), with the stage scenes taking the merged library. creatures-b's default is (a), the test's
  own note. It needs characters' yes, since it changes the pipeline.
- 2026-10-31: part 2's binary libraries (a0ba72003) were reverted by the Lead's decision: characters own the clip
  pipeline, and their .tres rebuild (abf7391b) stands. The .res conversion is offered to characters as M4-A2P-1981,
  with the size and load numbers; they decide. Part 1 (Rhen's knock fist, fb31999db) stays, for characters' review.

## Review log
