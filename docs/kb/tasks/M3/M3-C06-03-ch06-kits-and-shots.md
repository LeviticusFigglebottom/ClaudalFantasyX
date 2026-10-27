---
id: M3-C06-03
title: Ch6 kits swap-in (Brine Shoals, the Saltwright camp, the white barge) and the W shots, with the no-wake water
role: environment
status: doing
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
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
- **env-art, 2026-10-27:** where each item stands. act1-chapters placed the kit under M3-C06-1200 (ADR 0200), which
  lists what was still open.
  1. **The Brine Shoals kit (items 1, 2 and 4).** Built: M3-ENV-02 (the flats, wrecks and channel), the camp and its
     burning states, the white barge, and M3-ENV-703 (the tide-wheel, the Level-stone shrine, the vendor boat, the
     hatch, and the chalk camp-signs `chalk_mark` / `chalk_mark_heavy`).
  2. **Order props (item 3).** The brazier and brine-irons are `branding_brazier`. New here: **`stillguard_torch`**,
     a 2.2 m iron haft in the Order's red bands with a brass cup and a glowing pitch wrap. Its origin is at the foot;
     the hand grips about 0.9–1.3 m. It is a hand prop for the Stillguard actors (Character), or planted in the sand
     by the camp's edge. The flames are VFX (Rendering), as `ridge_fire`'s are.
  3. **The no-wake water (item 5).** M3-ENV-1000 (doing): the moving boats' `boat_wake` is built and the barge has
     none. Sefir's still reflection is Rendering's M3-RND-03, waiting on the integration branch.
  4. **The tideline (item 6).** New: **`lamp_hole_open`**, **`lamp_hole_covered`** and **`hand_print`** (1.2 m and
     0.44 m patches of wet sand, flush with the flats). For act1-chapters: the `LampHole` block becomes
     `lamp_hole_open` while the lamp is being buried, then `lamp_hole_covered` (the layout's `states`, by
     `ch06_saw_lamp_buried`). Put `hand_print` beside it for the insert shot.
  5. **The grades (item 7).** Still open. The colour script has only `ch06`; `ch06_hold`, `ch06_dusk` and `ch06_dawn`
     need sub-frames first (Art), then the Environments for the layout's light rows (`environment_res`).

## Review log
