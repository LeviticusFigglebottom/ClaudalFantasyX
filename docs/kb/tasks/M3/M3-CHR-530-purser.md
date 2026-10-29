---
id: M3-CHR-530
title: "The Brightwater ferry's purser (Ch4): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`purser` is a capsule stand-in in game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/purser.json`), host snaps and garment_fit opted in, a
      `villager_purser` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `offer_goods` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_purser_front`, `villager_purser_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/purser/purser_actor.tscn`).

## Notes
- Who: The Brightwater ferry's purser (Ch4, the ferry shop; act1_ch04.md: sells Pemakar-bound supplies), about 34, a woman. Brisk, precise; black hair under a sand head wrap, a sea-blue short-sleeved wrap top, a sand calf skirt with an indigo apron (the purse and tally are props), sandals. Reach-bands left 2, right 2. (M3-CHR-530.)
- Budget: LOD0 31,062 tris, 1.77 MB GLB; LOD1 14,563 tris, 0.61 MB.
- Rendered: fine; the head wrap and apron read. Shop gesture `offer_goods`.
- Dialogue polish (chr-npc-polish): before, the head wrap's edge stood a little off the brow with a dark line of hair in its shadow. After: the edge drawn in to the skin (`headwrap.edge_off_m`) and a dimmer hair specular (`_hair.spec`) on the black hair that shows at the temples.

## Review log
