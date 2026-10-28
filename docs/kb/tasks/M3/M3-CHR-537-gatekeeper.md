---
id: M3-CHR-537
title: "The Corrow stair-watch gatekeeper (Ch8): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`gatekeeper` is a capsule stand-in in game/levels/ch08/corrow/corrow.tscn (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/gatekeeper.json`), host snaps and garment_fit opted in, a
      `villager_gatekeeper` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `open_gate` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_gatekeeper_front`, `villager_gatekeeper_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/gatekeeper/gatekeeper_actor.tscn`).

## Notes
- Who: The stair-watch's gatekeeper at Corrow's watch-red wall-gate (Ch8 W07, `@anim gatekeeper open_gate`; act1_ch08.md: lets the party through for the Cantor; the gate Kerrid kept in 1001), about 45. Solid, unhurried; short black hair, a dark stubble; a storm-slate long-sleeved wrap top, indigo shin trousers, a watch-red sash (the watch's colour, corrow.md: browner than the Order's lacquer red), a watch-red headband, sandals. Reach-bands left 4, right 4. (M3-CHR-537.)
- Budget: LOD0 29,200 tris, 1.85 MB GLB; LOD1 13,629 tris, 0.67 MB.
- Rendered: watch-red sash and headband on storm slate and indigo; reads as a watch member, not the Order (watch_red #8E3B2E, not lacquer red).

## Review log
