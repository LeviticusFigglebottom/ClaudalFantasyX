# Handoff — cinematics — 2026-10-24 #9

Session: m2-slice subagent (FP-20/21), in a worktree under the m2-slice session (session_01DQ9tdk8Uatb8Jr6raAkXiC). Items: M2-FP-20 and M2-FP-21 from the m2-slice playthrough pass.

## Done
- **M2-FP-20:** the causeway head is no longer silent before the first save.
  - `Triggers/CausewayHeadUnsaved` has the same box as `Triggers/CausewayHead`: a touch trigger that requires `ch02_met_asha` and is blocked by `ch02_saved_once`.
  - It plays the overheard `ch02_bark_causeway_unsaved`, in which Toma and Asha point Rhen to the town shrine. Rhen is not stopped.
  - The trigger is not `once`: the bark plays on every walk-in until the save, but never over itself.
- **M2-FP-21:** B05 (`ch02_low_tide`) opens on Asha's question, then a choice between "Go now" and "Not yet".
  - "Not yet" ends the scene with `<<event departure_declined>>`, a new event declared in `events.json`.
  - `HalunaStory._end()` then places Rhen at `haluna.ending_decline_spawn` (`CausewayHead`) and hands nothing off. The trigger stays armed.
  - "Go now" plays B05 and hands off to the Shell Shrine, as before.
  - The new config keys are `ending_decline_event` and `ending_decline_spawn` in `first_playable.json` "haluna".
- **Docs:** PLAYTEST step 7, `first_playable_flow.md`, the "declared events" line in `dialogue_format.md`, and the trigger table in the Haluna README are updated.
- **Tests:** `tests/integration/test_haluna_causeway_head.gd` (new, 5 tests, on the real zone).

## In progress
- Nothing. Both tasks are in `review`.

## Exact next step
- **Narrative:** review the four new lines (the bark, plus B05's question, options and reply).
- **Design:** review the choice. A held beat or a visible threshold was the alternative.
- **Lead:** merge.

## Known issues
- "Not yet" moves Rhen about 4 m back with a hard cut (`place_at` snaps the camera). There is no walk-back motion. That reads fine at field distance, but a short walk-back is a polish option.
- The unsaved bark can replay often if a player keeps stepping in and out of the box's edge. It never overlaps itself; a cooldown is possible if testers find it noisy.
- Asha's question plays on every approach, so B05's choice repeats each time Rhen walks in. That is intended.

## Files touched
- game/data/dialogue/events.json
- game/data/dialogue/ch02/ch02_bark_causeway_unsaved.dlg (new), game/data/dialogue/ch02/ch02_low_tide.dlg, their compiled JSON, game/data/loc/dialogue.csv (generated)
- game/data/flow/first_playable.json, game/flow/haluna_story.gd
- game/levels/ch02/haluna/haluna.tscn, game/levels/ch02/haluna/README.md
- tests/integration/test_haluna_causeway_head.gd (new)
- docs/PLAYTEST.md, docs/kb/tech/first_playable_flow.md, docs/kb/tech/dialogue_format.md
- The two task files and this handoff

## Gates
- `gdlint game tests` is clean, and `gdformat -l 120 --check game tests` leaves all files unchanged.
- `validate_data`: 0 errors and 0 warnings. `dlgc --check`: 0 errors. `taskboard --check`: OK.
- Godot test runs, all with 0 failures:

  | Run | Tests |
  |---|---|
  | `--filter=haluna` | 39 |
  | `--filter=fp_` (includes `test_fp_thread`) | 22 |
  | full suite | 1442 |
- Skipped:
  - Coverage: nothing changed in game/battle or game/progression.
  - Tools unittest: nothing changed in tools/.
  - Screenshots: no visible change.
  - Blender: no Blender sources touched.
