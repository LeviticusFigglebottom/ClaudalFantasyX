---
id: M3-CHR-528
title: "Skipper Sadi Moru (Ch1): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`skipper_sadi` is a capsule stand-in in game/levels/ch01/oruvel/oruvel.tscn (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/skipper_sadi.json`), host snaps and garment_fit opted in, a
      `villager_skipper_sadi` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `cast_off`, `laugh` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_skipper_sadi_front`, `villager_skipper_sadi_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/skipper_sadi/skipper_sadi_actor.tscn`).

## Notes
- Who: Skipper Sadi Moru of the Seventh Terrace, a red-lacquered Pemakar copper coaster at Oruvel's outer mooring (Ch1 C1-10/11, speaker `skipper_sadi`; act1_ch01.md: bought a lamp-housing off Rhen and paid short; they argue amiably; 'Cast off! Sea room!'), about 40, a woman, Pemakar-born. Quick and strong; black hair in a low knot; a lacquer-red sleeveless wrap top (her ship's colour), ash-grey knee trousers, a gold-ochre sash, a black headband; barefoot on deck. Reach-bands left 5, right 5. (M3-CHR-528.)
- Budget: LOD0 34,884 tris, 2.14 MB GLB; LOD1 16,472 tris, 0.81 MB.
- Rendered: reads as a quick, strong Pemakar skipper (lacquer-red top, black headband). The black band sits wide on the brow at dialogue distance.
- Dialogue polish (chr-npc-polish): before, the black headband stood off the brow, wide and high, with a shadow gap under it, and her black hair showed warm highlight chips. After: the band's edges drawn in to the skin with a rounder face (`headwrap.edge_off_m`, `off_m`), the hair under it pressed inside it (`headwrap.press_hair`), less sheen on the black cloth so it reads black, not grey (`_cloth_params.cloth_d.sheen_intensity`), and a dimmer hair specular (`_hair.spec`).

## Review log
