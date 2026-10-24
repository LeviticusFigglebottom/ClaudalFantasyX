# 0038 — A hero motion layer over the field, battle and cutscene bodies

- **Status:** proposed
- **Date:** 2026-10-24
- **Roles affected:** architect (field), combat / ui (battle stand-ins), cinematics (sequencer), character (clips)
- **Author role:** cinematics (hero-integration track)

## Context
The human's playtest: the real hero models appear only in cutscenes; in the field the player is a capsule, and in
battle the fighters are stand-ins. Where the heroes do move, turns snap (FieldMotor turns at 720°/s; the sequencer's
`_face` sets the yaw at once) and walks start and stop instantly. SPEC §1 pillar 2 (beauty) and §7 (presentation)
want bodies that move like bodies. The pieces are owned by four tracks (Systems/m2-slice: the field controller and
zones; UI+Combat and battle-presentation: the stand-ins and choreography; m2-slice: the sequencer; characters: the
models and clips).

## Options
1. Each owner swaps in models and smooths its own motion.
2. One shared, presentation-only motion layer: pure maths (`HeroLocomotion`: rate-capped eased yaw, gait blend by
   speed) plus thin nodes that sit on top of the existing gameplay nodes (`HeroFieldActor` on a FieldController,
   followers, the cutscene `HeroMotion` API), tuned in one data file, hooked in with one line per owner.

## Decision
Option 2. `game/hero_motion/**` and `game/data/hero_motion/hero_motion.json` (hero-integration). Gameplay keeps its
own state: the FieldController still moves and collides as before, and the visible body follows it, turning at most
`turn.max_rate_deg_per_sec` per second, easing in and out, and blending idle/walk/run by measured ground speed.
Owners opt in with one call (`HeroFieldActor.attach(self)` in FieldController._ready; the sequencer's turn, move
and clip cues through `HeroMotion`). Only spawns, teleports and cuts may snap a yaw.

## Consequences
- Every place a hero is seen moves the same way, and one data file tunes it.
- The visible yaw lags the gameplay facing by up to a few frames; interaction reach uses the controller, not the body.
- Clips the layer fakes (turn-in-place, run stops) are requested from the characters track (M2-HRO-05).
- Battle choreography stays battle-presentation's; the layer only gives hero actors crossfades and micro-motion.
