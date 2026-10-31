# Gate big39 (fast gate, ADR 0205), rebuilt 04:5x per the Lead's 04:43 decision

Base: lead/gate-big38 @ 37735247, now in integration @ 8b546285 (big38's merge). A dry run into 8b546285 has 0 conflicts.

**Rebuilt:** the first big39 (be2685ce) merged claude/characters @ c10c23ea, which carried the Act III WIP c61187ce (M5-A3P-1202/1982):
7 props with no PROVENANCE row and 2 characters (hesper_oan, ilsabet_rue) with no Blender build job. That's a guardrail (CLAUDE.md §2). The
Lead's decision is to hold that work out. Reverting it inside the batch would break characters' later merges, so I rebuilt this unmerged branch
from big38's tip with the same pins, characters pinned at **b0cf4111** (its "MERGE-READY @ a480b2cb", just before the WIP claim), and
force-pushed it with a lease on be2685ce.

## Pinned heads (merged --no-ff, in order)
- claude/hero-integration @ 349dbe50
- claude/m2-slice @ 1086628b
- claude/env-art @ 986bd43a
- claude/env-art-b @ e36768b0
- claude/characters @ b0cf4111

- characters @ b0cf4111: **row 56, Asha's hem momentum** (a480b2cb, viewed). The Act III WIP (5880037c, c61187ce, c10c23ea) is **held out**.
- env-art-b @ e36768b0: **row 78** (7ddf44d4: the court's loggia shows fire-lit ash).
- hero-integration @ 349dbe50: ReturnPark A/B switches (`--no-park`, `--no-park-prewarm`). The PC's big37 "regression" was a false alarm
  (the display was off); the switches stay, as tooling.
- env-art @ 986bd43a, m2-slice @ 1086628b.
- Held out: claude/act2-plan (still not rebased onto act1-chapters' Ch17) and characters' Act III WIP.

## Build checks
**validate_data 0/0** · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1101 files) · test_gdignore_imports OK · no
conflict markers · no new duplicate PROVENANCE rows.

## Fast-gate results
- Rebuilt tree, fresh import: import check clean · boot 0 ERROR lines · all 9 selected Godot files green (graphics_runtime, haluna_zone,
  battle_stings, frame_clock, oruvel_kit_preview, return_park, scene_change_cover, scene_router_swap, shader_globals_hold).
  (On the first tree, lane A 5/5 and lane B 4/4 @ 4793c37e were green too.)
- Tools: with the WIP out, test_validate_data 23/0, test_items_validate 33/0, test_lattice_validate 15/0, test_boss_validate,
  test_set_piece_validate, test_stillguard and test_blender_builds all pass. The rest is the routed set from the first run: test_hero_locomotion
  (characters), test_ch08_flow (act1-chapters, ch18/kite), test_status_names (ui), test_freed_cast_lint (audio), test_creatures (creatures-b),
  test_cutscene_sfx_files, test_villagers and test_hero_clips. Known: test_palette_check, test_screenshots.

GATE-FAST-DONE @ afd0f02f (the last merge; this log sits on top) (merge-approved: no batch-caused red; characters' Act III WIP and act2-plan held out).
