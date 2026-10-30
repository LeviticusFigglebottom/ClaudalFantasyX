---
id: M3-CHR-535
title: "The Tamsule pool-keeper (Ch7): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`poolkeeper` is a capsule stand-in in game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/poolkeeper.json`), host snaps and garment_fit opted in, a
      `villager_poolkeeper` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `chalk_slate` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_poolkeeper_front`, `villager_poolkeeper_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/poolkeeper/poolkeeper_actor.tscn`).

## Notes
- Who: The Tamsule pool-keeper (Ch7, speaker `poolkeeper`; act1_ch07.md: an old Tamsule woman with chalk on her fingers and the draw-slate; keeps Oruvel's name on the roll), about 70. Thin, straight-backed; white hair under an undyed head wrap; a bronze-green long-sleeved wrap top (the Bell's civic green), a dark slate ankle skirt, an undyed apron, a sand sash, sandals. Few reach-bands (2/2). Chalk-pale fingertips are not painted (villager_textures' fingertip term only darkens); the slate and chalk are props. (M3-CHR-535.)
- Budget: LOD0 29,946 tris, 1.74 MB GLB; LOD1 14,004 tris, 0.59 MB.
- Rendered: old, thin, white hair under a wrap, bronze-green top. Chalk on the fingers is not painted (the fingertip term only darkens); the slate and chalk are props for `chalk_slate`.
- Dialogue polish (chr-npc-polish): before, a band of shadowed hair showed under the head wrap's edge at the brow, and the chalk on her fingers was not painted. After: the wrap's edge drawn in to the skin (`headwrap.edge_off_m`) and chalk-pale, unevenly dusted fingertips (`_skin.fingertip_chalk`, a new villager_textures term: the last phalanx toward `chalk_hex`, mottled).

## Review log
