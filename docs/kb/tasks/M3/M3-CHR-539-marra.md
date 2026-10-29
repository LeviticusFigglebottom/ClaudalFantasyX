---
id: M3-CHR-539
title: "Old Marra of Corrow (Ch8-9): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`marra` is a capsule stand-in in game/levels/ch08/corrow/corrow.tscn, game/levels/ch09/corrow_night/corrow_night.tscn (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/marra.json`), host snaps and garment_fit opted in, a
      `villager_marra` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `hold_hands`, `look_back` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_marra_front`, `villager_marra_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/marra/marra_actor.tscn`).

## Notes
- Who: Old Marra, a Corrow fishwife (Ch8-9, speaker `marra`; act1_ch08.md: about 70, mends nets on a doorstep in the low town; one of the 1001 stair-watch, a faded watch-red cord with one knot on her wrist; the only climber who looks back down; in Ch9 holds Toma's hands among the shrouds). Small, round-shouldered, warm; grey hair under a storm-grey head wrap; a faded indigo long-sleeved top, a wrapped storm-grey ankle skirt, an undyed apron, a faded watch-red sash. The netting shawl and the wrist cord are not modelled (no shawl or bracelet piece in villager_costume). Reach-bands left 6, right 6. (M3-CHR-539.)
- Budget: LOD0 29,994 tris, 1.75 MB GLB; LOD1 14,029 tris, 0.60 MB.
- Rendered: small, round-shouldered, storm-grey wrap and skirt, apron, faded watch-red sash. Not modelled: the netting shawl and the one-knot wrist cord (villager_costume has no shawl or bracelet piece); the wrap's underside shows a dark band at the brow at dialogue distance (as Osu's).
- Dialogue polish (chr-npc-polish): before, a dark blue-black band showed between the wrap's edge and her brow (the wrap stood a centimetre off the skin and the hairline cards in its shadow showed under it), and the netting shawl and wrist cord were not modelled. After: the wrap's edge is drawn in to the skin (`headwrap.edge_off_m`), and two new optional pieces: a grey twine netting shawl over the shoulders in a diamond mesh (`shawl`, about 5.6k tris, LOD0 35,578) and the faded watch-red cord with one knot on her left wrist (`wrist_cord`).
- Dialogue polish 2 (chr-npc-polish2): before, the brows read as a flat grey zigzag band. After: painted wiry brow hairs under lighter cards (`_skin.brow_strands`, `_hair.brow_params`), as Fenn's and Osu's.

## Review log
