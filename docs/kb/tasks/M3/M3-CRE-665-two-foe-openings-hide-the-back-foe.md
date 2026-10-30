---
id: M3-CRE-665
title: "Two-foe openings: the back foe stands hidden behind the front one (BattleLineup separates footprints, not lines of sight)"
role: combat
status: todo
owner_session: ""
reviewer: character
depends_on: []
milestone: M3
request-from: creatures
---
## Goal
The Act I final-quality audit (creatures, 2026-10-29) rendered every Act I encounter with a regular foe at its opening
(arena_shot.gd, seed 20261024). In two of them the second foe stands directly behind the first along the battle
camera's line, so the player sees one foe and a stray tail or sail:
- `ch05_stair_tortoise_sparker` (ash_terrace_lanternfall): the vein sparker is hidden behind the slag tortoise; only
  its curled tail shows over the shell.
- `ch06_ridge_crab` (brine_shoals_afternoon): the shoal skipper is hidden behind the wreck crab; only its red sail shows.
`BattleLineup.spread` (M3-BPR-403) keeps the footprints apart on the ground, but the back rank's slot is in the front
foe's shadow from the opening camera. Pillar 4 (tactical clarity): every foe on the field should read at the opening.

## Acceptance criteria
- [ ] At the opening of every Act I encounter, no foe's silhouette is more than half hidden by another (a lateral
      stagger for the back rank, or the opening camera's yaw), with a test like test_battle_lineup's.
- [ ] Re-render `ch05_stair_tortoise_sparker` and `ch06_ridge_crab` at the opening and view them.

## Review log
