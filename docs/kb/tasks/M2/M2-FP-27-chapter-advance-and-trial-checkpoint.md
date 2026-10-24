---
id: M2-FP-27
title: Advance the chapter at the Ch2→Ch3 hand-off; a checkpoint autosave after the trial; save-slot chapter labels
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: []
reviewer: architect
milestone: M2
request-from: lead
---
## Goal
The Lead's 2026-10-24 13:09 intro audit found this M2-review BLOCKER; it goes ahead of M3. Only debug code calls `Game.set_chapter`, so every save reads "Chapter 0" and the chapter autosave never runs. Set the chapter at Haluna's arrival (2) and at the Ch2→Ch3 hand-off (3, the chapter autosave), and add a checkpoint autosave once the Shell Shrine trial is solved. Then "Return to last save" after a Drownbell loss resumes at the shrine's open door instead of replaying the trial.

## Acceptance criteria
- [x] The chapter is 2 in Haluna and 3 from the causeway on, and the chapter autosave fires at the boundary.
- [x] The Shell Shrine is a location with `place_at` and spawns, and solving the trial writes a checkpoint autosave that resumes at its exit with the door open.
- [x] Save slots show the right chapter label (Prologue for 0).
- [x] Tests cover the Drownbell loss → Return to last save path.

## Notes
- 2026-10-24 m2-slice, **done, for review by architect.**
  - **Chapters:**
    - Chapter 1 at C1-01 (Ch1's `{"chapter": 1}`).
    - Chapter 2 on every Haluna arrival (`haluna.chapter`, `HalunaStory.begin`).
    - Chapter 3 on the causeway (ZoneStory's new `{"chapter": n}` step).
    - Each moves `Game.set_chapter`, so the chapter autosave fires at the boundary.
  - **The shrine is a location:** `ch03/shell_shrine` (`Spawns/Entry` and `Spawns/Exit`, `ShellShrineLevel.place_at`).
  - **The checkpoint:** filling the pool moves the respawn to `Exit` and requests a checkpoint autosave (`shell_shrine.checkpoint_*`). A Drownbell loss followed by Return to last save resumes at the open door, with the door and side pool restored from their flags. `test_fp_thread` walks that path.
  - **Slot labels:** "Prologue" for chapter 0, "Chapter n" otherwise (`SaveSlotInfo.chapter_text`, `test_save_slot_chapter_label.gd`). This touches Systems' `game/ui/save/save_slot_info.gd`, a one-function change, so please review it.

## Review log
