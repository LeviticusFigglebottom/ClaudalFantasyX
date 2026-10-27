---
id: M2-FP-115
title: "FAST-TRACK: B11 'The dock at night': Rhen walks out to Asha, and they turn to each other (an E scene: the rail camera)"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-FP-15]
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
Queue item 3, the motion and staging audit. In B11, Rhen is sworn as Asha's guardian; it is one of the beats the slice
"never cuts" (vertical_slice.md). Rhen spoke his lines from his spawn, eight metres from Asha, and nobody moved but
Toma.

## Acceptance criteria
- [x] B11 is an **E** scene: vertical_slice.md defines E as in-engine, with no letterbox, and the player keeps the
  camera rail. So the staging is in the bodies:
  - Rhen walks out to her at the dock end (new night mark `rhen_by_asha`);
  - the two turn to each other;
  - Asha turns to Toma as she answers him.

  The lines are unchanged.
- [x] A first pass (4f616566) also letterboxed B11 and cut between three new camera setups. That broke the E
  definition, so it was taken out again (the B02 two-shot too, before it landed). The scene keeps the rail.
- [x] Tests: test_haluna_night (Rhen beside Asha); haluna 57, 0 failed.
- [x] A PC shot of B11: `slice_dock_night_yes`. The rig's new `story_call` runs HalunaStory._night.

## Review log
