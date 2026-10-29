---
id: M3-CHR-509
title: "The Order clerk (Ch6, speaker `clerk`)"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Ch6's Order clerk is a capsule (M3-C06-06 #4, act1_ch06.md §9 #27: speaker `clerk`, CHAR_CLERK). A villager-path
build (the villager pipeline, `assets_src/characters/villagers/`), in the Order's colours without armour.

## Acceptance criteria
- [ ] Built from source under `assets_src/characters/` on the base-body path, host snaps opted in (M2-CHR-11), a
      `tools/dev/blender_builds.json` job verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [ ] Replaces the capsule in every scene listed in the goal (a request task to the scene's owner if it is not ours).
- [ ] Clips for the scripts' `hand_over` proposal and talk/idle.

## Notes
- Filed 2026-10-27 by the characters track from the Lead's Act I capsule audit (the Act I encounter, boss and level tables).

- 2026-10-28 (chr-npc-wip): ready for review by **rendering**. Built on the villager pipeline (`assets_src/characters/villagers/`, params in `params/<npc>.json`, `host_snaps` + `garment_fit`), a `villager_<npc>` job in `tools/dev/blender_builds.json` verified byte-identical on the three numpy paths (native, `NPY_DISABLE_CPU_FEATURES="X86_V4"`, `"X86_V3 X86_V4"`), PROVENANCE rows, the folder in `game/data/import/characters.json`, a rig-probe entry in `tools/dev/rig_checks.json` (ratchets noted there) and a `test_rig_integrity` class. The module extensions are optional params keys (`top.cuff_roll_m`, `apron.over_trousers`/`flare`/`extra_m`, cloth_d, `_cloth_params`, `_skin.body_size`, `_skin.line_marks`) whose defaults leave every existing villager byte-identical (verify on villager_vendor and villager_reed). Clips: idle, talk, walk plus the story clips in `villager_story_clips.json` (hero_clips' story vocabulary). Stage scenes and face-pose tables in `game/levels/_tests/characters/villagers/`; shots in tests/screenshots/shots.json (no baselines written: the Lead writes them on merge). The capsule swap in the level scenes is M3-CHR-519 (not ours to edit). Budgets: `clerk` LOD0 30,376 tris, 1.89 MB GLB, LOD1 14,218 tris. Shots `villager_clerk_front`, `villager_clerk_face`, `villager_clerk_clip_heat_iron`. Clips `heat_iron` (loop) and `iron_into_water` (the scripts' `@anim clerk` calls in ch06_raid / ch06_barge) and `hand_over` (shared give_r). Looks: the Order's colours without armour: ivory robe, still-blue tabard, lacquer-red sash. The brine-iron is a scene prop (no prop bone in a villager GLB). Scene: `assets/characters/villagers/clerk/clerk_actor.tscn`.

## Review log
