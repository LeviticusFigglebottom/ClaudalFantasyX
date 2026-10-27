# 0192 — No snapping is a test: motion guards and foot IK

- **Status:** proposed
- **Date:** 2026-10-27
- **Roles affected:** combat (hero-integration, battle-presentation), cinematics (slice-polish, act1-chapters),
  character (characters, creatures), qa
- **Author role:** combat (hero-integration)

## Context
The human's first playtest complaint was that the heroes and villagers looked like placeholders and that their motion
was rigid and snapping (SPEC §1 pillar 2, beauty in decline). Fixes landed track by track: eased turns
(CutsceneMotion, HeroLocomotion), cross-fades (HeroBattleActor), the gait blend. Nothing stopped a new scene, clip or
data value from bringing a snap back, and nobody could say in numbers what "smooth" meant. The first audit found
snaps nobody had seen: a follower dropping through a pier edge, cutscene actors peaking near 800 deg/s, a walk jumped
to its mark when its scene ended, a placeholder clip flipping an arm in a cross-fade, and a crash installing
placeholder clips under a playing player.

## Options
1. Keep relying on viewing shots. Shots are still frames: they can't see a snap between frames.
2. Per-feature asserts in each track's tests. These miss the interactions (a cutscene's end against a walk's length).
3. Shared guards with one set of limits, run over everything that moves: the field zones, the cutscenes, the battle
   clip changes, the villagers.

## Decision
Option 3.
- `HeroMotionGuard` (game/hero_motion/hero_motion_guard.gd) has its limits in
  `game/data/hero_motion/motion_guard.json`:
  - a visible body's root may not step faster than 6 m/s or turn faster than 480 deg/s in a frame;
  - steps of 2.5 m or more count as deliberate cuts, and so does anything on a camera cut in cutscenes;
  - a clip change may not move any bone more than 1.5 × (the clips' own fastest step plus the pose gap spread over
    the blend) + 1 cm per frame;
  - no cross-fade may be shorter than 0.04 s.
- The tests that use it: test_hero_battle_pops (every hero, every battle change), test_hero_field_snaps (13 zones),
  test_hero_cutscene_snaps (26 scenes), test_villager_snaps (Haluna's villagers; it skips until creatures' layer
  lands).
- A snap that another track owns goes into the test's KNOWN list, tied to a request task. It is reported, not failed,
  and leaves the list when the fix lands, so the gate stays green without hiding anything.
- Feet meet uneven ground through `HeroFootIK` (foot_ik.json), which leaves flat ground untouched.

## Consequences
- A regression in any track's motion fails a hero-track test with the frame, the actor and the speed, which tells its
  owner where to look.
- The limits are data. Changing one is a design call; record it in the json doc and here.
- The cutscene guard plays 26 scenes in driven time (about a minute of CPU). It's an integration test, so the Lead's
  full gate runs it; tracks run it with `--filter=hero_cutscene_snaps` when they touch staging or CutsceneMotion.
- Foot IK costs 2 rays and 2 small solves per field body per frame. The PC measures it (M2-HER-1116).
