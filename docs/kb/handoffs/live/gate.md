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
