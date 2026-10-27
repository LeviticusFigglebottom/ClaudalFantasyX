---
id: M2-FP-115
title: "FAST-TRACK: B11 'The dock at night' is staged: shots, a walk out to Asha, Toma's arrival"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-FP-15]
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
Queue item 3, the motion and staging audit. B11, Rhen sworn as Asha's guardian, is one of the beats the slice
"never cuts" (vertical_slice.md). It played with no letterbox and no shots: every line ran over the field camera
behind Rhen, standing at his spawn eight metres from Asha.

## Acceptance criteria
- [x] Three night setups on the zone stage:
  - H10 from the dock end (haluna.md §5), the village's lamps and the sea-glow;
  - N01, a side-on two-shot of Rhen and Asha at the dock end;
  - N02, on Toma coming up the dock.
- [x] The script:
  - letterbox on;
  - H10 while Rhen walks out to her (new night mark `rhen_by_asha`), drifting into N01 as he arrives;
  - the two turn to each other;
  - N02 for Toma's objection, N01 for "This one was, Toma.", N02 for his sigh and "Then you walk behind me."
  The lines are unchanged.
- [x] Tests: test_haluna_night (Rhen beside Asha) and test_haluna_zone (the stage's shots; the night setups are
  unkeyed); haluna 57, 0 failed.
- [ ] A PC shot of B11 needs SliceCutsceneShot to replay HalunaStory's night setup (set_night, place_cast) first.
  Next on slice-polish's list.

## Review log
