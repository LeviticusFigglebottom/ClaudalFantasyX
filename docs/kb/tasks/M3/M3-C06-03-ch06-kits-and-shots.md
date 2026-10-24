---
id: M3-C06-03
title: Ch6 kits swap-in (Brine Shoals, the Saltwright camp, the white barge) and the W shots, with the no-wake water
role: environment
status: todo
owner_session: ""
depends_on: [M3-C06-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch6's zone `ch06/brine_shoals` is greybox blocks (`game/levels/ch06/brine_shoals/brine_shoals_layout.json`). act1_ch06.md §9 Environment 1–5 and Art 6–9 ask for:
1. **The Brine Shoals kit:** silted mud-flats (`silted_flats` water look), wreck-ridges of Lit Age hull plating and wooden hulks, tide-channels, the Saltwright chalk camp-sign decals (thickening toward the camp), and a wayside Level-stone shrine set in a wreck's bow. Today the ridges and the flats are painted slabs on one flat floor; keep every walkable route flat or give the controller step-up (ADR 0035 Watch).
2. **The Saltwright camp kit,** in two states: intact (reusable for Hollowmere) and burning (B03–B06: fire, smoke, a collapsing tide-wheel). The hulk with the hold the party stands in is `HoldHull` / `Hatch`; the burning hulk Kerrid holds the rib on is `BurningHulk`. The layout's `states` hide and show by flag, so a kit piece can take over a block id.
3. **Order props:** the salt brazier and brine-irons on long hafts; Stillguard torches.
4. **Sefir's white barge** (block `Barge`, actors `sefir`, `reed_a`–`reed_d`): long, low, white-lacquered, gold Level symbols at the bow, four poler positions, a bow platform. The shoal channel (`Channel`) must stay wide enough for it.
5. **The no-wake water (with Rendering):** the water's wake and ripple response suppressed in a volume that moves with the barge, so the stern shot (W11) holds unbroken water for 3 s. The iron's hiss is the one ripple. Sefir's reflection doesn't ripple, and he has no breath cycle (Character). Build it once: Ansedra uses it in Ch13–14.
6. **The tideline at dusk** (B09, W16): wet sand that takes a hand-print and a diggable two-state patch (`LampHole`).
7. **Light and grade:** the layout's `lights` row is a stand-in dusk; the sheet asks for `ch06`, `ch06_hold`, `ch06_dusk` and `ch06_dawn` grades in `cues.json` (none exist yet, so no `grade=` is used). The barge is the only clean white in the frame.
8. **Shots:** the stand-in shots W01–W16 (plus `W02_share`, `W04_smoke`, `W08_hatch`, `W06_after`, `W12_crate`, `W10_dawn`) are in the layout. Re-place them on the kit. W11 and W10 must show Sefir small at the bow before his first line; W16 must never read the lamp's collar.

## Acceptance criteria
- [ ] The kit replaces the blocks, and `tests/integration/test_ch06_thread.gd` still passes (it checks spawns, marks, actors and shots by id).
- [ ] The barge's water shows no wake in W11, and the iron's hiss ripples.
- [ ] Every route can be walked on the kit.

## Notes

## Review log
