---
id: M2-FP-27
title: Advance the chapter at the Ch2→Ch3 hand-off; a checkpoint autosave after the trial; save-slot chapter labels
role: cinematics
status: doing
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: []
reviewer: architect
milestone: M2
request-from: lead
---
## Goal
The Lead's 2026-10-24 13:09 intro audit found this M2-review BLOCKER; it goes ahead of M3. Only debug code calls `Game.set_chapter`, so every save reads "Chapter 0" and the chapter autosave never runs. Set the chapter at Haluna's arrival (2) and at the Ch2→Ch3 hand-off (3, the chapter autosave), and add a checkpoint autosave once the Shell Shrine trial is solved. Then "Return to last save" after a Drownbell loss resumes at the shrine's open door instead of replaying the trial.

## Acceptance criteria
- [ ] The chapter is 2 in Haluna and 3 from the causeway on, and the chapter autosave fires at the boundary.
- [ ] The Shell Shrine is a location with `place_at` and spawns, and solving the trial writes a checkpoint autosave that resumes at its exit with the door open.
- [ ] Save slots show the right chapter label (Prologue for 0).
- [ ] Tests cover the Drownbell loss → Return to last save path.

## Notes

## Review log
