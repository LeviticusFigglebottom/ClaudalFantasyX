---
id: M2-HER-1107
title: "Field gait on M2-CHR-12's locomotion clips: measured speeds, starts and stops, turn in place, idle variants"
role: architect
status: review
owner_session: "hero-integration (claude/hero-integration)"
reviewer: character
depends_on: [M2-HER-1101, M2-HER-1102]
milestone: M2
request-from: lead
---
## Goal
The field bodies (HeroFieldActor, its followers) use the characters track's new locomotion set (M2-CHR-12,
`game/data/characters/locomotion.json`): the rebuilt walk and run at their measured speeds, walk/run starts and stops,
turn in place with the feet stepping, and an idle variant. Today the old walk is stiff and the run slides ~25%.

## Acceptance criteria
- [x] Gait speeds come from `locomotion.json` (per hero walk/run `speed_mps`) when it exists, else hero_motion.json
      field.heroes; the foot-plant test compares the effective data with HeroClipGait's measure of the model's clips.
- [x] Starts and stops: from still (speed over a data threshold) the body plays walk_start / run_start over the blend,
      and walk_stop / run_stop when it slows to a stop; hysteresis and a minimum still time stop the churn.
- [x] Turn in place: still with a facing error over a data threshold, the closest of turn_in_place_l90 / r90 / 180
      plays and the visible yaw follows its root_yaw_deg curve, capped per frame, ending on the target.
- [x] Idle variant: idle_shift once after a deterministic per-hero idle time.
- [x] Re-tune field speeds so the foot slide is under ~10% at walk and run (rationale below).
- [x] Duck-typed: everything works and tests pass with and without M2-CHR-12's clips.
- [x] Tests (`-- --filter=hero` on both branches; field and zone on ours). Shots viewed on the trial.

## Notes
- **Built (worktree agent, 2026-10-24).** `game/hero_motion/hero_gait_clips.gd` (HeroGaitClips: a pure state
  machine, no Nodes, no randomness) plus a small layer in `hero_field_actor.gd`. Each action slot now plays through
  its own TimeScale (`ts_a` / `ts_b`), so a gait clip's time is driven frame by frame. Data:
  hero_motion.json `field.gait_clips` (thresholds, blends, clip names) and `field.gait_measure.planted_ball`.
  Public APIs are unchanged: HeroLocomotion, `HeroFieldActor.play_clip`, `HeroMotion.play` and
  `set_locomotion_speed`.
- **Duck-typed.** `HeroFieldActor.gait_speeds(id)` reads `game/data/characters/locomotion.json` walk/run `speed_mps`
  when it exists, else hero_motion.json `field.heroes`. A clip plays only when the model has it AND locomotion.json
  has its root curve. Without M2-CHR-12 the body blends and spins exactly as before.
- **Starts are played by distance, not time.** The start's clip time is wherever its `root_travel_m` curve has
  covered the ground the body has, with the scale capped at `max_scale`. So the feet stay planted whatever the
  controller's acceleration (9 m/s2 plays the run start at about 1.3x). Its last frame is the cycle's first frame,
  and the blend restarts there (`hand_back_sec` 0.08). The FieldController's stick gives the target speed (walk or
  run start). Followers and cutscene roots can't tell, so they walk off and switch to the run start while it has
  covered at most 0.12 m.
- **Stops.** A stop triggers when the stick is released, or for other sources when the speed falls under
  0.5 x walk speed. It enters where its remaining root travel equals the distance left to stop (v^2/2·decel), plays
  by distance, and finishes at 1x once the body is still. Hysteresis: one stop per run of motion, a start needs
  `min_still_sec` (0.3 s) of rest, and pressing again cancels a stop at once.
- **Turns in place.** These play when the body is still and rested and the facing is 60° or more away. The 90s are
  used up to 135°, and the 180 beyond it (it turns left, so a right turn past 135° goes the long way, ≤ 225°). The
  visible yaw follows the clip's `root_yaw_deg` curve scaled to land on the facing, and each frame is still capped
  at max_rate (400°/s).
- **Idle variant.** `idle_shift` plays once after 8 s + a per-hero share of 5 s (HeroIdleMicro.share). **idle_breathe
  is not used as the standing loop.** HeroIdleMicro already layers breathing and a weight shift procedurally over
  `idle`, so idle_breathe would double the breath. `idle` also joins every start, stop and turn exactly.
- **Gait measure.** M2-CHR-12's walk and run pivot the planted foot on its ball, so the ankle-based measure reads
  them 30–43% slow (Rhen walk 0.69 vs 0.98). The `planted_ball` block measures the toe bones' heads within 5 mm for
  those clips. Our independent numbers come within 3.4–7.9% of locomotion.json's (Rhen 0.931/2.763 vs 0.984/3.00,
  Asha 0.841/2.474 vs 0.882/2.59, Toma 1.007/2.760 vs 1.042/2.863), inside the 10% tolerance. The old clips keep
  the ankle measure. The foot-plant test checks whichever set the model has.
- **Re-tune (field_movement.json, with m2-slice's OK): walk 1.5 → 1.0 m/s, run 4.6 → 3.6 m/s.** The other option was
  raising max_playback_scale.
  - **Run.** The new run clips plant at 2.59–3.00 m/s with 1.9–2.1 m strides, so 4.6 m/s needs scales of 1.53–1.78.
    That gives 4.6–4.9 steps/s, a sprint cadence on a jog stride, which reads frantic. Under the 1.5 cap it slides
    2% (Rhen), 15.5% (Asha) and 6.7% (Toma). At 3.6 the scales are 1.20 / 1.39 / 1.26 (3.4–3.8 steps/s), under the
    cap, so the nominal slide is 0%; by our own planted-ball measure it is 7.9% / 4.5% / 3.6%. Before this task, with
    the old clips at 4.6, the run slid 23% (Rhen), 34% (Asha) and 26% (Toma). 3.6 rather than 3.4 keeps
    footsteps.json's `run_above_m_s` 3.5 classifying it as a run (audio's file, untouched).
  - **Walk.** The new walks are deliberately slow (0.88–1.04 m/s, 1.0–1.25 m strides). At 1.5 the blend was 25–35%
    run cycle mixed into the walk (unsynced cycles, mushy feet). At 1.0 Rhen is a pure walk (slide 0% nominal, 5.4%
    measured), Asha (a follower at his pace) carries 7% run and Toma 4% idle. Viewed: the walk now reads as a real
    heel-to-toe stride (field_hero_rhen_walk on the trial).
  - Acceleration 9 and deceleration 12 are unchanged, for responsiveness. The cost is the walk stop: the body stops in
    about 4 cm, so only the walk stop's last step plays, crossfaded from the cycle. The run stop (from 3.6, about
    0.54 m) plays nearly whole, planted.
- **Tests.** `tests/unit/test_hero_field_gait.gd` has 13 tests. Most run on an injected locomotion table; three drive
  the field body and check whichever clips the model has. `test_hero_field_actor.gd`'s foot-plant test now uses
  `gait_speeds` and `measure_config`. `test_hero_followers.gd`'s spacing check runs 300 frames: obstacles past the
  Court kink the trail, and at 3.6 m/s the followers were mid-sway at frame 240.
- **Shots.** New `field_hero_gait_strip` (`game/levels/_tests/hero_motion/`): rows for a run start, a run stop and a
  turn in place. It renders sensibly on this branch too (blend and spin). It, `field_hero_rhen_walk` (now 122 frames,
  so the walk ends beside the capsule at 1.0 m/s) and `field_hero_party` need their baselines approved **after the
  Lead merges characters**.

## Review log
