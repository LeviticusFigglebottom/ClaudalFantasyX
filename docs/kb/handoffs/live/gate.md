# Gate session live log

The cloud gate session builds `lead/gate-bigN`, runs the full `tools/ci_local.sh` and publishes the results to
`lead/gate-bigN-shots`. It never writes or approves baselines; the Lead views and approves every shot.

## big17

GATE-BUILT big17 @ 1a986abf (branch `lead/gate-big17`), from `lead/gate-big16` @ ff82858c.

Pinned heads, merged with `--no-ff` in this order:
1. claude/new-session-mj8c3c @ 5a9978bc: conflict in pc-gpu.md, kept ours (big16's newer PC text: coverage done).
2. claude/env-art @ b68d1920: clean.
3. claude/characters @ 3346484b: PROVENANCE and shots.json by merge_union.
4. claude/creatures @ f6846325: clean.
5. claude/battle-presentation @ e641579e: PROVENANCE by merge_union; `tests/unit/test_battle_arena.gd` was a
   comment-only conflict, kept ours (the M3-BPR-1305 comment).
6. claude/ui @ b2118f76: clean.
7. claude/hero-integration @ 5c11d034: clean.
8. claude/m2-slice @ 595be6eb: `haluna.tscn` combined both sides (env-art's M3-ENV-753 kit props from ours, plus
   m2-slice's M3-ENV-748/750 capsule removals from theirs; the one hunk was the two sides' different deletions,
   so both were dropped; every Sub/ExtResource reference resolves). M3-CIN-1221's task file takes theirs'
   owner_session and keeps both review lines.
9. claude/env-art-b @ a5e650bd, claude/creatures-b @ d5f7b2b2, claude/act1-chapters @ 483dcb91,
   claude/audio @ 1cb9654d: no new commits since big16, so not merged.

Merge fallout fix (1a986abf): PROVENANCE's line union re-added 3 rows for the deleted ch04 wake dressing (from
claude/characters, which still carries them); big16 had dropped them. Removed.

Checks at the build: validate_data 0 errors 0 warnings; taskboard --check ok; gdlint and gdformat --check clean;
no duplicate loc keys, PROVENANCE rows or shot ids; no conflict markers; no `docs/kb/qa/gate-runs/**` images.

### big17 gate in progress (on 2e266c6a = 1a986abf + this log)
- 2026-10-29 17:15 UTC: `tools/ci_local.sh` started (HYMN_STEP_TIMEOUT=10800). Data 0/0. The tool suite: 182 units,
  1914 tests, 4 failing units, **all four also red on big16 @ ff82858c** (re-run there), so not merge fallout:
  test_freed_cast_lint (`game/vfx/ebbing/ebbing_motes.gd:168` casts `row["node"] as Node3D` before
  is_instance_valid; M3-C09-03), test_npc (crowd_girl_teen too near wright_child_a, 0.229 < 0.28, and its generator
  output differs from the committed json), test_post_import (a `crowd` category with no rules file), test_screenshots
  (`villager_shopkeeper_front` has no baseline).
- ci_local stops at the first failure, so the remaining steps run through the same commands without stopping:
  audio, taskboard, gdlint, gdformat, manifest (612 shots, 2 NO BASE: pell_battle_attack, pell_storm_ch8) all ok.
- Blender: base = the integration branch (`origin/claude/new-session-mj8c3c`, which holds only big13), so ~150 jobs
  (heroes, villagers, crowd, creatures, kits). That takes hours, so it runs after the suite and coverage, in
  parallel with the screenshot capture (both deterministic under load), not before the timing-sensitive suite.
- 20:15 UTC: Godot import clean. **Suite: 3241 run, 5 failed** (6639 s), plus one parse error. Every red but one is
  pre-existing (re-run on big16 @ ff82858c in a worktree, same result):
  - test_ch04_zones::test_the_wakes_field_camera_is_halunas: expects 8 Haluna camera volumes, Haluna has 10 (big16 too).
  - test_iskarra_city::test_the_city_instances_its_pieces_with_kit_materials: "VigilLights has meshes" (big16 too).
  - test_zone_cast::test_a_cast_actor_shows_its_model_and_idles_out_of_step: "the fisher idles", "out of step" (big16 too).
  - test_cutscene_vfx_hosts.gd: parse error, `CutsceneMotes` doesn't exist (ADR 0041's 93c1aa2d removed it; big16 too).
  - **NEW in big17:** test_dialogue_box::test_every_act1_speaker_with_a_model_has_a_portrait: "pell has a model, so a
    portrait". claude/characters' Pell adds `pell_stage.tscn`, and Pell has no portrait yet (speakers.json points at
    `portrait_pell_placeholder`). Branch content, not merge fallout; it needs a Pell portrait render (characters +
    ui-menus), so the gate doesn't fix it.
- Boot smoke: no ERROR lines.
- **Skipped as redundant (the human's productivity directive, 10-29):** the full coverage re-run. With the suite red,
  run_coverage aborts with no numbers ("suite did not pass under instrumentation", as on big14), so ~1.5 h would buy
  nothing. Instead, report-only coverage with `--filter=battle` and `--filter=progression` (game/battle and
  game/progression changed: 30 files since the integration branch).
- **Blender narrowed:** base = `origin/lead/gate-big14` (8707ff90, the last Blender-verified gate: 77 jobs, 2 DIFF),
  not the integration branch: ~85 jobs instead of ~150. It runs alongside the full-manifest capture (612 shots).

GATE-PLAYABLE big17 @ 1a986abf (21:00 UTC, the human asked to play it at once): every non-render check is done.
Data 0/0, lint and format clean, the suite has 3241 run and 5 failed (only the Pell portrait is new; see above), the boot
smoke is clean, and Blender so far is 12/12 identical. The screenshots (67/612 at 21:00, ~01:00 UTC to finish) and
the rest of Blender keep running for the Lead's baseline review; GATE-DONE follows.
LEAD-ASK: the human wants to play big17 now. Merge lead/gate-big17 @ 1a986abf into the integration branch ahead of the
shots? The gate session doesn't touch the integration branch; until then the human can play `lead/gate-big17` directly.
