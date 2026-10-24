# Handoff — cinematics — 2026-10-24 #5

Session: m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`. Task: M2-FP-15, B11 "The dock at night". Also the PC's FP-10 follow-ups (key pitch 30 on H05/H06; key layer 20 → 19).

## Done
- The Drownbell victory travels to Haluna's new `DockNight` spawn. `HalunaStory` lights a data-driven night stand-in (`HalunaZone.set_night`), places Asha and Toma (`place_cast`) and plays `ch03_dock_at_night`. Toma walks up mid-scene, Rhen is sworn in, and the end card follows.
- Night blessings for the four barks, played once Rhen is sworn.
- PLAYTEST step 9 and first_playable_flow.md.

## In progress
- Nothing. M2-FP-15 is in review (reviewer: narrative).

## Exact next step
- M2-FP-17 once M2-CMB-05 lands; otherwise ask the Lead for more queue.

## Known issues
- The stand-in night isn't H10. The field camera frames the dock from its sea end, back toward land; the real H10 shot and light come with M2-ENV-02.
- Asha keeps her kneeling beach pose (no clips).

## Files touched
- game/flow/haluna_story.gd; game/levels/ch02/haluna/haluna_zone.gd, haluna.tscn (the DockNight spawn); game/levels/ch03/first_verse/first_verse_scene.gd
- game/data/flow/first_playable.json; game/data/dialogue/ch03/ch03_dock_at_night.dlg and four ch03_bark_*_night.dlg files (+ compiled, dialogue.csv)
- tests/integration/test_haluna_night.gd (new), test_fp_thread.gd, test_fp_first_verse.gd, test_haluna_zone.gd
- docs: first_playable_flow.md, PLAYTEST.md, the task file
