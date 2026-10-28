---
id: M3-HER-1119
title: "Cutscene walks on steep stairs: @mark walks stand on a HeroStairFlight's steps (request to slice-polish)"
role: cinematics
status: todo
owner_session: ""
depends_on: [M3-ARC-1216]
milestone: M3
request-from: combat
---
## Goal
ADR 0193: steep flights are walked on a marked profile. A cutscene `@mark` walk lerps its actor in a straight line,
so on a flight it glides up a ramp through the steps. Once Ashcrown's flights are in (M3-C05-1215), its cutscenes
will walk them.

## Acceptance criteria
- [ ] In the `@mark` walk's apply (CutsceneSequencer `_cue_mark`): after the lerped point, when
      `HeroStairs.height_at(actor, point)` is a number, use it as the point's height. Optionally slow the walk to
      `HeroStairs.speed_cap_at` while on the flight.
- [ ] The hero track's cutscene guard (test_hero_cutscene_snaps) passes on Ashcrown's scenes once the flights are
      placed.

## Notes
- The same profile the player and followers use (game/hero_motion/hero_stairs.gd). It can ride with M3-CIN-1220's
  `via=` path patch, which touches the same walk code.

## Review log
