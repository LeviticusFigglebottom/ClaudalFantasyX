---
id: M3-C06-06
title: Ch6 characters and creatures (Sefir, Liss, Inquisitor Moll, the raid's NPCs; shoal skipper, wreck crab, raid-hound)
role: character
status: todo
owner_session: ""
depends_on: [M3-C06-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch6's cast are capsules in the greybox (`brine_shoals_layout.json` `actors`). act1_ch06.md §9 Character Art 10–13 and Creatures 14–17 ask for:
1. **Sefir Aurane**, from his first appearance: the right-shoulder gold half-mantle, the bowl halo-crown, the pale-blue silk, no idle motion, **no breath cycle** (sefir_aurane.md). He stays aboard the barge's bow for the whole scene.
2. **Liss Varrow**: line-marks on the right arm, collarbone and neck; the copper-mesh work-sleeve on the left; the launcher; the bead-tail; the crate with bound teal light at its seams (`glimmer_bound`).
3. **Inquisitor Hadric Moll** (a person, so the character track builds him): forties, red-lacquered shell armour with an Inquisitor's white sash, a round shield, a long-hafted brine-iron held upright like a standard.
4. **NPCs:** Stillguard (six variants if the set is short), an Order clerk, four Reeds (the polers), and Saltwright wrights with visible line-marks on pushed-up sleeves (the girl at the brazier and two children).
5. **Creatures:** `shoal_skipper` (a dog-sized mudskipper: blunt head, goggle eyes on top, a long low body on fins), `wreck_crab` (a reef-crab variant living in a broken Lit Age lamp housing, its back glowing faint `glimmer_bound` teal), `raid_hound` (an Order shoal-hound: a greyhound's legs under a mastiff's chest, mud-coloured, a red-lacquered muzzle cage; driven off, never killed). `gull_harrier` is reused (a palette variant is fine).
6. **Anim clip proposals** used by the scripts: `kneel_palms_flat`, `hold_rib_on_shoulder`, `bow_from_barge`, `bow_palms_flat`, `pole_barge`, `iron_into_water`, `dig_sand`, `flatten_sand`, `stand_watch_seaward`, `shield_up`, `level_spear`, `crawl_out`, `hand_over`, `set_in_hole`.

## Acceptance criteria
- [ ] Each model replaces its capsule; `tests/integration/test_ch06_thread.gd` still passes.
- [ ] Sefir has no breath cycle and his reflection doesn't ripple (with Rendering, M3-C06-03).
- [ ] PROVENANCE rows for every asset.

## Notes

## Notes (creatures)
- 2026-10-27, creatures: **item 5 is done.** shoal_skipper, wreck_crab and raid_hound stand in battle as models (enemies.json `model`; approved renders, PC render fce2e82). Items 1–4 and 6 (Sefir, Liss, Moll, NPCs, clips) are the characters track's; Moll's battle model is M3-CRE-625.

## Review log
