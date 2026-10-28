---
id: M3-CHR-511
title: "Saltwright wrights: the girl at the brazier and two children (Ch6)"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Ch6's Saltwright wrights are capsules (M3-C06-06 #4): the girl at the brazier and two children, line-marks visible
on pushed-up sleeves. Villager-path builds using `liss_textures.line_marks` / `paint_marks` with their own seeds and
placements (act1_npcs.md §2.3).

## Acceptance criteria
- [ ] Built from source under `assets_src/characters/` on the base-body path, host snaps opted in (M2-CHR-11), a
      `tools/dev/blender_builds.json` job verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [ ] Replaces the capsule in every scene listed in the goal (a request task to the scene's owner if it is not ours).
- [ ] Clips for `dig_sand`, `flatten_sand`, `set_in_hole`, `crawl_out` (the children).

## Notes
- Filed 2026-10-27 by the characters track from the Lead's Act I capsule audit (the Act I encounter, boss and level tables).

- 2026-10-28 (chr-npc-wip): ready for review by **rendering**. Built on the villager pipeline (`assets_src/characters/villagers/`, params in `params/<npc>.json`, `host_snaps` + `garment_fit`), a `villager_<npc>` job in `tools/dev/blender_builds.json` verified byte-identical on the three numpy paths (native, `NPY_DISABLE_CPU_FEATURES="X86_V4"`, `"X86_V3 X86_V4"`), PROVENANCE rows, the folder in `game/data/import/characters.json`, a rig-probe entry in `tools/dev/rig_checks.json` (ratchets noted there) and a `test_rig_integrity` class. The module extensions are optional params keys (`top.cuff_roll_m`, `apron.over_trousers`/`flare`/`extra_m`, cloth_d, `_cloth_params`, `_skin.body_size`, `_skin.line_marks`) whose defaults leave every existing villager byte-identical (verify on villager_vendor and villager_reed). Clips: idle, talk, walk plus the story clips in `villager_story_clips.json` (hero_clips' story vocabulary). Stage scenes and face-pose tables in `game/levels/_tests/characters/villagers/`; shots in tests/screenshots/shots.json (no baselines written: the Lead writes them on merge). The capsule swap in the level scenes is M3-CHR-519 (not ours to edit). Budgets: `wright_girl` LOD0 32,866 tris, 2.07 MB GLB, LOD1 15,462 tris; `wright_child_a` LOD0 29,654 tris, 1.81 MB GLB, LOD1 13,859 tris; `wright_child_b` LOD0 31,412 tris, 1.89 MB GLB, LOD1 14,737 tris. Shots `villager_wright_girl_front`, `villager_wright_child_a_front`, `villager_wright_child_b_front`, `villager_wright_girl_clip_arm_held_out`, `villager_wright_child_a_clip_crawl_out`. Line-marks: `liss_textures.line_marks`/`paint_marks` on each villager's own `liss_charts`, right side only, seeds 5111/5112/5113 (Liss's is her own), placements girl forearm 3 + upper arm 1, each child forearm 1; strokes 1.0 mm / 1.4 mm gap / 2.2 mm dots on 2K body maps (`_skin.body_size`). Clips: girl `arm_held_out` (kneeling, the arm held out palm-up, head turned away: W06), `kneel_wait`, `dig_sand`, `flatten_sand`, `set_in_hole` (Liss's specs); children `crawl_out` (on all fours, up through a kneel to stand; the scripts' `@anim wright_child_a/b crawl_out`) and `kneel_wait`. Known: the marks are not legible in the 960x540 full-body shots (they are ~3-5 cm, sub-pixel there); they need a close camera. Scenes: `assets/characters/villagers/wright_*/wright_*_actor.tscn`.

- 2026-10-28 (chr-npc-wip): the Lead re-split the Act I capsule work (docs/kb/qa/act1_final_inventory.md): generic villagers go to the creatures track's villager generator. This build is complete and committed; the Lead decides whether it ships or the generator's output replaces it.

## Review log
