---
id: M2-HER-1101
title: "Field hero actor: the player's capsule becomes Rhen, with a locomotion blend, eased turning and ground alignment"
role: architect
status: review
owner_session: "hero-integration (claude/hero-integration)"
reviewer: character
depends_on: []
milestone: M2
request-from: lead
---
## Goal
The human's playtest: walking around in the field, the heroes are still capsules. The player becomes the real Rhen
model in every slice zone (Haluna, the Saltgrass Causeway, the Shell Shrine, the tideline / First Verse) and moves
naturally: no snapping turns, no instant start or stop.

## Acceptance criteria
- [x] `HeroFieldActor` (game/hero_motion/) shows a hero model on a FieldController and hides its capsule stand-in;
      one hook line (`HeroFieldActor.attach(self)` in FieldController._ready, like FieldHud) covers every zone, the
      greybox zones included, with no zone scene edits.
- [x] An AnimationTree locomotion BlendSpace1D (idle / walk / run by ground speed) with a playback scale so the feet
      plant (clip speeds measured from the clips, in game/data/hero_motion/hero_motion.json).
- [x] The visible body turns toward its travel at a data-driven max turn rate, eased in and out, never snapping
      (HeroLocomotion). When still it turns to its node's facing (so cutscene `_face` calls on the player ease too).
- [x] Foot-plant-friendly start and stop: the gait speed is filtered, and the field acceleration and deceleration are
      tuned so the body visibly accelerates (field_movement.json, coordinated with m2-slice).
- [x] Ground alignment: feet on the floor (the controller's origin is its feet), teleports and zone loads snap.
- [x] Tests: turn-rate cap and no snapping frame to frame, blend weights by speed, the hook hides the stand-in, the
      clips exist on the model. Shots: field_hero_rhen_* (viewed).

## Notes
- ADR 0190. Core maths: game/hero_motion/hero_locomotion.gd (tests/unit/test_hero_locomotion.gd).
- m2-slice owns the zone flow and scenes; this adds no zone edits. Its live log is told.
- **Built (worktree agent, 2026-10-24):** `game/hero_motion/hero_field_actor.gd` (HeroFieldActor, the body; one hook
  line in FieldController._ready), `hero_clip_gait.gd` (HeroClipGait, the clip speed measure), data under
  hero_motion.json `field`. The body is a top_level child of the node it follows; it copies the position (feet on
  the origin) and turns through HeroLocomotion (toward travel when moving, the node's facing when still), so the
  controller's instant rotation and the sequencer's `_face` never show as a snap. Speed = the node's per-frame
  position delta (cutscene moves animate too); a jump over gait.teleport_m snaps. AnimationTree (manual advance):
  BlendSpace1D loco -> TimeScale, plus two action slots behind a Transition: `play_clip(name, blend = -1, hold =
  false) -> bool` is the sequencer's entry point (a locomotion clip name returns to the blend; a one-shot returns
  when it ends unless `hold`; a loop stays). Plays the sequencer still starts on the model's AnimationPlayer are
  routed through play_clip (the player itself is kept inactive), so nothing fights the tree before m2-slice
  switches `_play_clip`/`_cue_anim` to `play_clip`.
- **Stage actors (m2-slice's added scope):** the same attach scans the zone's CutsceneStage `Actors/<id>` (at the
  player's _ready and every followers.rescan_sec) and gives every hero-id capsule a body (`attach_actor`), hiding
  the stand-in visuals named in `field.standin_names` (StandIn, Facing, Body, Spear); villagers (no hero row) and
  actors that already show a real model (an AnimationPlayer or Skeleton3D under them, e.g. Haluna's posed asha)
  are left alone. So greybox `_build_stage` needed no edit: the runtime scan covers it and the hand-placed
  Haluna / Shell Shrine / First Verse capsules alike. The Lantern (and LanternLight) stay on the controller.
- **Clip speeds, measured** (HeroClipGait: each DEF-foot bone in contact while within 2 cm of its lowest height;
  its backward speed then, averaged over contact samples of both feet; 240 samples a cycle): Rhen walk 1.09 /
  run 2.35 m/s, Asha 0.95 / 2.01, Toma 1.08 / 2.26. In hero_motion.json `field.heroes` (per hero) and `gait`
  (Rhen's); test_the_clip_speeds_match_the_measured_foot_plant guards 10%. When M2-CHR-12's
  game/data/characters/locomotion.json (speed_mps, stride_m) lands, the per-hero rows can read from it; start,
  stop and turn clips slot into the action layer (play_clip) or a Transition before `loco`.
- **The clips are the limit:** the current walk and run swing the feet only BEHIND the hips (DEF-foot.L z runs
  +0.02 .. -0.36 m in the walk, -0.04 .. -0.56 m in the run, model space, the hips at -0.03), pendulum-like with
  no real stance, so their natural speeds are low and some frames read as trailing legs (seen in a test frame of
  field_hero_rhen_walk). Request (M2-HER-1105 / M2-CHR-12): a walk at ~1.4–1.6 m/s and a run at ~4 m/s with the
  feet passing under and ahead of the hips, plus walk/run start and stop and turn-in-place.
- **Field tuning (field_movement.json, OK'd by m2-slice):** walk_speed 2.4 -> 1.5 m/s (a human walk; the blend is
  ~2/3 walk 1/3 run there, the feet near planted); acceleration 18 -> 9 m/s² (0 to run in 0.5 s, so the gait rolls
  through walk into run instead of popping); deceleration 24 -> 12 m/s² (run to stop in 0.38 s, ~0.9 m). Run stays
  4.6 m/s (traversal pace, not this track's row): the run clip plays at the max_playback_scale cap 1.5 there
  (natural 3.5 m/s), so the run feet still slide ~25% until the improved run clip lands; then raise run_clip_mps
  (or lower run_speed toward it). Turn: the body's 400°/s eased cap (hero_motion.json turn) is what shows; the
  motor's 720°/s facing is untouched.
- **Tests:** tests/unit/test_hero_field_actor.gd 11/0 (hook hides the stand-in and shows Rhen, idempotent; the
  locomotion clips exist; feet on the origin facing forward; blend by speed and the run playback scale; the tree
  animates the skeleton; a 180° stick reversal through FieldController.step never turns more than the cap per
  frame and lands on travel / rests on facing; a still body eases to a `_face`; teleport snaps; play_clip loop /
  one-shot / hold / locomotion / missing / routed AnimationPlayer play; stage hero capsules get bodies, villagers
  and real models don't; measured clip speeds). Regression filters run green: field 97/0, zone 42/0, cutscene
  34/0, haluna 46/0, fp_ 24/0, ch0 13/0, shrine 35/1 (the one failure, test_shrine_audio
  test_the_zone_plays_the_shrine_cue, fails the same with the hook off: the music stream is absent in this
  worktree, unrelated), interact_prompt 6/0, objective 11/0, town_services 4/0, tutorial 4/0, test_camera_director
  34/0.
- **Shots:** field_hero_rhen_walk (Rhen mid-walk beside a greybox capsule for scale) and field_hero_party (the
  three on an arc), from game/levels/_tests/hero_motion/hero_field_shot.gd (fixed steps through the game's own
  calls, then frozen; re-captures were byte-identical). Viewed: feet on the floor, shadows under them, facing the
  travel, Rhen ~1.6 m beside the 1.72 m capsule; also viewed (not a baseline) real Haluna at its spawn: Rhen by the
  save shrine, no capsule, the lantern glow at his side.

## Review log
