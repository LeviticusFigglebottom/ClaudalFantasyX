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
- **audio's FootstepAudio** (M3-AUD-802/810, claude/audio) listens to `HeroFieldActor.foot_contact(foot, run)`
  (696fa2f9). It also reads the `HeroBody` name, `hero_id`, and the tree layout (`loco` 0/1/2, `act_a`/`act_b`,
  `ts_a`/`ts_b`, `mode`).
- **m2-slice's sequencer patch** uses `HeroMotion.play` and `set_locomotion_speed`, and HeroFieldActor's `play_clip`.

- **M2-HER-1107: the field gait on characters' M2-CHR-12 clips → review (character).** Commits 17081887 and
  c04639bf.
  - **HeroGaitClips** (pure): walk/run starts and stops played by distance (feet planted at any acceleration),
    turns in place driven by `root_yaw_deg` (still capped at 400°/s), and an idle_shift after 8 s plus a per-hero
    share of 5 s. Gait speeds come from `game/data/characters/locomotion.json` when it exists. Everything is
    duck-typed: without characters' clips the body behaves as before.
  - **ADR 0191:** the field walk goes 1.5 → 1.0 m/s and the run 4.6 → 3.6 m/s, so the new cycles plant. Run foot
    slide drops from 23–34% to under 8%. m2-slice will set the sequencer walk_mps to 1.0 with the patch.
  - **On a trial merge with claude/characters (viewed):** a real heel-to-toe walk, clean party strides, a run start
    that leans and pushes, a stop that decelerates to feet together, and a stepped turn. Flaw, sent to characters:
    Rhen's forward arm reaches out at shoulder height in the run.
  - **Tests:** hero 68/0, field 112/0, zone 42/0, fp_ 24/0, haluna 46/0, cutscene 41/0 on this branch. On the
    trial: hero 71/0, field 112/0.
  - **Shots field_hero_rhen_walk, field_hero_party and the new field_hero_gait_strip** are approved on this branch
    with the OLD clips (viewed). **Lead: re-approve all three after viewing once claude/characters merges** (the new
    clips change them).
- **M3-AUD-810 (for audio): `HeroFieldActor.foot_contact(foot, run)`** from the clips' footfall markers (696fa2f9).
  hero_foot 5/0.

## In progress
- **(done above) M2-HER-1107: the field gait on characters' M2-CHR-12 clips.** They're on claude/characters
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

## STATE AT HANDOVER (2026-10-25)
Read this section first; everything above is history. The branch is `claude/hero-integration`. It was cut from the
integration branch at 07781cba and merged with it again at 0b1e76a4. The handover sha is in the last line.

