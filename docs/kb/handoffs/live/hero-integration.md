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
| M2-HER-1101 field hero actor (Rhen, locomotion blend, eased turns, start/stop, ground) | architect | doing (worktree agent) |
| M2-HER-1102 field party followers (Asha, Toma on a trail) | architect | doing (same agent) |
| M2-HER-1103 battle hero actors (meet UI-07 + CHR-07 + BPR-10, check every contract clip on the real models) | combat | doing (worktree agent, trial merge) |
| M2-HER-1104 cutscene motion API (eased turn, walk start/stop, idle micro-motion) for m2-slice's sequencer | cinematics | doing (worktree agent) |
| M2-HER-1105 clip-gap requests to the characters track | character | todo (list follows the field and cutscene passes) |
| M2-HER-1106 shots and tests | qa | doing |

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
  - **UI agreed:** they take the set_ko fix on claude/ui now, with a test. They repoint the stand_ins at the wrappers
    after this branch reaches the integration branch. Their files stay off this branch.
  - **Shots** `battle_heroes_*` wait until the three branches are merged.

## In progress
- Field: HeroFieldActor via one hook line in FieldController._ready (no zone scene edits), AnimationTree BlendSpace1D,
  measured clip speeds, followers; tuning the field acceleration and deceleration (field_movement.json) with m2-slice.
- Cutscene: a HeroMotion API plus a ready-to-apply sequencer patch for m2-slice (they own game/cutscene/**).
- Battle: a trial merge of claude/ui + claude/characters + claude/battle-presentation to check the real heroes play
  the contract clips; gaps go back to the owners as exact patches.

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
Merge the three worktree agents' branches as they finish, run scoped checks, post a MERGE-READY line here.

## Un-pushed state
None (the worktree agents' commits are local until merged here).
