---
id: M3-CHR-529
title: "Imbe, the Brightwater ferry-master (Ch4): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`ferrymaster` is a capsule stand-in in game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/ferrymaster.json`), host snaps and garment_fit opted in, a
      `villager_ferrymaster` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `nod` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_ferrymaster_front`, `villager_ferrymaster_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/ferrymaster/ferrymaster_actor.tscn`).

## Notes
- Who: Imbe, master of the Brightwater ferry (Ch4, speaker `ferrymaster`; act1_ch04.md: the first stranger to name Rhen's loss aloud, 'Salt and stone. I'm sorry, lad'; keeps sea-law and will not send his crew aboard a moving drowned hull), about 58. Big, slow, weathered; grey-black short hair and a grey beard-stubble; a faded teal long-sleeved wrap coat-shirt with the sleeves pushed to mid-forearm, sand shin trousers, a sea-blue sash (the ferry's reef band), sandals. Reach-bands left 9, right 8. (M3-CHR-529.)
- Budget: LOD0 29,254 tris, 1.85 MB GLB; LOD1 13,657 tris, 0.66 MB.
- Rendered: big, grave, grey stubble faint at dialogue distance. Only `nod` beyond the shared clips: the dialogue calls none.
- Dialogue polish (chr-npc-polish): before, the grey beard-stubble was faint at dialogue distance and the grey share of his hair read as white chips (the head albedo was also stale against M2-CHR-524's beard lens, so the job failed its verify). After: a denser stubble over a soft cool beard shadow (`_skin.stubble_density`, `stubble_shadow`) and grey cards as thin strands (`_hair.grey_strands`); rebuilt, the job verifies again.

## Review log
