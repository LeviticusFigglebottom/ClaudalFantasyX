---
id: M2-FP-13
title: Haluna by day at slice quality (B02 Neme's table, B03's four overheard fragments, B05 Low tide)
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-04, M2-FP-09]
milestone: M2
request-from: lead
reviewer: narrative
---
## Goal
Queue item 4 of the m2-slice track. The playable Haluna has Cutscene A, three of the four "Cantor" fragments as interact-only barks, the tideline battle, the save shrine and the causeway trigger. The vertical-slice beat sheet (docs/kb/story/beats/vertical_slice.md §1–2) asks for more: Neme's table (B02) after the beach, the four fragments *overheard by walking past* (B03), and the low-tide beat at the causeway head (B05) before the pilgrimage starts. Stage those in engine.

## Acceptance criteria
- [x] B03 fragment 4: the lane child's skipping rhyme (`ch02_bark_lane`, a new `child` speaker) and a child stand-in in the lane.
- [x] All four fragments play once each when Rhen walks past (TOUCH triggers after `ch02_met_asha`). They don't freeze the player, they advance by themselves, and they never block the battle or causeway triggers. Talking to the villager still plays the bark.
- [x] B02: Rhen wakes at Neme's (the Village spawn) and `ch02_nemes_table` plays in engine (a new `neme` speaker, about 40 words, starting black). It plays once, on the first arrival after the tideline win, because the strip closes the beach path until then.
- [x] B05: the causeway-head trigger plays `ch02_low_tide` (Toma and Asha, about 40 words) in engine before handing off to Cutscene B.
- [x] Data-driven (first_playable.json), loc through `.dlg` `#line:` tags, and tests; the whole-thread test still passes.

## Notes (m2-slice, 2026-10-24)
- **Design change from the claim: B02 plays after the tideline win, not straight after Cutscene A.** The strip closes the beach path until the fight is won (M2-FP-05). Waking Rhen in the village straight after the beach would have let the player skip the first battle. The order is now dawn → the walk up → the fight → noon at Neme's, which still reads as the beat sheet's time jump. New flag `ch02_ate_at_nemes`, set by the scene.
- **Overheard fragments** play on `HalunaStory.overhear`, a second sequencer with the new `CutsceneSequencer.hold_player = false` and `auto_advance` (`overheard_hold_sec` 2.4). Anything else that starts cuts them off.
- **Text I wrote, for narrative's review** (≈40 words each; voice guide and beat sheet followed):
  - `ch02_bark_lane`: the rhyme is "One for the shell and two for the ash, / three for the bell and four for the hush...". It counts verses and foreshadows the bell. It's tagged `#sung` (Audio: diegetic, unaccompanied).
  - `ch02_nemes_table`.
  - `ch02_low_tide`: Asha's last line, "I know. I'm already walking, Toma.", plays the "already walking" beat without echoing B11's "walk behind me".
- Stand-ins: Neme by the Village spawn, the child in the lane. Both are capsules, like the other villagers.
- Docs: first_playable_flow.md, "Haluna's slice beats". PLAYTEST.md steps 4, 5 and 7.
- Gates: dlgc and `--check` (11 scenes, 0 errors); validate_data (which includes banned terms); lint and format; the full Godot suite, 1269 green (including fp_thread and the new `test_haluna_slice_beats.gd`, 5 tests). No manifest shot covers Haluna's playable zone.

## Not in this task (filed separately)
B04, Pila's granddaughter, is M2-FP-14. B11, the dock at night, is M2-FP-15, with M2-ENV-02 for Haluna's night light. The inn and the equipment shop are M2-UI-05. The lintel-gull look-at (H03) and the camera insert of Asha's packed bag in B02 are part of M2-FP-14.

## Review log
