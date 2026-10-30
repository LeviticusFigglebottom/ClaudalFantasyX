---
id: M4-A2P-1702
title: "Act II first-time hints: Seven heroes, Records, Dark shrines (act2-plan's text), once, on time, dismissible; Ch1's objective tip at the bell room"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: narrative
milestone: M4
request-from: lead
---
## Goal
The Act II first-time hints, with the same once, timing and dismiss checks as M4-A2P-1701. The text is act2-plan's
(docs/kb/plan/act2/ui/tutorials.md; TIP_* in ch13.csv and ch14.csv). The rows and seen flags are ui-menus'.

## Acceptance criteria
- [x] Seven heroes on `ch10_started`: a flag tip, caught up on the first field if the flag was set in the fade-in.
- [x] Records on `ch13_archive_read`.
- [x] Dark shrines at the first shrine in reach once `ch14_declared_heretics` is set, never before.
- [x] Each tip is once per save (`tut_records_seen`, `tut_dark_shrine_seen` declared) and dismissed by pressing what
      it names.
- [x] M4-A2P-1004 (narrative's request):
  - **F1:** done in M4-A2P-1701.
  - **F5:** the objective tip now waits for `ch01_saw_bell_room` (a Ch1 field_ready fires in the fade-in, before
    `ch01_started`) or `ch02_met_asha` on the slice route.
  - **F8:** a layout trigger's `save_shrine` payload is tagged `shrine`.
  - **Optional wording:** "errand" is now "objective", and "items, gear … the map" is now "Items, Equip … the Map".
- [x] test_tutorial_tips 9/0.

## Notes
- **Not here, by act2-plan's plan:** the Act II Vowbound (calling was taught in Act I; each new one is a new Call row)
  and the document reader (it teaches itself).
- **Waiting:**
  - The Swell-mode tip waits for Progression's `<mode>_unlocked` flags (none exist yet).
  - The new statuses' lessons are battle prompts (`TUT_CH10_ROOTED`, `TUT_CH10_DRAIN` and the rest), combat's
    `encounters.json` rows, which aren't in yet. The help line shows them once per fight when they land, as
    TUT_CH01_COMMANDS does.

## Review log
