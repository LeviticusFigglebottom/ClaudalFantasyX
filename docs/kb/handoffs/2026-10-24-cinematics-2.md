# Handoff — cinematics — 2026-10-24 #2

Session: m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`. Task: M2-FP-13, Haluna by day at slice quality.

## Done
- **B02, Neme's table:** plays once, on the first arrival after the tideline win. The scene opens black at Neme's door and sets `ch02_ate_at_nemes`.
- **B03:** the four "Cantor" fragments are overheard as Rhen walks past. They play on a second sequencer that doesn't freeze him or block anything (`CutsceneSequencer.hold_player`). The lane child's rhyme is new.
- **B05, Low tide:** plays at the causeway head before Cutscene B.
- New speakers `neme` and `child`, and their stand-ins.
- Data in first_playable.json; docs in first_playable_flow.md; PLAYTEST updated.
- Filed: M2-FP-14 (B04, plus the B02 bag insert and the H03 gulls), M2-FP-15 (B11), M2-ENV-02 (Haluna night light) and M2-UI-06 (shop and inn).

## In progress
- Nothing. M2-FP-13 is in review (reviewer: narrative, for the three new scripts).

## Exact next step
- m2-slice queue: M2-FP-14 (B04, in my area), then item 5, the Shell Shrine trial.

## Known issues
- No manifest shot covers the playable zone.
- The overheard fragments use the same dialogue box as everything else (bottom of the screen). A smaller "overheard" style is a UI nicety.

## Files touched
- game/flow/haluna_story.gd; game/cutscene/cutscene_sequencer.gd (`hold_player`)
- game/levels/ch02/haluna/haluna.tscn (stand-ins, the lane Talk area, the Overhear triggers)
- game/data/dialogue/ch02/ch02_bark_lane.dlg, ch02_nemes_table.dlg, ch02_low_tide.dlg (new), plus compiled/ and loc/dialogue.csv; speakers.json; flags.tres; first_playable.json; strings.csv
- tests/integration/test_haluna_slice_beats.gd (new), test_haluna_zone.gd
- docs/kb/tech/first_playable_flow.md, docs/PLAYTEST.md, the task files listed above
