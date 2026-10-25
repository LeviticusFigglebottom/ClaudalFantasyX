# Hero motion: the cutscene side (M2-HER-1104, ADR 0190)

The human's playtest said the prologue's heroes moved "too spontaneous and rigid". m2-slice's M2-FP-29 fixed
the motion itself: `CutsceneMotion` (game/cutscene/cutscene_motion.gd) eases every turn and ramps every walk,
and the sequencer cross-fades clips. **The motion maths stays there.** The sequencer moves and turns the actor
**root**; this layer only reaches the body under that root.

## API: `HeroMotion` (game/hero_motion/hero_motion.gd, static)
| Call | What it does |
|---|---|
| `play(actor: Node3D, clip: StringName, blend_sec := -1.0, restart := true) -> bool` | A body under the actor (two levels deep) with `play_clip(clip, blend) -> bool` plays it (HeroFieldActor's AnimationTree, M2-HER-1101). Otherwise the actor's AnimationPlayer cross-fades to it (`blend_sec < 0`: the player's default). `restart = false` leaves a clip already playing alone. False when nobody has the clip. |
| `set_locomotion_speed(actor: Node3D, mps: float)` | Forwards the root's ground speed to a body with `set_locomotion_speed(mps)`, so a speed-driven gait blend follows the walk's ramps. It also fades the idle micro-motion out above `still_below_mps`. |
| `set_idle_amount(actor: Node3D, amount: float)` | Sets the micro-motion's target strength (1 standing, 0 walking). It eases there by itself. |
| `add_micro_motion(actor: Node3D, actor_id := &"") -> HeroIdleMicro` | Adds a `HeroIdleMicro` under the actor's Skeleton3D, once. Returns null and changes nothing on a capsule. |
| `body_of(actor)`, `player_of(actor)`, `skeleton_of(actor)`, `micro_of(actor)` | Finders. |

The calls are duck-typed (`has_method`), so this branch needs no body class.

## Idle micro-motion: `HeroIdleMicro` (a SkeletonModifier3D)
It runs after whatever clip or pose the skeleton shows (Godot 4.6's `_process_modification_with_delta`). The
skeleton restores the pose after each frame, so nothing accumulates. It adds:
- **Breathing:** the chest pitches back over `DEF-spine.002..004`, the head counters it, and the shoulders lift.
- **Weight shift:** the hips roll and yaw, the thighs counter so the feet stay planted, and the spine counters
  so the head stays level.
- **Head lead:** while the body turns at rate r, the neck and head (`DEF-spine.003..006`) turn `r * lead_sec`
  ahead of it, capped at `max_deg`. The rate is measured from the skeleton's own yaw each frame, so it works
  under any turn: the sequencer's eased root turn or the field's. A driver may set `turn_rate` instead
  (`use_measured_rate = false`).

The tuning is in `game/data/hero_motion/idle_micro.json`. Each actor's phases and periods come from a hash of
its id, so the motion is deterministic and no two heroes breathe in step. `amount` scales the breathing and
the sway only, never the head lead. A bone missing from a rig is skipped.

## Sequencer opt-in: `docs/kb/tech/hero_motion_sequencer.patch`
The patch is a unified diff against `origin/claude/m2-slice` `game/cutscene/cutscene_sequencer.gd` (94feee33,
which includes M2-FP-29). Apply it with `git apply docs/kb/tech/hero_motion_sequencer.patch` after merging this
branch, which brings `game/hero_motion/**`. It changes four places:
- `_begin`: `HeroMotion.add_micro_motion` on every `stage.cast()` member (the player as `rhen`).
- `_play_clip`: `HeroMotion.play(actor, clip, _clip_blend(), false)`, which keeps the old "don't restart"
  behaviour.
- `_cue_anim`: `HeroMotion.play(actor, clip, _clip_blend())`.
- `_cue_mark`: each frame of the move reports the root's speed (`_locomotion`), and the move reports 0 when
  it lands.

`_turn_to` and `_face` are unchanged. The eased root turn is already M2-FP-29's, and the head lead rides on
top of it.

## Shot
`hero_cutscene_turn_strip` (game/levels/_tests/hero_motion/cutscene_turn_strip.tscn) shows Asha five times,
left to right, at 0, ¼, ½, ¾ and the end of a 120° cutscene turn. The yaw comes from the M2-FP-29 curve
(`ease(t, -2)` over 0.25..0.45 s by angle), and the head lead is fed the curve's rate. It uses an
orthographic camera, so the frames compare without perspective skew.
