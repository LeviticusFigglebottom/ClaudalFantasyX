---
id: M2-FP-112
title: "FAST-TRACK: Cutscene B (the first verse): Rhen and Toma on their real bodies"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-HER-1101, M2-FP-103]
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
The first verse (Cutscene B) has its own stage and no FieldController, so hero-integration's attach never reached
it: Rhen and Toma were still capsules beside Asha's real model through the slice's emotional peak.

## Acceptance criteria
- [x] FirstVerseScene attaches HeroFieldActor bodies to its stage at `_ready` (as the prologue does). The held
  poses (Toma's `sit_steps`) and the camera breath apply.
- [x] test_fp_first_verse asserts both bodies; first_verse 2, fp_thread 2, memory 6 and shell_shrine 15, 0 failed.
- [x] Shot `slice_verse_steps` (the S06 steps beat) for the PC.
- [ ] Rhen's `sit_steps` is a requested clip: he stands beside the seated Toma until it's built.

## Review log
