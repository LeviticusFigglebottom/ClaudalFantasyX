# Handoff — architect (hero integration, field) — 2026-10-24 #1

## Done
- M2-HER-1101 (review, reviewer character): HeroFieldActor puts the real hero model on the field player through one
  hook line in FieldController._ready, and on every CutsceneStage `Actors/<hero id>` capsule (runtime scan, no zone
  edits). AnimationTree locomotion (BlendSpace1D by measured speed -> TimeScale) plus a `play_clip(name, blend,
  hold)` action layer for the sequencer; eased, rate-capped yaw decoupled from the controller; teleport snap.
  Clip speeds measured by HeroClipGait (per hero in hero_motion.json `field.heroes`). Field tuning: walk 1.5 m/s,
  accel 9, decel 12.
- M2-HER-1102 (review): HeroFieldParty, Asha and Toma on Rhen's breadcrumb trail, hidden while a cutscene holds the
  player or the stage shows the same hero.
- Shots field_hero_rhen_walk and field_hero_party with baselines; 18 new tests.

## In progress
- Nothing.

## Exact next step
- m2-slice: switch CutsceneSequencer `_play_clip` / `_cue_anim` to call `play_clip(clip, clip_blend_sec)` on the
  actor's `HeroBody` child (`HeroFieldActor.NAME`) when present (the AnimationPlayer route works meanwhile).
- characters (M2-CHR-12): a walk and a run whose feet pass under and ahead of the hips (today they swing only
  behind), then update `field.heroes` speeds (the test re-measures them) and raise the run toward 4.6 m/s.

## Known issues
- The run slides ~25% at 4.6 m/s (clip natural 2.35, playback cap 1.5). See the task notes.
- The Lantern on the Haluna player turns with the controller, not the eased body (a few frames at most).
- test_shrine_audio::test_the_zone_plays_the_shrine_cue fails in this worktree with or without the hook (music).

## Files touched
game/hero_motion/hero_field_actor.gd, hero_field_party.gd, hero_clip_gait.gd; game/data/hero_motion/hero_motion.json;
game/data/world/field_movement.json (walk, accel, decel); game/world/field_controller.gd (one line);
game/levels/_tests/hero_motion/**; tests/unit/test_hero_field_actor.gd, test_hero_followers.gd;
tests/screenshots/shots.json (two rows); tests/screenshots/baselines/field_hero_{rhen_walk,party}.png;
docs/kb/tasks/M2/M2-HER-1101-*.md, M2-HER-1102-*.md.
