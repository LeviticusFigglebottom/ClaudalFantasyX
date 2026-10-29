---
id: M3-CHR-536
title: "Old Fenn of Coilspire (Ch8-9): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`fenn` is a capsule stand-in in game/levels/ch08/coilspire/coilspire.tscn, game/levels/ch09/corrow_night/corrow_night.tscn (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/fenn.json`), host snaps and garment_fit opted in, a
      `villager_fenn` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `feed_fire`, `hand_driftwood`, `hand_key` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_fenn_front`, `villager_fenn_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/fenn/fenn_actor.tscn`).

## Notes
- Who: Old Fenn, who has kept Coilspire's low flame for forty-one years (Ch8-9, speaker `fenn`; act1_ch08.md: 'Shut the door, Lady. She doesn't like a draught'; feeds the fire, hands Asha the driftwood and the key), about 74. Lean, stooped, cheerful; thin white hair cropped and receding, a white stubble; a soot-dark slate long-sleeved coat-shirt with the sleeves pushed to the forearm, storm-grey shin trousers, a long scorched hide apron over them, a faded copper-green sash, sandals. Soot-dark fingertips. Reach-bands left 4, right 3 (fisher years before the flame). (M3-CHR-536.)
- Budget: LOD0 27,870 tris, 1.80 MB GLB; LOD1 12,966 tris, 0.66 MB.
- Rendered: lean old man, white crop over a bare scalp, soot-dark slate shirt, scorched apron. `feed_fire` crouches to a low hearth (0.2 m drop).
- Dialogue polish (chr-npc-polish): before, his white crop read as bright white rectangular chips on a flat beige scalp cap with a hard edge. After: every card is a thin sparse strand (`_hair.grey_strands: "all"`, `grey_width_k`), the scalp underpaint warmer and half as dense so the bare scalp shows through, and a light stubble shadow; reads as thin white cropped hair over an old man's scalp.
- Dialogue polish 2 (chr-npc-polish2): before, the brows read as a flat grey smear. After: single wiry hairs painted on the brow skin in the brow cards' own frame, about a third dark among the white, a few strays (`_skin.brow_strands`), under the cards at a lighter `alpha_boost` with per-strand value jitter (`_hair.brow_params`); reads as an old man's brows.

## Review log
