---
id: M3-CHR-510
title: "Four Reeds (the Ch6 barge polers)"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14, M2-CHR-515]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Ch6's four Reed polers are capsules (M3-C06-06 #4). `villager_reed` exists: these are four variants of it (build,
face, wrap, weathering) with the `pole_barge` clip (the pole gripped by the M2-CHR-515 prop grip).

## Acceptance criteria
- [ ] Built from source under `assets_src/characters/` on the base-body path, host snaps opted in (M2-CHR-11), a
      `tools/dev/blender_builds.json` job verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [ ] Replaces the capsule in every scene listed in the goal (a request task to the scene's owner if it is not ours).
- [ ] `pole_barge` and `bow_from_barge` clips.

## Notes
- Filed 2026-10-27 by the characters track from the Lead's Act I capsule audit (the Act I encounter, boss and level tables).

- 2026-10-28 (chr-npc-wip): ready for review by **rendering**. Built on the villager pipeline (`assets_src/characters/villagers/`, params in `params/<npc>.json`, `host_snaps` + `garment_fit`), a `villager_<npc>` job in `tools/dev/blender_builds.json` verified byte-identical on the three numpy paths (native, `NPY_DISABLE_CPU_FEATURES="X86_V4"`, `"X86_V3 X86_V4"`), PROVENANCE rows, the folder in `game/data/import/characters.json`, a rig-probe entry in `tools/dev/rig_checks.json` (ratchets noted there) and a `test_rig_integrity` class. The module extensions are optional params keys (`top.cuff_roll_m`, `apron.over_trousers`/`flare`/`extra_m`, cloth_d, `_cloth_params`, `_skin.body_size`, `_skin.line_marks`) whose defaults leave every existing villager byte-identical (verify on villager_vendor and villager_reed). Clips: idle, talk, walk plus the story clips in `villager_story_clips.json` (hero_clips' story vocabulary). Stage scenes and face-pose tables in `game/levels/_tests/characters/villagers/`; shots in tests/screenshots/shots.json (no baselines written: the Lead writes them on merge). The capsule swap in the level scenes is M3-CHR-519 (not ours to edit). Budgets: `reed_a` LOD0 29,976 tris, 1.87 MB GLB, LOD1 14,019 tris; `reed_b` LOD0 31,300 tris, 1.91 MB GLB, LOD1 14,681 tris; `reed_c` LOD0 29,764 tris, 1.81 MB GLB, LOD1 13,915 tris; `reed_d` LOD0 30,912 tris, 1.89 MB GLB, LOD1 14,487 tris. Shots `villager_reeds_lineup`, `villager_reed_a_clip_pole_barge`. Clips `pole_barge` (loop; the scripts' `@anim reed_a..d pole_barge`) and `bow_from_barge`. Variants of the chapel Reed: tall/rolled sleeves (a), stocky and weathered (b), the youngest, shaved, knee robe over shin wraps (c), the senior with a stubble and an ochre brow band (d). Not done: the pole itself and its M2-CHR-515 grip: a villager GLB has no prop bone, so the pole is a scene prop the barge scene parents to DEF-hand.R; the clip's hands are stacked for a near-vertical pole on the right side. Scenes: `assets/characters/villagers/reed_{a,b,c,d}/reed_*_actor.tscn`.

- 2026-10-28 (chr-npc-wip): the Lead re-split the Act I capsule work (docs/kb/qa/act1_final_inventory.md): generic villagers go to the creatures track's villager generator. This build is complete and committed; the Lead decides whether it ships or the generator's output replaces it.

## Review log
