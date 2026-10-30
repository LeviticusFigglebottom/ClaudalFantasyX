---
id: M4-A2P-1980
title: "Story clips: a per-clip finger curl for a free hand (a fist), and binary .res libraries for Asha and Rhen"
role: character
status: todo
owner_session: ""
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

## Review log
