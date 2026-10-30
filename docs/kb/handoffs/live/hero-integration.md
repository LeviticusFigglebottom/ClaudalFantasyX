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

## TRIAL MERGE
Run with `python3 tools/dev/trial_merge.py --keep` (tools/dev/trial_merge.py: a throwaway worktree, never pushed). Each conflict names the files and the merged tracks holding a different version of each (tracks that merged each other share a "+"). The trial resolves the append-only files by union and keeps the merged side for the rest, so later tracks still go in.

### 2026-10-28 ~04:30
TRIAL MERGE @ integration 8d03e6d1: env-art ba895bee, env-art-b 8240c0e0, creatures 1514bd69, creatures-b 134251ef, characters fc74c29c, ui 8964614e, battle-presentation c832a740, act1-chapters 0737523e, m2-slice c536ade7, audio 29d5982b, hero-integration bf5749ea
- **env-art-b** (8240c0e0): 3 conflicted file(s); 2 resolved by union (append-only files):
  - `docs/kb/ownership.md`: env-art-b vs env-art (the trial keeps the merged side)
- **creatures** (1514bd69): 4 conflicted file(s); 3 resolved by union (append-only files):
  - `docs/kb/ownership.md`: creatures vs env-art vs env-art-b (the trial keeps the merged side)
- **creatures-b** (134251ef): 2 conflicted file(s); 0 resolved by union (append-only files):
  - `docs/kb/ownership.md`: creatures-b vs env-art vs env-art-b vs creatures (the trial keeps the merged side)
  - `game/data/creatures/creatures.json`: creatures-b vs creatures (the trial keeps the merged side)
- **characters** (fc74c29c): 4 conflicted file(s); 3 resolved by union (append-only files):
  - `tools/dev/blender_builds.json`: characters vs creatures+creatures-b (the trial keeps the merged side)
- **ui** (8964614e): 15 conflicted file(s); 4 resolved by union (append-only files):
  - `assets/ui/portraits/creatures/flue_moth.png`: ui vs creatures (the trial keeps the merged side)
  - `assets/ui/portraits/creatures/mangrove_drowner.png`: ui vs creatures+creatures-b (the trial keeps the merged side)
  - `assets/ui/portraits/creatures/mangrove_drowner.png.import`: ui vs creatures+creatures-b (the trial keeps the merged side)
  - `assets/ui/portraits/creatures/oil_slug.png`: ui vs creatures (the trial keeps the merged side)
  - `assets_src/characters/requested_clips.json`: ui vs characters (the trial keeps the merged side)
  - `docs/kb/ownership.md`: ui vs env-art vs env-art-b vs creatures vs creatures-b (the trial keeps the merged side)
  - `docs/kb/tasks/M3/M3-CRE-634-portrait-test-enemies-only.md`: ui vs creatures+creatures-b (the trial keeps the merged side)
  - `docs/kb/tasks/M3/M3-ENV-1214-pemakar-story-pieces.md`: ui vs env-art+env-art-b (the trial keeps the merged side)
  - `game/data/battle/arenas.json`: ui vs env-art vs env-art-b (the trial keeps the merged side)
  - `game/data/ui/battle_sandbox.json`: ui vs env-art-b (the trial keeps the merged side)
  - `tools/dev/blender_builds.json`: ui vs creatures+creatures-b vs characters (the trial keeps the merged side)
- **battle-presentation** (c832a740): 6 conflicted file(s); 3 resolved by union (append-only files):
  - `docs/kb/ownership.md`: battle-presentation vs env-art vs env-art-b vs creatures vs creatures-b vs ui (the trial keeps the merged side)
  - `game/battle/scene/battle_choreo.gd`: battle-presentation vs ui (the trial keeps the merged side)
  - `game/data/ui/battle_sandbox.json`: battle-presentation vs env-art-b vs ui (the trial keeps the merged side)
- **act1-chapters** (0737523e): 15 conflicted file(s); 1 resolved by union (append-only files):
  - `game/data/audio/creature_voices.json`: act1-chapters vs ui (the trial keeps the merged side)
  - `game/levels/_tests/act1_zones/ch07_tamsule_shots.tscn`: act1-chapters vs env-art-b (the trial keeps the merged side)
  - `game/levels/act1/zone_kit_dressing.gd`: act1-chapters vs env-art-b vs ui (the trial keeps the merged side)
  - `game/levels/ch05/pemakar/pemakar_dressing.json`: act1-chapters vs env-art-b vs ui (the trial keeps the merged side)
  - `game/levels/ch07/tamsule/tamsule.tscn`: act1-chapters vs env-art-b vs ui (the trial keeps the merged side)
  - `game/levels/ch07/tamsule/tamsule_dressing.json`: act1-chapters vs env-art-b (the trial keeps the merged side)
  - `game/levels/ch08/coilspire/coilspire_dressing.json`: act1-chapters vs env-art-b vs ui (the trial keeps the merged side)
  - `game/levels/ch08/corrow/corrow_dressing.json`: act1-chapters vs env-art-b vs ui (the trial keeps the merged side)
  - `game/levels/ch09/corrow_night/corrow_night_dressing.json`: act1-chapters vs env-art-b vs ui (the trial keeps the merged side)
  - `tools/act1/ch05_pemakar_dressing.py`: act1-chapters vs env-art-b vs ui (the trial keeps the merged side)
  - `tools/act1/ch07_tamsule_port_dressing.py`: act1-chapters vs env-art-b (the trial keeps the merged side)
  - `tools/act1/ch08_coilspire_dressing.py`: act1-chapters vs env-art-b vs ui (the trial keeps the merged side)
  - `tools/act1/ch08_corrow_dressing.py`: act1-chapters vs env-art-b vs ui (the trial keeps the merged side)
  - `tools/act1/ch09_corrow_night.py`: act1-chapters vs env-art-b vs ui (the trial keeps the merged side)
- **m2-slice** (c536ade7): 9 conflicted file(s); 3 resolved by union (append-only files):
  - `assets/levels/ch03/shell_shrine/shrine_gi_closed.res`: m2-slice vs ui (the trial keeps the merged side)
  - `assets/levels/ch03/shell_shrine/shrine_gi_inputs.json`: m2-slice vs ui (the trial keeps the merged side)
  - `assets/levels/ch03/shell_shrine/shrine_gi_open.res`: m2-slice vs ui (the trial keeps the merged side)
  - `docs/kb/tasks/M2/M2-HER-1113-cutscene-turns-and-end-jumps.md`: m2-slice vs env-art-b+ui (the trial keeps the merged side)
  - `game/levels/ch03/first_verse/first_verse.tscn`: m2-slice vs ui (the trial keeps the merged side)
  - `tests/integration/test_slice_primitives.gd`: m2-slice vs ui (the trial keeps the merged side)
- **hero-integration** (bf5749ea): 4 conflicted file(s); 0 resolved by union (append-only files):
  - `docs/kb/tasks/M2/M2-QA-100-runner-suspended-tests.md`: hero-integration vs ui+m2-slice (the trial keeps the merged side)
  - `docs/kb/tasks/M3/M3-HER-1120-liss-battle-stand-in.md`: hero-integration vs ui (the trial keeps the merged side)
  - `tests/integration/test_qa_capsules.gd.uid`: hero-integration vs ui (the trial keeps the merged side)
  - `tests/unit/test_hero_stairs.gd`: hero-integration vs env-art-b vs ui (the trial keeps the merged side)
**What needs an owner's eye (the Lead's call):**
1. **act1-chapters vs env-art-b: both are dressing Ch5/Ch7/Ch8/Ch9.** The clashing files:
   - pemakar_dressing.json, tamsule_dressing.json, coilspire_dressing.json, corrow_dressing.json and
     corrow_night_dressing.json;
   - their generators in tools/act1/;
   - game/levels/act1/zone_kit_dressing.gd;
   - tamsule.tscn and the Ch7 shot rig.

   Exactly the "two tracks dressing the same zones" case. One owner per zone, per ADR 0041's split
   (env-art-b: Ch5–Ch9 zones; act1-chapters: placement and flow).
2. **ui carries its own versions of other tracks' files:** act1-chapters' dressing generators, m2-slice's shrine GI
   bake and first_verse.tscn, creatures' portraits (flue_moth, mangrove_drowner, oil_slug), characters'
   requested_clips.json, arenas.json and battle_choreo.gd. Most likely ui merged older heads of those tracks; its
   next integration merge should take theirs.
3. **creatures vs creatures-b on game/data/creatures/creatures.json:** both write rows (the regulars/bosses split).
4. **battle_sandbox.json differs between env-art-b, ui and battle-presentation;** this branch's Liss and Kerrid rows
   are in it too.
5. **blender_builds.json:** characters vs creatures (both add jobs). A union-style resolve is likely right.
6. **docs/kb/ownership.md conflicts on every merge,** and tools/dev/merge_union.py doesn't union it although
   TRACK-RULES lists it as append-only. A one-line addition to merge_union.py would end that (QA & Tools' file;
   not edited here).
