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
