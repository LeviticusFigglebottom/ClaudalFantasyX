---
id: M2-HER-1104
title: "Cutscene motion quality: eased turns, walk start/stop blending and idle micro-motion for the sequencer"
role: cinematics
status: doing
owner_session: "hero-integration (claude/hero-integration)"
reviewer: cinematics
depends_on: [M2-HER-1101]
milestone: M2
request-from: lead
---
## Goal
The human: the prologue's animations read "too spontaneous and rigid" (snapping turns, instant walk start and stop).
Give m2-slice's CutsceneSequencer a blending API so every on-screen hero turns on an ease, rolls into and out of a
walk, and breathes and shifts weight while it stands.

## Acceptance criteria
- [ ] `HeroMotion` API (game/hero_motion/): turn_to(actor, yaw) eased and rate-capped (HeroLocomotion), play(actor,
      clip, blend) with crossfades, and a walk start/stop that blends idle -> walk -> idle over the move.
- [ ] Idle micro-motion (breathing, weight shift) as a SkeletonModifier3D layered on any clip or pose, data-driven,
      deterministic per actor.
- [ ] Opt-in for the sequencer: a short patch (or m2-slice applies it) so `_turn_to`, `@move` and `@anim` go through it.
- [ ] Tests (no snapping in a turn, blend weights through a start and a stop) and a cutscene turn strip shot, viewed.

## Review log
