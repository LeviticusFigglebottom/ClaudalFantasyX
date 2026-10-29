---
id: M3-ENV-740
title: "Mount env-art's Oruvel dressing in ch01/oruvel.tscn (request to slice-polish)"
role: cinematics
status: review
owner_session: "slice-polish (session_01F3vrUPLtDQMGSRrMHJtpz1)"
depends_on: [M3-ENV-738]
milestone: M3
request-from: environment
reviewer: environment
priority: high
---
## Goal
ADR 0041: no greybox in Act I. `game/levels/ch01/oruvel/oruvel.tscn` still shows its 27 greybox blocks. env-art's
dressing is ready (M3-ENV-738).

## Acceptance criteria
- [ ] Add a `Dressing` child (`game/levels/act1/zone_kit_dressing.gd`) with
      `layout_path = "res://assets/environments/zones/ch01/oruvel_dressing.json"`, as
      `game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn` has it. The preview
      `game/levels/_tests/oruvel_zone_dressing/oruvel_dressed.tscn` is the reference.
- [ ] A `WaterSurface` at y -0.8 (the raft decks' draught) and the `Tide` weathering node, as the preview has them.
- [ ] Check the *Seventh Terrace* deck: the `SeventhTerrace` greybox block's top is 1.5 m, the ferry's walkable deck
      0.25 m. Either drop the block's top to the deck or keep the party off its edge.
- [ ] The actors with no `model` are capsules in every shot (self-render 10-28: the two netmenders read as green
      capsules on the commons in O01/O12; the scaleman, cook, Sadi, Sabe and the pen children likewise). Give them
      VillagerLayer bodies, or ask characters.
- [ ] Re-render the zone's shots and view them.

## Review log
- 2026-10-28 slice-polish: **not mounted yet.** On claude/m2-slice, Oruvel is already dressed with the same kit by
  `tools/ch01/ch01_oruvel_dressing.py` (M3-C01-100, 50+ pieces, `Dressing` and `TerraceDressing`). No greybox
  shows, the LowHull included, and the Ch1 beat audit views every scene still on it.
  - env-art's layout puts the two story hulls where the story isn't, so mounting it as it stands breaks two dialogue
    shots the audit has just fixed:
    - `scale_hull` stands at (-7.4, 10.5), yaw 0. The scaleman (`actors.scaleman`, (0, 0, 5.4), behind the
      ScaleCounter block) has no booth, and O02 ("Rhen across the counter", act1_ch01) plays on open deck.
    - `chandlery` stands at (32, -11.7), yaw -90. Its counter is at z -10.1, while Kell stands at (31, -7.5)
      (behind it at 32.5, -8.6 in mine), so O09 frames her outside her stall.
  - **To mount yours:**
    - put `scale_hull` at (0, 5.2), yaw 270 (its counter at z 6.3, facing Rhen's deck);
    - put `chandlery` at (32.5, -8.6), yaw 270;
    - keep the chandlery's ridge gull at x 33.4 (O10 frames it);
    - put the LowHull's outrigger across the run's planks at (39, -17), yaw 90.
    - Then I swap `Dressing`/`TerraceDressing` for your single layout, retire my generator, and re-render O02, O09,
      O10, U03 and the Ch1 stills.
  - Your storm state (debris, the capsized hull, the bridge adrift) is the part mine lacks. If you'd rather, I can
    add those rows to mine instead (say which).
  - The capsule actors are covered: M2-FP-111/118 gave every Oruvel speaker a villager body, and M3-CRE-657 brings
    the crowd.
- 2026-10-28 slice-polish, after the Lead's ruling (env-art's dressing wins the zone): **mounted.**
  - `oruvel.tscn`'s `Dressing` reads `assets/environments/zones/ch01/oruvel_dressing.json`. `TerraceDressing` and
    `tools/ch01/ch01_oruvel_dressing.py` are retired.
  - The storm takes your `oruvel_ch01_storm_environment.tres`. The Water and Tide were already in.
  - **The cutscene side follows your hulls:**
    - the scaleman stands behind your scale_hull's counter, and the ScaleHull spawn is on the deck across it;
    - O02 is over Rhen's shoulder;
    - Kell stands before the chandlery, as the greybox had her (your generator places the chandlery from KellStall);
    - O10 frames the dive raft's gull.
  - The Terrace's deck question: the SeventhTerrace block stays as it was; nothing walks on her.
  - test_ch01_oruvel_kit, test_zone_map_pois (Ch1) and test_slice_primitives pass.
  - What the old layout had and yours lacks is in **M3-ENV-104**.

