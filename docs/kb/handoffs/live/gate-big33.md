# Gate big33 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 8889542f (Merge lead/gate-big32). Act III (M5-A3P) work rides the batches from
here on (ADR 0207).

## Pinned heads (merged --no-ff, in order; the Lead's priority first)
- claude/act1-chapters @ c2616407
- claude/m2-slice @ 97c591c3
- claude/hero-integration @ 7fbb97a9
- claude/env-art @ deff0d41
- claude/env-art-b @ 1281c188
- claude/act2-plan @ fee86431
- claude/ui @ d6d05a6d
- claude/creatures @ f2c0e49b
- claude/audio @ 14f59173
- claude/characters @ 425abec3
- claude/creatures-b @ 8dfdbaa9
- claude/battle-presentation @ 78b0a1bb
- claude/creatures @ b05a9294

The Lead's list is in: act1-chapters 7a37c3d5 (the Ch6/Ch8 Act I objectives FAST-TRACK), slice-polish's 97c591c3 on
claude/m2-slice (M4-A2P-070: Haluna's beach actor posed a frame after the swap, part of the Haluna add-frame split),
integration-qa's newest (the --ready-profile probe), and every other new head.

## Resolutions
- ownership.md: three new Act III claim rows (env-art's Ch20 memory rooms and Undertow kit; env-art-b's Ch17 Hollowmere
  dry-dock; creatures-b's Act III bosses and Vowbound), kept by the marker strip. There are no duplicate paths, and the
  table is intact.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1072 files) ·
test_gdignore_imports OK · no conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ c2f4ec9f

## Fast gate
- Selected: 55 test files (plus test_qa_capsules for the routed red).
- Lane A (mine): 28; lane B (GATE-HELPER): 27, in `gate-big33-lanes-b.txt` @ 1067c447.

## Fast-gate results
- Import check clean · boot 0 ERROR lines · log check 0.
- Lane A (mine, 28 files): 27 green. test_qa_capsules 3/1, routed since big30 (act1-chapters' foes have no bodies).
- Lane B (GATE-HELPER, 27 files @ 1067c447, arrived 22:49): 26 green.
  - **test_debug_overlay** 14/1: `res://game/core/scene_router.gd names SceneSwapProbe` (release strips game/core/debug/). It is
    integration-qa's 7fbb97a9 (M3-HER-1168 --ready-profile), a doc comment at scene_router.gd:74; the same line is on
    claude/hero-integration, and the test is a static scan. Routed: **integration-qa / hero-integration** (reword the
    comment without the class name).
- Tools suite (-j 2, 215 units):
  - New from **Act III**: act2-plan's 9adf414c (M5-A3P-1000) puts the Ch17–Ch21 scripts in the game, and they call what
    doesn't exist yet:
    - test_cutscene_sfx_files: music cues (credits_suite, dace_ledger, ending_dock and others) and Ch17 SFX files;
    - test_villagers: `ch17_bark_lookout.dlg: clerk nod` has no clip;
    - test_hero_clips: scripts call hero clips (Sefir, Toma and others) that don't exist.
    The same holds on claude/act2-plan alone. Routed: **act2-plan** (put the gaps on the tests' TODO/known lists or file
    the requests with audio, characters and creatures; the scripts may land before their assets).
  - Unchanged, still routed: test_rig_integrity (characters); test_act1_audio_audit and test_battle_vfx_coverage
    (act1-chapters). Known: test_palette_check, test_screenshots.

GATE-FAST-DONE @ 8d752059 (merge-approved: no batch-caused red). Routed: act2-plan (Act III scripts' missing
cues and clips: test_cutscene_sfx_files, test_villagers, test_hero_clips); integration-qa (test_debug_overlay); act1-chapters
(test_qa_capsules, test_act1_audio_audit, test_battle_vfx_coverage); characters (test_rig_integrity). Known: test_palette_check,
test_screenshots.
