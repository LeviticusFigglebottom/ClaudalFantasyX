---
id: M3-CHR-516
title: "The Haluna smith (Ch2 Haluna, a capsule stand-in)"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The Haluna smith is a CapsuleMesh stand-in in `game/levels/ch02/haluna/haluna.tscn` (`NPCs/Town/Smith/StandIn`). A
villager-path build (`assets_src/characters/villagers/`, the M1/M2 villager pipeline), dressed for the trade, with the
field idle and talk clips the town uses.

## Acceptance criteria
- [ ] Built from source under `assets_src/characters/` on the base-body path, host snaps opted in (M2-CHR-11), a
      `tools/dev/blender_builds.json` job verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [ ] Replaces the capsule in every scene listed in the goal (a request task to the scene's owner if it is not ours).
- [ ] Idle, talk and a trade gesture clip (the villager clip set).

## Notes
- Filed 2026-10-27 by the characters track from the Lead's Act I capsule audit (the Act I encounter, boss and level tables).

- 2026-10-28 (chr-npc-wip): ready for review by **rendering**. Built on the villager pipeline (`assets_src/characters/villagers/`, params in `params/<npc>.json`, `host_snaps` + `garment_fit`), a `villager_<npc>` job in `tools/dev/blender_builds.json` verified byte-identical on the three numpy paths (native, `NPY_DISABLE_CPU_FEATURES="X86_V4"`, `"X86_V3 X86_V4"`), PROVENANCE rows, the folder in `game/data/import/characters.json`, a rig-probe entry in `tools/dev/rig_checks.json` (ratchets noted there) and a `test_rig_integrity` class. The module extensions are optional params keys (`top.cuff_roll_m`, `apron.over_trousers`/`flare`/`extra_m`, cloth_d, `_cloth_params`, `_skin.body_size`, `_skin.line_marks`) whose defaults leave every existing villager byte-identical (verify on villager_vendor and villager_reed). Clips: idle, talk, walk plus the story clips in `villager_story_clips.json` (hero_clips' story vocabulary). Stage scenes and face-pose tables in `game/levels/_tests/characters/villagers/`; shots in tests/screenshots/shots.json (no baselines written: the Lead writes them on merge). The capsule swap in the level scenes is M3-CHR-519 (not ours to edit). Budgets: `smith` LOD0 30,680 tris, 1.90 MB GLB, LOD1 14,372 tris. Shots `villager_smith_front`, `villager_smith_face`. Trade clip `hammer_strike` (loop). Looks: heavy-shouldered 42-year-old, hide apron (cloth_d, less sheen via `_cloth_params`) over indigo knee trousers, undyed shirt with sleeves pushed up above the elbow, soot-dark fingertips. Known: the rolled cuff (`cuff_roll_m` 0.013) barely reads in the front shot (the sleeve tube has 8 rows; the roll band is one): the sleeve reads as pushed up, not visibly rolled. Scene: `assets/characters/villagers/smith/smith_actor.tscn`.

- 2026-10-28 (chr-npc-wip): the Lead re-split the Act I capsule work (docs/kb/qa/act1_final_inventory.md): generic villagers go to the creatures track's villager generator. This build is complete and committed; the Lead decides whether it ships or the generator's output replaces it.

## Review log
