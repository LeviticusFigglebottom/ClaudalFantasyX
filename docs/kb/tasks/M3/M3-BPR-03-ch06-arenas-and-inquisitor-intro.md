---
id: M3-BPR-03
title: Ch6 battle arenas (Brine Shoals, the burning salvage camp) and the Inquisitor's intro
role: combat
status: review
owner_session: battle-presentation (claude/battle-presentation)
reviewer: lead
depends_on: [M3-BPR-01, M3-BPR-02]
milestone: M3
request-from: lead
---
## Goal
m2-slice's Ch6 encounters (act1_ch06.md) need arenas and the boss fight needs an intro:
- `brine_shoals_afternoon`: ch06_ridge_skippers, ch06_ridge_crab, ch06_ridge_gulls, ch06_flats_crabs. Black Lit Age hull
  plating and wooden hulks on grey-green silted flats (`silted_flats` water), gulls, tide channels; Ch6 grade (15:30
  haze: key #FFD5B3 2.4, fill #A8B8B0 0.55, sky #7FA3C0 / #D8C8A8, fog #B8A890, exposure 0.70, saturation 0.9).
- `salvage_camp_burning`: ch06_inquisitor (B04, the camp by the burning hulk, 15:40): lashed hulls, tide-wheels, lamp
  racks burning; smoke; the same grade with orange fire light. Nobody dies in this fight; the staging stays sober.
- The Inquisitor's boss intro (B04): a careful, sincere title (a living officer of the Order, not a monster).
Env-art's Brine Shoals zone (M3-ENV-02) is the kit for the final versions (request in M3-ENV-06's spirit).

## Acceptance criteria
- [x] Two greybox arenas on the contract, the encounter rows' `arena`, shots viewed
- [x] The Inquisitor's intro row and loc keys (sincere; Narrative may refine)
- [x] Tests

## Notes
- 2026-10-24 (worktree agent): `game/battle/arenas/brine_shoals_afternoon.tscn` and `salvage_camp_burning.tscn`
  (greybox, hand-written primitives; the grade in each header). arenas.json scenes; `arena` on the five Ch6 rows.
  Every light in both sets `light_volumetric_fog_energy = 0.0` (Lead rule). Shots `battle_arena_shoals`
  (ch06_ridge_gulls), `battle_arena_camp` (ch06_inquisitor) and `battle_boss_intro_inquisitor`, viewed and approved.
- The intro row `ch06_inquisitor` (shot `boss`, hold 2.0): `BOSS_TITLE_INQUISITOR` "Inquisitor Hadric Moll",
  `BOSS_EPITHET_INQUISITOR` "A tired officer who still believes the Edict" (Narrative may refine). Tested: the help
  line (`TUT_CH06_HOUND`) is hidden while it plays and back after, and Toma's bark shows on his first turn.
- Open: the shoals' hull plates read dark brown under the warm haze rather than black; env-art's kit (M3-ENV-02)
  replaces the greybox. A pre-existing quirk, not the intro's: if Toma's first turn came before any other party turn,
  his bark would replace the unshown `TUT_CH06_HOUND` prompt (BattleBossHud keeps one pending prompt).

## Review log
