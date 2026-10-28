---
id: M3-C08-102
title: "Corrow (day and storm) and Coilspire kits for Ch8's greybox"
role: environment
status: todo
owner_session: ""
depends_on: [M3-C08-02]
milestone: M3
request-from: cinematics
---
## Goal
Replace the blocks of Ch8's two greybox zones (M3-C08-02) with env-art's kits. The story only needs the ids the layouts and the chapter flow use to stay. The brief is act1_ch08.md §9, Environment Art 1-4.

## Acceptance criteria
- [ ] **`ch08/corrow`** (`game/levels/ch08/corrow/corrow_layout.json`): the laterite seawall with its rebuild strata, and the 1001 section paler (`WallSection`, `PaleBlocks`). The Watchers (`WatchersW`, `WatchersSection`, `WatchersE`). The wall-head walk, the Fisher Stair with its iron hand-line rings (`FisherStair`, `HandLine`), the watch-red wall-gate (`WallGate`), the low town, the Bastion, the harbour mole and the shingle.
- [ ] **The storm variant on the same layout**, which today is flag-driven `states` and `lights`:
  - rain and spray, and the flood at the stair foot (`Flood`);
  - Liss's hoist props (`HoistPins`, `HoistRope`, `Basket`);
  - the breakable section for B17 (`WallSection` and `WatchersSection` go and `Breach` shows);
  - the black lake after it (`Lake`).
- [ ] **`ch08/coilspire`** (`game/levels/ch08/coilspire/coilspire_layout.json`):
  - the headland path and its scrub;
  - the keeper's hut and hearth;
  - the spire's four tiers. Keep the ids `Key_<key>`, `Flame_<tier>` and `Gate_<tier>`: the zone root turns, lights and opens them;
  - the tier-2 side flue and the niche (`NicheSeal`);
  - the crown chamber and the beacon gallery (`Beacon`, `GreatKey`), and the storm wall seen from it (`StormWall`).
- [ ] **`docs/kb/art/environments/corrow.md`**: the mood brief and the W/F shot list (act1_ch08.md §7). The greybox shots in both layouts use those ids.
- [ ] **Whether Ch9's `ch09/corrow_night` becomes this zone's night variant** is M3-C09-04's call. Ch8 hands off to it at `Strand` today.

## Notes
- The greybox is flat, because the controller has no step-up. The stair, the wall-head and the tiers are painted slabs or rooms in a row. A kit with real height needs the controller's step-up, or ramps.

- **env-art, 2026-10-27 (the kit side is done; the rest is placement):**
  - **Kits:** the Corrow kit (M3-ENV-04; the seawall, the Watchers, the breach and the storm pieces), the Corrow
    story pieces (M3-ENV-707) and the Coilspire kit (M3-ENV-10).
  - **Ch8's arenas:** M3-ENV-713, five of them.
  - **Sheets:** `corrow.md` and `coilspire.md`, with their shots.
  - **What's left is placement,** which is act1-chapters' (ADR 0200), as M3-ENV-1203 did for the mole. For the
    Lead: re-route or close into act1-chapters' swap.

## Review log
