# Handoff — environment (env-art worktree, M3-ENV-01) — 2026-10-24 #7

Session `session_01QmWUfYxd8DMg7XM3MyR6ps`, a worktree branched from `claude/env-art` (not pushed; the env-art
session merges it). Renumber on merge if #7 is taken. Live state: `docs/kb/handoffs/live/env-art.md`.

## Done
- **M3-ENV-01, the Tamsule Bell and the Tidecup arena (status review, reviewer Rendering).** Design notes
  `docs/kb/art/environments/tamsule_bell.md` (with the water-drop contract, §1); the kit
  `assets_src/environments/kits/tamsule_bell/` (18 pieces, Blender job `tamsule_bell_kit`, 25 materials, a ch07 LUT);
  `game/shaders/environment/env_bronze.gdshader`; the `tamsule_bell_kit` import kind; the preview
  `game/levels/_tests/tamsule_bell_kit/` (8 composed cameras); baselines `tamsule_t01_bell_from_the_mouth` and
  `tamsule_t03_oruvel_moorings`; tests in `tools/tests/test_tamsule_bell_kit.py` and
  `tests/unit/test_tamsule_bell_kit.gd`. Details, tri counts, measurements and the read of each shot: the task file.
- **M3-RND-01** filed (rendering, request-from environment): PC GPU to accept or amend the drop contract and build
  the drop's look on `SphereAnchor`.

## In progress
- Nothing.

## Exact next step
1. env-art merges this worktree branch into `claude/env-art`. After merging, delete
   `.godot/imported/<tamsule_bell kit>.glb-*` in the gate worktree before `--import` (the import-script gotcha).
2. Character + Tools: sign off the `tamsule_bell_kit` kind (`game/data/import/tamsule_bell_kit.json`,
   `game/core/import/tamsule_bell_kit_post_import.gd`).
3. Rendering reviews M3-ENV-01; PC GPU answers M3-RND-01.

## Known issues
- Lavapipe only; no crowd; the drop is a placeholder; the port rows read uniform; galleries plain at 150 m (task
  file, "Open issues").

## Files touched
`docs/kb/art/environments/tamsule_bell.md`, `docs/kb/tasks/M3/M3-ENV-01-tidecup-arena.md`,
`docs/kb/tasks/M3/M3-RND-01-reefball-drop-look.md`, `docs/kb/handoffs/live/env-art.md` (swap-in note),
`docs/kb/ownership.md` (row appended), `assets/PROVENANCE.md` (45 rows appended),
`assets_src/environments/kits/tamsule_bell/**`, `assets/environments/kits/tamsule_bell/**`,
`game/shaders/environment/env_bronze.gdshader`, `game/data/import/tamsule_bell_kit.json`,
`game/core/import/tamsule_bell_kit_post_import.gd`, `game/levels/_tests/tamsule_bell_kit/**`,
`tools/dev/blender_builds.json` (job appended), `tests/screenshots/shots.json` (2 shots appended),
`tests/screenshots/baselines/tamsule_t0{1,3}_*.png`, `tools/tests/test_tamsule_bell_kit.py`,
`tools/tests/test_post_import.py` and `tests/unit/test_post_import.gd` (the new kind),
`tests/unit/test_environment_shaders.gd` (the new shader), `tests/unit/test_tamsule_bell_kit.gd`.
