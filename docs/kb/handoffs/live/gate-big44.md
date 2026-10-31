# Gate big44 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ a86c366f (Merge lead/gate-big43).

## Pinned heads
- claude/characters @ 137b6597: row 56 polish (cloud pass 6): the underskirt drawn in under the outer skirt, so no notch shows through its folds.
  The only head with new commits since big43.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1107 files) · test_gdignore_imports OK · no conflict
markers · no new duplicate PROVENANCE rows.

GATE-BUILT @ 06588c8d

## Fast gate
- Selected: 3 test files (plus test_hero_stage for big42's routed red).
- Lane A (mine): 2; lane B (GATE-HELPER): 1, in `gate-big44-lanes-b.txt` @ 2e9f94b8.

## Fast-gate results
- Import and boot clean; log check 0; `Parameter "t" is null`: not seen.
- Lane A (mine, 2 files): test_hero_cutscene_motion 7/0; **test_hero_stage** 11/1, but better: Asha's walk skirt helper bones now **10.6°** off the
  baked clips (17.1° in big42/43). Row 56 in progress. Routed: **characters**.
- Lane B (GATE-HELPER, 1 file @ 2e9f94b8, arrived 08:08): green.
- Tools suite (221 units): with characters' rebuilt asha.glb, asha_lod1.glb and asha_clips.tres, **test_hero_clips, test_hero_locomotion and
  test_rig_integrity Asha are all green**. The rest is the standing routed list: test_b_arenas (env-art-b), test_cutscene_sfx_files' sequencer
  check and test_freed_cast_lint (audio), test_creatures (creatures-b), test_status_names (ui). Known: test_palette_check, test_screenshots.

GATE-FAST-DONE @ de8963c7 (merge-approved: no batch-caused red). In: row 56 polish with Asha's rebuilt outputs. Routed: characters
(test_hero_stage, the skirt helper bones), and the standing list.
