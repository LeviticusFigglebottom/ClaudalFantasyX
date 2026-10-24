---
id: M2-HER-1104
title: "Cutscene motion quality: eased turns, walk start/stop blending and idle micro-motion for the sequencer"
role: cinematics
status: review
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
- [x] `HeroMotion` API (game/hero_motion/): turn_to(actor, yaw) eased and rate-capped (HeroLocomotion), play(actor,
      clip, blend) with crossfades, and a walk start/stop that blends idle -> walk -> idle over the move.
      (Changed by m2-slice's M2-FP-29: see Notes.)
- [x] Idle micro-motion (breathing, weight shift) as a SkeletonModifier3D layered on any clip or pose, data-driven,
      deterministic per actor.
- [x] Opt-in for the sequencer: a short patch (or m2-slice applies it) so `_turn_to`, `@move` and `@anim` go through it.
- [x] Tests (no snapping in a turn, blend weights through a start and a stop) and a cutscene turn strip shot, viewed.

## Notes (2026-10-24, worktree agent)
- **Plan change (coordinator, after m2-slice's M2-FP-29):** `CutsceneMotion` already eases the root turns and
  ramps the walks, so this task does not duplicate that maths. `HeroMotion` is the per-body entry point
  (`play`, `set_locomotion_speed`, `set_idle_amount`, `add_micro_motion`). It is duck-typed against the field
  agent's body (`play_clip(name, blend) -> bool`, `set_locomotion_speed(mps)`). No rate-capped body-yaw
  follow was built: the root turn is m2-slice's, and the head lead rides on top of it. A cap needs a body that
  turns separately from its root, which is HeroFieldActor's job (M2-HER-1101).
- `HeroIdleMicro` (a SkeletonModifier3D using `_process_modification_with_delta`) adds breathing, a weight
  shift and a head lead measured from the skeleton's own yaw. Its data is
  `game/data/hero_motion/idle_micro.json`. Godot 4.6.3 restores the pose after modifiers (checked), so
  nothing accumulates.
- The patch is `docs/kb/tech/hero_motion_sequencer.patch`, against origin/claude/m2-slice @ 94feee33.
  `git apply --check` is clean. With it applied, plus game/hero_motion/**, a scratch copy of m2-slice passes
  cutscene 44/0, prologue 5/0, fp_ 26/0 and sequencer 17/0. The docs are in `docs/kb/tech/hero_motion.md`.
- Tests: test_hero_cutscene_motion 7/0, test_hero_idle_micro 8/0.
- Shot `hero_cutscene_turn_strip`: Asha at five times through a 120° eased turn. The head visibly leads
  mid-turn and settles as the turn lands. The baseline is approved, and a re-capture gives rmse 0.

## Review log
