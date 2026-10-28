---
id: M3-CHR-531
title: "The Pemakar elder (Ch5): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`elder` is a capsule stand-in in game/levels/ch05/pemakar/pemakar.tscn (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/elder.json`), host snaps and garment_fit opted in, a
      `villager_elder` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `give_boat` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_elder_front`, `villager_elder_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/elder/elder_actor.tscn`).

## Notes
- Who: The Pemakar elder who puts a folded leaf-boat with a pinch of rice in it into Asha's hands (Ch5 B04, `@anim elder give_boat asha`), about 74, a woman. Small and upright; white hair in a low knot; a lacquer-black long-sleeved wrap top, an ash-grey ankle skirt, a gold-ochre sash wound twice, a lacquer-red narrow apron panel (a festival cloth), sandals. Reach-bands left 3, right 3 (Pemakar is a harbour). (M3-CHR-531.)
- Budget: LOD0 35,158 tris, 2.13 MB GLB; LOD1 16,608 tris, 0.81 MB.
- Rendered: small, upright, white knot; lacquer-black top with a lacquer-red panel and gold sash. The rice and the boat are props for `give_boat` (two hands).
- Dialogue polish (chr-npc-polish): before, her white knot had a few bright streaks of solid grey cards. After: the grey cards (70%) as thinner strands (`_hair.grey_strands`); reads as white hair drawn back.

## Review log
