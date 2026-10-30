---
id: M4-A2P-050
title: "Tobin Varrow and Merel Dask: models, rigs, faces and wedding costumes"
role: character
status: review
owner_session: "claude/characters"
depends_on: []
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
Two new named people for Ch13–14: Tobin (charming, idealistic, Saltwright) and Merel (a Warden's living daughter), their wedding costumes, Merel's bloodied sleeve variant and her pole work, faces with the expression set.

## Acceptance criteria
- [x] Built on the MPFB2 base (ADR 0021), within budgets; shots viewed. Portraits: M4-A2P-081 (ui), which depends on this task.
- [x] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch13–14.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30 (characters, ADR 0205): done on the **villager build**, the path the Act I named NPCs take (Skipper Sadi,
  the tender, Marra), with all 40 face shapes.
  - **Tobin** (`params/tobin.json`): Liss's family face (her skin, ancestry mix and eye tilt; act1_npcs.md §2.10) on
    a 1.78 m man, a dark-brown crop. He wears the Saltwright coat in indigo_dye, long-sleeved and hip-length, with
    the Warden's lacquer_red sash over it with long tails, sand-cloth shin trousers and sandals. His eleven
    Saltwright line-marks (forearm 5, upper arm 4, collar and neck 2) use liss_textures' generator; the neck pair
    shows at the coat's V. LOD0 27,480.
  - **Merel** (`params/merel.json`): wedding red, a lacquer_red bodice and a lacquer_red_deep ankle skirt, a
    gold_leaf sash, an Ansedra knot. The **bridal cloth** is a new `solid` shawl (villager_costume: the sheet itself
    with a back face, on the head wrap's crepe island). The cloth is what she lays over Tobin at L01. LOD0 35,582 of
    36,000.
  - **Bloodied sleeve** (B08): `_blood` in her params. villager_textures.blood_atlas paints a dried stain into the
    shared cloth atlas's right-sleeve island (soaked at the cuff, patches and a wiped edge up the forearm, a few
    spatters) as `merel_blood_albedo.png`. write_materials writes `cloth_a_blood.tres`, which no glTF slot takes.
    `CostumeVariant` (game/characters/costume_variant.gd, test_costume_variant 2/2) swaps it in. Scene owners add the
    node with slot `cloth_a` for B08 and every later shot.
  - **Faces:** `tobin_face_poses.json` has a resting half-smile, a wide lopsided smile and a small, quiet `surprised`
    for B05. `merel_face_poses.json` has a contained composure, a small real smile and `determined` for the pole;
    both carry the full tag set.
  - **Clips:** `hold_hands` (the vows, W05) for both, Merel's `pole_barge` (B07, the reeds' stroke), and Tobin's new
    `tobin_falls` (B05: he sits down on the slabs, one hand to his ribs, the other on the ground).
  - **Shots** (pending baselines): villager_tobin_{front,face,falls}, villager_merel_{front,face,pole_barge,bloodied},
    all viewed. Blender jobs villager_tobin and villager_merel are identical on the 3 numpy paths.
  - **Known limits:** the faces are at the villager build's level, the same as Skipper Sadi's and the tender's.
    Merel reads young and plain at a close-up. If the GPU review holds Ch14's close-ups (W05, B08) to the hero bar,
    the hero path is a follow-up for both. Tobin's coat is hip-length, because the villager top has no tails.

## Review log
