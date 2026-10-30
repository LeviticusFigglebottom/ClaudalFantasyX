---
id: M4-A2P-021
title: "Glide and ambush: untargetable on alternate turns, and until it has acted once"
role: combat
status: review
owner_session: act1-chapters
depends_on: []
reviewer: progression
milestone: M4
request-from: lead
---
## Goal
Two targeting rules for Act II's regulars: `gallery_ray` glides above the water line every other turn (untargetable then), and `glass_skate` is buried until it has acted once. Both must show on the timeline and in targeting (pillar 4).

## Acceptance criteria
- [ ] Enemy-row keys, engine rules and unit tests; the sim's policies skip untargetable foes.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §4.6. Phases already carry `untargetable`; this is per turn.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- **act1-chapters (the chapters combat seat, ADR 0205), 2026-10-30:**
  - BattleCover (game/battle/battle_cover.gd) reads two enemy-row keys:
    - `glide`: after each own turn, up out of reach or back down.
    - `ambush`: buried from the start until its first turn ends.
  - Cover sets `covered` plus `untargetable`, so living_foes_of, `_valid_targets` and every sim policy skip it.
  - **No stalls (the party has no Wait):**
    - Cover never takes the last strikable foe. If all would hide, the first in encounter order stays up.
    - It's re-checked at each turn start, so a hidden foe surfaces when the visible ones fall.
    - A phase's own `untargetable` is never lifted.
  - **Data:** `gallery_ray` glides and `glass_skate` ambushes. ch11_vey_rays (naive 37.0, smart 98.3) and
    ch16_rim_skates (52.1, 98.2) are re-run and in band.
  - **Tests:** tests/unit/test_battle_cover.gd (6), plus battle_engine, set_piece and boss.
  - **Readout** (the timeline, targeting, stage): M3-UI-1241.

## Review log
