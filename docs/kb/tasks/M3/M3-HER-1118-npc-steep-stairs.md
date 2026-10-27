---
id: M3-HER-1118
title: "Villagers on steep stairs: FieldNpc stands on a HeroStairFlight's steps (request to creatures)"
role: character
status: todo
owner_session: ""
depends_on: [M3-ARC-1216, M3-CRE-610]
milestone: M3
request-from: combat
---
## Goal
ADR 0193: steep flights (Ashcrown's 48° and 60° stairs) are walked on a marked profile, not their collision. The
player and the followers do it already. A villager whose route crosses a flight should climb its steps rather than
follow its own straight line, and take them at the same pace.

## Acceptance criteria
- [ ] In FieldNpc's move step: when `HeroStairs.height_at(self, point)` is a number (not NAN), set the villager's
      height to it, and cap its ground speed with `HeroStairs.speed_cap_at(self, point)`.
- [ ] A test: a route across a HeroStairFlight climbs it step by step, with no snap (HeroMotionGuard).

## Notes
- API: game/hero_motion/hero_stairs.gd (static `height_at`, `speed_cap_at`); a flight is a HeroStairFlight node or
  a zone layout "stairs" row (M3-ARC-1216's notes).

## Review log
