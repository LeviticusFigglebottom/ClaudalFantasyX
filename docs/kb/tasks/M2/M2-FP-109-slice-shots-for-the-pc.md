---
id: M2-FP-109
title: "Slice shots in the manifest: the cutscene and zone beats the PC renders for review"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-FP-103, M2-FP-108]
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
All rendering now runs on the PC, from `tests/screenshots/shots.json` (TRACK-RULES "RENDERING GOES TO THE PC",
2026-10-27). No manifest shot covered the slice's cutscene moments or its zone beats, so the playtest fixes
(M2-FP-102..108) couldn't be reviewed as frames.

## Acceptance criteria
- [x] `SliceCutsceneShot` (`game/levels/_tests/slice_shots/`): a shot's setup sets the level, flags, spawn and
  cutscene. The rig plays the cutscene in real time with auto-advance, so settle_frames picks the moment
  (60 fps).
- [x] Shots:
  - `slice_prologue_vigil_line`: the line with the lantern lit;
  - `slice_beach_h05_asha`: "There you are", H05;
  - `slice_beach_h06_toma`: H06, the kneeling pair;
  - `slice_haluna_villagers_village`: the villagers, live;
  - `slice_causeway_head` and `slice_causeway_harrier_view`: the final route.
- [x] test_slice_shots boots every rig headless.
- [ ] PC renders viewed and approved as baselines.

## Review log
