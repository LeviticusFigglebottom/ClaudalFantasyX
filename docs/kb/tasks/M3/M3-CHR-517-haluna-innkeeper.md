---
id: M3-CHR-517
title: "The Haluna innkeeper (Ch2 Haluna, a capsule stand-in)"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The Haluna innkeeper is a CapsuleMesh stand-in in `game/levels/ch02/haluna/haluna.tscn` (`NPCs/Town/Innkeeper/StandIn`). A
villager-path build (`assets_src/characters/villagers/`, the M1/M2 villager pipeline), dressed for the trade, with the
field idle and talk clips the town uses.

## Acceptance criteria
- [ ] Built from source under `assets_src/characters/` on the base-body path, host snaps opted in (M2-CHR-11), a
      `tools/dev/blender_builds.json` job verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [ ] Replaces the capsule in every scene listed in the goal (a request task to the scene's owner if it is not ours).
- [ ] Idle, talk and a trade gesture clip (the villager clip set).

## Notes
- Filed 2026-10-27 by the characters track from the Lead's Act I capsule audit (the Act I encounter, boss and level tables).

- 2026-10-28 (chr-npc-wip): ready for review by **rendering**. Built on the villager pipeline (`assets_src/characters/villagers/`, params in `params/<npc>.json`, `host_snaps` + `garment_fit`), a `villager_<npc>` job in `tools/dev/blender_builds.json` verified byte-identical on the three numpy paths (native, `NPY_DISABLE_CPU_FEATURES="X86_V4"`, `"X86_V3 X86_V4"`), PROVENANCE rows, the folder in `game/data/import/characters.json`, a rig-probe entry in `tools/dev/rig_checks.json` (ratchets noted there) and a `test_rig_integrity` class. The module extensions are optional params keys (`top.cuff_roll_m`, `apron.over_trousers`/`flare`/`extra_m`, cloth_d, `_cloth_params`, `_skin.body_size`, `_skin.line_marks`) whose defaults leave every existing villager byte-identical (verify on villager_vendor and villager_reed). Clips: idle, talk, walk plus the story clips in `villager_story_clips.json` (hero_clips' story vocabulary). Stage scenes and face-pose tables in `game/levels/_tests/characters/villagers/`; shots in tests/screenshots/shots.json (no baselines written: the Lead writes them on merge). The capsule swap in the level scenes is M3-CHR-519 (not ours to edit). Budgets: `innkeeper` LOD0 35,940 tris, 2.17 MB GLB, LOD1 17,001 tris. Shots `villager_innkeeper_front`, `villager_innkeeper_face`. Trade clip `welcome_bow`. Looks: stout 50-year-old, low knot, terracotta top, indigo ankle skirt, long undyed apron, sea-blue sash. Hair cards trimmed (26 bun ribbons) to stay inside the 36k LOD0 cap. Known: the hair shader's warm specular reads as light streaks on black hair in the face shot, as on the other villagers. Scene: `assets/characters/villagers/innkeeper/innkeeper_actor.tscn`.

- 2026-10-28 (chr-npc-wip): the Lead re-split the Act I capsule work (docs/kb/qa/act1_final_inventory.md): generic villagers go to the creatures track's villager generator. This build is complete and committed; the Lead decides whether it ships or the generator's output replaces it.

## Review log
