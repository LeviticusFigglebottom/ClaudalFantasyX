---
id: M3-CHR-533
title: "Tender Ruwen, the Ashcrown Tender (Ch5; speaker `tender`, also Ch8-9): a villager-path model for the capsule"
role: character
status: review
owner_session: "chr-npc-wip (characters worktree)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
`tender` is a capsule stand-in in game/levels/ch05/ashcrown/ashcrown.tscn, game/levels/ch08/coilspire/coilspire.tscn, game/levels/ch09/corrow_night/corrow_night.tscn (docs/kb/qa/act1_final_inventory.md). Build them as an individual on the villager
pipeline, with the clips their dialogue calls.

## Acceptance criteria
- [x] Built from source (`assets_src/characters/villagers/params/tender.json`), host snaps and garment_fit opted in, a
      `villager_tender` job in `tools/dev/blender_builds.json` verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Clips: `idle`, `talk`, `walk`, `open_pavilion`, `palms_level`, `paint_gilt`, `open_chamber`, `hand_key` (villager_story_clips.json; `look_at` is CutsceneSequencer's own).
- [x] Stage scene, face-pose table and shots `villager_tender_front`, `villager_tender_face` (no baselines written).
- [ ] The capsule swapped in the level scene(s): M3-CHR-519 (the level owners'; the actor scene is
      `res://assets/characters/villagers/tender/tender_actor.tscn`).

## Notes
- Who: Tender Ruwen, the Tender of Ashcrown (Ch5, speaker `tender` shown as 'Tender Ruwen': opens the crown pavilion, paints the gilt line, opens Kahre's chamber, hands Asha the key; the same speaker id serves the later temples' Tenders, Coilspire's in Ch8-9), about 52, a woman. Composed, tired, kind; grey-streaked black hair in a low knot; the Order's ivory robe (a long-sleeved wrap top over an ankle skirt) with the skirt's cloth greyed with ash (soot on the hems, act1_ch05.md), a gold-leaf sash wound twice, a lacquer-black stole panel to the shin, sandals. No reach-bands. (M3-CHR-533.)
- Budget: LOD0 35,436 tris, 2.16 MB GLB; LOD1 16,748 tris, 0.83 MB.
- Rendered: ivory Order robe, ash-grey skirt for the sooted hem, gold sash, black stole. One model serves the `tender` speaker in Ch5 (Ruwen), Ch8 and Ch9 (Coilspire's Tender); if Coilspire's Tender is meant to be a different person, file a second params file (an hour's work on this pipeline).

## Review log
