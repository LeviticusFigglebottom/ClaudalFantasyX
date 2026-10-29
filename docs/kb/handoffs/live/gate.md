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
