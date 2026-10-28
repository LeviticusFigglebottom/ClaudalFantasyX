---
id: M3-CHR-538
title: "Hobb, captain of the stair-watch (Ch8-9): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`hobb` is a capsule stand-in in game/levels/ch08/corrow/corrow.tscn, game/levels/ch09/corrow_night/corrow_night.tscn (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/hobb.json`), host snaps and garment_fit opted in, a
      `villager_hobb` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `drill_call` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_hobb_front`, `villager_hobb_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/hobb/hobb_actor.tscn`).

## Notes
- Who: Hobb, captain of Corrow's stair-watch (Ch8-9, speaker `hobb`; act1_ch08.md: a fisher of fifty with the three-knot watch-red captain's cord on his hip, the same cord as Kerrid's; drills the young fishers on the stair: 'First down, last up'). Wiry and loud; grey-black short hair, a grey stubble; a faded indigo sleeveless fisher's vest over a bare chest, storm-grey knee trousers, the watch-red captain's cord as a narrow sash with long tails at the hip (its three knots are not modelled), barefoot on the stair. Reach-bands left 8, right 7. (M3-CHR-538.)
- Budget: LOD0 30,164 tris, 1.84 MB GLB; LOD1 14,114 tris, 0.66 MB.
- Rendered: open indigo vest over a bare chest, watch-red captain's cord as a narrow sash with long tails. The cord's three knots are not modelled.
- Dialogue polish (chr-npc-polish): before, the grey share of his short hair read as bright white chips on the dark hair, the grey stubble did not show at dialogue distance, and the captain's cord was a wide sash with no knots. After: grey cards are thin sparse strands (`_hair.grey_strands`), a soft cool beard shadow under the stubble (`_skin.stubble_shadow`, `stubble_density`), and the cord's tails narrowed (`tail_w_k`), its waist knot smaller (`knot_k`) and three knots tied down the front tail (`cord_knots`, `cord_knot_m`); all optional keys, every other villager byte-identical.
- Dialogue polish 2 (chr-npc-polish2): before, the short hair's painted edge ended in a blunt line across the forehead. After: a broken, feathered painted hairline (`_hair.hairline_feather`: asha_textures' opt-in HAIRLINE_FEATHER); textures only, the GLB unchanged.

## Review log
