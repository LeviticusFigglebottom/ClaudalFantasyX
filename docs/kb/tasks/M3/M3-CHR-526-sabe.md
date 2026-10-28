---
id: M3-CHR-526
title: "Sabe, Oruvel's old diver (Ch1): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`sabe` is a capsule stand-in in game/levels/ch01/oruvel/oruvel.tscn (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/sabe.json`), host snaps and garment_fit opted in, a
      `villager_sabe` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `sit_watch`, `shout_lines` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_sabe_front`, `villager_sabe_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/sabe/sabe_actor.tscn`).

## Notes
- Who: Sabe, Oruvel's old diver (Ch1 C1-10/11, speaker `sabe`; act1_ch01.md: sits under the keel-hull's carved lintel-gull, says the gulls have been quiet all morning, then shouts 'Lines in!'), about 72, a woman. Small, hard and weathered, white hair cropped short as divers keep it, dense faded reach-bands to the elbow (a lifetime of dives), a faded sea-blue sleeveless diver's tunic over faded indigo shin trousers, an undyed sash, barefoot on the hulls (M3-CHR-526).
- Budget: LOD0 30,154 tris, 1.88 MB GLB; LOD1 14,109 tris, 0.68 MB.
- Rendered: front and face read as an old, weathered diver (white crop, dense faded bands to the elbow); the sleeveless tunic's armholes are cut deep (a halter-like front). sit_watch uses hero_clips' step-height sit: place her on the keel-hull's step.
- Dialogue polish (chr-npc-polish): before, her white crop read as bright white rectangular chips. After: every hair card is a thin strand (`_hair.grey_strands: "all"`), so the crop reads as white hair (the fringe still ends in a fairly blunt line). The halter-like front of the sleeveless tunic is unchanged: a cap sleeve and broader shoulder straps were both tried and both broke the rig-integrity ratchets (holes at the shoulder, or the arm through the cloth in the walk), so it needs its own garment-fit pass (a follow-up).

## Review log
