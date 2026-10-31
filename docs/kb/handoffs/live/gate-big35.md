# Gate big35 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 9317c6b6 (Merge lead/gate-big34).

## Pinned heads (merged --no-ff, in order; the Lead's priority first)
- claude/act1-chapters @ 782ff863
- claude/hero-integration @ 6555ccf4
- claude/env-art @ 6f0aee74
- claude/env-art-b @ b3e7c493
- claude/ui @ fa75e3ed
- claude/creatures @ b97186e3
- claude/audio @ 1c14fa74
- claude/characters @ f0ce0f53
- claude/battle-presentation @ 94ee0995

- act1-chapters @ 782ff863 carries the 23:05 FAST-TRACK: d74da756 (a touch beat entered while a scene plays is kept and plays
  when the scene ends), f46ec395 (Ch9's landing trigger and its marker on the strand), and Ch8's interior headless.
- integration-qa's cross-zone prewarm (the Drownbell, 8.2 s on the PC) isn't posted yet. A watcher is on
  claude/hero-integration; it is merged between test runs, followed by a fresh import and a re-gate.

## Resolutions
- Every merge was clean. On flags.tres, merge_union used what the two real merge bases agree on; no flag was dropped or
  duplicated (one line gained a trailing comma before the appended rows).

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1083 files) ·
test_gdignore_imports OK · no conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ a22bb284

## Fast gate
- Selected: 140 test files.
- Lane A (mine): 70; lane B (GATE-HELPER): 70, in `gate-big35-lanes-b.txt` @ f91030ac.

## Mid-batch (the Lead, 00:26): ReturnPark, the human's last playtest item
- **claude/hero-integration @ 74c732fc**: eea6c24e, row 74, a fight builds its cross-zone return scene while it runs
  (ReturnPark, ADR 0209). The Drownbell → Haluna field-in goes from 3.39 s to 1.05 s headless. Clean; checks clean (validate_data
  0/0, taskboard, gdlint, gdformat 1085).
- To avoid testing a half-imported tree (big24's lesson), lane A was stopped at 50 of its 70 files (50 done, all green but the
  routed test_qa_capsules), then the merge, then a fresh import. The re-gate is 33 files: lane A's 20 unrun ones, the
  merge's selection, and every scene_router, return_park, battle_return, field_battle, battle_request and resident test,
  plus a fresh tools suite. Every log is scanned for the engine's `Parameter "t" is null` (1 in 5 parked runs logged it,
  per the Lead); if it appears it is routed to integration-qa and doesn't hold the batch.

## Fast-gate results
- Lane A, before the stop: 50 of 70 files done on the pre-ReturnPark tree. 49 green; test_qa_capsules is the routed red (act1-chapters).
- Lane B (GATE-HELPER, 70 files @ f91030ac, arrived 00:39): 69 green.
  - **test_battle_act2_ability_vfx** 2/1: the Act II foes' skills (flat_engine flat_pulse and engine_churn; malcor_venn venn_sentence,
    grapnel_line, rod_sweep, still_hand and level_guard; abiding_first and abiding_guard hook_* and close_ranks; court_stillguard
    seize_the_line; storm_crawler storm_drag) have no effect in battle-presentation's map. Red on claude/act1-chapters alone
    (probed). Routed: **act1-chapters** (request the effects from battle-presentation).
- Re-gate after ReturnPark (33 files, fresh import): import check clean · boot 0 ERROR lines · log check 0 · 32 green.
  - test_debug_overlay 14/1: `scene_router.gd names SceneSwapProbe`, the doc comment from big33. Still routed: **integration-qa**.
  - **`Parameter "t" is null`: not seen** in any test log or the boot log.
- Tools suite (fresh, on the final tree; 217 units): **test_rig_integrity is green for every rig**. The rest are the routed set:
  test_act1_audio_audit and test_battle_vfx_coverage (act1-chapters); test_cutscene_sfx_files, test_hero_clips and test_villagers
  (act2-plan's Act III scripts). Known: test_palette_check, test_screenshots.

GATE-FAST-DONE @ 5be8a3b7 (merge-approved: no batch-caused red). In: act1-chapters' 23:05 FAST-TRACK and
**ReturnPark** (the human's last playtest item). Routed: act1-chapters (test_qa_capsules, test_battle_act2_ability_vfx,
test_act1_audio_audit, test_battle_vfx_coverage); integration-qa (test_debug_overlay); act2-plan (Act III cues and clips).
Known: test_palette_check, test_screenshots.
