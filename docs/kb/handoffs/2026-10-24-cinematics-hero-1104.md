# Handoff: cinematics (hero integration), M2-HER-1104 cutscene motion, 2026-10-24

## Done
- `HeroMotion` (game/hero_motion/hero_motion.gd): the static per-body entry point.
  - `play(actor, clip, blend, restart)` goes to the body's `play_clip`, else to the AnimationPlayer cross-fade.
  - `set_locomotion_speed` and `set_idle_amount` are there too.
  - `add_micro_motion` returns null on a capsule.
- `HeroIdleMicro` (game/hero_motion/hero_idle_micro.gd), driven by `game/data/hero_motion/idle_micro.json`:
  breathing, a weight shift, and a head lead measured from the skeleton's yaw.
- Sequencer patch `docs/kb/tech/hero_motion_sequencer.patch`, against m2-slice @ 94feee33. It applies cleanly,
  and the cutscene, prologue, fp_ and sequencer tests pass with it. Docs: `docs/kb/tech/hero_motion.md`.
- Shot `hero_cutscene_turn_strip` and its baseline. Tests: test_hero_cutscene_motion (7) and
  test_hero_idle_micro (8).

## Exact next step
m2-slice merges this branch (for game/hero_motion/**), then runs
`git apply docs/kb/tech/hero_motion_sequencer.patch`. Then capture a prologue or Haluna shot to confirm Asha
breathes in situ.

## Known issues
- Haluna's posed Asha (`Actors/asha`) has her model facing +Z under a root that the sequencer turns with -Z as
  forward. A `_turn_to` on her would turn her back to the target. Either the body or the root needs a 180°
  offset (HeroFieldActor's or m2-slice's decision).
- The head lead caps at 24° for most of a fast 120° turn, because the M2-FP-29 peak rate is about 600°/s. It
  reads well in the strip. Lower `max_deg` if it reads twitchy in motion.

## Files
game/hero_motion/hero_motion.gd, hero_idle_micro.gd; game/data/hero_motion/idle_micro.json;
game/levels/_tests/hero_motion/cutscene_turn_strip.{gd,tscn}; tests/unit/test_hero_cutscene_motion.gd,
test_hero_idle_micro.gd; tests/screenshots/shots.json, baselines; docs/kb/tech/hero_motion.md,
hero_motion_sequencer.patch; the M2-HER-1104 task file.