- hero-integration's own clashes are task files and the Lead's test_hero_stairs fix (taking theirs is right).
- I can't self-schedule while send_later is off, so I'll re-run this trial at each wake, about hourly.
**The placeholder audit on the trial-merged tree** (inventory rewritten from it @ 8b8cb3f0; its Source line says so):
- **45 items** (26 high, 15 medium, 4 low), against 159 on this branch alone: the tracks' unmerged work clears most
  of Act I. By owner:

  | Owner | Items |
  |---|---|
  | env-art | 13 |
  | audio | 12 |
  | creatures | 4 |
  | creatures-b | 4 |
  | act1-chapters | 3 |
  | characters | 3 |
  | env-art-b | 3 |
  | integration-qa | 2 (Pell) |
  | ui-menus | 1 (Kerrid's portrait) |
- **Seen only on the merged tree. Check these at the real merge:**
  - **Haluna's 7 villagers are capsules again** (Child, Fisher, Neme, Netmender, Osu, Reed, Vendor). Neither branch
    alone shows them as capsules, so this is likely the duplicate villager systems (creatures' VillagerLayer vs
    slice-polish's HalunaVillagers) meeting.
  - **The merged tree has a parse error:** BattleChoreo.REACT_IMMUNE is missing. battle-presentation's code uses
    it and ui's battle_choreo.gd lacks it; the trial kept ui's side, but the real merge must take
    battle-presentation's.
- **Audio:** every Act I music cue now plays at least a stand-in on audio's head. The music.json-vs-sequencer seam
  stands: the cue rows' own files are never played.

### FAST-TRACK @ b66981e9: the party sits still inside each other when the game begins (the human's playtest)
**Cherry-pick b66981e9 alone.** It touches game/hero_motion/hero_field_party.gd, hero_motion.json (field.followers:
hand_off_radius_m, spawn_search_steps, steer_turns_deg, slide_min_share) and a new test.
- **Cause 1, the opening.** Cutscene A ends with Asha and Toma walked onto Rhen's spot, and nothing handed them
  back. Their stage bodies stood still inside him, and Asha's follower stayed hidden behind her stage double.
  - **Fix:** when a held cutscene ends, the party members it cued that stand by the leader hide, and the
    followers take over.
  - A later cutscene that cues them shows them again. Field staging that no cutscene left by the leader stays as
    the zone set it.
- **Cause 2, stacked spawns.** A follower whose trail spot was blocked was put on the leader's own spot (the Bell
  galleries' Entrance: two bodies 0.11 m apart). Now every follower is placed at least min_gap_m from every
  other body.
- **Cause 3, frozen followers.** A step into a rail post slid to nearly nothing and was accepted, so the follower
  froze (the causeway at FromHaluna). Now the slide must keep a share of the step, else the follower steers
  around the post. A follower in the leader's way also steps aside instead of being shoved ahead.
- **Checked:**
  - Every spawn in the slice and Ch1 (Haluna, causeway, Underway, Oruvel) with real physics: all followers end
    behind Rhen and walk.
  - The Prologue hands off to Haluna's Beach, which is covered by the start test.
  - **tests/integration/test_qa_party_spawns.gd:** every Act I spawn (no overlap; each follower moves within 30
    frames) plus the real game start. On the old code it fails all three ways.
  - qa_ 9/0, hero_ 110/0.
- **SELF-RENDERED @ b66981e9** (a temporary shot, not committed: New Game, Cutscene A, the beach, side view). Asha and
  Rhen stand apart on the sand with no stacked figure, and Toma (in reserve) no longer stands on the spawn.
  - Seen in passing: Asha holds no staff, and a stick lies on the sand. Her staff not showing in static views is
    characters' known item (M1-QA-09); the stick may be beach dressing.
- **Not mine, seen while probing:** LifeAudio.advance (life_audio.gd:124) casts a freed object when a zone is
  freed. That's the audio item already in CONSOLIDATED.

### The FAST-TRACK cherry-pick failure (the Lead, 04:03): found
- **b66981e9 alone doesn't compile on the integration branch.** The hand-off calls `HeroFieldActor.hero_of`, which
  8fdf266d (M3-HER-1149) added together with hero_motion.json's actor_aliases and actor_prefixes. 608db549 has
  neither. So hero_field_party.gd fails to parse, and every `HeroFieldParty.new()` fails with it
  (hero_field_actor.gd:171).
- **To cherry-pick:** take 8fdf266d, then b66981e9. Or take the whole branch (big14).
- **On this branch merged with big13 (003fb560):** hero_ is 110/0 (compiles). The qa_ run, including the two
  party-spawn tests and the new encounter guard, is still going.
MERGE-READY @ c47eaa037 (+ this log): **big13 merged (003fb560); the encounter guard.**
- **Merged tree:** hero_ 110/0 and qa_ 10/0, so HeroFieldParty compiles and both party-spawn tests pass. Liss's
  model came with big13, so her field body and battle actor are live (the hero guards run on her real model).
- **New: tests/integration/test_qa_encounters.gd.** Every Act I fight (33) is entered as the field enters it
  (BattleRequest.make with its return zone and spawn), won, accepted, and left back to its zone. The party walks
  there under a QaLogger. All 33 are clean: no engine or script error.
  - Five scripted fights don't end by attack within 80 turns and are reported, not failed: ch06_inquisitor (he
    yields), ch08_stair_hold_1–3 and undertows_reach (objectives and a scripted escape).
  - **It didn't reproduce the human's "cast a freed object" entering a fight.** That likely sits in the real
    scene-change path (SceneRouter fade, BattleStinger, start_battle_staged), which a headless test can't drive
    without frames. **Next:** a probe scene that runs the real BattleRequest.submit → router → staged build with
    real frames, for the slice and Ch1 fights.
- **SELF-RENDERED @ 003fb560:** ch07_bell_galleries and ch08_corrow_stair, both pixel-identical to big13's
  approved baselines. No capsule is visible; Liss is too small to read at those distances.

### TRIAL MERGE, 2026-10-28 ~05:00
TRIAL MERGE @ integration 6b89f4a6: env-art af40b3af, env-art-b ce8d1e3d, creatures 0d50432b, creatures-b 6a48fcb7, characters 9ea8d3d7, ui 4ffa64bd, battle-presentation 1daa0fa7, act1-chapters 4e122798, m2-slice 9f31066b, audio 1e237a01, hero-integration 470e7b5e
- **env-art-b** (ce8d1e3d): 1 conflicted file(s); 1 resolved by union (append-only files).
- **creatures** (0d50432b): 2 conflicted file(s); 2 resolved by union (append-only files).
- **characters** (9ea8d3d7): 2 conflicted file(s); 1 resolved by union (append-only files):
  - `tools/dev/blender_builds.json`: characters vs env-art vs env-art-b vs creatures vs creatures-b (the trial keeps the merged side)
- **ui** (4ffa64bd): 4 conflicted file(s); 3 resolved by union (append-only files):
  - `tools/dev/blender_builds.json`: ui vs env-art vs env-art-b vs creatures vs creatures-b vs characters (the trial keeps the merged side)
- **battle-presentation** (1daa0fa7): 5 conflicted file(s); 3 resolved by union (append-only files):
  - `docs/kb/ownership.md`: battle-presentation vs env-art vs env-art-b vs creatures vs creatures-b vs ui (the trial keeps the merged side)
  - `game/data/ui/battle_sandbox.json`: battle-presentation vs env-art vs env-art-b vs creatures-b vs ui (the trial keeps the merged side)
- **act1-chapters** (4e122798): 9 conflicted file(s); 4 resolved by union (append-only files):
  - `docs/kb/ownership.md`: act1-chapters vs env-art vs env-art-b vs creatures vs creatures-b vs ui vs battle-presentation (the trial keeps the merged side)
  - `game/data/audio/creature_voices.json`: act1-chapters vs env-art vs env-art-b+creatures-b (the trial keeps the merged side)
  - `project.godot`: act1-chapters vs env-art vs env-art-b+creatures-b vs ui (the trial keeps the merged side)
  - `tests/unit/test_zone_map.gd`: act1-chapters vs env-art vs env-art-b+creatures-b vs ui (the trial keeps the merged side)
  - `tools/tests/test_ch08_flow.py`: act1-chapters vs env-art+env-art-b+creatures-b vs ui (the trial keeps the merged side)
- **hero-integration** (470e7b5e): 1 conflicted file(s); 0 resolved by union (append-only files):
  - `tests/unit/test_hero_stairs.gd`: hero-integration vs env-art vs env-art-b vs creatures-b+m2-slice+audio (the trial keeps the merged side)
**Since the last trial:** act1-chapters and env-art-b no longer clash over the Ch5–Ch9 dressing; ui no longer
carries stale copies of others' files; creatures and creatures-b merge cleanly.
**New or still open:**
1. **project.godot `locale/translations`** (act1-chapters, env-art, env-art-b+creatures-b, ui): each appends its
   own translation files (Act II ch10–16, kite, maps_act2, towns_act2) in a different order. Keeping one side drops
   the others' strings, which then show as raw keys. Resolve as a union; adding it to merge_union.py would end it.
2. tools/dev/blender_builds.json (characters, ui and the env-art/creatures tracks all add jobs): union.
3. battle_sandbox.json (battle-presentation vs env-art, env-art-b+creatures-b and ui).
4. docs/kb/ownership.md, as every time.
5. tests/unit/test_hero_stairs.gd: other branches carry the Lead's identical fix; either side is fine.

**The placeholder audit on this merged tree: 39 items** (19 high, 16 medium, 4 low), down from 45. The inventory
is rewritten from it:

| Owner | Items |
|---|---|
| audio | 12 |
| env-art | 12 |
| creatures | 4 |
| creatures-b | 4 |
| characters | 3 |
| env-art-b | 2 |
| integration-qa | 2 (Pell) |

act1-chapters' Ch8 arenas and ui-menus' Kerrid portrait are cleared.

MERGE-READY (+ this log): **the real-frame battle entry probe, every Act I chapter** (the Lead's item 4).
- **New: `tools/dev/battle_entry_probe.tscn`** (`godot --headless --path . res://tools/dev/battle_entry_probe.tscn -- --chapters=1,2,3`).
  For each Act I fight: New Game, then SceneRouter into its zone at its spawn, `BattleRequest.start` as the zone does
  it (stinger, router fade, staged build), a win, accept, and the router back to the zone. A QaLogger watches the
  whole run. It prints one PROBE line per fight and ends with "PROBE done: N error(s)". It's a dev tool, not a test,
  because one chapter takes minutes of real frames.
- **Results, chapters 1–9 (33 fights):** no SCRIPT ERROR, no freed-object cast, no missing resource. **Still not
  reproduced: the human's "cast a freed object".** Two engine errors went to their owners:
  - **M3-HER-1150 → audio:** `ashcrown_audio.gd:49` calls `unbind(0)` for a three-argument signal, an engine error
    on every Ashcrown entry. The fix is one line (`unbind(n) if n > 0`, as its siblings do).
  - **M3-HER-1151 → architect:** "Attempting to initialize the wrong RID" from `ShaderGlobals.set_value` ←
    `WeatherClock._process`, during a router swap that instantiates on a thread (the return into saltgrass_causeway).
    It's intermittent (1 in 2 runs) and a race between threads, which is **my best lead for the human's freed-object
    crash**.
- Scripted fights that don't end by attack (reported as before): ch06_inquisitor, ch08_stair_hold_1–3,
  undertows_reach. ch04_sail_leeches only needed the probe's frame budget (fixed), and is clean.
- Gates: gdlint/gdformat, validate_data, taskboard --check. No Godot test touched.

MERGE-READY (+ this log): **reproduced the human's "Trying to cast a freed object"; my own case fixed; a lint for the rest.**
- **Cause:** a stored node is cast before its `is_instance_valid` check. `var x := stored as T` errors on the cast
  itself when the node is freed. My own `HeroFieldParty.should_hide` did this with the cutscene sequencers it watches
  (the FAST-TRACK hand-off code). A watched sequencer freed before the party (a cutscene's temporary sequencer, or a
  teardown order) gives exactly the human's message, every frame.
  - Fixed: check first, then cast.
  - New test `test_qa_party_spawns::test_a_freed_sequencer_is_not_cast` frees Haluna's sequencers and runs the
    party's frame. The old code logs "SCRIPT ERROR: Trying to cast a freed object." twice and fails; the fix passes
    (3/3 qa_party).
- **New: `tools/freed_cast_lint.py`** (+ `tools/tests/test_freed_cast_lint.py`, 5 tests). It finds the pattern
  across `game/`. A new hit fails the tools suite; known hits are listed with their request task:
  - `footstep_audio.gd:590` → M3-HER-1150 (audio; added to the unbind task);
  - `revenant_tells.gd:162` → **M3-HER-1152** (rendering);
  - `battle_choreo.gd:801` → **M3-HER-1153** (ui/battle-presentation).
  Each fix is one line. The owner removes the KNOWN row when it lands.
- Gates: hero_ 110/0, qa_party 3/0, freed_cast_lint unittest 5/0, gdlint/gdformat, validate_data, taskboard.
- **Lead:** the lint belongs in `tools/ci_local.sh` (it runs through the tools suite already, via
  test_freed_cast_lint).

### TRIAL MERGE, 2026-10-28 ~05:45
TRIAL MERGE @ integration 6b89f4a6: env-art 62409951, env-art-b 6edde924, creatures 0d50432b, creatures-b 557a9ea5, characters 73917b03, ui 296ceb69, battle-presentation 1c1f89b3, act1-chapters 0d19e1f4, m2-slice 9f31066b, audio 5061e0fa, hero-integration 41c277d2
- **New since 05:00, the one that matters: env-art vs env-art-b on the Haluna kit, 10 files.** These don't union:
  `assets/environments/kits/haluna/kit_manifest.json`, `assets_src/environments/kits/haluna/build.py` and
  `materials.py`, `game/data/ui/zone_maps.json`, `tools/tests/test_ch08_flow.py` (+ ownership.md). env-art (M3-ENV-743,
  Ch4 wake-night dressing) and env-art-b (M3-ENV-721, Ansedra) both grew the shared Haluna kit build. **Lead:** one of
  them should merge the other before the next batch, since a by-hand merge of build.py decides the kit's geometry.
- As at 05:00: `blender_builds.json` (characters, ui vs env-art/creatures), `battle_sandbox.json`, ownership.md, and
  act1-chapters' `project.godot`/`creature_voices.json`/`test_zone_map.gd`/`test_ch08_flow.py`.
- **hero-integration:** `test_hero_stairs.gd` clashed only on integration's one-line comment on `_done()`. I took
  integration's file, so my branch no longer clashes.
- **Audit on the merged tree (static half only, 20 items: audio 12, creatures-b 4, env-art 4).** The runtime scan
  needs an import of the merged tree, so it waits for the next full one. The 05:00 inventory (39, runtime included)
  stands.
- **freed_cast_lint on the merged tree:** 0 new hits (only the three filed ones).

MERGE-READY (+ this log): **the encounter guard now wins every Act I fight, set pieces included.**
- `test_qa_encounters`:
  - Each turn the party attacks. Where a set piece refuses that (Toma won't strike the Inquisitor, the stair is
    held), it uses the first skill the engine accepts, on a foe, the ward, itself or no one (`_take_turn`).
  - `rig()` keeps foes at 1 HP and standing heroes at full, so the tide can't win before the objective is met.
  - Every fight **must** now be won or end in its scripted escape. A defeat or a fight that never ends fails it.
    Before, ch06_inquisitor, ch08_stair_hold_1–3 and undertows_reach were only reported, and undertows_reach was
    actually a party wipe: its "result" was Retry.
  - Result: 33/33 won and left, 0 failed.
- `tools/dev/battle_entry_probe`:
  - Uses the same turn driver and rig.
  - Waits by wall clock (90 s): headless frames run uncapped, but the router's loads take real time.
  - Accepts only once the result panel shows.
  - Adds `--only=<encounter>`.
  - Ch6 and Ch8 with real frames, set pieces included: clean.
- Gates: gdlint/gdformat, qa_encounters 1/0, the probe on ch6, ch8 and undertows_reach.

### TRIAL MERGE, 2026-10-28 ~06:45
TRIAL MERGE @ integration 6b89f4a6: env-art 62409951, env-art-b 6edde924, creatures e1fd27df, creatures-b 557a9ea5, characters 73917b03, ui 296ceb69, battle-presentation bd97051f, act1-chapters d150d529, m2-slice 9f31066b, audio 659ed2d8, hero-integration 29944240
- Conflicts are the same as at 05:45, **env-art vs env-art-b on the Haluna kit still included** (Lead: still open).
  hero-integration now merges clean.
- **Full audit on the merged tree (runtime scan included, after an import): 44 items**, up from 39. Rewritten
  in `docs/kb/qa/act1_final_inventory.md`.
  - **New:** act1-chapters' latest stages bring the Ch6 Brine Shoals stage actors as capsules (stillguard_a–c,
    hound, inquisitor → creatures/characters by the people split), plus Ch4 spar_wraith and the stillguard_inquisitor
    battle model.
  - Env-art went from 4 items to 3.
  - integration-qa's 2 items are Pell and vigil_pell in Ch9's ch09_pell_joined variant, which wait on M3-CHR-506
    as before.

MERGE-READY @ 201d21068 (+ this log): **big14 fixes on the merged tree** (origin/gpu/gate-big14-shots merged as 8268e80b6,
without the 391 gate-run PNGs, 131 MB).
- **(5) The human's party-start bug ("Rhen not on screen"): FIXED.** He was on screen, about 20 m out, but Asha's
  follower stood exactly between the trailing field camera and him and covered him. The playtester read the pair as
  Asha and Toma; Toma is in reserve then.
  - HeroFieldParty now keeps every follower off the camera's line of sight to the leader:
    - A follower point between the camera and him, within `sight_clear_m` (0.9) of that line, steps aside.
    - It keeps its side until the line is clear, and takes the other side at a wall.
    - It never comes nearer him than min_gap.
  - Also: a leader faster than `jump_mps` (20) counts as a teleport, so the party relays out. A 2.0 m place_at, just
    under teleport_m, left a follower stacked beside him.
  - **New test** `test_qa_party_spawns::test_no_follower_hides_the_leader_from_the_field_camera`. On the old code a
    follower stood 0.02 m off the line; it passes with the fix. qa_party 4/0.
  - **SELF-RENDERED** (lavapipe, 960x540, after Cutscene A at beach_path, a walk up the beach): Rhen and Asha stand
    side by side by the wall gap, both in frame. Viewed.
  - The "empty sky" lines inside Cutscene A are H05 framed for Rhen lying down, which he stands up out of →
    **M3-HER-1155 (cinematics)**.
- **(1) test_hero_field_snaps haluna_wake:** Rhen falls. The NemeDoor spawn is 7.8 m above the ground (y 9.706,
  ground 1.90). Act1-chapters' data → **M3-HER-1154** (patch inside), KNOWN in the test. drowned_choir's 2 snaps are an
  Act II greybox (M4-C14-02, paused), also KNOWN.
- **(2) test_fp_prologue "Liss waits":** Liss has a body since big13. The test now checks each vigil against
  HeroFieldActor.scene_path. fp_prologue 8/0.
- **(3) test_qa_capsules:** Haluna's 7 wake villagers, ossa_fen's pell and the 10 Act II foes (Ch10–16, creatures)
  are listed with owners. 3/0.
- **(4) test_qa_save_shrines haluna_wake:** there's no Shrine spawn, **and the shrine respawns in ch02/haluna** (a save
  there would load in Ch2). Both are in M3-HER-1154 (act1-chapters), KNOWN in the test. 2/0.
