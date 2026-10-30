# Handoff 2026-10-28, character (worktree `chr-ivo-wip`, M3-CHR-540 Ivo Brannick)

## Done
- **Ivo Brannick** as a named Stillguard: `named.ivo` in `assets_src/characters/stillguard/stillguard_variants.json`,
  built by `build_stillguard.py --variant ivo` to `assets/characters/ivo/` (speaker id `ivo`). His own face, skin and
  crop, no helm, the weathered kit, the shield on the left arm, no spear, a chipped front tooth. LOD0 40,256 / LOD1
  17,602 tris; GLBs 2.50 / 0.91 MB.
- Pipeline: `sg_table.named()` / `builds()` (the squad's `variants()` unchanged), `build_moll` `no_prop` (default path
  unchanged: the moll and stillguard jobs re-verified, 40 and 178 identical), `build_stillguard.broken_tooth`,
  `write_materials` skips spear/steel without a spear, `build.sh ivo`.
- Clips: idle, walk, run, talk (right-handed), `hug_lift`, `kneel_palms_flat` (`requested_clips.json` `heroes.ivo`);
  hero_clips' Ivo block (`STORY_LEG_HEROES` lets a non-fighter use the legs' solvers).
- Wiring: job `ivo` (native, X86_V4, X86_V3+V4: 27 identical each), PROVENANCE, import rule + `.glb.import` script,
  rig_checks ratchets, `TestRigIntegrityIvo`, `test_stillguard.TestIvo`, test_hero_clips' dialogue check, stage scenes
  and seven `ivo_*` shots (viewed, no baselines). M3-CHR-519 has the actor path and staging notes for the level owners.

## In progress / next step
- Task at `review` (reviewer: rendering). **Exact next step:** the characters Lead merges `chr-ivo-wip` into
  `claude/characters`, runs the `ivo_*` shots on the integration branch and writes their baselines after viewing them.
- Open: a Ch9 lying-in-shroud pose if the Ch9 owner wants one (not built).

## Known issues
- The stage shots show the shield on his arm through the hug and kneel; in the Ch8 scene it is dropped first (the level
  hides the `Shield` node, M3-CHR-519 note). The crop is the squad's card hair, blocky at face distance. The laugh shot
  uses Asha's face poses and reads a little lopsided. The tooth chip is about 2 mm and barely shows.
- Touching `hero_clips.py` (under `asha/**`) and `build_moll.py` marks most character Blender jobs as changed; only moll,
  stillguard and ivo depend on the changed build code (hero_clips is not imported by any Blender build).

## Files
`assets_src/characters/stillguard/*`, `assets_src/characters/moll/build_moll.py`, `assets_src/characters/asha/hero_clips.py`,
`assets_src/characters/requested_clips.json`, `assets/characters/ivo/`, `assets/PROVENANCE.md`,
`game/data/import/characters.json`, `game/levels/_tests/characters/stillguard/ivo_*.tscn`, `tests/screenshots/shots.json`,
`tools/dev/blender_builds.json`, `tools/dev/rig_checks.json`, `tools/tests/test_stillguard.py`,
`tools/tests/test_rig_integrity.py`, `tools/tests/test_hero_clips.py`, `docs/kb/tasks/M3/M3-CHR-519..540`.
