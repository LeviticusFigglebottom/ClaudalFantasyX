---
id: M3-BPR-424
title: Status ticks show on their fighter (poison, regen, Doom, a turn lost to Sleep or Stop)
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: [M3-BPR-420]
milestone: M3
reviewer: rendering
request-from: lead
---
## Goal
The Lead, 09:35: every Act I fighter's status ticks have VFX. Until now only the HUD's numbers marked them.

## What changed
- BattleVfx listens to `BattleEngine.turn_ended` and `turn_lost`. `play_ticks` plays `map.ticks[cause]` on each
  change's fighter:
  - poison and regen;
  - a Zombie's regen, which hurts, plays the poison tick;
  - a Doom count, and Doom falling;
  - a turn lost to Sleep or Stop shows on the sleeper.
- Six effects come from `tools/vfx/gen_act1_ability_vfx.py` (TICKS), each in palette swatches:
  - poison: sick green welling out;
  - regen: shallow water lifting off (never glimmer);
  - the Doom count: a little dark settling;
  - Doom falling: the dark coming down whole (never a release);
  - Sleep: slow pale motes;
  - Stop: a still ring of salt-glass.
- Sounds borrow existing rows (status_apply, heal, ko_release) until audio's own (M3-BPR-421).

## Acceptance criteria
- [x] test_battle_status_tick_vfx: each cause plays its tick on its fighter; Sleep and Stop; no glimmer in regen or
  Doom.
- [ ] Viewed on an Act I arena (self-render, the live log).

## Review log
