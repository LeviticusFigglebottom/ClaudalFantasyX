# Live log: hero-integration environment

**This environment owns this file** (CLAUDE.md §7a). Cloud session `session_013oczHh2qUMy5kVz7nXsZef`, branch
`claude/hero-integration` (cut from `claude/undertow-lead-handoff-423ixt` at 07781cba). The Lead
(`session_019iimsngAgPLEram1wcbLpE`) reads it every 20 minutes.

**Why this track exists (the human's playtest):** the real heroes show only in cutscenes; in the field and in battle
they are capsules and stand-ins, and the prologue's motion reads "too spontaneous and rigid" (snapping turns, instant
walk start and stop). Make the real Rhen, Asha and Toma appear and move naturally everywhere the player sees them.

## Tasks (filed 2026-10-24; ids checked free on every branch)
| Task | Role | State |
|---|---|---|
| M2-HER-1101 field hero actor (Rhen, locomotion blend, eased turns, start/stop, ground) | architect | review (character) |
| M2-HER-1102 field party followers (Asha, Toma on a trail) | architect | review (character) |
| M2-HER-1103 battle hero actors (meet UI-07 + CHR-07 + BPR-10, check every contract clip on the real models) | combat | doing: waits on ui / characters / battle-presentation merges |
| M2-HER-1104 cutscene motion API (eased turn, walk start/stop, idle micro-motion) for m2-slice's sequencer | cinematics | review (cinematics) |
| M2-HER-1105 clip-gap requests to the characters track | character | doing (characters, M2-CHR-12) |
| M2-HER-1106 shots and tests | qa | doing (battle shots wait on the merges) |

**Lead: please record the claims on the integration branch** (commit 34f0ce2e: the six task files, the ownership row
`game/hero_motion/**`, `game/data/hero_motion/**`, `game/levels/_tests/hero_motion/**`, `tests/unit/test_hero_*.gd`,
and ADR 0190 "hero motion layer", proposed).

