---
id: M3-CHR-527
title: "The Oruvel scale-man (Ch1): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`scaleman` is a capsule stand-in in game/levels/ch01/oruvel/oruvel.tscn (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/scaleman.json`), host snaps and garment_fit opted in, a
      `villager_scaleman` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `weigh_stamp`, `nod` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_scaleman_front`, `villager_scaleman_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/scaleman/scaleman_actor.tscn`).

## Notes
- Who: The scale-man of Oruvel's scale-hull (Ch1 C1-07, speaker `scaleman`; act1_ch01.md: an Order-licensed dealer who weighs plain brass by the pound and stamps each chit 'Unbound, by the Level': the Order's only presence in Oruvel), about 50. Neat, soft-handed, a little stout; close-cropped greying hair, clean-shaven; an ivory long-sleeved shirt in the Order's cloth (the licence shows), a slate-grey calf skirt, a narrow gold-ochre licence sash, sandals. No reach-bands: he never dived. (M3-CHR-527.)
- Budget: LOD0 29,718 tris, 1.87 MB GLB; LOD1 13,890 tris, 0.70 MB.
- Rendered: the first face render showed the teeth strip printed on his left temple (the head's skin pack landed on the teeth's authored UV strip); fixed in build_villager.clear_teeth_strip (also elder, purser, tender, poolkeeper, gatekeeper, hobb), re-rendered clean.
- Dialogue polish (chr-npc-polish): before, the grey share of his close crop read as bright white chips. After: grey cards as thin strands (`_hair.grey_strands`); reads as greying hair.

## Review log
