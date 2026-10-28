---
id: M3-CHR-532
title: "Garo Tenmak, the Pemakar smith (Ch5): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`garo` is a capsule stand-in in game/levels/ch05/pemakar/pemakar.tscn (also the ch05_kahre_bound variant) (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/garo.json`), host snaps and garment_fit opted in, a
      `villager_garo` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `fold_boat`, `nod`, `laugh`, `take_boat` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_garo_front`, `villager_garo_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/garo/garo_actor.tscn`).

## Notes
- Who: Garo Tenmak, a Pemakar smith (Ch5 B03 'The Smith's Question', speaker `garo`; act1_ch05.md §4: sixties, burn-scarred forearms, a big careful voice, hands made for tongs, a leather apron; trying to fold a leaf-boat for his son Benet). Big and heavy; grey cropped hair receding, a grey stubble; a soot-grey work shirt with the sleeves pushed up and rolled above the elbow (the forearms bare, as the scene needs), ash-grey knee trousers, a long hide apron straight over them (cloth_d, less sheen), sandals. Soot in the fingertips. (M3-CHR-532.)
- Budget: LOD0 29,660 tris, 1.88 MB GLB; LOD1 13,860 tris, 0.71 MB.
- Rendered: big, grey crop and stubble, forearms bare below the pushed-up sleeves, long hide apron. The burn scars on the forearms are NOT painted (villager_textures has no scar term; a follow-up could reuse liss_textures.burn_scars). The ch05_kahre_bound variant needs no separate model (it is the same Garo).
- Dialogue polish (chr-npc-polish): before, his greying crop read as white rectangular chips, the grey stubble barely showed, and the burn scars on his forearms were not painted (the committed head albedo was also stale against M2-CHR-524's beard lens, so the job failed its verify). After: grey cards as thin strands (`_hair.grey_strands`), a soft beard shadow (`_skin.stubble_shadow`), and healed burns on both forearms: irregular pale, mottled patches with a darker rim (`_skin.burn_scars`, a new villager_textures term; body maps at 1K via `_skin.body_size` so they resolve). Rebuilt, the job verifies again.

## Review log