- Still running at the time of this line: the full `--filter=hero / party / fp_ / qa_` on the merged tree. Results
  follow in the next line.

MERGE-READY @ a7e4f4f78 (+ this log): **big15 merged in (integration 2d6a25a7), plus the hero tests after the sight-line step.**
- `--filter` results on the big14 tree before the follow-up commit 94c6f1d4: hero 110/2, party 35/1, fp_ 30/0. All
  three failures are fixed in 94c6f1d4:
  - test_hero_followers "facing her walk again" now measures against her follow point (she walks to her stepped-aside
    spot, not straight at him);
  - test_battle_party_stand_ins checks Liss's tint against her own capsule colour, not a literal (the data changed
    to #7A8C5A);
  - Toma's 3 wake snaps are the same NemeDoor fall (KNOWN, M3-HER-1154).
  - hero_followers 12/0, party_stand_ins 3/0.
- qa_ (merged big14 tree, the sight-line fix in): **12/0**: the playthrough, every Act I encounter entered, won and left, shrines, capsules, party spawns, the freed-sequencer guard.

### TRIAL MERGE, 2026-10-28 ~11:10
TRIAL MERGE @ integration 2d6a25a7 (big15): env-art 5d81885c, env-art-b 697bc32d, creatures a6eada94, creatures-b 3bf1fa2b, characters 4ab59bc1, ui 115f20b2, battle-presentation c358c481, act1-chapters e66297f9, m2-slice 7dba5bc2, audio 6adbda62, hero-integration 94c6f1d4
- **creatures vs creatures-b: the Vowbound portraits** (`assets/ui/portraits/creatures/ilun*.png`, `kahre*.png` and
  their .import). Both tracks drew them, and binary files can't union. **Lead:** pick one.
- `ui_sfx.json` (audio vs ui) and ownership.md (several tracks) need hand merges.
- hero-integration's 3 "clashes" (qa_known.json, test_fp_prologue, test_battle_party_stand_ins) are only tracks still
  on pre-big15 versions. My branch has merged big15 cleanly.
- **The Env-art vs env-art-b Haluna kit clash is gone.**
- **Audit on the merged tree, full (import + runtime scan): 17 items, down from 44.** `act1_final_inventory.md` is
  rewritten. env-art 10, creatures-b 4, env-art-b 1, integration-qa 2. Audio, characters and creatures are all clear.
- **integration-qa's 2 are Pell and vigil_pell (Ch9, ch09_pell_joined).** They wait on characters' Pell model,
  **M3-CHR-506, still todo**; nothing in my lane can make them real (no model, no AI art). The wiring is ready: the
  `vigil_` prefix and HeroFieldActor.hero_of take his body the moment hero_motion.json gets a `pell` row.

