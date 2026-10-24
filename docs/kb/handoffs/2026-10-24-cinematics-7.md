# Handoff — cinematics — 2026-10-24 #7

Session: m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`. Items: M2-FP-19 (the field menu in Haluna) and the slice playthrough pass. These were Lead top-up items e and f, the last two.

## Done
- **M2-FP-19:**
  - The field menu already opens in Haluna through UI-04's `FieldController` hook.
  - Asha and Toma now join after Cutscene A: `HalunaStory` writes `party_ids` and `reserve_ids` from first_playable.json `party_after_intro`, and backfills saves made after the beach. The menu's Heroes page therefore lists the real party.
  - Test: `tests/integration/test_haluna_field_menu.gd` (3).
- **Playthrough pass:**
  - The whole thread runs headless (test_fp_thread: New Game → the end card, green on this head).
  - Checked PLAYTEST.md against the flow and the zone. Fixed:
    - step 7 sent testers the wrong way (the causeway head is north, *away* from the dock);
    - step 5 now covers Osu, the gull Look and the field menu;
    - step 8 notes Call Ilun works only in the flood;
    - step 9 describes the real night;
    - the integration branch name and the placeholders list are current.
  - Filed two friction tasks:
    - **M2-FP-20:** the causeway head is silent before the first save.
    - **M2-FP-21:** nothing signposts the causeway head as the end of Haluna's day (B04 and the barks are lost after it).

## In progress
- Nothing. The Lead's standing queue and top-up are both done; everything is in review.

## Exact next step
- Lead: queue more work. The obvious candidates on this track:
  - FP-20 and FP-21;
  - removing `call_ilun` once M2-UI-05 lands;
  - swapping Osu's stand-in wall once M2-ENV-04 lands.
- A rendered, interactive playthrough on a real GPU (the PC session) would catch feel issues that headless runs can't.

## Known issues
- This pass was headless: it checks flow, triggers and docs, not feel, pacing or readability on screen.

## Files touched
- game/flow/haluna_story.gd; game/data/flow/first_playable.json (`party_after_intro`)
- tests/integration/test_haluna_field_menu.gd (new)
- docs/PLAYTEST.md
- docs/kb/tasks/M2/M2-FP-19-*.md, M2-FP-20-*.md, M2-FP-21-*.md (new)

## Gates
- lint and format; validate_data; taskboard --check.
- The full Godot suite: 1366 green, including test_fp_thread.
