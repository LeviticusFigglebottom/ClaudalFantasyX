---
id: M2-FP-105
title: "FAST-TRACK: the slice's first battle teaches the timeline and the commands (Pillar 4)"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: []
reviewer: combat
milestone: M2
request-from: lead
---
## Goal
On the M2 route (prologue → Haluna) the tideline is the first battle the human meets. Ch1's command tip and the
Hullgnaw's timeline tip sit behind the Act I switch, so the slice's first fight opened with no guidance at all.

## Acceptance criteria
- [x] `ch02_tideline` opens on `TUT_TIDELINE_TIMELINE` ("The turn order runs down the right, next at the top. Every
  action costs time: watch where yours will land before you choose.") and Rhen's first turn shows
  `TUT_CH01_COMMANDS`.
- [x] Test: test_slice_first_battle.

## Notes
- When the Lead flips the Act I switch, Ch1 teaches both first; act1-chapters may then drop these two keys from the
  tideline (or keep them as a reminder).

## Review log