MERGE-READY (+ this log): **the party start, take two (the big15 GPU playtest), merge_union three-way, the threaded-load RID race.**
- **(1) Party start** (pc-gpu.md big15: "camera opens ~15 m back over the shallows, Toma isn't in frame, the lane turn
  swings into the walls"):
  - **Toma walks too.** HeroFieldParty `followers.include_reserve`: the reserve follows after the active party, up to
    `max` (the slice's Toma is in reserve).
  - **A FOLLOW camera** (new CameraShot.Mode.FOLLOW, ADR 0194): it rides `follow_distance` (7 m) back along the shot's
    authored heading and `follow_height` (4 m) up, smoothed, aimed at him. Haluna's beach_shallows, beach_path and the
    lane's H09 use it now (beach_shallows takes beach_path's heading, so the handover doesn't jump). The party stays
    the same size on screen and the camera never swings.
  - **Followers judged in 3D:** a follower only covers him if the camera's line down to his chest passes under her
    head (`head_m` 1.8). Otherwise she steps aside (`sight_clear_m` 1.1, falling back through
    `sight_clear_shares` near walls, the side she stands on). Bodies level with him (`sight_depth_m`) don't count.
  - **Occlusion is judged by drawn meshes, not collision** (Coilspire's shell collider missed the wall the player
    sees): the director's `view_blocker` tests visible meshes of at least `min_size_m` by their triangles.
  - **New guard** `test_qa_field_camera::test_the_walk_from_the_beach_to_the_village_keeps_the_party_in_view`: from
    Cutscene A's mark up the beach, through the gap and down the lane to the Village. Every frame he's seen and
    every follower is in frame. A follower may only cross his line for under 20 frames, rounding a corner. **2/0**
    with the 106-spawn guard.
  - **SELF-RENDERED** (lavapipe 960x540, the walk at frame 90): Rhen, Asha and Toma close together in frame, the
    camera just behind and above. Viewed.
- **(2) tools/dev/merge_union.py merges every keyed file three-way** (shots.json by id, baselines.json,
  prewarm_materials by path, flags.tres):
  - a key only theirs changed takes theirs in place, a key one side deleted is deleted, both-changed keeps ours and
    is reported;
  - big15 lost battle-presentation's `settle_frames` edits this way;
  - test_merge_union 12/0, including an end-to-end git merge that fails on the old code (settle 30, not 90).
- **(3) Architect role:**
  - **M3-HER-1151 FIXED (the RID race):** ShaderGlobals holds its RenderingServer writes while SceneRouter
    instantiates on a worker thread and sends the last value per global after. test_shader_globals_hold 3/0;
    weather_clock 11/0, scene_router 15/0, haluna_weather 3/0. **Three ch3 probe runs: 0, 0, 0 RID errors** (1 in 2
    runs before). Their 2,708 other errors are all M3-HER-1158, battle_result_panel.gd:266.
  - **M3-ENV-747 → review:** already done by M3-ENV-101 (186848eb8); the inventory lists no save-shrine item.
  - M3-ARC-1216 (my own steep stairs) waits on its cinematics review and on act1-chapters placing Ashcrown's flights.
- Tests: hero_ 110/1 → the 1 is Asha in haluna_wake's NemeDoor fall (KNOWN now, M3-HER-1154); qa_party 3/0,
  hero_followers 12/0, camera 54/0, haluna_zone 7/0.
- LEAD-ASK: M3-C05-1215 (act1-chapters, Ashcrown on the kit) still says "blocked on M3-ARC-1216". The walkable stair
  mode is on integration (HeroStairFlight, or a zone layout `"stairs"` row, see M3-ARC-1216's notes). Please tell
  act1-chapters it can unblock and place the 48° flying stair and the 60° vein stairs.
- LEAD-ASK: haluna.tscn's camera shots (M2-FP-109's) now use the FOLLOW mode on the beach and the lane. Slice-polish
  should know before re-composing them.
- LEAD-ASK (urgent, the human's error class): **big15 brings a freed-object cast at every fight's end.**
  `BattleResultPanel._set_count` (battle_result_panel.gd:266) logs "Trying to cast a freed object" ~930 times in one
  real-frame ch3 probe run. FieldBattle re-shows the result panel, which frees the old rows but leaves the old open
  tween counting into them. Filed as **M3-HER-1158 (ui / battle-presentation, FAST-TRACK)** with a 3-line patch.
  Please have battle-presentation take it, or give me the word to apply it myself.
- LEAD-ASK (architect, on ADR 0111 / ResidentLoads): claude/ui's SceneRouter change merges cleanly with mine (a
  scratch merge shows no conflict). But ResidentLoads loads a zone's models on threads while the router waits frames
  for them, and each of those frames runs WeatherClock's hymn_wind_time write. That's M3-HER-1151's race: a
  global-shader write walking the material list while a worker thread creates materials. My fix holds
  ShaderGlobals' writes only around the router's own threaded instantiate. ResidentLoads should do the same around
  its loads: `ShaderGlobals.hold_writes()` when a load starts, `release_writes()` when it lands. Holds nest, so
  overlapping loads are fine. I can add it after ui-menus merges, if you give the word.
- **SELF-RENDERED** (party start, the whole walk; lavapipe 960x540, viewed):
  - start: all three close together;
  - the wall's gap (turn1): Rhen clear, Toma near the camera to the side;
  - entering the lane (turn2) and the lane turn itself (turn3, where big15's camera swung into the stone walls): the
    camera looks down the lane over the party, all three in frame between the walls, no clipping.

MERGE-READY (+ this log): **M3-ARC-1326 (env-art-b's ask, Ch9's Ebbing): the sequencer offers `@vfx` cues to the stage's VFX hosts.**
- New `game/cutscene/cutscene_vfx_hosts.gd` (CutsceneVfxHosts.offer): every node in the `cutscene_vfx_hosts` group
  with `play_vfx(effect, at_id, kwargs) -> bool`, first taker wins. `CutsceneSequencer._cue_vfx` returns before
  spawning the CutsceneMotes placeholder when a host takes the cue (one line; the file stays at 999).
- **Vocabulary: accepted as proposed.** cues.json `vfx` kwargs gain `follow` (`<actor>` or `<actor>_staff`) and
  `anchors` (`<actor group>`). They reach hosts whole, the placeholder ignores them, and dlgc --check is 0/0.
- tests/unit/test_cutscene_vfx_hosts.gd **4/0**: a taking host means no placeholder and gets the kwargs; a declining
  host leaves the placeholder; no host means the placeholder; the vocabulary. It fails 2/4 on the old sequencer.
  ch09_thread 7/0.
- For env-art-b: M3-ARC-1326's task file is only on your branch, so I haven't copied it (an add/add clash). Please
  tick its boxes and record "vocabulary accepted" when you merge this.

### TRIAL MERGE, 2026-10-28 ~15:50
TRIAL MERGE @ integration 8870ea9c: env-art 885fba18, env-art-b 6a8f1504, creatures 958ad402, creatures-b d5f7b2b2, characters d0422fdc, ui 249bcafc, battle-presentation 1d4df7bf, act1-chapters d212b041, m2-slice 36d3c958, audio 1cb9654d, hero-integration 5f59e287
- **Still open:**
  - creatures vs creatures-b on the Vowbound portraits (ilun*, kahre* .png and .import; binary, pick one);
  - ui_sfx.json (audio vs ui);
  - ownership.md (several tracks).
- **New:**
  - **m2-slice vs env-art on Ch1's Oruvel and Underway**: 7 files that don't union (both dressing generators
    `tools/ch01/ch01_*_dressing.py`, the dressing and layout json, the environment .tres). Lead: one should merge the
    other first.
  - battle-presentation vs env-art-b on `test_battle_arena.gd`, battle_sandbox.json and two task files;
  - act1-chapters vs env-art on brightwater_ferry_layout.json.
- **hero-integration's 3 clashes are gone.** Act1-chapters, m2-slice and battle-presentation fixed the same big14
  failures in their own files. I took their versions (qa_known.json, test_fp_prologue.gd,
  test_battle_party_stand_ins.gd): fp_prologue 8/0, party_stand_ins 3/0.
  - **On my branch alone**, qa_capsules fails on Haluna's 7 villagers, since act1-chapters' qa_known drops them for
    their fix. It's green on the merged tree.
- **Audit on the merged tree, full (import + runtime scan): 11 items, down from 17** (env-art 9, integration-qa 2).
  `act1_final_inventory.md` is rewritten. creatures-b and env-art-b are clear now. integration-qa's 2 are still
  Pell and vigil_pell (Ch9), waiting on M3-CHR-506.

MERGE-READY (+ this log): **architect seat: reviews, Sefir's body, and the audit sees layout states.**
- Reviews:
  - **M2-MNU-06 and M2-ARC-12 accepted** (scene_router 15/0, frame_clock 8/0, boot_card 27/0).
  - **M3-ARC-02 accepted** (chapter select Ch1–Ch9, debug_overlay 14/0), with a caveat: F8 → Ch4 lands on the
    broken NemeDoor (M3-HER-1154, which now notes it).
  - M2-ARC-04: its release guard still passes on big15 (4/0); environment reviews and the PC still has to export.
- **M3-HER-1225 → review: Sefir's field body.**
  - A hero row can name its own locomotion clips (`clips`). Sefir walks and runs on his `walk_glide` (0.21 m/s,
    measured), since he has no stepping walk.
  - New test: his stage actor takes his body and glides. hero_field_actor 15/0, hero_ 110/0.
- **M3-HER-1219 → review:** Ysolde's row was already in. The audit lists no Ysolde capsule.
- **The audit and the capsule guard now walk layout `states`** (Ch4/Ch6/Ch8's refresh_states rows, flags set in
  story order). They found two capsules a playthrough sees but neither tool did:
  - Ch8 corrow `pell` (from ch08_wave2_held) → M3-CHR-506;
  - Ch8 corrow `figure`, the stranger on the wall (from ch08_reach_survived) → characters by the people split.
  - Both are KNOWN in qa_known.json; the next audit lists them.

MERGE-READY (+ this log): **lead/gate-big16 (ff82858c) merged in; big15's two cloud failures checked on it.**
- **test_hero_followers::test_followers_turn_to_face_who_rhen_talks_to:** green on big16 (12/0). big15 had my
  sight-step follower code without its test follow-up (94c6f1d4, which big16 carries). Nothing more to do.
- **test_post_import::test_every_glb_import_runs_its_category_script (tech seat):**
  - The cause: creatures' new **crowd** import category (game/data/import/crowd.json + crowd_post_import.gd,
    M3-CRE-659; 22 `assets/crowd/*` glbs, whose .import files do run crowd_post_import.gd) was never added to the
    test's `KINDS` list. Every crowd glb read as "in no import category".
  - Fixed here: `"crowd"` is in `KINDS`. post_import 21/0 on big16 and on this branch.
- **TRIAL MERGE ~16:50:** every track head merges clean. The tree is big16 in progress (the Lead's batch already
  carries everyone's heads).
- **Audit on that tree, full: 13 items** (env-art 9, creatures 1, integration-qa 3). act1_final_inventory.md is
  rewritten. The layout-state scan adds two:
  - Ch8 corrow `pell` → integration-qa (M3-CHR-506);
  - Ch8 corrow `figure`, the stranger on the wall → creatures.
  The other two integration-qa rows are Ch9's pell and vigil_pell, also waiting on M3-CHR-506.
- **Re the Lead's 17:37 note:** test_hero_followers::test_followers_turn_to_face_who_rhen_talks_to ("expected
  0.6907... facing her walk again") is big15's head of mine, which had the sight-line step without the test's
  follow-up. The fix is f2f67ea1b: the follower test turns the sight step off in before_each (`sight_clear_m` 0),
  since it tests the trail itself and test_qa_field_camera tests the sight step. It's on big16 too.
  **`--filter=hero` on head 575ca4637: 112/0.**

MERGE-READY (+ this log): **party start fixed @ a6e9d5481** (big16 merged in, re-rendered on this head).
- **SELF-RENDERED** (lavapipe 960x540, Haluna after Cutscene A, a walk up the beach and into the lane), viewed:
  - **opening**: the camera is close behind the party, not 15 m out over the shallows, and **Rhen, Asha and Toma are
    all in frame**;
  - **the wall's gap (turn2) and the lane turn (turn3)**: the camera rides above the party down the lane, clear of
    the walls, all three in frame. This is the spot where big15's camera swung into the stone walls.
  So all three of the human's points are fixed.
- **The guard on this head** (test_qa_field_camera 2/0) found what big16 brought in, all routed:
  - **M3-HER-1160 → m2-slice:** at the walk's very end, Haluna's NemeTable volume (shot B02, the close shot at
    Neme's table) covers the Village spawn. The party arrives from behind that camera, so Asha and Toma leave the
    frame. KNOWN for the walk guard.
  - **M3-HER-1159 → act1-chapters:** four spawns whose volume's shot faces away. Brightwater DerelictDeck and Stern
    (FerryWaist), Coilspire Encounter (GallerySouth), Corrow Bastion (WallGate, Rhen behind the camera). KNOWN rows.
- M3-ARC-1326 (the Ebbing cue hook) has been in since 5f59e2878.

## FROM 2026-10-29 (Lead session_01Bg3iP7cPGyjbX4CyniBahc; integration branch claude/new-session-mj8c3c)
- Merged `origin/claude/new-session-mj8c3c` into this branch (1e87e60d2). One clash, `pc-gpu.md`, which my branch only
  carried through old gate merges: took integration's version (pc-gpu owns it).
- **tools/dev/trial_merge.py:** its integration branch is now `claude/new-session-mj8c3c` (it still pointed at the
  retired -ze8rrn), with `--integration` to override. New **`--prefold <ref>...`** merges an unlanded batch first.
  big17 is `lead/gate-big16` plus the track heads, and integration carries neither big15 nor big16, so a trial on
  bare integration reports clashes big16 already resolved. tools.tests.test_trial_merge 4/0 (new).

### TRIAL MERGE, 2026-10-29 ~17:40
TRIAL MERGE @ integration 5a9978bc + lead/gate-big16 ff82858c (= big17's base): env-art b68d1920, env-art-b a5e650bd,
creatures f6846325, creatures-b d5f7b2b2, characters 3346484b, ui b2118f76, battle-presentation e641579e,
act1-chapters 483dcb91, m2-slice d0433789, audio 1cb9654d, hero-integration 5c11d034
- **Seven of the eleven heads merge clean onto big16.** characters' 2 clashes resolve by union (PROVENANCE and the loc csv).
- **m2-slice (resolver: m2-slice, or the Lead in big17): `game/levels/ch02/haluna/haluna.tscn`, one hunk, mechanical.**
  - m2-slice's M3-ENV-748/750 (ad28e9f4b, 6fa376771; after big16 took m2-slice) delete Osu's capsule
    sub-resources (`Mat_osu`, `Mesh_osu`).
  - big16's env-art M3-ENV-753 (219b86861) deletes the bowl, shell and bag sub-resources (`Mat_/Mesh_bowl`,
    `_shell`, `_bag`), since those props are kit instances now.
  - Each side keeps the block the other deleted. **Resolution: delete the whole conflict block, keeping neither
    side.** Checked in a scratch merge: none of the 8 ids is referenced after it, and the rest of the file auto-merges.
- **m2-slice (resolver: m2-slice): `docs/kb/tasks/M3/M3-CIN-1221-sequencer-mark-via.md`:** keep m2-slice's
  `owner_session` and **both** Review-log lines (act1-chapters' and slice-polish's).
- **battle-presentation (resolver: battle-presentation, or the Lead): `tests/unit/test_battle_arena.gd`:** both sides
  map `ch05_cinder_matron` to `ashcrown_anvil_court`. Only big16's side has the `# M3-BPR-1305` comment. Keep big16's line.
- `pc-gpu.md` (big16 vs integration's 10-29 edits; env-art carries the old version as well): take integration's
  version. pc-gpu's log is the Lead's to merge.
- For reference, a trial on bare integration (no prefold) also hits haluna.tscn as m2-slice vs env-art and
  test_battle_arena.gd as battle-presentation vs env-art. Those are the same three hunks, seen from before big16.

### Audit on the big17 trial tree (full: import + runtime scan), 2026-10-29
- **9 items, down from 13** (creatures 1, env-art 5, integration-qa 3). `act1_final_inventory.md` is rewritten from that tree.
  - Gone: env-art's 4 medium rows (Haluna's and haluna_wake's `banyan_placeholder` / `windbreak_placeholder` nodes).
  - Nothing new, so no new tasks: every row is already filed (M3-HER-1140 env-art, M3-HER-1142 creatures, M3-HER-1149 mine).
  - My 3 rows are Pell's Ch8/Ch9 capsules. They clear when claude/characters (Pell, M3-CHR-506) merges with the
    row below.
- The import logs `TideNotchStyleBox` parse errors and a missing SourceSans3-Bold.otf. Both show up on any fresh
  `.godot` (this branch too) and the files exist, so they're first-import order noise, not a finding.

MERGE-READY @ fa046a497 (+ this log):
- **M3-HER-1149, Pell's field row:** walk 1.27 m/s, run 3.13 m/s, measured by HeroClipGait on characters'
  pell_lod1 in the trial tree. Ch9's `pell` and `vigil_pell` (via the `vigil_` prefix) take his body once his model
  merges, and stay capsules before that. test_hero_field_actor's alias test handles both cases, and checks that a
  no-row actor keeps its capsule. No battle wrapper, because Ch9 gives him no battle row in Act I (M3-C09-07).
  - Note: ResidentLoads already preloads every field body that has a model, so `scene_loads.json` needs no regeneration.
- **M3-HER-1227 → review:** the fix had been in since 41c277d26. Added the regression test (a freed cached
  sequencer ahead of a playing one); it fails on the old order. hero_followers 13/0.
- **M3-C09-09 → review (architect):** Ch9's grade ids `ch09`, `ch09_dawn`, `prologue` and the `act_card <int>`
  event (ActCard already listens for it). **Ruling: `hold_input`/`hold_input_end` stay events.** Moving
  ch09_the_road_out's card to `<<event act_card 2>>` is act1-chapters' edit. test_dlgc 129/0, dlgc --check 0/0.
- **M3-ARC-1324 → review (architect, env-art-b's ask):** `apply_system_tiers` sets WaterSphereRig's and
  SmokeColumn's tiers. test_graphics_runtime_system_tiers 2/0, underwater 8/0.
- Checks: gdlint/gdformat on the touched files, validate_data 0/0, taskboard --check, hero_field_actor 15/0,
  tools test_trial_merge 4/0.
- Skipped: screenshots (no scene, shader or camera change; the Pell row only acts once his model is on the tree).
- Act I GPU QA rows for me (act1_gpu_qa.md on gpu/act1-qa-2):
  - 21 (party start) is fixed @ 5c11d034;
  - 37 and 38 are fixed on the camera and follower side. The spawn and volume remainders are M3-HER-1156
    (environment) and M3-HER-1157 (environment).

### TRIAL MERGE, 2026-10-29 ~18:45 (prefold lead/gate-big17, i.e. what big18 builds on)
TRIAL MERGE @ integration 4f9c3732 + lead/gate-big17 be74f9a0: env-art c3038a18, env-art-b 6322659f,
creatures f6846325, creatures-b d5f7b2b2, characters 3346484b, ui 625dabd1, battle-presentation 80e565ea,
act1-chapters 7f49b2f3, m2-slice e7b19992, audio 1cb9654d, hero-integration 1ff590fa
- **`docs/kb/handoffs/live/pc-gpu.md`** (env-art, ui, battle-presentation, act1-chapters, hero-integration): these
  tracks merged integration's 10-29 copy, and big17 carries the older one. Resolver: the Lead. Take integration's.
- **env-art: `docs/kb/tasks/M3/M3-ENV-750-...md`.** Resolver: env-art or the Lead. Take env-art's side
  (status done, plus its 10-29 review line).
- **ui: `tests/screenshots/shots.json` CRASHED merge_union.** ui and big17 have 3 merge bases, so git's recursive
  strategy gives stage 1 a *virtual* base that holds its own conflict markers, and merge_union's `json.loads` died.
  **Fixed in merge_union @ 47fdc185c** (tech seat). When stage 1 won't parse, it merges against the real merge
  bases instead:
  - a side equal to any base's version of a key counts as unchanged;
  - if both sides differ and each sits on a different base, ours is kept and the key is reported.
  - On big17 × ui it resolves to 612 shots with no duplicate ids. It reports 13 keys, and keeping ours is right
    for all 13:
    - 8 × `zone_wake_*`, whose scene `haluna_wake_dressing/` big16 deleted;
    - 5 × `shrine_s0*` `warm_shader_groups: true`.
  - The 10 `pending_baseline` and 5 `setup`/`settle_frames` rows where ui only carries an older base all take big17's.
  - test_merge_union 17/0, including a criss-cross repo whose stage 1 has markers; the new test fails on the old
    code with big17's JSONDecodeError.
  - **Lead: use this merge_union when you fold ui into big18.** Without it, shots.json stays conflicted.

### big17's tool-suite reds (gate.md: 4 units, red on big16 too), by owner
- **test_post_import** (tech seat, mine): its `KINDS` set lacked creatures' `crowd`. Fixed @ 96bd14658 (6/0).
- **test_freed_cast_lint** (my lint): a real hit in env-art-b's `game/vfx/ebbing/ebbing_motes.gd:168` (it casts a
  freed mourner). Filed **M3-HER-1161 (rendering, env-art-b)** with the 3-line patch, plus a KNOWN row so the unit
  is green; it passes on big17 with the row.
- **test_npc** (creatures): green on claude/creatures alone and red on the merged tree. Characters' new Act I
  villagers (`wright_child_a`) changed what the crowd generator must stay distinct from. Filed
  **M3-HER-1162 (character, creatures)**: regenerate the crowd once big17 lands.
- **test_screenshots** (`villager_shopkeeper_front` has no baseline): the Lead's baseline approval, not a code fix.

### SELF-RENDERED on the big17 trial tree (Pell's row + characters' model), 2026-10-29
- `ch09_corrow_rocks`, cropped and brightened: **Pell** (crest, staff, Kirru face) stands upright on the rock top,
  feet on the stone, at hero scale. He was a capsule before. `ch09_corrow_road`, `ch09_corrow_landing` and
  `slice_prologue_vigil_line` don't frame him closely; nothing wrong in them. Their drift against baselines comes
  from the batch (big16/17 art), not from this row. No baselines written.
- Audit on that tree with Pell's row: **5 items** (creatures 1, env-art 4 low); **integration-qa 0**. The
  Prologue's City/Vigils capsule clears too: it was Pell's vigil.
- After big17 lands, I drop Pell's stale KNOWN capsule rows from qa_known.json (corrow, corrow_night ×2,
  ossa_fen). The guard doesn't fail on stale rows, so nothing is red meanwhile.

MERGE-READY @ 47fdc185c (+ this log): everything above (M3-HER-1149 Pell row, M3-HER-1227, M3-C09-09, M3-ARC-1324,
trial_merge --prefold, merge_union's virtual base, test_post_import's crowd, freed-cast KNOWN for M3-HER-1161).

### Act I encounter-entry smoke on lead/gate-big17 (import + `--filter=qa_encounters`), 2026-10-29 ~19:20
- **Every Act I fight is entered, won and left clean: 1/0.** Its log held two `HalunaZone: no spawn ''` warnings
  that the guard skipped. That was a gap in the guard, not in the game: its `_first_spawn` reads `<zone>_layout.json`
  spawns, but Haluna's spawns are scene markers, so Haluna's fights were never returned to a real spawn. **Fixed in
  test_qa_encounters:** it falls back to the zone's `spawn_names()`, and now **fails** when a zone with `place_at`
  gets no spawn. Re-run on big17: 1/0, with no such warning.
- Every other error in the log is known: `refresh_bounce_passes` with a freed root (M3-HER-1124, PC rendering), plus
  exit-time leak lines.
- **M3-HER-1158 verified and in review:** ui's 503b99839 (in big17). The ch3 `battle_entry_probe` logs 0
  battle_result_panel errors (big15: ~930).
- LEAD-ASK: you routed big17's test_post_import red to creatures. **It's already fixed here @ 96bd14658** (the
  python test's `KINDS` lacked `crowd`; I fixed the Godot twin for big16). Please tell creatures to skip it.
  test_npc does need creatures (M3-HER-1162 here: regenerate the crowd on the merged tree). The freed-cast hit is
  env-art-b's, M3-HER-1161, with the patch and a KNOWN row here.

### Reviews and routing, 2026-10-29 ~19:00–19:30
- **Done (qa reviewer):**
  - M3-HER-1141 (env-art-b) and M3-HER-1143 (creatures-b): the merged-tree audit lists none for either.
  - M3-AUD-861 (audio): on big17 all 5 named blockers are cleared.
- **Done (architect reviewer):**
  - M3-ENV-715 (Ashcrown's flights);
  - M3-ARC-1216's last box: env-art's M3-ENV-1303 placed the 24 HeroStairs rows, and test_ch05_ashcrown_walkable
    passes 5/0;
  - a note on M3-C05-1215 (act1-chapters) that its blocker is gone.
- **Changes requested: M3-C04-1226 (act1-chapters).** test_ch04_zones hard-codes Haluna's 8 camera volumes, and
  Haluna has 10 since m2-slice's M2-FP-109 (B02, B11). The fix is to count haluna.tscn's own. This fails on my
  branch (big16 in), so expect it in big17's suite.
- **New, filed:**
  - **M3-HER-1163 (audio):** M3-BPR-1325's `battle_sfx.json` `vfx` rows give the Climb's three stair skills
    `status_apply`, which layers under the real sounds made for them. Fix: delete the 3 rows.
  - **M3-HER-1164 (cinematics):** GPU QA row 39, "Rhen walks Ch9 alone". Probed: Ch9's stage keeps `Actors/asha`
    and `Actors/toma` visible from load, so HeroFieldParty hides both followers (`staged`, by design). This is a
    staging call: they follow, or they wait on purpose. Both options are written up.
- Act I audit note: icons and faces are covered by UI's test_menu_glyphs and test_battle_portraits, and sounds by
  audio's audit. The stale "not audited: icons" line is gone.
- Pell's dialogue portrait: `pell_neutral.png` is on claude/ui, so it comes with the next batch. speakers.json's
  `portrait_*_placeholder` ids are dead data; DialogueBox reads HeroPortraits by speaker id.
- LEAD-ASK: audio isn't started, and M3-HER-1163 is a 3-row data fix in audio's `battle_sfx.json`. Start audio for
  it, or let me apply it (I'd rather not edit another track's file unasked).
- In flight: the full Godot suite on lead/gate-big17 in my container, for an early read and M3-HER-1130's leak list.

### The Lead's three asks (messages of 17:58, 19:04, 19:24), 2026-10-29 ~20:00
1. **Audit rows re-routed @ 07a2f41a7:** `tools/placeholder_audit.py` gains `ROUTES` (path and what regexes,
   owner, reason; first match wins), applied after the owner rules; test_placeholder_audit has a routing test.
   - The Prologue's City/Vigils capsule → **characters** (Pell's vigil; slice-polish puts him on his mark);
   - `tamsule_bell/reefball_drop_proxy.glb` and `materials/tb_drop_proxy.tres` → **env-art-b** (M3-RND-26).
   - Inventory re-generated on big17 + claude/ui (full scan): **9 items**: characters 1, creatures 1, env-art 2,
     env-art-b 2, integration-qa 3 (Pell's capsules, which clear with this branch's Pell row). Note: with Pell's
     row, the Prologue vigil clears as well (it's his `vigil_pell`), so characters' row should close by itself.
2. **taskboard --check fails on a duplicate task id @ 8266adbf5** (`duplicate_ids`, tools/tests/test_taskboard 2/0).
   **On lead/gate-big17 the only duplicate is M3-CRE-627:**
   - `M3-CRE-627-act2-regulars-ch10-11.md` (character, blocked, creatures);
   - `M3-CRE-627-virel-field-body.md` (character, todo, filed by act1-chapters' M3-CIN-1217; the one being
     renamed to M3-CRE-700).
   Until that rename lands, `--check` is red on every tree that carries both, mine included. That's intended.
3. **test_hero_field_snaps: no fix needed; it's ui's head, not the code.**
   - Green on lead/gate-big17 (2/0), on this branch's head (2/0), and on **big17 + claude/ui merged** (2/0, the tree
     big18 builds).
   - It fails only on claude/ui's own head a9ae00b7 (haluna_wake: rhen 38 snaps, drowned_choir 2). That head mixes
     newer hero-motion files, which came in through its merge of characters, with pre-big16 `field_camera_director.gd`,
     `camera_shot.gd` and the old haluna_wake layout, because integration doesn't carry big16 yet.
   - It goes away when big17 lands on integration and ui merges it.
- Also: the same big17 × ui merge went through merge_union's new virtual-base path for real (shots.json resolved).
- **Lost to a container restart (~19:35, memory: three Godots at once):** my full-suite run on big17 and the
  inventory re-run. The inventory is redone above. The full suite is NOT re-run; the gate session has it. From now on
  I run one Godot at a time.
MERGE-READY @ (this commit): ROUTES, the taskboard duplicate check, the inventory.

### TRIAL MERGE, 2026-10-29 ~20:00 (prefold lead/gate-big17)
TRIAL MERGE @ integration ccf44ba4 + lead/gate-big17 be74f9a0: env-art 8d48173e, env-art-b c28b7b01,
creatures 02d0280e, creatures-b 4d0150e3, characters 3b55279e, ui a9ae00b7, battle-presentation b1316ebb,
act1-chapters a9c44edc, m2-slice 530b8551, audio 1cb9654d, hero-integration 4059ada9
- **trial_merge now runs this checkout's merge_union** (it ran the tree's own copy, which is big17's, without the
  virtual-base fix). With it, **every `shots.json` clash resolves** (creatures, ui).
- `pc-gpu.md` (characters, ui, battle-presentation, act1-chapters, mine): take integration's. Lead.
- **Mine, fixed @ 32dd72a34:** `tools/tests/test_post_import.py` (creatures added the same `crowd` row, wrapped
  differently: I took theirs) and `M3-C05-1215`'s task file (act1-chapters moved it to review itself: took theirs).
- **env-art:** `M3-ENV-750` task file again. Take env-art's (done + review line).
- **env-art-b:** `docs/kb/ownership.md`. Resolve by hand. merge_union doesn't union it, because line union would keep
  both old and new versions of an edited row. TRACK-RULES' list says it does; that line is wrong, so resolve it by hand.
- **characters (M3-CHR-519, casting named NPCs as themselves) vs the layout owners.** The layouts were written once
  by the generators, so hand edits are fine. Resolver: whoever merges second keeps the layout owner's side and
  re-applies characters' one-field `cast` changes. Those are `tender: reed→tender`, `fenn: fisher→fenn`, and the
  like in 9 layouts.
  - `ch01/oruvel/oruvel_layout.json` vs env-art-b and creatures;
  - `ch05/ashcrown/ashcrown_layout.json` vs act1-chapters (M3-CIN-1220 cameras) and env-art-b (M3-ENV-1325);
  - `ch08/coilspire/coilspire_layout.json` vs act1-chapters (M3-CRE-627 Virel).
- **act1-chapters vs env-art-b: `tools/act1/ch08_coilspire_dressing.py`** (Virel's chamber vs M3-ENV-1326's zone looks).
  A generator, so act1-chapters resolves it and re-runs it. Also the `M3-ENV-744` task file: take act1-chapters'.

### Reviews, 2026-10-29 ~20:30 (on lead/gate-big17, one Godot at a time)
- **42 M3-AUD tasks → done** (qa reviewer). Every criterion is ticked. Godot `--filter=audio` 175/0, the tools
  audio suites 50/0, and the Act I audio audit is clean apart from M3-HER-1163. Review lines say it's technical
  only; the listening is the human's. M3-AUD-802 notes the separate M3-HER-1150. **M3-AUD-19** stays in review
  (its one box is unticked).
- **M3-UI-211:** verified (battle_portraits 3/0, menu_glyphs 3/0, hero_portraits 9/0, creature_portraits 4/0); Kerrid's
  box ticked. It stays in review for the Inquisitor's bestiary picture (none on big17) and the Lead's baselines.

### TRIAL MERGE, 2026-10-29 ~21:00 (prefold lead/gate-big17 @ 1bdaea53; big17 isn't on integration yet)
Heads: env-art d63eeea3, env-art-b 0e9db81d, creatures df6b8e2d, creatures-b 4d0150e3, characters 9fe30416,
ui b2137061, battle-presentation b1316ebb, act1-chapters e7b065b4, m2-slice 8aa6f6a6, audio 1cb9654d,
hero-integration 78e9df9c. shots.json resolves everywhere. pc-gpu.md: take integration's.
- **NEW, mine to call: `tests/unit/test_hero_field_actor.gd`, hero-integration vs characters.** characters
  5667eedbd added Pell's field row too: the same numbers, walk 1.27 and run 3.13, so `hero_motion.json` merges clean.
  It also edited the alias test. **Resolve by taking hero-integration's version.** characters' version asserts
  that `vigil_sefir` "has no field row" and keeps its capsule, but Sefir has had a row and a model since M3-HER-1225
  (both are on big17), so it fails on the merged tree. Mine handles Pell's model being there or not, and uses
  `vigil_neme`, an actor with no row.
- **NEW:** `tests/unit/test_zone_cast.gd` (creatures vs env-art-b); `tests/integration/test_fp_prologue.gd`
  (characters vs env-art-b and creatures; characters' edit is the Prologue vigil now having Pell's body);
  `oruvel_underway_layout.json` (act1-chapters vs everyone, generated: act1-chapters re-runs its generator).
- As at 20:00: M3-ENV-750 (take env-art's), ownership.md (by hand), the characters `cast` edits in 9 layouts,
  ch08_coilspire_dressing.py and M3-ENV-744 (act1-chapters).

### Full Godot suite on lead/gate-big17 (be74f9a0 = 1a986abf + docs), in my container, 2026-10-29 ~21:15
**3241 run, 5 failed (6 FAILURE lines), 59 tests leave nodes.** By owner:
- **test_cutscene_vfx_hosts.gd failed to load (mine, M3-ARC-1326). FIXED @ 791495cfa.** 93c1aa2df replaced the
  `CutsceneMotes` placeholder with CutsceneVfx's GlimmerField, so the test now counts the sequencer's own
  `Vfx_*` field. 4/0.
- **test_ch04_zones::test_the_wakes_field_camera_is_halunas** (act1-chapters): expects 8 Haluna volumes, there are 10
  (M2-FP-109). Already requested on M3-C04-1226.
- **test_dialogue_box::test_every_act1_speaker_with_a_model_has_a_portrait** (ui): Pell has a model on big17 and no
  portrait. `pell_*.png` is on claude/ui's newer head, so folding ui's head in fixes it.
- **test_iskarra_city::test_the_city_instances_its_pieces_with_kit_materials** (env-art): "VigilLights has meshes".
  env-art's own M3-ENV-724 added a `VigilLights` group that holds only lights. The test should skip a light-only
  group.
- **test_zone_cast::test_a_cast_actor_shows_its_model_and_idles_out_of_step** (creatures): "the fisher idles" and
  "out of step". The same file clashes creatures vs env-art-b in the 21:00 trial, so check it after that merge.
- **Leaks (M3-HER-1130's list refreshed):** ui-menus 48 (act_card, objective_hud, shrine_travel and
  shrine_services, interact and hold prompts, dialogue_assist, area_title_card and more), battle-presentation 9
  (fighter_actor, battle_controller, battle_boss_vfx), creatures-b 1, env-art 1. Down from the 10-28 list; creatures'
  and act1-chapters' are gone.
- Not run here: coverage, screenshots (the gate session has them).

MERGE-READY @ 37adb2fb3 (+ this log):
- **M3-CRB-012 → review (creatures-b's request):** the audit finds a Vowbound's body in its creatures.json row
  (`vowbound: true` + `scene`), the game's own rule. New test; test_placeholder_audit OK.
- **M2-HER-1128 → review (slice-polish reviews):** test_fp_thread arrives after the tideline win as the game does
  (`story.begin()`), so B02 plays and `ch02_ate_at_nemes` is set before the shrine save. qa_known `unraised` is empty
  now. fp_thread 2/0, qa_threads 1/0.
- **M3-ARC-1326's test fix** (791495cfa) and the M3-HER-1130 leak list are above.

### PC-QUEUE
- **M1-QA-09** (qa, todo): the next Asha real-GPU re-check (grief) with the QA-08 rigour fixes. It needs the PC's GPU
  and waits on M1-RND-24 and M1-CHR-12. Not runnable in a cloud container.

### big17 is on integration (96222b301, 22:00); merged here @ 198230aed
- pc-gpu.md: took integration's. Tools suites green (trial_merge, merge_union, taskboard, placeholder_audit,
  post_import, freed_cast_lint, dlgc). validate_data 0/0. taskboard --check shows only M3-CRE-627's duplicate
  (act1-chapters' rename pending).

### TRIAL MERGE, 2026-10-29 ~22:10 @ integration 502f6999 (big17 in; no prefold)
env-art d63eeea3, env-art-b 0e9db81d, creatures 93829b74, creatures-b 4d0150e3, characters a5b60821, ui a8df61a8,
battle-presentation 8da23b91, act1-chapters 72254f9f, m2-slice 7e0bba54, audio 1cb9654d, hero-integration 294d98de.
The same clashes as at 21:00, with the same resolvers, now against integration itself:
- M3-ENV-750 task file (env-art: take env-art's);
- ownership.md (env-art-b: by hand);
- test_zone_cast.gd (creatures vs env-art-b);
- characters' `cast` edits in oruvel, ashcrown and coilspire layouts, plus test_fp_prologue.gd;
- act1-chapters' generated layouts, ch08_coilspire_dressing.py and M3-ENV-744;
- **test_hero_field_actor.gd: take hero-integration's** (characters' assumes Sefir has no field row).
- shots.json resolves everywhere (merge_union's virtual-base path).

MERGE-READY @ (this commit), after big17 landed:
- **test_qa_capsules is a ratchet now:** in each zone it scans, a KNOWN capsule row whose actor has its body fails
  ("drop it from qa_known.json"), so a stale row can't hide a capsule that comes back. **115 stale rows dropped.**
  big17 gave almost every villager, NPC and vigil a body. Only `corrow.tscn: figure` (creatures, the stranger on
  the wall) stays known. `--filter=qa_` 13/0.
- **Act I inventory on integration 502f6999 (big17) + this branch: 5 items**, all low except one: creatures 1 high
  (Ch8's figure), env-art 2 low and env-art-b 2 low (placeholder-named kit files). **integration-qa 0, characters
  0:** Pell's capsules and the Prologue's vigil are gone.
- **M3-HER-1149 → review (reviewer: lead):** every box ticked.
- Hero motion, followers and the camera on integration (big17) + this branch: `--filter=hero_` 113/0,
  `--filter=camera` 62/0. Pell's model is in, so the alias test now runs its with-model branch.

### TRIAL MERGE, 2026-10-29 ~23:00 @ integration 502f6999
env-art d63eeea3, env-art-b cc7ab368, creatures 93829b74, creatures-b 4d0150e3, characters fe626d0e, ui a8df61a8,
battle-presentation cdfe126a, act1-chapters 175d2b5e, m2-slice 7e0bba54, audio 1cb9654d, hero-integration e287b61a
- **NEW: Pell's portraits, ui vs characters (binary).** Both baked `assets/ui/portraits/heroes/pell_*.png` (5 + .import):
  ui at 17:37 (fa8ab4424, "framed closer for the Kirru head"), characters at 22:15 (e374376be, for big17's
  test_dialogue_box red). Also `tools/portraits/portraits.json` and `tests/unit/test_hero_portraits.gd` (ui vs
  creatures vs characters). **Take ui's:** `assets/ui/portraits/**` and `tools/portraits/**` are ui's (ownership.md).
  Characters' bake duplicates work ui already did.
- **Mine, cleared @ 70793031a:** env-art-b fast-tracked the same test_cutscene_vfx_hosts fix, so I took theirs (4/0).
  test_hero_field_actor.gd vs characters is unchanged: take hero-integration's.
- Unchanged:
  - M3-ENV-750 (take env-art's);
  - test_zone_cast.gd (creatures vs the merged tree);
  - act1-chapters' generated layouts, coilspire dressing.py and M3-ENV-744, with characters' `cast` edits
    (oruvel, ashcrown, coilspire).
- env-art-b's ownership.md clash is gone.

## The Lead's 23:10 list (big18)
### 1. Act I inventory on lead/gate-big18 @ d00d3284 (full: import + runtime scan): **2 items, both low**
- env-art-b (M3-HER-1141): `tamsule_bell/materials/tb_drop_proxy.tres` and `tamsule_bell/reefball_drop_proxy.glb`,
  both named as placeholders (names only, nothing on screen). Those are the only rows left in all of Act I.
- creatures' figure and env-art's banyan/windbreak files have cleared. **M3-HER-1140 (env-art) and M3-HER-1142
  (creatures) → done** (qa review). M3-HER-1144 (characters) has a note: nothing left. Inventory @ f9e9540c8.

### 3. TRIAL MERGE onto lead/gate-big18 (what big19 hits), 2026-10-29 ~23:50
Heads: env-art d63eeea3, env-art-b d5660abb, creatures 93829b74, creatures-b 4d0150e3, characters fe626d0e,
ui dae73fd8, battle-presentation cdfe126a, act1-chapters 175d2b5e, m2-slice 9d9e9653, audio 1cb9654d,
hero-integration f9e9540c. The other claude/* branches are retired (ze8rrn, 423ixt, menus, gate-runner-a/b,
first-playable).
- **Only characters (fe626d0e) clashes, 13 files.** Resolver: the Lead, taking big18's side for all of them.
  - Pell's 5 portraits (+ .import), `tools/portraits/portraits.json`, `tests/unit/test_hero_portraits.gd`: big18
    already has ui's bake. ui owns `assets/ui/portraits/**` and `tools/portraits/**`; characters' 22:15 re-bake
    duplicates it.
  - `tests/integration/test_fp_prologue.gd`: big18's (creatures') version asserts that Pell's and Liss's vigil
    capsules go, which is right now that both have bodies.
- Mine (M3-HER-1140/1142 task files) cleared @ 5e285a886. env-art-b and ui merge clean (union only). Everyone else
  merges clean.

### 2. The Act I headless smoke on lead/gate-big18 @ d00d3284, 2026-10-30 ~00:40 (one Godot at a time)
Boot past the title (600 frames), plus the guards and suites that play the game:
- `qa_` (every chapter thread start to end with a save round trip at each shrine, every Act I encounter
  entered/won/left, capsules, party spawns, field camera, flag reach);
- `fp_` (title → New Game → Prologue → slice → Ch3);
- `title`, `save_`, `boot_card`.
**Results: boot clean · qa_ 12/13 · fp_ 30/0 · title 40/0 · save_ 149/0 · boot_card 27/0.**
- **The one red, fixed here @ dc88d2aee:** `test_qa_threads` failed on 4 "CutsceneGrade: no grade 'ch03' / 'ch03_steps' /
  'ch03_boss' / 'ch03_shrine_int' in the zones' grade tables" warnings in the first-playable thread. They're new in
  big18 from slice-polish's M2-FP-120, which makes a grade with no row a **soft failure by design**. The colour
  script names grades nobody has built yet; those are M3-ENV-106 (environment, todo), and test_cutscene_directives
  lists them. The guard now knows the pattern under M3-ENV-106 and is 1/0 on big18 (with M2-HER-1128's
  test_fp_thread). **Owner of the real work: environment, M3-ENV-106** (Ch3's four grades).
- Every error and warning in the run, by owner:
  - **Boot:** one `ShaderPrewarm: transition hitch over budget (301 ms, budget 50)`. On the headless dummy renderer
    the timing is meaningless → PC-QUEUE (real GPU).
  - **`Parameter "material" is null` (material_get_instance_shader_parameters, dummy storage):** 56 here, 132 in
    big17's full suite. It fires whenever a node carrying instance shader parameters (the character shading) is freed
    under the headless dummy renderer, whose material storage is a stub (even freeing a bare hero glb in
    test_hero_field_actor does it). It's headless noise rather than a game error → PC-QUEUE: confirm a real-GPU run
    logs none (rendering, if it does).
  - **The save suites' ERRORs and WARNINGs** (corrupt slots, broken tables, negative counts, unknown equipment,
    "autosave failed: Unconfigured"): every one is a test feeding bad data on purpose (test_save_recovery,
    test_save_data_tables, test_save_item_tables). Nothing to route.
  - **Leaks:** `test_area_title_card.gd` ×3 (ui-menus; already in M3-HER-1130's list).
- Not covered by a headless run: what the player sees and hears. Item 4's scripted walk stills cover the hero side.

### PC-QUEUE (added)
- ShaderPrewarm's transition hitch on boot (301 ms in headless; measure on the GPU).
- `Parameter "material" is null` on freeing a character mesh: confirm a real-GPU run logs none.

### 4. Hero, follower and camera audit (2026-10-30 ~01:00), @ d1a2a3674
New guard **tests/integration/test_qa_walk_audit.gd** (routes in `qa_walk_routes.json`). It walks the real party
with the real FieldController, a stick toward each waypoint through the live camera, with HeroStairs, HeroFieldParty
and every body stepped as in play. Routes:
- Haluna's lane (narrow, props);
- Ashcrown's 48° flying stair, up and down;
- Coilspire's spiral (1 m ramps, the gates open).
It fails on stuck, follower-in-geometry, camera-in-geometry, or leader-hidden runs over 30 frames. It reports
run-up, stop, vertical jumps, airborne frames, foot slide per hero, follower gaps and catch-ups. Two harness
mistakes cost me a false "stuck at the stair head": HeroStairs not stepped, and its deferred flight build. The guard
now does both as the game does.
- **Fixed, sticky:** a full-stick run on a steep flight was capped at the walk's 1 m/s along the slope, so the
  flying stair took **64 s**. `stairs.json` gains `slope_run_speed_mps` 1.9 (a stair run; walk stays 1.0) and the
  climb now takes **~35 s**. Followers are capped at the run speed so they keep pace. test_hero_stairs has a new case,
  a run climbs faster than a walk; 8/0.
- **Fixed, floaty:** running feet slid 16-28%. The field run is 3.6 m/s, the run clips measure 1.8-2.35, and the gait
  sped the run up at most 1.5x. Followers also sprinted to 5.4 m/s to close gaps. Now `gait.max_playback_scale` 1.8
  and `followers.max_speed_mps` 4.4: **0% foot slide for every hero on every route**, no catch-up teleports, max gap
  3.1 m. The real fix is a faster authored run, **M3-HER-1165 (character)**: Kerrid still needs 2.0x, and a leg cycle
  at 1.8x may read as scurrying.
- **Clean:** no follower clips into geometry, the camera is never inside geometry or hiding the leader, the stairs are
  smooth (max 0.044 m a frame), a run takes 0.38 s to reach and stops in 0.5 m.
- **Found, not mine to fix: followers hidden by standing stage actors in 12 Act I zones** (M3-HER-1164 widened; probe
  above): Haluna, the ferry, the wake, Ashcrown, Pemakar, Brine Shoals, Tamsule, the Bell galleries, Coilspire,
  Corrow, Corrow night.
- LEAD-ASK: Should the follower win in free play everywhere? The stage actor would hide until a scene cues it.
  That's a one-place change in HeroFieldParty, but it also hides talk-prompt actors such as Toma's Shield-Mate on
  Ch9's strand. My default: no rule change; act1-chapters stages each zone (M3-HER-1164).
- Stills: the rig (tools/hero/walk_stills.tscn) is written but not yet rendered or viewed, so it's not committed.
- Checks: hero_ 114/0, hero_stairs 8/0, hero_followers 13/0, ch05_ashcrown_walkable 5/0, qa_walk_audit 1/0.
  The full `qa_` was cut off by a timeout; it's re-running.

### The Lead's 00:20 items (ADR 0203), @ 150670d1a
- **placeholder_audit `--act 2`:** Ch10-Ch16 into docs/kb/qa/act2_inventory.md, **report-only** (`--check` never
  fails for Act II), with the title and lead-in saying so. Act I stays the default. Rows with no chapter (shared asset
  names) stay on Act I's list. scan.gd now loads every chapter's scene steps, and Python keeps the act.
  test_placeholder_audit 14/0, including 3 new scope tests.
  - The static half on this branch already lists 20 Act II items (act1-chapters 10, creatures 10).
  - The full inventory (runtime scan) is next, on big18.
- **tools/dev/lead/act1_gate_check.py:** ADR 0203 criteria 1-2, PASS/FAIL each, exit 0 only when both pass.
  1. The Act I audit with the runtime scan has zero items (`--static-only` never PASSes).
  2. qa_threads, qa_encounters, fp_ and save_ pass with zero SCRIPT ERRORs, plus the continuous title → Ch9 → title
     test found by name (`tests/integration/test_*continuous*.gd`).
  - **Criterion 2 FAILs until M3-CIN-1233's continuous-path test exists** (act1-chapters' finding: the Prologue skips
    Ch1, and the slice's end card returns to the title).
  - test_act1_gate_check 3/0. Run it from a batch worktree root: `python3 tools/dev/lead/act1_gate_check.py`.

MERGE-READY @ e83e411ed (+ this log): the walk audit and its fixes (d1a2a3674), the ADR 0203 tools (150670d1a), and
the **Act II inventory** (report-only, lead/gate-big18, full scan): **34 items, all high**:
- 13 greybox zones, Ch10-Ch16: ossa_fen, reedhollow, lowlight, sunken_vey, cloudloom, keth_pass, quellan, ansedra,
  ansedra_lacquer_court, lamp_archive, sanctum, open_sea, drowned_choir, pale_rim;
- 10 Act II foes still primitive stand-ins (fen_leech, root_crab, tannin_archer, gallery_ray, rime_urchin, cord_moth,
  ridge_lynx, scree_crawler, glass_skate, rim_crawler);
- 10 Act II encounters with no arena of their own.
Owners follow the Act I split until act2_tracks.md's ownership lands: env-art-b 14, act1-chapters 10, creatures 10.
- Checks: `--filter=qa_` 14/0 on this branch (the walk audit included), hero_ 114/0, tools tests (placeholder_audit
  14/0, act1_gate_check 3/0, taskboard, merge_union, trial_merge) green, gdlint/gdformat clean, validate_data 0/0.
- Running: act1_gate_check.py on lead/gate-big18 (the Lead's first reading of criteria 1-2).

### act1_gate_check.py on lead/gate-big18 @ d00d3284 (the first reading of ADR 0203 criteria 1-2), 2026-10-30
- **1. Audit: FAIL.** 2 items, both low: env-art-b's `tb_drop_proxy.tres` and `reefball_drop_proxy.glb` (names only;
  M3-HER-1141).
- **2. Playthrough: FAIL**, for two reasons:
  - the continuous title → Ch9 → title test doesn't exist yet (M3-CIN-1233, slice-polish / act1-chapters);
  - qa_threads fails on 5 `CutsceneGrade: no grade …` warnings (ch02 in the Ch1 thread, plus ch03, ch03_steps,
    ch03_boss and ch03_shrine_int in the slice). That's **already fixed on this branch @ dc88d2aee** (the known
    pattern, M3-ENV-106), so it clears when this head is folded in.
  - The rest pass with zero SCRIPT ERRORs: qa_encounters 1/0, fp_ 30/0, save_ 149/0.
- So with this branch folded in, the remaining Act I gate work for criteria 1-2 is:
  - env-art-b renames or replaces the two drop proxies;
  - M3-CIN-1233 lands its flow fix and the continuous test.

### 4, continued: stills from the scripted walks, and a camera fix (2026-10-30 ~03:00), @ b07d5bf35
- **New tool: `tools/hero/walk_stills.tscn`.** It renders any route of qa_walk_routes.json with the audit's own
  walker: `godot-render --path . --resolution 960x540 res://tools/hero/walk_stills.tscn -- --route=<id> --every=<n>
  --out=<dir>`. It simulates between stills, so a 2,000-frame climb renders in minutes. Viewed:
  - **Haluna's lane:** on the beach and down the lane, the camera rides behind and above, all three in frame,
    nothing clipping. At the stop by Neme's table, Toma's shield fills the left third of the frame: that's
    **M3-HER-1160** (m2-slice's B02 close volume covers the Village arrival), already routed.
  - **Ashcrown's flying stair:** Rhen climbs with his feet on the steps, framed from above, and stands on tier 6 at
    the top. He's alone, because the followers are staged (M3-HER-1164).
  - **Coilspire's spiral: FOUND and FIXED.** Under Tier1 and Tier2 (PAN_FOLLOW shots looking down the well), Rhen
    climbed out of the frame: **215 frames (3.6 s) out of frame**. PAN_FOLLOW's pan is capped (`max_pan_deg`) and
    nothing kept the player in frame. My audit had only checked whether a wall hid him, not whether he was in the
    frustum.
    - **FieldCameraDirector.keep_in_frame:** after the capped pan, if the leader is outside `keep_in_frame_share`
      (0.5) of the frame's half angles, the aim turns just enough to hold him. The limits are vertical from the fov
      and horizontal from `keep_in_frame_aspect` (16:9), so a composition with him on a third stays as authored.
    - Coilspire now loses him for **0 frames**, and the re-rendered stills show him whole, head included, mid-climb.
    - **The audit now fails on the leader out of frame for more than 30 frames in a row.**
  - Screenshots it could move, self-rendered: field_court_pan (PAN_FOLLOW) PASS 0.00025, field_lane_fixed PASS,
    field_causeway_dolly PASS. save_shrine_field FAILs at rmse 0.10456 **identically with keep_in_frame switched
    off**, so it was already drifting: a gate item, not this change.
- Checks:
  - camera 63/0 (test_camera_director: the new keep_in_frame unit test plus the pan test's rule);
  - qa_field_camera 2/0, qa_walk_audit 1/0 (every route 0 frames out of frame);
  - gdlint/gdformat clean, validate_data 0/0.
MERGE-READY @ b07d5bf35 (+ this log).

### The PC's GPU QA pass 3 rows for me (21, 37, 38, 50), 2026-10-30 ~05:00
Checked on lead/gate-big18 plus this branch, with **spawn stills** (`walk_stills.tscn -- --scene=… --spawn=…`, the
party arriving and standing 60 frames, and `--unstage` to show the followers where a zone stages them), the walk
audit, and probes.
- **Row 37, the causeway (FIXED):**
  - Encounter and AfterHarrier: the close camera behind the arrival had Toma 1.5 m from the lens filling a third
    of the frame. Now **followers never stand within `camera_near_m` (3 m) of the lens.** At a spawn they're laid
    out clear of it, and while standing they **flank** the leader instead of walking back into the foreground
    (`off_lens`).
  - BeforeHarrier: the FIXED shot C07 faced away and showed no one. Now a **FIXED shot that would lose the leader
    entirely turns to hold him** (`keep_in_frame_fixed_share` 0.95; a locked frame with him anywhere in it is never
    moved).
  - Stills after: Encounter shows Rhen centred and Asha well off to the side; BeforeHarrier shows Rhen in frame.
  - Tests: test_hero_followers' new no-follower-in-the-lens test (laid out and after 120 frames), and
    test_camera_director's FIXED safety-net test.
- **Row 38, Coilspire (FIXED on the camera side; the spawn is env-art-b's):**
  - SpireBase and Tier2 read fine (keep_in_frame from earlier).
  - **Tier4: the spawn stands inside the spiral's step mass.** Rays from his chest hit `coilspire_tiers` within
    0.02-0.13 m in every direction, and 0.51 m straight up, so no camera can see him clearly. Evidence is on
    **M3-HER-1157 (environment):** move the spawn.
  - The camera no longer makes it worse. Deep occlusion (clear stretch < `min_view_m` 1.8) now **cranes**: straight
    up to a clear height, clear of solids (`crane_clear_m`), looking down. Under a ceiling it tries **a ring of side
    spots** (`crane_ring_m` 2.5/1.9, `crane_ring_up_m` 0.6, 12 turns). When nothing clears, it pulls in as before
    while `min_distance_m` is free, and **keeps the shot's own pose when not even that is** (Tier4).
  - The Tier4 still now shows him down the shaft framed by the valve wheels: the head-cam is gone.
  - Encounter: Rhen is in frame (keep_in_frame), but the GallerySouth shot looks out over empty sea. The shot's
    direction is **M3-HER-1159 (act1-chapters)**.
- **Row 50, Toma sunk at Ashcrown's crown: NOT REPRODUCED.** At the Crown spawn (with `--unstage`, all three
  showing) everyone stands on the 42 m floor (still and probe). Climbing the flying stair both ways with the
  followers visible, the walk audit's new **sunk** check (feet > 0.3 m under the floor or the stair profile) gives
  0 frames. The likely cause was the pre-fix stair handling. If the PC sees it again, the exact story state would
  help.
- **Row 21: re-checked by stills** of the start after the beach and the Village spawn: Rhen and the party in frame.
  The PC couldn't reach it in pass 3 (New Game runs into the beach cutscene), so a hand playthrough confirms it.
- The walk audit now walks the Ashcrown and Coilspire routes **with the followers visible** (`unstage`) and fails
  on a follower **sunk** in the floor or **inside the body ahead** (OVERLAP_M 0.4) for more than 30 frames. All
  routes pass. On the way down the flying stair, Toma closes to 0.13 m of Asha for 9 frames at the start (well
  under the limit).
- **ADR 0205:** `act1_gate_check.py` now names ADR 0205 §3 as its criteria (2 s hitches). Its two checks are unchanged.
- **Row 44 / the PC-QUEUE `material is null`:** creatures' storm figure (row 44), so not mine. Done on my side.
- Checks: camera 64/0, camera_director 49/0, hero_ 115/0, qa_field_camera 2/0, qa_party 3/0, qa_walk_audit 1/0,
  gdlint/gdformat clean, validate_data 0/0.
MERGE-READY @ (this commit).

### Act II starts here (ADR 0205: no open Act I row of mine), 2026-10-30 ~05:30
- **The walk audit covers Act II**, report-only (`report_only` routes print `ACT II REPORT` lines, while Act I routes
  still fail). Party Rhen, Ysolde and Kerrid (per-route `party`); ramps by exact id.
  - **Keth Pass** (Ch12, three 4 m flights PassFoot → FromQuellan): walks clean, smooth (max dy 0.030/frame), no
    follower clipping or sinking. The camera is inside geometry for 2 frames.
  - **Lowlight** (Ch11, two 3 m flights down to the Sanctum): walks clean. A collider hides the leader from the
    camera for 39 frames on the descent, and the camera is inside geometry for 1 frame.
  - **Cloudloom** (Ch12, the hall stair): clean, nothing reported.
  - **Kerrid's feet slide 25-26% at the run** (run clip 1.8 m/s needs 2.0x, cap 1.8x), and Ysolde's 14% while
    catching up. **M3-HER-1165 (character)**, a faster authored run, is the fix. Act II leans on Kerrid, so it
    matters more now.
  - The zones are still greybox. The camera items are re-checked against the kits when env-art-b builds them (the
    routes stay in the audit). The audit judges "hidden" by physics rays and the director by drawn meshes, so
    Lowlight's 39 frames may be an invisible collider.
- Act II party bodies: Ysolde, Kerrid, Liss, Pell and Sefir all have field rows and models (spawn guards
  qa_party_spawns and qa_field_camera already scan every field zone, Act II's too, green).
- Next (Act II, my lane):
  1. the followers-hidden-by-standing-actors rule (M3-HER-1164) as Act II zones get staged;
  2. walk-audit routes for each Act II kit as it lands;
  3. the Act II inventory refresh per batch (`placeholder_audit.py --act 2 --write`).
MERGE-READY @ (this commit).

### Lead's Act I fast-track (10-30 03:44): M3-CIN-1251 and the spawn-camera rows 24, 25/47
- **M3-CIN-1251 (review: cinematics / act1-chapters) @ 1da21c732:** the field camera now leaves a volume for the hub
  shot. Outside every volume with a volume still active, `update()` blends to `initial_shot` (its own blend_sec or
  hard_cut, else default_blend_sec) and `snap()` cuts to it. A zone with no hub shot keeps the last volume's shot,
  as before. New test `test_leaving_every_volume_returns_to_the_hub_shot`. `qa_field_camera` is 2/0 **with
  act1-chapters' held c9da92f3f (the Harbour and Weir volumes) applied on top**.
  - **For act1-chapters:** re-apply GPU QA row 49's camera side (c9da92f3f) once this lands.
- **Rows 24 and 25/47, the spawn cameras (game/world/**, mine):** reproduced in stills. There were three causes:
  - **DockShore (the Ch4 wake):** the wake reuses Ch2 Haluna's volumes, and the spawn stands 1.0 m from Ch2's
    pan-follow shot H04. **Fix:** with nothing between them, a free-play camera nearer his chest than
    `occlusion.standoff_m` (2.6) backs off along its own line to 2.6 m. There's no jump, because at 2.6 m it is the
    shot's own place. If that line is blocked, it goes to the ring direction with the most room. Now 2.6 m: a full
    shot of Rhen on the jetty.
  - **FerryAft:** the spawn is inside the deckhouse (3.5 × 3.8 m, roof 2.1 m). The pull-in took the camera 9.45 m in,
    to 1.1 m from him, because the crane can't clear under the roof. **Fix:** when the crane fails, `widest_view()`
    tries the ring at crane_ring_up_m and then at chest height, and takes the direction with the most room. Now
    2.6 m: Rhen full-length in the cabin.
  - **FeastEdge, InkLamp and WallDawn:** the greybox hub orbit looked down at 33° from 8.9 m. **Fix:**
    `orbit.max_pitch_deg` 24 (`clamp_pitch`: swung down round the aim point, same distance and heading). This
    affects **every greybox zone's hub orbit**, so the Lead's full manifest may show drift on free-play field
    shots. Authored framings are untouched; scripted shots never get occlusion.
  - The party at the feast is still small at 8.9 m: the orbit's distance is the greybox default. A tighter
    feast shot is a camera volume, **act1-chapters'** (the wake's camera_volumes).
- **The guard:** `test_qa_field_camera` now also fails on a camera **in his face** (under 1.5 m from his chest) and
  on a director-computed pitch (orbit or follow) **steeper than 55°**. Authored looks down a stairwell, like
  Coilspire's Tier1 at −74°, belong to their authors. Against the old director it fails at exactly FerryAft (1.09 m)
  and DockShore (1.00 m). New unit tests: `test_clamp_pitch_swings_a_steep_orbit_down` and
  `test_a_shot_in_his_face_backs_off_to_the_standoff`.
- `tools/hero/walk_stills.gd` prints the pose with each still: the shot, its volume and mode, the authored position,
  the pull, the camera, the pitch, and the distance to the chest.
- Row 47's black landing pier at night is lighting: env-art's, not the camera.
- **A follower fix, found on the merged tree:** `test_no_follower_is_laid_out_in_front_of_the_lens` went red after
  integration's merge. My party code hadn't changed, and I didn't find which merged change exposed it. With the camera
  1.5 m behind Rhen, both flank spots were still inside `camera_near_m`, so `off_lens` gave up and Asha walked back to
  0.31 m from the lens. It now also tries the spot beyond him, away from the lens, and otherwise takes the unblocked
  spot farthest from it. hero_followers 14/0.
- Checks on the final tree:
  - Godot suites: camera 69/0 (qa_field_camera included), hero_ 115/0, qa_party 3/0, qa_walk_audit 1/0, fp_ 30/0,
    zone_cast 5/0.
  - Static checks: gdlint and gdformat clean, validate_data 0/0, taskboard OK.
  - Screenshots: none self-rendered. Most of the Ch4 wake and ferry shots use fixed preview cameras, which this
    change doesn't touch. **The hub-orbit clamp can drift any shot taken through the field camera's orbit in free
    play**, so that needs the Lead's full manifest.
MERGE-READY @ (this commit).
- **Trial merge @ integration 8de373e5 (all 11 heads):** my only conflict is
  `docs/kb/tasks/M3/M3-CIN-1251-camera-returns-to-the-orbit.md` (both act1-chapters and I added it). Mine is their copy
  (fetched 10-30) plus my status and review entry: **take hero-integration's side**. If act1-chapters has added to
  it since, also keep their newer lines. The other conflicts are other tracks' shared data files (enemies,
  encounters, skills, battle_sandbox, battle_sfx, ownership), the same as in the trial-merge report.

### Lead 10-30 04:06: row 66 (Ch4 opening → field) and the rows "still open on big19"
- **Row 66 FIXED (game/world/**, mine):** reproduced headless in real time (the wake's C4-01 with auto-advancing
  lines, fixed 60 fps).
  - **Cause:** the release blends from the cutscene's H12 shot, 120 m off. On the first blended frame a windbreak tree
    on that 120 m line pulled the camera in by about 87 m. The pull was stored as metres in from the shot's place and
    eased out at release_mps 4 m/s. Once the blend shortened the line to 9.8 m, a pull longer than the whole line put
    the camera **on Rhen's chest, inside Neme's house wall, for about 19 s** (the PC's ch04_03/05).
  - **Fix:** occlusion now keeps the pulled-in camera at a **distance from his chest** (`_kept_m`; INF when not
    pulled), not a pull from the shot's place, so a shortening line can never leave the camera on him. After it, the
    camera is never nearer than 5.9 m and is on NemeDoor's shot 2.3 s after the release.
  - **Test:** `test_a_pull_on_a_long_line_never_leaves_the_camera_on_him` fails on the old director (0.00 m) and
    passes now.
- **Rows 24 (DockShore), 37, 38 and 50 "still open on big19":** none of my fixes were in the PC's pass-4 tree
  (integration @ 2f544938). 692b55156, cb04c330f, 2e5292613, 1da21c732 and 0ffe9260d are all after it, so they come
  in with this branch's merge:
  - **37 (Toma's shield filling one side):** fixed by camera_near_m, 692b55156, plus today's off_lens fix in 0ffe9260d.
  - **38 (Tier4 camera in Rhen's head):** fixed on the camera side by cb04c330f, today's widest_view and this fix. The
    spawn standing inside the steps is still M3-HER-1157 (env-art-b). The Encounter shot looking at open sea is
    M3-HER-1159 (act1-chapters).
  - **50 (Toma sunk at the Crown):** I couldn't reproduce it (walk audit sunk check, stills). The pass-4 tree also
    lacked the stair fixes. If it shows on a tree with them, the save or story state would help.
  - **24 (DockShore):** fixed by 0ffe9260d.
- Checks: camera 70/0 (qa_field_camera included), hero_ 115/0, qa_walk_audit 1/0, qa_party 3/0, ch04 13/0; gdlint and
  gdformat clean. No shots rendered: the change only moves a pulled-in camera, which no fixed-camera shot uses.
MERGE-READY @ (this commit).

### Lead FAST-TRACK 10-30 09:00 (big20 @ 7dc3ab41)
- **test_no_follower_is_laid_out_in_front_of_the_lens:** big20 took my branch @ 202668789, before the fix.
  - The fix was already in 0ffe9260d: off_lens tries beyond him, else the unblocked spot farthest from the lens.
  - On big20's merged tree it showed two more cases, both fixed now (layout, not threshold):
    - **Ch13's Sanctum Gate (big20's new field camera near the spawn):** catch_up laid the followers out about 5 m
      back, behind the lens, while follow_point pulled them beside or beyond Rhen. They were more than catch_up_m
      apart, so catch_up re-ran every few frames, and each re-run was a visible 0.77–7 m teleport
      (test_hero_field_snaps: asha 1 snap, toma 3). `_formation_spot` now lays a near-lens follower on the same
      off-lens spot follow_point chases.
    - **The lens test's camera 1.5 m behind him:** the spot beyond him was still 2.65 m from the lens. It now goes far
      enough past him to clear camera_near_m (LENS_CLEAR_M 0.05 past it).
- **New red from big20, not mine: Lowlight (Ch11)** `rhen never snaps (241 snaps)`. The atrium's west gate opening
  (x 0, z −2.5..2.5) has no floor or bound past it. The Gate spawn faces through it, so Rhen walks off the level and
  falls without end. It walked clean before big20's dressing (M4-A2P-041, 79fc304f0).
  **Filed M4-HER-1166 (environment: act1-chapters' layout, env-art's dressing)**; KNOWN in test_hero_field_snaps
  until it lands.
- **M3-CIN-1251 @ 1da21c732 and row 66 @ e7af4147d are both done** (the earlier entries above), and both are after
  big20.
- **Row 50: CLOSED, not reproduced.** At the Crown spawn with all three visible, everyone stands on the 42 m floor
  (still and probe). Up and down the flying stair (qa_walk_audit's ashcrown routes, followers unstaged), the sunk
  check (feet more than 0.3 m under the floor or the stair profile) finds 0 frames. The PC's pass-4 tree lacked my
  stair and follower fixes (692b55156 onward). If it shows on a tree with them, the PC reopens it with the save.
- Checks on big20 + this branch: hero_ 116/0, camera 70/0, qa_party 3/0, qa_walk_audit 1/0; gdlint and gdformat
  clean, validate_data 0/0, taskboard OK. ACT II REPORT: Keth Pass's camera is inside geometry for 30 frames (2
  before big20's Ch12 cameras). It's report-only and is re-checked against the kit.
MERGE-READY @ (this commit).
- Next: the Act I encounter-entry smoke and the headless playthrough on 7dc3ab41, in a clean worktree. Results follow.

### Act I gate criterion 2 on big20 (7dc3ab41), clean worktree, 10-30 ~11:00
- **PASS.** Each suite ran alone with its own XDG_DATA_HOME, all with **0 SCRIPT ERRORs**:
  - qa_threads 1/0: every chapter thread start to end, save and load at every shrine;
  - **qa_encounters 1/0 (the encounter-entry smoke):** every Act I encounter entered, won and left;
  - fp_ 30/0: title → New Game → Prologue → the slice → Ch3;
  - save_ 153/0;
  - **act1_route 3/0:** M3-CIN-1233's continuous path, New Game → Ch1 → the slice → Ch4 → Ch9's end card → the title.
- **act1_gate_check.py fix:** it looked only for `test_*continuous*.gd`, so it reported M3-CIN-1233's test as missing.
  It now runs `tests/integration/test_act1_route.gd` too (CONTINUOUS_TESTS), with a unit test.
- **Row 38's Encounter ("looks at open sea, no Rhen"): FIXED, and it was the spawn, not the camera.** A zone's
  "Encounter" spawn is where the last random fight left Rhen. Before any fight, its marker sat at the world origin
  (0, 0, 0), so the PC's spawn walk put Coilspire's party at the origin, far off the tower at x ≈ 308, looking at sea.
  Real play always has a return point. The marker now starts on the zone's first spawn (greybox_zone.gd). The stale
  `coilspire.tscn:Encounter` KNOWN entry in test_qa_field_camera is gone.
  - Checks: camera 70/0 (qa_field_camera with no Encounter row), encounter 3/0, hero_field_snaps 2/0, qa_party 3/0.
- **Pass-5 rows after this branch merges:**
  - 24 DockShore and 47 FerryAft: fixed by 0ffe9260d (standoff, widest_view).
  - 66: fixed by e7af4147d (the pull kept as a distance).
  - 38 Encounter: fixed by this commit.
  - 37 AfterHarrier (Toma's shield at frame right): next, stills on this tree.
  - 21: next, the beach-cutscene hand-off in real time (likely the same pull bug as 66).
MERGE-READY @ (this commit).
- **Row 37 at AfterHarrier (Toma's shield at frame right): fixed.** C07 is a fixed camera at eye height (1.2 m), 6 m
  behind Rhen. Toma was laid out just outside camera_near_m (3.0), so at that height he filled the right third.
  `followers.camera_near_m` is now **4.0**: the still shows all three at a reading scale, with Rhen clear at centre.
  - 4.5 was tried first. It also read well, but at Ch13's Sanctum Gate the followers then started following 33–39
    frames after Rhen, against qa_party's 30-frame limit.
  - Checks: hero_ 116/0, hero_followers 14/0, qa_party 3/0, qa_walk_audit 1/0, qa_field_camera 2/0 (4.5 results,
    with qa_party and hero_followers re-run at 4.0); validate_data 0/0.
MERGE-READY @ (this commit).
- **Row 21 (Haluna's field start after the beach): reproduced headless, and clean on this tree.** The PC's walk can't
  reach it, so I played it as New Game does: `prologue_seen`, Haluna loaded, HalunaStory.begin(), Cutscene A in real
  time with auto-advancing lines at fixed 60 fps, then the camera sampled every 0.25 s for 12 s after the release.
  - The release (t = 95.5 s) blends from H01 to `beach_shallows` (1.2 s blend, settled after about 1.5 s).
  - Rhen is **in frame on every sample** from the first frame after the release, and nothing blocks the view.
  - The camera settles at 7.5 m from his chest and stays there; it isn't left at H01.
  - This tree has row 66's pull fix (e7af4147d), the likely cause of the pass-3 "camera over the shallows, Rhen off
    screen".
  - **For the PC:** confirm by hand on the merge of this branch. Close it if it's clean.
- Open on my side after this branch merges: nothing on act1_gpu_qa.md. Rows 21, 24, 37, 38, 47 and 66 are fixed or
  verified here; row 50 is closed, not reproduced. Still waiting on other tracks: M3-HER-1157 (env-art-b, Tier4's spawn
  inside the steps), M3-HER-1159 (act1-chapters, shots facing away), M4-HER-1166 (Lowlight's open gate).
MERGE-READY @ (this commit).
- **Inventories on big20 + this branch:**
  - **Act I:** 2 items, both low and both env-art-b's (the tamsule_bell drop proxies, as before).
  - **Act II:** `act2_inventory.md` refreshed: 38 items (15 high, 23 medium), up from 34 as big20 brought Act II
    zones in. Audio has 19, env-art-b 11 and battle-presentation 4. It is report-only (ADR 0205).
- **Trial merge @ integration 857c73ad; integration merged into this branch.** act1-chapters fixed M3-HER-1159 the
  same day: a layout can name its own "Encounter" fallback. Their change touched my lines in greybox_zone.gd and
  test_qa_field_camera.gd, so I reworked mine to merge clean with every head:
  - my first-spawn fallback is now in `place_at()`, used only when no fight was recorded and the layout names no
    Encounter spawn of its own;
  - the build lines and the KNOWN block are back to the base text (their merge drops the KNOWN rows).
  - Re-tested after an import: qa_field_camera 2/0, encounter 3/0, hero_field_snaps 2/0, qa_party 3/0.
MERGE-READY @ (this commit).

### Lead FAST-TRACK 10-30 12:13: the human's playtest (top priority)
1. **The black screen after a won battle: root cause measured, fix in this branch.**
   - The way back from a fight was a full zone entry: load, instantiate on a thread and add to the tree, all behind
     the fade. Haluna headless: **entry 6,527 ms**, of which instantiate 1,532 ms and the add-to-tree frame
     2,678 ms. That is the human's multi-second black.
   - **Fix (SceneRouter, mine):** the field stays resident through a random fight.
     - A change from a field zone into `field_battle.tscn` for a random encounter (`BattleRequest.pending()`: no
       victory flag, no return scene of its own) detaches the zone instead of freeing it. Its zone shader globals
       are snapshotted at the same time (`ShaderGlobals.zone_snapshot`).
     - The change back to that zone re-attaches the same instance, with no load, no instantiate and no `_ready`.
       The globals are restored after the swap's reset, and the party is placed on the spawn as before.
     - Any other change, or a loaded game (`EventBus.game_loaded`), frees the kept zone.
     - Scripted fights still reload their zone, because their story plays on the zone's arrival.
     - `stats.resident` and `instantiate_ms` 0 mark a resident return.
   - **Test:** `tests/integration/test_battle_return.gd`. It enters the causeway in the child-process probe
     (`scene_swap_probe --encounter=ch03_causeway_shore --return=<zone>`; `--no-resident` measures the old reload),
     fights, comes back, and fails unless the return is resident and its hidden time is ≤ 1 s.
2. **The docks: `FieldShore` (game/world, mine), a generic guard in FieldController.** Oruvel's decks sit at y 0
   over a solid "Sea" block at −1, under water at about −0.8, so stepping off a hull dropped him onto a walkable sea
   floor. A step is now refused, and he stays at the edge as at a wall, in two cases:
   - the ground drops more than 0.4 m into water deeper than 0.15 m (a dock, pier or hull edge);
   - he would wade deeper than 0.6 m, and deeper than where he stands. Walking back out is always allowed.
   - **Safety catch:** grounded deeper than 0.6 m anyway, he goes back to his last safe spot.
   - **Seabed walks** (more than 2 m under, Oruvel's underway) have no shore rule.
   - Tuning: `field_movement.json` "shore".
   - **Test:** `tests/integration/test_qa_dock_edges.gd` runs Rhen flat out in 16 directions for 6 s from every spawn
     of every Act I zone with water (19 zones), failing on a drop into water or a deep stand.
3. **The jog speed: LEAD-ASK.** There's no new jog clip from characters on any branch yet (M3-HER-1165 is still
   todo). Today's run clips measure 1.80–3.13 m/s against the field's 3.6 m/s run. Matching them without the clip
   would mean slowing the field run to about 2.3 m/s, a game-feel call, not mine. **When characters push the clip,
   I set run_speed_mps (or the gait rows) to its measured speed the same hour.** Which should it be: wait for the
   clip, or lower the run now?
- **Measured (causeway, `ch03_causeway_shore`, real time, headless):**
  - **resident return:** entry 389 ms (mostly the fade), worst hidden frame 31 ms, instantiate 0;
  - **the old full reload** (`--no-resident`): entry 1,737 ms, worst hidden frame 1,264 ms.
  - Heavier zones (Haluna: 6.5 s cold) gain more.
- **FieldShore details:** a spot where the ground ray finds nothing isn't judged (a ray starting inside Haluna's
  terrain collider missed it, which stalled the lane walk), and the ray starts 1 m up. With the guard off,
  qa_dock_edges fails in Coilspire, Ansedra, the lacquer court and others, so it catches real edges.
- **Checks:** battle_return 1/0, scene_router 17/0, flow_routing 4/0, shader_globals 3/0, qa_dock_edges 1/0
  (19 zones), qa_walk_audit 1/0, field_controller 5/0, hero_field 30/0, qa_party 3/0, fp_ 30/0, qa_encounters 1/0,
  save_ 153/0; gdlint and gdformat clean over game and tests; validate_data 0/0.
MERGE-READY @ (this commit).
- **MERGE-READY @ 99989c2bc** (for big24): the battle-return resident field (1,737 → 389 ms black on the causeway)
  and the FieldShore water guard, with their tests.
- **Jog speed (the Lead, 10-30 14:28): no pre-slowing.**
  - When characters push the jog clip, I set the field run speed **in data** from the clip's own travel (root travel
    per loop, else stride × cadence, as HeroClipGait measures it), within 2.3–3.6 m/s, so the feet plant.
  - Then max_playback_scale comes back down and test_qa_walk_audit's foot-slide check confirms it.
- **Next:** re-measure Haluna's cold entry and the battle return (`scene_swap_probe --encounter --return`) once big24
  merges; the Act II items as before.

### The field-camera rows verified on big23 (8fe3644b, a clean worktree), the Lead 10-30 15:08
- `qa_field_camera` 2/0, `qa_party` 3/0, `camera_director` 56/0. qa_field_camera's spawn sweep now fails on a camera
  in his face (under 1.5 m) or a director pitch steeper than 55°, so every spawn below is under it.
  - **24 (DockShore) and 47 (FerryAft):** clean in the sweep (the standoff and widest_view in 0ffe9260d).
  - **38 (Coilspire Encounter):** clean, with no KNOWN line. The Lead's big23 resolution of the Encounter fallback
    (a layout's own, else the first spawn, at build) supersedes my place_at version (7e0f44802); I take integration's
    side on my next merge. Tier4 is still KNOWN: its spawn stands inside the steps (M3-HER-1157, env-art-b).
  - **37 (AfterHarrier):** the still on big23 shows Rhen clear at centre, with Asha and Toma at a reading scale
    (camera_near_m 4.0).
  - **66 (Ch4 opening):** real time with auto-advancing lines. In the 12 s after the release, the camera is never
    nearer than 5.1 m and settles on NemeDoor at 9.8 m. Only 6 of 111 samples had Rhen out of frame or walled off,
    all during the 1.2 s cross-town blend; there's no 10 s spell inside a wall.
  - **21 (Haluna beach start):** real time. 0 of 121 samples with Rhen out of frame or walled off; it settles on
    beach_shallows at 7.5 m.
- **For the PC:** all six rows are fixed on big23 in the headless checks; please confirm them by hand on the next
  pass.
- **Next:** big24 (with characters' jog, b344b974, and my 99989c2bc), then the run speed from the jog's measured
  travel and Haluna's cold entry.

### Lead FAST-TRACK 10-30 15:49: big24's red test_qa_field_camera (lowlight.tscn:Sanctum), fixed
- **Reproduced on big24 (efe7fb10, merged here):** with the committed FieldShore, `lowlight.tscn:Sanctum (shot Hall):
  the leader is out of frame`. It passes with the fix.
- **Cause:** a safety-catch bug in my guard. Lowlight's hall water plane (x 32–72, y −2.05) does cover the Sanctum
  spawn (60, −8, 4), 6 m under it, the drowned sanctum. The refusals skip anyone more than underwater_m under (a
  seabed walk), but the catch in `settle()` didn't. It put Rhen back on his last safe spot, the previous spawn's
  (Gate or EngineHall), across the zone, so the camera at Sanctum lost him.
- **Fix:**
  - `settle()` does nothing more than underwater_m under a surface (the same rule as the refusals);
  - a last safe spot more than `teleport_m` (2.0, field_movement.json "shore") away is forgotten, because a spawn or
    a teleport put him here and the old spot is elsewhere.
  - New `tests/unit/test_field_shore.gd`: the catch near the safe spot, a teleport forgets it, and no catch under a
    surface.
- **Checks:** test_qa_field_camera 2/0 (red before the fix), field_shore 3/0, qa_dock_edges 1/0 (23 zones).
MERGE-READY @ (this commit).