## Done
- **HeroLocomotion** (`game/hero_motion/hero_locomotion.gd`, data `game/data/hero_motion/hero_motion.json`): the pure
  maths every hero body shares. The yaw turns at most `max_rate_deg_per_sec` (400) per second, eases in
  (`max_accel`) and out (`settle_gain`), lands without overshoot; the gait blend (idle/walk/run weights by speed, a
  playback scale past the run's clip speed, a filtered speed so a stop rolls through the gait). 9 tests,
  `-- --filter=hero_locomotion` 9/0, lint and format clean, validate_data 0.

- **M2-HER-1104 cutscene motion → review (cinematics)** (408a5bc1, da6dd917):
  - `HeroMotion` (static): `play(actor, clip, blend, restart)` goes to the body's `play_clip`, or cross-fades the
    AnimationPlayer; `set_locomotion_speed`; `add_micro_motion`.
  - `HeroIdleMicro` (a SkeletonModifier3D): breathing, a weight shift with the feet planted, and the head leading
    the turn (capped at 24°). Deterministic per actor id. Data: `idle_micro.json`.
  - **The sequencer patch** is `docs/kb/tech/hero_motion_sequencer.patch`, against claude/m2-slice 94feee33. It
    builds on M2-FP-29 rather than replacing it. `git apply --check` is clean, and with the patch applied cutscene is
    44/0, prologue 5/0, fp_ 26/0, sequencer 17/0. m2-slice merges this branch first, then applies the patch.
  - **Tests:** 15 new, plus the hero filter at 30/0.
  - **Shot `hero_cutscene_turn_strip`** (viewed): Asha through a 120° turn on M2-FP-29's curve. The head visibly
    leads the torso at ¼ and ¾ and settles over the body at the end.
  - **Haluna's Asha facing: fixed by m2-slice** (claude/m2-slice 74ed95b4). Her Model is turned 180° with the pose
    conjugated, and the root's -Z is now her face.
  - **m2-slice applies the patch after the Lead gates claude/hero-integration onto the integration branch.** The human
    plays claude/m2-slice. **Lead: the patch waits on this branch's merge.**

- **M2-HER-1103 battle hero actors** (6d5fcf4a, 95081441; still doing, waiting on other tracks):
  - **Trial merge** of ui 427c65fc, characters 34cea6d6 and battle-presentation 329ce604 (local, not pushed).
    Conflicts: field_encounters.gd (additive), shots and flags (merge_union), project.godot translations (union),
    and a duplicate BOOT_FIRST_RUN_NOTE dropped. **Lead:** `rate_pct` isn't in FieldEncounters `meters`.
  - **On the real models** (freeze-frames viewed): idle, attack at contact and cast read well. Every clip change
    crossfades with no pop.
  - **Gaps:**
    - The KO sinks 0.25 m through the floor (UI fix).
    - Victory is near idle (characters).
    - The KO is a kneel, not a fall (contract or clip).
    - Rhen strikes empty-handed (characters).
    - 4 battle-presentation tests assume capsule heroes and fail once UI-07's data lands (test-only diffs given).
  - **Built:** HeroBattleActor wrapper scenes (`game/hero_motion/battle/<hero>_battle_actor.tscn`). They give
    per-pair crossfades (so a revive takes 0.9 s instead of springing up), an offset idle phase per hero, and
    micro-motion. They take effect when UI points `battle_sandbox.json` at them.
  - **Proposed patches** for UI and battle-presentation: `docs/kb/tech/hero_battle_proposed.patch`. Requests were
    sent to ui, battle-presentation and characters (M2-HER-1105 lists the clip asks).
  - **Tests:** hero 35/0 on this branch. On the trial with the patches: choreo 40/0, fighter 4/0, clips 7/0.
  - **UI landed the set_ko fix** on claude/ui @ 781f9da6, with a test: an actor with a KO clip fades without sinking. They repoint the stand_ins at the wrappers
    after this branch reaches the integration branch. Their files stay off this branch.
  - **Shots** `battle_heroes_*` wait until the three branches are merged.

- **M2-HER-1105 was taken by characters in full.** M2-CHR-12 covers the locomotion clips under our names, plus
  run_start, idle_breathe, a better walk and run, `game/data/characters/locomotion.json` (stride_m and speed_mps per
  clip) and foot-down markers. The battle fixes follow it: victory, a lying KO, Rhen's hooks in hand, and a revive.
  They'll message each landing sha.

- **M2-HER-1101 / 1102: field hero actor and followers → review (character).** Commits 9e9a3f70..d7b4237b,
  then fa411948 and 32d59835.
  - **One hook line** in `FieldController._ready`: `HeroFieldActor.attach(self)`. It hides the capsule
    (StandIn/Facing) and shows the real Rhen (LOD1), in every zone, with no zone scene edits.
  - **The same attach covers the cast.** It gives bodies to the CutsceneStage/Actors hero capsules: the greybox
    `_build_stage` actors and the hand-placed ones in Haluna, the Shrine and First Verse. Villagers and real models
    are left alone.
  - **Animation:** an AnimationTree with an idle/walk/run BlendSpace1D by measured speed, and a playback scale.
    `play_clip(name, blend, hold)` plays one-shots over the locomotion and returns to it; clips started on the
    model's AnimationPlayer are routed through it.
  - **Turning:** the visible yaw follows HeroLocomotion (400°/s cap, eased in and out). A still body eases to its
    node's facing, so the sequencer's `_face` on the player eases too.
  - **Idle micro-motion** (M2-HER-1104) is on every field body, fading out while walking.
  - **Followers** (`HeroFieldParty`): up to 2 from `party_ids`, on Rhen's breadcrumb trail at 1.15 m. They
    accelerate at 9 and brake at 12, and stand on a floor ray. They snap after a teleport, and hide during
    `hold_player` cutscenes and while the stage shows the same hero.
  - **Measured clip speeds** (`HeroClipGait`, foot plant from the bone tracks):

    | Hero | Walk m/s | Run m/s |
    |---|---|---|
    | Rhen | 1.09 | 2.35 |
    | Asha | 0.95 | 2.01 |
    | Toma | 1.08 | 2.26 |

    A test holds the data within 10% of these.
  - **field_movement.json:** walk 2.4 → 1.5 m/s, acceleration 18 → 9, deceleration 24 → 12. Run stays 4.6 m/s;
    that clip plays at its 1.5× cap, so the feet slide about 25% at a full run until M2-CHR-12's run clip lands.
  - **Shots** `field_hero_rhen_walk` and `field_hero_party`, viewed and re-approved with the micro-motion on. Rhen
    reads at the right scale with his feet on the floor. The party trails on his curve. The walk pose itself is
    stiff; that's the clip, which M2-CHR-12 replaces.
  - **Haluna** (viewed, not a baseline): Rhen at the spawn, with no capsule left.
  - **The field camera shots re-approved after viewing** (e758a9a5+):

    | Shot | RMSE before |
    |---|---|
    | field_lane_fixed | 0.063 |
    | field_court_pan | 0.022 |
    | field_causeway_dolly | 0.063 |

    In all three the only change is Rhen replacing the capsule: grounded, shadow right, framing kept.
    shrine_s01..s05 pass unchanged (no player in frame).
  - **Rhen carries the zone's LanternLight** in his own lantern glass (bone-attached), and Haluna's duplicate capsule
    lantern mesh is hidden (e758a9a5).
  - **Known limits:** after a teleport, a follower can briefly stand inside a wall until the trail fills in. The
    Haluna Lantern turns with the controller, not the eased body.

## MERGE-READY @ 96a93363 (+ this log commit)
- **Since the full suite on 555714d3:** the lantern carry (e758a9a5; hero_field 13/0) and the field shot re-approvals.
- **Items:** M2-HER-1101, 1102, 1104 (with its sequencer patch for m2-slice) and 1103's helper; claims, ADR 0190.
- **Checks run** (on 32d59835, with the integration branch 0b1e76a4 merged in):

  | Check | Result |
  |---|---|
  | hero | 54/0 |
  | field | 98/0 |
  | zone | 42/0 |
  | cutscene | 41/0 |
  | haluna | 46/0 |
  | fp_ | 24/0 |
  | shrine | 35/1 |
  | shots field_hero_rhen_walk, field_hero_party, hero_cutscene_turn_strip | 3/0, viewed |
  | gdlint, gdformat, validate_data, taskboard | clean |

- **The one shrine failure is pre-existing.** `test_shrine_audio::test_the_zone_plays_the_shrine_cue` fails the same
  on a pristine checkout of the integration branch 0b1e76a4.
- **Checks skipped:**
  - coverage: no `game/battle` or `game/progression` change;
  - Blender: no source touched;
  - tools unittest: no `tools/` change;
  - other shots: the field_* camera shots were re-approved after viewing (see above). The remaining zone shots don't
    show the player.
- **Full Godot suite on 555714d3: 1996 run, 0 failed.** The shrine audio test passes in the full run, so it's an
  ordering race in the filtered run, not this change.

## API consumers (keep these stable; tell them before changing)
- **creatures' FieldNpc** (M3-CRE-610, parked on claude/creatures until this branch merges) uses:
  - HeroLocomotion: `new(data)`, `configure`, `reset_yaw`, `step_yaw`, `step_speed`, `weights`, and the
    hero_motion.json keys;
  - HeroMotion: `play(actor, clip, blend)`, `add_micro_motion`, `set_locomotion_speed`;
  - HeroIdleMicro.
- **m2-slice's sequencer patch** uses `HeroMotion.play` and `set_locomotion_speed`, and HeroFieldActor's `play_clip`.

## In progress
- **M2-HER-1107 (worktree agent): the field gait on characters' M2-CHR-12 clips.** They're on claude/characters
  eee3099a+ (MERGE-READY): walk_start, walk_stop, run_start, run_stop, turn_in_place_l90/r90/180, idle_breathe,
  idle_shift, a rebuilt walk and run, and `locomotion.json` speeds. The code is duck-typed, so it lands here without
  the clips and is verified on a local trial merge with claude/characters.
  - Field speeds get re-tuned to the new clip speeds (Rhen walk 0.98, run 3.00 m/s).
  - **Lead:** the field_hero_* baselines get re-approved after characters merges.
- Battle: waiting on the three tracks (see M2-HER-1103) to merge; then the battle_heroes_* shots get approved.
- Characters' M2-CHR-12 clips: when they land, feed `locomotion.json`'s speeds to the gait, and slot start, stop and
  turn clips into `play_clip`.

## Coordination (2026-10-24 ~20:55)
- **m2-slice OK'd** the FieldController hook and the field_movement.json tuning. FieldEncounters only reads metres
  walked, with a 1.5 m per-frame cap. They also OK'd editing the field_hero_hooks.md hook points (the greybox
  `_build_stage` actors and the hand-placed cast capsules), so the field agent covers stage actors too.
- **The sequencer already eases** (M2-FP-29, claude/m2-slice 716c2db4: CutsceneMotion). Our patch builds on it: the
  hero body gets a `play_clip(name, blend)` entry point, and the sequencer's `_play_clip` and `_cue_anim` call it when
  present. The idle micro-motion layer also goes in. The patch is checked against claude/m2-slice.
- **Renumbered (Lead id rule, CONSOLIDATED §4 "id blocks"):** tasks M2-HRO-01..06 are now M2-HER-1101..1106 and ADR 0038 is ADR 0190,
  so there is no clash with m2-slice's 0038. Handoffs are named `<date>-<role>-hero-<n>.md`.
- **Messaging the Lead:** my send_message to the Lead was refused (trusted device); the Lead's messages reach me. This
  log is the channel.

## Exact next step
The Lead gates and merges this branch. Then m2-slice applies the sequencer patch, and UI repoints the battle
stand_ins at the wrappers. Meanwhile, take M2-CHR-12's clips into the field gait
when characters reports them.

## Un-pushed state
None. The battle trial merge (`hro03-trial`) is local scratch by design.
