---
id: M3-HER-1231
title: "FAST-TRACK: Rhen's walk animation randomly stops (he slides): a cutscene clip left on the field body"
role: architect
status: review
owner_session: "integration-qa (claude/hero-integration)"
depends_on: []
milestone: M3
reviewer: character
---
## Goal
The human's 2026-11-03 playtest: "the walk animation stops playing for the main character randomly". Find the
root cause headless, fix it, and add a regression test that fails on the old code.

## Root cause
HeroFieldActor keeps a looping clip, or one played with `hold`, until the next `play_clip`, and while one shows
it holds the gait clips and the locomotion blend off. The CutsceneSequencer plays `talk` (a loop) on a line's
speaker, but sends it back to `idle` only after a line the player advanced by hand. An overheard bark
(`auto_advance`, `hold_player = false`: the player keeps walking), a timed line or a skipped line leaves the
speaker in `talk`. A held pose (`hold_clips`: kneel, spear_level and the like) also stays on after a scene's
`_finish`. On Rhen, the field player's body, that meant the player walked a talking or kneeling Rhen across
the field. "Randomly" was whenever Rhen spoke a bark or a scene ended on a held pose.

## Fix (game/hero_motion/hero_field_actor.gd, data hero_motion.json field.clip_release)
- When the player steers (a FieldController that accepts input, with the stick pushed), any clip gives way
  to the locomotion.
- A loop nobody asked to hold gives way after a body (a follower, a stage root) has travelled at least
  0.5 × its walk clip speed for 0.6 s. That is longer than a stand-in glide (0.5 s).
- Explicit holds on bodies the player doesn't steer stay, and so does every clip while a scene holds the
  player's input.

## Acceptance criteria
- [x] `tests/unit/test_hero_walk_cycle.gd`: 3 of its 5 tests fail on the old code (talk left on: thigh swing
  0.0°); all 5 pass with the fix.
- [x] Shot `field_hero_walk_release` (pending_baseline), self-rendered and viewed: before the fix the bark row
  slides in `talk` and the held row slides kneeling; after it, all three rows show the stride.
- [x] Stop and start, reversals, a teleport: the walk shows on every travelling frame (old code too: the
  gait state machine was not the cause).

## Review log