### Done and MERGE-READY (all on this branch, pushed)
| Task | State | What | Key commits |
|---|---|---|---|
| M2-HER-1101 | review (character) | Real Rhen on the field player via one hook line in `FieldController._ready` (`HeroFieldActor.attach(self)`): AnimationTree gait, eased 400°/s turns, idle micro-motion, lantern light carried on his lantern; stage-actor capsules for hero ids get real bodies at runtime (every slice zone, no zone scene edits) | 9e9a3f70, fa411948, e758a9a5 |
| M2-HER-1102 | review (character) | Asha and Toma followers on Rhen's breadcrumb trail (`HeroFieldParty`) | 7084976e |
| M2-HER-1104 | review (cinematics) | `HeroMotion` (play / set_locomotion_speed / add_micro_motion), `HeroIdleMicro` (breathing, weight shift, head leads turns), sequencer patch `docs/kb/tech/hero_motion_sequencer.patch` for m2-slice | 408a5bc1, da6dd917 |
| M2-HER-1107 | review (character) | Gait clips from characters' M2-CHR-12: starts and stops by distance, turns in place on `root_yaw_deg`, idle_shift; duck-typed (no-ops without the clips); ADR 0191 field speeds walk 1.0 / run 3.6 m/s | 17081887, c04639bf, ADR 0191 |
| M3-AUD-810 (audio's request) | done here | `HeroFieldActor.foot_contact(foot, run)` from footfall markers | 696fa2f9 |
| ADR 0190 | proposed | the hero motion layer | 34f0ce2e (renumbered in 0c86e694) |

- **Last full Godot suite:** 1996/0 on 555714d3.
- **Scoped since then on 6c8a0ec2:** hero 68/0 (+5 hero_foot), field 112/0, zone 42/0, fp_ 24/0, haluna 46/0, cutscene 41/0.
- **Shots:** field_hero_rhen_walk, field_hero_party, field_hero_gait_strip, hero_cutscene_turn_strip,
  field_lane_fixed, field_court_pan and field_causeway_dolly are approved after viewing. The shrine_s01..05 shots
  are unchanged.
- **Known pre-existing flake:** `test_shrine_audio::test_the_zone_plays_the_shrine_cue` fails in a filtered run on
  the pristine integration branch too; it passes in the full suite.

### In progress or waiting (nothing is half-written in code)
- **M2-HER-1103 battle heroes (doing).**
  - Built and on this branch: the `HeroBattleActor` wrapper scenes `game/hero_motion/battle/<hero>_battle_actor.tscn`
    (per-pair clip cross-fades, offset idle phase, micro-motion; 6d5fcf4a).
  - They take effect only when UI repoints `game/data/ui/battle_sandbox.json` stand_ins `scene` at them. UI agreed
    to do it after this branch reaches the integration branch.
  - UI's KO no-sink fix is on claude/ui 781f9da6.
  - Patches still waiting for their owners:
    - battle-presentation tests: `docs/kb/tech/hero_battle_proposed.patch`;
    - the battle shot rig (stage, scenes and rows for battle_heroes_*): `docs/kb/tech/hero_battle_shots.patch`. It
      was taken from a local trial merge that is not pushed; apply it after ui, characters and battle-presentation
      merge, then capture, view and approve.
- **M2-HER-1105 clip gaps (doing, owned by characters).**
  - Locomotion clips landed as M2-CHR-12 on claude/characters eee3099a+ (MERGE-READY, not yet on the integration
    branch).
  - Battle fixes are pending as M2-CHR-513: a livelier victory, a lying-down KO, Rhen's hooks in hand, and a ~0.8 s
    revive.
  - Also requested: Rhen's forward arm reaches out at shoulder height in the run; lower its peak.
- **M2-HER-1106 shots and tests (doing):** only the battle shots remain (see 1103).

### EXACT next steps for the new owner
1. **Lead:** gate and merge `claude/hero-integration`. Then merge claude/characters (M2-CHR-12), claude/ui and
   claude/battle-presentation, then **re-approve after viewing** field_hero_rhen_walk, field_hero_party and
   field_hero_gait_strip, which change with the new clips.
2. **m2-slice** then applies `docs/kb/tech/hero_motion_sequencer.patch` (against claude/m2-slice 94feee33+).
   Agreed in the same change: sequencer.json walk_mps 1.3 → 1.0, and `_cue_mark` calls
   `HeroMotion.set_locomotion_speed(actor, run_mps)` at the start of a run move.
3. **UI** repoints the battle stand_ins at `game/hero_motion/battle/*_battle_actor.tscn` and re-approves the battle
   shots. battle-presentation takes the 4 test-only diffs in `hero_battle_proposed.patch` (its tests assume capsule
   heroes once UI-07's data lands).
4. **Hero track:**
   - apply `hero_battle_shots.patch`, capture battle_heroes_{idle,attack,hit,ko,victory,cast,finisher}, view and
     approve;
   - when M2-CHR-513 lands, re-check KO, victory and revive;
   - consider staggering the victory clips (a BattleOutro suggestion to battle-presentation).
5. **Field polish backlog:**
   - after a teleport next to a wall, a follower can briefly stand inside it;
   - a cutscene `@move` can't tell its target speed, so it only gets a run start if the sequencer sets it (step 2).

### Gotchas
- **API consumers; keep these signatures, or tell the owners first:**
  - creatures' FieldNpc (M3-CRE-610): HeroLocomotion new/configure/reset_yaw/step_yaw/step_speed/weights;
    HeroMotion.play/add_micro_motion/set_locomotion_speed; HeroIdleMicro.
  - audio: `foot_contact`, `HeroBody`, `hero_id`, and the tree node names loco / act_a / act_b / ts_a / ts_b / mode.
  - m2-slice's patch: HeroMotion and `play_clip`.
- **Ownership:** game/cutscene/** is m2-slice's; battle_sandbox.json and fighter_stand_in.gd are UI's; clips are
  characters'. This track only edited the one FieldController hook line and the field_movement.json speed rows,
  with m2-slice's OK.
- The visible body is `top_level` and follows its source node. Gameplay (collision, interaction, encounters)
  still uses the FieldController.
- Never merge claude/characters into this branch just to test: it's ~340 files. Use a local trial merge (that is
  what `her1107-trial` and `hro03-trial` were; they're local scratch and were not pushed).
- send_message to the Lead's session was refused ("trusted device"); this live log was the channel.

HANDOVER DONE @ f6d90968 (this note is the commit after it).

## NEW ACCOUNT (from 2026-10-25)
Session `session_01PzF7Jc4XVQdTWcaYUyCjPB`. Per the Lead: no send_message; requests go through task files and this log.
- 4da79410: merged the integration branch (-ze8rrn @ c6a960ab). Conflicts: shots.json, baselines.json (union by id),
  ownership.md (both rows kept). No duplicate loc keys.
- **Patch status (for the Lead to relay):**
  - `hero_motion_sequencer.patch` still applies cleanly to claude/m2-slice 6c50823f → request task **M2-HER-1109**
    (slice-polish).
  - `hero_battle_proposed.patch`: the choreo test hunks and the KO no-sink are ALREADY on claude/battle-presentation
    (a3e489bb) and the no-sink on claude/ui (776a24a1). Nothing left for battle-presentation. Only the three-line
    `battle_sandbox.json` repoint remains → request task **M2-HER-1108** (ui-menus), after big9 lands.
- **MERGE-READY @ f79449c5** (FAST-TRACK: the human's #1 complaint, snapping motion): M2-HER-1110 HeroMotionGuard and
  its tests (battle pops on the real heroes: 26 clip changes x 3, none pop or cut; field snaps over 13 slice and Act I
  zones), **fix: followers no longer drop 2 m through the Brightwater Ferry's pier edge** (HeroFieldParty takes a floor
  only within step_m of Rhen's trail height and eases the feet: stairs and slopes no longer pop); M2-HER-1103 revive
  blend rows for characters' coming revive clip. Merged big9 (5c5b9292) in. Checks run: gdlint and gdformat on
  game/hero_motion and the new tests, validate_data, taskboard --check, Godot filters hero_ 90/0, field 123/0, zone
  50/0, haluna 49/0, battle_choreo 28/0, fighter 5/0, clips 7/0. Skipped: shots (no scene or shader touched; the
  followers' feet only change where a floor sits more than 0.45 m off Rhen's path), Blender (none touched), coverage
  (no game/battle or game/progression change).
- For the Lead to relay: request tasks M2-HER-1108 (ui-menus: repoint the battle stand_ins, now that big9 has
  landed), M2-HER-1109 (slice-polish: the sequencer patch), M2-HER-1111 (QA & Tools: run_tests.gd counts a parse
  error as 0 failed). The choreo hunks for battle-presentation are already on its branch: nothing to relay there.
- Note for m2-slice / slice-polish (FieldController owner): Rhen peaks at 5.85 m/s on Pemakar and 5.49 on Ashcrown
  (run 3.6): step or slope push-ups. Under the 6 m/s snap limit, but worth a look in play.
- **MERGE-READY @ 1518a17f** (FAST-TRACK, snapping motion): M2-HER-1110 guards for villagers and cutscenes.
  - `tests/unit/test_villager_snaps.gd` is duck-typed on creatures' VillagerLayer (it skips until creatures lands).
    On a local trial merge with claude/creatures, all 7 Haluna villagers pass: no snaps, eased turns, and 42 clip
    changes under half the pop limit.
  - `tests/integration/test_hero_cutscene_snaps.gd`: 26 slice and Act I scenes. The heroes are clean. 11 non-hero
    actor/scene pairs snap: whip turns, and a walk jumped at a scene's end. They're listed as KNOWN until request
    **M2-HER-1113** (slice-polish) applies `docs/kb/tech/cutscene_no_snap.patch`, which I verified on claude/m2-slice
    7d981830: guard clean, cutscene 61/0, fp_ 28/0, haluna 55/0, prologue 7/0, _thread 34/0.
  - Request **M2-HER-1112** (slice-polish): put creatures' VillagerLayer in haluna.tscn after creatures merges. No zone
    places it yet, so Haluna would keep its stand-ins.
  - Checks run: gdlint and gdformat, validate_data, taskboard --check, Godot hero_ filters, villager_snaps,
    hero_cutscene_snaps. Skipped: shots (no scene or shader touched up to here), Blender, coverage.
- **NOT merge-ready yet @ b2453cfd:** the battle_heroes_* shot rig (M2-HER-1106, from hero_battle_shots.patch). The
  tools test `test_repo_manifest_is_valid_and_baselined` is red until its 7 baselines are approved after the PC
  render below. Merge only 1518a17f until then.
- M2-HER-1109 is done: slice-polish has the HeroMotion sequencer patch on claude/m2-slice.
- For the Lead to relay: M2-HER-1108 (ui-menus: repoint the battle stand_ins; big9 has landed, so it's unblocked),
  M2-HER-1111 (QA & Tools: the runner hides parse errors), M2-HER-1112 and M2-HER-1113 (slice-polish).

### Render requests
RENDER-REQUEST @ b2453cfd: battle_heroes_idle, battle_heroes_attack, battle_heroes_hit, battle_heroes_ko, battle_heroes_victory, battle_heroes_cast, battle_heroes_finisher, field_hero_party, field_hero_rhen_walk, field_hero_gait_strip; why: new battle hero shots (M2-HER-1106), and the field hero shots after characters' gait clips and the followers' floor change (M2-HER-1110)
- **MERGE-READY @ 1b84b89c** (FAST-TRACK, the human's #1 complaint). Merged big10 (7f187123) in.
  - M2-HER-1116: foot IK on every field and cutscene hero body (`HeroFootIK`; flat ground untouched, a continuous
    1 cm dead zone); followers turn to face whoever Rhen talks to; Ysolde gets a field and cutscene body (her stage
    actors no longer whip-turn).
  - M2-HER-1103: Ysolde's battle wrapper. **Fix:** placeholder clips on a hero who lacks some (Ysolde) were untuned,
    so her KO stood up in one frame. The wrapper now installs them on a stopped player, then tunes them.
  - M2-HER-1110: the cutscene guard now covers the prologue and every cue-named actor (27 scenes) and prints what each
    sampled. On claude/m2-slice + the M2-HER-1113 patch, the real prologue cast and every KNOWN pair are clean.
  - ADR 0192 (no snapping is a test).
  - Checks run after big10: gdlint and gdformat on game/hero_motion and my tests, validate_data, taskboard --check,
    tools test_screenshots, Godot filters hero_ 97/0, villager 2/0 (the layer half skips: M3-CRE-613 isn't merged
    yet), npc 10/0, battle 703/0, field 147/0, zone 51/0, haluna 50/0, cutscene 52/0, _thread 34/0, fp_ 27/0.
  - Skipped: Blender (none touched), coverage (no game/battle or game/progression change), shots (cloud renders are
    off; see the request below).
- **Crash for battle-presentation (M2-HER-1114), please relay:** BattlePlaceholderClips._install swaps the library
  under a playing AnimationPlayer, and Godot segfaults. My wrapper now avoids it. The 2-line fix for every other
  caller is in the task.
- New requests for the Lead to relay:
  - **M2-HER-1114** (battle-presentation): that crash, plus the placeholder finisher's arm flip;
  - **M2-HER-1115** (characters): Ysolde's battle clips;
  - **M3-HER-1117** (creatures): villagers' foot IK, a one-liner;
  - **M2-HER-1108** now covers Ysolde's stand_in too.
  - Still open: 1108, 1111, 1112, 1113.

### Render requests
RENDER-REQUEST @ 1b84b89c: field_hero_rhen_walk, field_hero_party, field_hero_gait_strip, hero_cutscene_turn_strip, field_lane_fixed, field_court_pan, field_causeway_dolly, haluna_h02_tidewall_lane, haluna_h04_dock, haluna_h07_chapel_court, haluna_h10_dock_night; why: foot IK on uneven ground and the followers' floor and facing changes (M2-HER-1116), and characters' M2-CHR-12 gait clips now in via big10 (the earlier battle_heroes_* request @ b2453cfd stands)
- @ bc444574: docs only. M3-AUD-810: confirmed the HeroBody half of audio's footstep request (foot_contact(foot, run) and the tree names); M2-HER-1116: foot IK costs 18 us per body-frame on the cloud CPU (Haluna run, legs bent on 13% of frames).
- **Blockers, all on other tracks.** Each is a request task; the next step is mine once it lands.
  1. **Haluna's villagers are still frozen in the game** (top blocker). big10 brought FieldNpc but not creatures'
     VillagerLayer (M3-CRE-613), and no zone places one (M2-HER-1112, slice-polish). The villager guard's clip half
     now runs on this branch and passes; its routine half runs once the layer is here.
  2. Battle wrappers: UI's stand_ins repoint (M2-HER-1108). Then I re-run the pop guard on the integration branch.
  3. PC renders: battle_heroes_* @ b2453cfd and the field/hero set @ 1b84b89c. I view and approve them.
  4. Owners' fixes:
     - M2-HER-1113 cutscene patch → I empty the cutscene guard's KNOWN list;
     - M2-HER-1114 placeholder crash and arm flip → I empty the battle guard's KNOWN entry;
     - M2-CHR-513 → I re-check KO, victory and revive (the pop test picks them up by itself).
- **Approved after viewing @ d036076d:** battle_heroes_idle, _attack, _hit, _ko, _victory, _cast, _finisher (PC render
  gpu/render-hero-integration-b2453cf); the rows are back in shots.json. What the shots show:
  - real models, grounded and facing the foes; attack contact, hit recoil, cast and finisher all read;
  - victory is nearly idle, and Rhen strikes empty-handed (both waiting on M2-CHR-513);
  - **a felled hero (Toma) dissolves away** in the KO shot: the felled-foe fade applies to the party too. Added to
    M2-HER-1114 for battle-presentation.
- **MERGE-READY @ d4430397 (FAST-TRACK, the Lead's Ysolde item):** Ysolde is her real model in battle, not a tan capsule.
  - Her wrapper (`ysolde_battle_actor.tscn`, placeholder contract clips tuned) is wired in battle_sandbox.json's
    `stand_ins.ysolde`. That's one row of UI's file, changed on the Lead's instruction.
  - Two battle-presentation tests stopped assuming she's a capsule (test-only).
  - The same change is in `docs/kb/tech/ysolde_battle_fasttrack.patch` for the owners (noted in M2-HER-1108).
  - Her field and cutscene body landed earlier (hero_motion.json @ 549afe82).
  - Real battle clips: request M2-HER-1115 (characters).
  - **Shots this changes (not re-approved by me):** battle_choreo_cast, battle_choreo_read, battle_choreo_toll,
    battle_statuses, battle_swell_glyph, battle_read_panel, plus any other battle shot with Ysolde in the party.
  - Checks run: battle 703/0, hero_ 97/0, fighter 5/0, clips 7/0, validate_data, gdlint and gdformat; the six shot
    scenes load headless with 0 errors.
  - Skipped: rendering (the PC's job), Blender, coverage (no game/battle code change).

### Render requests
RENDER-REQUEST @ d4430397: battle_choreo_cast, battle_choreo_read, battle_choreo_toll, battle_statuses, battle_swell_glyph, battle_read_panel; why: Ysolde's real model replaces her capsule (FAST-TRACK); for the Lead to view and approve (the field and hero set @ 1b84b89c still stands)
- **@ e8b43b5d + the M2-HER-1113 re-cut (Act I hero checks, for act1-chapters and slice-polish):**
  - The guards now read their zones and scenes from the game's data: field over **15 zones** (Ch8's Coilspire and
    Corrow included), cutscenes over **79 scenes** (every chapter-file `play` step, the prologue, HalunaStory's
    scenes).
  - **Field: every zone clean.**
  - **Cutscenes:** 30 actor/scene pairs snap on this branch. All of them are fixed by the re-cut
    `cutscene_no_snap.patch` (against claude/m2-slice d4921946), now with a third fix: a stand-in clip mark farther
    than 2.5 m is a cut, not a glide. Ch9's `@anim asha pole_out` glided Asha 30 m across the harbour at 120 m/s;
    ch09_zone.gd says it should cut.
  - Verified on m2-slice + the patch: the guard is clean on all 79; cutscene 61/0, fp_ 28/0, haluna 57/0, prologue
    7/0, _thread 34/0, ch09 7/0.
  - ch0 62/1: test_ch01_oruvel_kit's storm swap fails only inside the ch0 sweep. It passes alone with the patch and
    without it, so it depends on test order and isn't the patch.
  - The 30 pairs are KNOWN in the test until the patch lands.
- **Merge note for the Lead:** claude/ui's 80d358bf and my d4430397 both edit game/data/ui/battle_sandbox.json's
  stand_ins, on adjacent rows. Resolve by keeping both: UI's Rhen, Asha and Toma rows, and my Ysolde row with her
  scene and yaw_deg.
- **MERGE-READY @ bccce923**
  - **M3-ARC-1216, steep stairs (ADR 0193).** HeroStairFlight and HeroStairs: Rhen climbs 48° and descends 60°
    flights on their profile, step by step, eased, at slope_speed_mps 1.0. Standing still doesn't slide; pushing
    sideways keeps him inside the edges; walking under a flying stair doesn't climb it. Asha and Toma follow up the
    steps (test_hero_stairs, 7).
  - **M2-HER-1116 followers:** never inside a wall (slide along it; a clear catch-up side; an eased min-gap push);
    take steep flights; Ysolde follows when she joins (test_hero_followers, 11). Foot IK on/off switch.
  - Checks run: hero_ 107/0, field 147/0, zone 51/0, haluna 50/0, hero_stairs 7/0, hero_followers 11/0, gdlint and
    gdformat, validate_data, taskboard --check.
  - Skipped: shots (no scene or shader touched; followers only differ next to walls), Blender, coverage.
- **For act1-chapters (unblocks M3-C05-1215, the Ashcrown swap): how to place a steep flight.** Full notes are in
  M3-ARC-1216.
  - Mark it with a `HeroStairFlight` node (origin = the centre of the foot on the lower floor; it climbs along the
    node's -Z; run_m, rise_m, width_m), **or** a row in the zone layout's `"stairs"` list:
    `{"id": "FlyingStair", "foot": [x, y, z], "head": [x, y, z], "width_m": 2.0}`. No code change on your side:
    HeroStairs builds the rows when the zone loads.
  - Keep the flight's blocking collision, and give each end a landing floor.
  - Cutscene walks across a flight need M3-HER-1119 (slice-polish), and villagers need M3-HER-1118 (creatures).
- **For slice-polish (relay, please): ONE patch now,** `docs/kb/tech/cutscene_walks_combined.patch`.
  - It replaces both `cutscene_no_snap.patch` (M2-HER-1113) and act1-chapters' `cutscene_mark_via.patch`
    (M3-CIN-1221). Those two overlap in `_cue_mark`, and the via patch no longer applied to claude/m2-slice.
  - Cut against claude/m2-slice d4921946. The sequencer ends at 999 lines.
  - Verified there with my hero layer overlaid: the cutscene guard over all 79 scenes, mark_via 3/0, sequencer 17/0,
    cutscene 64/0, fp_ 28/0, haluna 57/0, prologue 7/0, _thread 34/0, ch09 7/0.
  - Once it lands, act1-chapters can write `via=` (M3-CIN-1220) and I empty my guard's KNOWN list (queue item 6).
- **Merge note:** M3-ARC-1216's task file was on act1-chapters only. My branch adds it with my claim (the Lead
  reassigned it). On an add/add conflict, keep mine.

### Perf requests
PERF-REQUEST @ bccce923: foot IK frame cost on hardware. Haluna, the party running the beach-to-court loop, 60 s each with game/data/hero_motion/foot_ik.json "enabled": true and then false; report the mean and p99 frame times and the delta. Cloud CPU estimate: 18 us per hero per frame.
- **Queue item 2 (M3-CIN-1220 support), prepared:**
  - The cutscene guard now measures every walking actor's floor gap with `HeroMotionGuard.floor_gap`: a ray under
    the feet, the cast's own colliders ignored, a tolerance of 0.15 m. It prints `OFF-FLOOR <scene> <actor>: <worst
    gap>` and doesn't fail yet.
  - Today: 17 actor/scene pairs, in ch04_long_way_round, ch06_liss_lantern, ch07_leaving_tamsule,
    ch07_after_the_bell, ch07_empty_moorings and ch09_the_ebbing. The 0.60 m gaps are walks passing under or through
    something at about waist height.
  - Once the combined patch is on the integration branch and act1-chapters has written its via= paths, I turn this
    into a failure, with a KNOWN list for whatever is left.
- **MERGE-READY @ 97fbd608: big11 merged in (0a10af32).**
  - battle_sandbox.json resolved: UI's three repointed rows plus Ysolde's wrapper row.
  - **Pop guard on the merged tree (UI's repoint in):** hero_battle 8/0, battle 710/0, fighter 5/0, clips 7/0. The
    only report is Ysolde's placeholder finisher (KNOWN, M2-HER-1114). M2-HER-1108 is done.
  - **Villager guard now runs for real** (creatures' VillagerLayer came with big11): all 7 Haluna villagers clean
    through their routines and visits. Haluna itself still doesn't place the layer: M2-HER-1112, slice-polish's top
    item.
  - New from big11: ch08_keeping_flame's Asha jumps 0.34 m on the scene's last frame. That's the end-of-scene
    completion the combined patch fixes, so it's KNOWN under M2-HER-1113 (31 pairs).
  - Checks run: hero_ 107/0 (with that entry), field 147/0, zone 60/0, haluna 56/0, villager 19/0, tools
    test_screenshots, gdlint.
- **MERGE-READY @ 7a8bff79**
  - **Ysolde FAST-TRACK, done.** Her battle actor has been wired since d4430397. Now her placeholder clips no longer
    flip an arm: HeroBattleActor gives them short-path keys and caps fades into fast placeholders at 0.06 s. The pop
    guard's KNOWN list is empty: hero_battle 8/0, battle 710/0.
  - **Liss on the hero layer:** her field body row (walk 0.97 and run 2.19 m/s, measured on her model) and her
    battle wrapper (the model by path; her stand-in's capsule until characters' model merges). Checked on a scratch
    worktree with her assets: all 26 battle changes clean, her revive included; hero_field_actor 13/0. Her
    battle_sandbox row: request **M3-HER-1120** (ui-menus).
  - Kerrid has no model anywhere yet; Sefir isn't a party member.
  - **Fold-into-characters handoff:**
    `docs/kb/handoffs/2026-10-27-tech-hero-integration-fold-into-characters.md`.
  - Items 3 (stairs) and 4 (face the speaker, narrow lanes) were done earlier (5091eb81, 0b15b4f6).
  - Checks run: hero_ 107/0, battle 710/0, fighter 5/0, clips 7/0, gdlint, validate_data, taskboard.

### Render requests
RENDER-REQUEST @ 7a8bff79: battle_choreo_cast, battle_choreo_read, battle_choreo_toll, battle_statuses, battle_swell_glyph, battle_read_panel, battle_heroes_idle; why: Ysolde's real model replaces her capsule (FAST-TRACK, same as the request @ d4430397 if it's still unanswered), and her placeholder clips' new fades; for the Lead to view and approve

## INTEGRATION-QA (from 2026-10-27 20:20; the same track and branch, repurposed by the Lead)
The aim: the human's next playtest finds nothing broken between tracks. Task M3-HER-1121 (status doing).

### The guards (all on this branch; run `--filter=qa_` plus `python3 -m unittest tools.tests.test_qa_flag_reach`)
| Guard | What fails it |
|---|---|
| `tests/integration/test_qa_threads.gd` | Every story-thread test (the slice's first-playable thread, Ch1 and Ch4–Ch9) is re-driven under a QaLogger. It fails on an engine error, a script error, an unexplained warning (a freed object, a missing clip or cue) or the thread's own failure. Known kinds: qa_known.json "known" (missing audio M3-HER-1122, placeholder cue features M3-HER-1123). |
| `tests/integration/test_qa_capsules.gd` | A visible StandIn capsule in a real zone (the prologue and every chapter location, each layout variant too: Ch9's dawn road); a party member with no battle actor; an encounter enemy, spawn, summon or Vowbound with no actor scene. Known: qa_known.json "capsules" (zone actors M3-HER-1125; battle_foes with owners). |
| `tools/tests/test_qa_flag_reach.py` | A softlock: a beat's `when`, a prompt's `requires_flag` or an objective's `requires` waits on a flag that nothing sets. |
| `tests/integration/test_qa_save_shrines.gd` | At every SaveShrine (Haluna) and every Act I rest beat (8: Ch1 bell rests, Ch4 ferry, Ch6 and Ch8 shrines with checkpoints): the flag, the respawn spawn exists and lies in this zone, and a save and load round trip keeps every GameStateData field. A zone step that names a method the zone lacks fails (ZoneStory skips it silently). |

### Runs, 2026-10-27
- **Integration big12** (e930595c, merged here at 0d19142a): qa_ 5/0 (now 6/0 with the foe check), flag reach 3/0.
- **Big12 plus each track head** (trial merges, nothing pushed): act1-chapters, audio, battle-presentation, characters,
  creatures, env-art and ui are clean (qa_ 5/0 and the new capsule guard 3/0). **m2-slice @ 2103aeca fails the
  first-playable thread:** its First Verse instances `kits/haluna/shrine_offering.glb`, which env-art renamed to
  `wayside_offering.glb` (39f66d4c, on the integration branch). Filed **M2-HER-1127** (slice-polish).
- **Capsules the Lead listed, now KNOWN with owners:**
  - Ilun, Kahre and Virel (the Vowbound): **M3-HER-1126** (creatures, filed);
  - Inquisitor Moll: M3-CRE-625 (characters);
  - the Ch9 road capsule: Kerrid at the milestone in corrow_night's dawn variant (M3-CHR-505; act1-chapters stages
    it), plus Pemakar's boat_fisher (variant). Any new capsule now fails.
- **Ysolde in battle:** big12 merged this branch at 91b92dda, before her FAST-TRACK row (d4430397). The integration
  branch still draws her as a capsule, and its baselines are capsule renders. The PC render
  gpu/render-hero-integration-d443039 shows her real model, and I viewed all six shots: no breakage. In Toll, at
  13 HP, she leans back hard in the placeholder weak pose (M2-HER-1115, characters). **Not approved,** because that
  render predates big12, and copying it would undo big12's approved changes in the same shots (the gripped spear,
  stances). I've asked for a re-render at this head below and will approve that one.

MERGE-READY @ 1c9bf8bd: big12 merged in; M3-HER-1121's save round-trip guard (shrines and Act I rest beats); the capsule guard
covers foes, summons, the Vowbound and layout variants; requests M3-HER-1126 and M2-HER-1127. Checks run: qa_ 6/0,
test_qa_flag_reach 3/0, gdlint, gdformat, validate_data, taskboard --check, and the guards on big12 plus all 8 track heads.
Checks skipped: screenshots (PC-only) and the hero_ suite (no hero-layer code changed since 7a8bff79's 107/0).

### Render requests
RENDER-REQUEST @ 1c9bf8bd: battle_choreo_cast, battle_choreo_read, battle_choreo_toll, battle_statuses, battle_swell_glyph, battle_read_panel, battle_heroes_idle; why: Ysolde's real battle model replaces her capsule (FAST-TRACK), now on big12's tree (d443039's render predates big12); for this track to view and approve

### Exact next step
- Approve the RENDER-REQUEST above when it lands, after viewing it.
- Re-run `--filter=qa_` on each new integration batch and track head; file failures as request tasks.
- Kerrid: when claude/characters exports kerrid_lod1.glb (M3-CHR-505), do the fold-into-characters handoff's §2 steps
  1–4.
- M3-ARC-1216 is in review; its last box is act1-chapters'.

### Render review, 2026-10-27 ~21:50
- **`lead/gate-render-hero-integration-7a8bff7` viewed (7 drift), NOT approved.** Ysolde's model is right in all
  of them, with no breakage. But 7a8bff79 predates big12, and against this branch's baselines (big12's approved ones)
  the drift also covers big12's own changes: the reef crab's and harrier's new models and poses, Toma and the
  tutorial text in battle_heroes_idle (which has no Ysolde in it). Copying these would revert big12's approvals.
- **Still needed:** the RENDER-REQUEST above, at a sha with big12 in (4d351143 or later on claude/hero-integration).
  Same 7 ids. Only Ysolde should drift.
- **`lead/gate-render-hero-integration-1c9bf8b` viewed and APPROVED (7 shots).** It was rendered on big12's tree, so
  against big12's baselines:
  - **The six Ysolde shots** (battle_statuses, battle_read_panel, battle_choreo_cast, battle_choreo_read,
    battle_choreo_toll, battle_swell_glyph) differ only where she stands: her real model replaces the capsule. In Toll
    she leans back hard at 13 HP (the placeholder weak pose; M2-HER-1115, characters).
  - **battle_heroes_idle:** big12's first-battle tutorial prompt now shows, and Toma and Asha are at another phase of
    their idle. Nothing is broken.
  - 7a8bff7's render is superseded (not approved; it predates big12).

## INTEGRATION-QA STATUS, 2026-10-28 00:15 (answers the Lead's backlog list, item by item)
1. **Field-snap clash: DONE.**
   - **Asha in the Ch7 galleries:** my bug. HeroFieldParty's min-gap push rode on top of the capped step (6.9 m/s).
     The whole step is now held to max_speed_mps (7b47e387).
   - **Rhen at Coilspire:** act1-chapters' geometry. He walks off a 2 m drop beside the PathFoot spawn and lands
     with a 0.31 m pop. Filed **M3-HER-1129** (act1-chapters) and KNOWN in the guard.
   - **Four new cutscene turn snaps** (ch08_spire_door liss/tender, ch08_stuck_key liss, ch09_the_ebbing
     kerrid_stair): verified clean with cutscene_walks_combined.patch applied, so they're KNOWN under M2-HER-1113.
   - hero_ is 109/0.
2. **Slice-thread playthrough guard: DONE** (test_qa_threads re-drives test_fp_thread: New Game → prologue → Haluna
   → B06 causeway → Shell Shrine → Drownbell → end card, battles forced won).
   - It fails on errors, unexplained warnings, missing cues and suspended awaits, and (new) on any flag the
     chapter or a main objective waits on that the thread never raises.
   - One flag is unraised: ch02_ate_at_nemes. The thread skips B02; the game plays it. Filed **M2-HER-1128**
     (slice-polish).
3. **Act I thread guards: DONE.** The same guard over test_ch01, ch04–ch09 threads. All of their chapter and
   objective flags are raised.
4. **Save/load at every shrine: DONE** (test_qa_save_shrines: Haluna's SaveShrine and Act I's 8 rest beats).
5. **Kerrid's actors: BLOCKED.** claude/characters @ 24dca3d1 has no assets/characters/kerrid yet (only the
   M3-CHR-505 WIP patch). I'll start the moment kerrid_lod1.glb is pushed (fold-into-characters handoff §2).

**Also done (self-directed backlog):**
- **M2-HER-1111 and M2-QA-100 are in review.** The runner fails a parse-error file and a test suspended on an
  await. Across the full suite this adds one failure: test_slice_shots, already fixed on m2-slice.
- **My test_hero_stairs leaked a zone.** That leak caused the ~30 cascading failures (the same fix as the Lead's
  9f98ccf6, in eaefe445). Attribution: the integration head gives 2820/2, and every extra failure on this branch
  was that cascade. The runner now also fails and frees any node a test leaves in the tree. A full run is
  measuring how many other tests leave nodes; if it's many, the check will report rather than fail, and I'll
  file the list.
- M2-HER-1106 and M1-QA-07 are in review.

MERGE-READY @ eaefe445 (superseded below: take the next one, which reports leaks instead of failing them): everything above. Checks run: hero_ 109/0, qa_ 6/0, hero_followers 12/0, gdlint and
gdformat, taskboard --check, validate_data, a full suite on this branch and on the integration head (the
attribution above). Skipped: screenshots (no rendered change since the approved 1c9bf8b render).

MERGE-READY @ 44295d79: as above, and the runner's leak check reports (LEAK lines) and frees, without failing (M3-HER-1130), so no other track goes red. Checks: the leak probe (a leak is freed and reported; the summary still parses for ci_local.sh and run_coverage.py), gdlint.

### M3-HER-100 (slice-polish: vigil field bodies), 2026-10-28 ~00:45
- **Liss: DONE on this branch** (`field.heroes.liss` since 1f190eb8). On a scratch merge of this branch, claude/characters
  @ 24dca3d1 and claude/m2-slice, `dress_vigils()` gives Liss her body and her capsule goes. Checks: prologue 7/0
  without m2-slice, hero_field_actor 13/0.
- **The seam that merge shows:** slice-polish's `test_a_vigil_takes_its_body_when_its_hero_has_one` asserts Liss's
  capsule stays. Filed **M3-HER-1131** (one line: erase liss and pell from the test's private data).
- **Kerrid, Pell: BLOCKED.** No models yet (M3-CHR-505, M3-CHR-506). Each is one row the day they land.

### Full suite after the stairs fix, 2026-10-28 ~01:10
- **2837 run.** The ~30-failure cascade is gone. What's left is the integration's two known failures (creature
  portraits: creatures; causeway footsteps: audio) and **test_slice_shots**, which the new runner fails as
  suspended (fixed on m2-slice, M2-QA-100).
- **Leaks (M3-HER-1130):** 76 tests left nodes in the tree. The runner now frees and reports them (LEAK lines), so
  none can cascade. The hero layer's 12 are fixed. The other 64 are listed in the task by owner: creatures 18, ui-menus 34,
  act1-chapters 8 (the act card, hold prompt and names), battle-presentation 4. When the list is empty, one line
  makes the runner fail a leak.

MERGE-READY @ c9cb7dc9: the stairs leak, the runner's leak report, the hero tests' cleanup, M3-HER-1131 (the Liss vigil
seam). Checks: full suite (above), hero_foot_ik 5/0, hero_battle_actor 5/0, hero_battle_pops 3/0, gdlint, taskboard.

BACKLOG EMPTY (2026-10-28 ~01:15): what's left waits on other tracks.
- Kerrid's and Pell's field and battle bodies: no models on claude/characters yet (M3-CHR-505, M3-CHR-506).
- Taking KNOWN entries out as their owners land fixes: M2-HER-1113 (the cutscene patch), M2-HER-1127, M2-HER-1128,
  M3-HER-1126, M3-HER-1129, M3-HER-1131.
- Switching the leak report to a failure once M3-HER-1130's list is empty.
- M3-ARC-1216: act1-chapters places the stair flights.
On every new integration batch or track head, I re-run qa_ and hero_ and file what fails.

### The Lead's 01:00 list, 2026-10-28 ~02:00
1. **SELF-RENDERED @ b04a188a** (a scratch merge: this branch e7d6e7a6+, claude/characters 24dca3d1 and
   claude/m2-slice; nothing committed from it): slice_prologue_p01, slice_prologue_vigil_line, field_hero_party,
   field_hero_rhen_walk.
   - **P01: Liss's vigil is her real body** (M3-HER-100 works): feet on the paving, no clipping. Kerrid's and Pell's
     vigils are still capsules (no models). The capsule behind Ysolde is Kerrid's vigil, 6.5 m behind her (checked
     positions), not clipping.
   - **vigil_line:** Asha and Rhen in frame, clean.
   - **field_hero_party:** the party's spacing is the same as the baseline (the follower push cap changes nothing
     here). The drift is characters' new grips: Toma's spear and Asha's staff now in hand. No sliding or clipping.
   - **field_hero_rhen_walk:** 156 px of drift at the lantern. The capsule beside him is the rig's size reference,
     also in the baseline.
   - No baselines written.
2. **Integration @ cd23f612, full suite: 2820 run, 2 failed.** Both already have owners:
   - **test_creature_portraits:** M3-CRE-634 (creatures → ui-menus, todo, with a verified patch).
   - **test_footsteps_slice_zones:** M3-AUD-812 (audio, review). Audio's head (5a4c8470, which contains the
     integration branch) passes it (5/0), so it's fixed once audio merges.
   - No new tasks were needed.
3. **Act I hero-motion audit: docs/kb/qa/act1_hero_motion_audit.md** (M3-HER-1132, review; re-run with
   --filter=qa_cutscene_motion_audit).
   - 171 of 244 @anim cues do nothing yet. The heroes' clips are requested in M3-CHR-1000 (except Liss's haul_rope
     and Pell's storm_call).
   - Filed: **M3-HER-1133** (characters: Act I's people's clips and those two), **M3-HER-1134** (creatures: the
     Matron's two).
   - Placeholder cue features: added to M3-HER-1123.

MERGE-READY @ 6c4e9d1e: the audit test and doc, and tasks M3-HER-1132–1134. Checks: qa_cutscene_motion_audit 1/0 (0 left
nodes), gdlint, taskboard, validate_data. No game code changed.

## ADR 0041: THE ACT I INVENTORY (integration-qa owns it, from 2026-10-28 ~02:40)
MERGE-READY @ ee41e2bd: **first pass of tools/placeholder_audit.py and docs/kb/qa/act1_final_inventory.md.**
- **159 items** (138 high, 17 medium, 4 low). One task per owner:
  - characters **107**, M3-HER-1144: the zones' capsule people and NPCs, plus Kerrid's and Liss's battle actors;
  - env-art 15, M3-HER-1140: greybox in the prologue city, Oruvel and the Underway, Haluna's dressing, the
    First Verse set, the Wake and the ferry; Haluna's banyan_placeholder and windbreak_placeholder meshes;
  - env-art-b 11, M3-HER-1141: greybox in Pemakar, Ashcrown, Tamsule, the Ch8/Ch9 Corrows and Coilspire; the Ch8
    **wall_head_storm arena is still game/battle/arenas' greybox**;
  - audio 12, M3-HER-1146: Act I music cues that are silent or play a stand-in. **Seam:** music.json has cue rows
    (oruvel_raft and others) that CutsceneSequencer never reads; it plays music_dir/<id>.ogg only;
  - creatures-b 6, M3-HER-1143: Moll, Ilun, Kahre and Virel as primitives, and the Matron and Spar Wraith
    capsules on stage;
  - act1-chapters 3, M3-HER-1145: Ch8's headland and flue fights have no arena (the sandbox's set);
  - ui-menus 3, M3-HER-1147: no menu portraits for Ysolde, Liss or Kerrid;
  - creatures 2, M3-HER-1142.
- Run it: `python3 tools/placeholder_audit.py --write` (Godot on PATH runs the zone scan itself, ~10 min).
  `--check` exits 1 while any item is left (ADR 0041's "done").
- Checks: tools.tests.test_placeholder_audit 7/0, taskboard --check, validate_data, gdlint on the scan script.
- **Next, refining:**
  - icons (items have no icon field yet);
  - NPC and wildlife scenes outside zones;
  - the battle VFX check (battle-presentation);
  - Act I cutscene-only actors (from the motion audit);
  - a recurring re-run on each merge batch.
MERGE-READY @ 7378b38b: **inventory refined.**
- **Boss set-piece VFX:** 5 Act I bosses have none (Hullgnaw, Spar Wraith, Cinder Matron, Moll, the Undertow's
  Reach). Filed M3-HER-1148 (battle-presentation).
- **Clearer rows:** the greybox rows now name what is greybox, e.g. Haluna's **SaveShrine is built from
  primitives**, Neme's bag is a box, and the Ch4/Ch5 arenas' **lamp flames are flat spheres**.
- **Not audited, with the reason:** icons (the Act I menus have none) and per-skill VFX (every hit falls back to
  its element's effect).
- **Now 164 items** (138 high, 22 medium, 4 low). Checks: tools test 8/0, taskboard --check.
- The Lead's item (1), self-render the hero shots: done earlier (SELF-RENDERED @ b04a188a above).
MERGE-READY @ 4a88c28d: **the inventory now lists its coverage.** The scan follows the Act I chapters' `scene` steps
(Ch7's Tidecup match: clean) and names the 28 scenes it loaded (17 zones, 11 arenas) at the top of the
inventory. Still 164 items. Checks: tools test 8/0, gdlint.
- **Next for the inventory:** re-run on each merge batch (`python3 tools/placeholder_audit.py --write`); move each
  owner's fixed rows out as they land. `--check` is the ADR 0041 "done" gate.

### The party's share of the inventory (M3-HER-1149, the Lead's split, 2026-10-28 ~03:30)
MERGE-READY @ 8fdf266d:
- **Stage actors that play a hero under another name now take the hero's body.** This uses hero_motion.json's
  actor_aliases (ysolde_edge, kerrid_stair) and actor_prefixes (vigil_).
  - Real bodies now: Ysolde at the Wake's edge; Ch9's vigil_asha, vigil_rhen, vigil_toma and vigil_ysolde.
  - Still waiting on models: Kerrid's, Liss's and Pell's (Liss's model is on claude/characters).
  - The vigils are staged kneeling, so the bodies stand until the scene plays a kneel (noted in the task).
- **Liss's battle row** (battle_sandbox.json → liss_battle_actor.tscn; M3-HER-1120 is in review, ui-menus has
  nothing to do).
- **The inventory's people rows are re-split:**
  - integration-qa 17: Kerrid, Liss and Pell everywhere, all waiting on models;
  - characters 33: named story NPCs, plus Liss's battle model;
  - creatures 54: background folk.
  - Total 159 items (133 high).
- **SELF-RENDERED @ 8fdf266d:**
  - ch09_corrow_road and ch09_corrow_strand: pixel-identical to their baselines. No manifest shot frames the
    vigils.
  - A probe view of the vigil set (temporary, not committed), viewed: Asha, Rhen, Toma and Ysolde are bodies, feet
    on the floor, no clipping. Liss and Kerrid are still capsules.
- **Checks:** hero_ 110/0, qa_capsules 3/0, tools test 9/0, validate_data, taskboard.
- **Next:** Liss in the field and battle the moment characters' liss_lod1.glb merges (nothing to change). Kerrid
  and Pell once M3-CHR-505 and 506 land.
MERGE-READY @ 9deaedce: **Kerrid on the hero layer** (M3-HER-1149):
- **Field row:** walk 0.71 and run 1.80 m/s, measured on kerrid_lod1.
- **Battle:** a wrapper on characters' kerrid_battle.tscn by path, his idle phase and his battle_sandbox row.
- Until claude/characters merges, he has no field body and his wrapper draws its own capsule. After it merges,
  he's real with no further change.
- **Checks:** hero_ 110/0 on this branch; on a scratch merge with claude/characters 24dca3d1, hero_ green (the pop
  guard over his real battle clips too) and hero_field 29/0.
- **SELF-RENDERED @ 9deaedce** (the scratch merge): ch09_corrow_road shows **Kerrid at the milestone as his real
  body** (the capsule in the baseline is gone), feet on the road, no clipping.
- **Left for the party:** Pell (no model yet: M3-CHR-506) and Liss's and Kerrid's models reaching the
  integration branch.
