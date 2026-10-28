---
id: M3-CHR-534
title: "Ione Sabe, Sorrin's captain (Ch7): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`ione` is a capsule stand-in in game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/ione.json`), host snaps and garment_fit opted in, a
      `villager_ione` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `nod` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_ione_front`, `villager_ione_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/ione/ione_actor.tscn`).

## Notes
- Who: Ione Sabe, captain of the Sorrin side at the Tidecup (Ch7, speaker `ione`; act1_ch07.md: a stocky atoll woman with reach-bands to the elbow; names her drowned brother Aldo at the naming), about 34. Broad, strong, short; black hair cropped short for the pool; the Sorrin side kit: a deep-green sleeveless top, slate knee trousers, a coral sash (a coral top read as bare skin against hers); barefoot. Reach-bands left 11, right 10, to the elbow. (M3-CHR-534.)
- Budget: LOD0 30,438 tris, 1.88 MB GLB; LOD1 14,251 tris, 0.68 MB.
- Rendered: the first tint (a coral top) read as a bare torso; re-tinted deep green and slate with a coral sash and re-rendered. Reach-bands to the elbow (11/10).
- Dialogue polish (chr-npc-polish): before, warm yellow-brown highlight chips on her black hair, and the sleeveless top's halter-like cut leaving the shoulders and the base of the neck bare. After: a dimmer, cooler hair specular (`_hair.spec`); the hair reads as dark strands. The cut is unchanged: a cap sleeve and broader shoulder straps were both tried and both broke the rig-integrity ratchets (the arm opens holes at the shoulder or passes through the cloth in the walk), so a reshaped top needs its own garment-fit pass (a follow-up).
- Dialogue polish 2 (chr-npc-polish2): before, the halter-like cut, and the short hair's painted edge a blunt line across the forehead. After: the tank cut (`armhole_cut: "tank"`), straps over the shoulders at the face shot; a broken, feathered painted hairline (`_hair.hairline_feather`). Rig probe: Body 58.11 -> 57.18 (ratchet 59/5 -> 58/2), no exposed boundary (max_exposed back to the default). Still reads wrong: the front shot shows the panel's sides standing out under the arms like short cap sleeves (as before this pass; the torso chart at the armhole floor), and the card tips at the fringe still show as short dark dashes. Budget now LOD0 33,548 tris, 2.00 MB GLB; LOD1 15,932 tris, 0.74 MB.

## Review log
