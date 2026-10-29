---
id: M3-AUD-802
title: Footsteps and movement foley for the real field heroes (claude/hero-integration), keyed to foot contacts
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agent)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
The human's note: parts feel primitive. claude/hero-integration is putting the real heroes on the field with M2-CHR-12's locomotion clips. FootstepAudio steps by distance today.

## Acceptance criteria
- [x] Surface-aware steps (sand, stone, wood, shallow water) and movement foley (cloth, gear), fired on the locomotion clips' foot contacts (falling back to distance), synthesized, PROVENANCE rows, tests. Coordination is through the request task M3-AUD-810 (CLAUDE.md §7a: another environment's live log is never edited).

## Notes
- **Sounds:** `assets_src/sfx/hero_foley.py` writes 84 files to `assets/audio/sfx/foley/`. It uses field_sfx.py's
  heel-and-toe envelope, Poisson grains, struck modes and small stone room, plus synth/water.py's bubbles and drips
  and field_ambience's stick-slip creak. All World bus, mono, q4, 704 KiB.
  - **Steps:** `step_<sand|stone|wood|water>_<walk|run>_01..06`. A run lands a heavier heel and rolls to the toe
    sooner (40–60 ms, against the walk's 65–100). Sand throws grains, stone gets grit under the sole, wood gets the
    next board's rattle, and water sprays more and drips more. Water is new: a foot slap, the cavity's falling
    plunk, bubbles round the ankle, drops falling back and the lifted foot's drag. Measured decoded: −17.98 to
    −19.18 LUFS momentary max, true peak ≤ −1.20 dBTP.
  - **Scuffs:** `stop_<surface>_1..2` (−19.98 to −20.79) and `turn_<surface>_1..2` (−20.98 to −21.42).
  - **Foley:** `cloth_<walk|run>_1..4`, plus `gear_lantern` (Rhen), `gear_shells` (Asha) and `gear_leather` (Toma),
    each `_1..4`. All −24.0 to −24.38, peaks ≤ −3.26 dBTP.
  - Rules in tools/audio/targets.py, specific before generic: steps −18.5 ±1, stop −20, turn −21, cloth and gear
    −24, then `sfx/foley/*.ogg`. A JOBS row is added at the end of render_all.py. `--only hero_foley --determinism`
    gives 84/84 identical. PROVENANCE has 84 rows, at the end, in their own commit. The total shipped audio is
    43.3 MiB, under the 48 MiB budget.
- **Runtime** (`game/audio/footstep_audio.gd`, data `footsteps.json` v2, rows `sfx_foley.json`):
  - **Contact source**, by name and guarded, on the walker's `HeroBody` child, else the walker:
    1. a `foot_contact` signal;
    2. else the AnimationTree's clip nodes (blend trees and 1D blend spaces), crossing the `foot_l_down` /
       `foot_r_down` markers at `parameters/<path>/current_position`. Only the dominant clip counts, at
       `min_weight` (0.3) or over;
    3. else a playing AnimationPlayer's marked clip.
  - `run_clips` (run, run_start, run_stop) mean a run. Contacts within 0.15 s are one step. Walking `stall_m`
    (3.2 m) with no contact plays a distance step. With no contacts at all, the old distance stepper runs unchanged.
  - Each step layers cloth, and the gear every 2nd step, by the body's `hero_id`.
  - **Halt:** the stop scuff plays once when a walk of 2+ steps slows from 0.8 to under 0.3 m/s (or stands still).
  - **Turn:** the turn scuff plays on a ≥100° heading change within 0.3 s.
  - **Ground:** the highest `surface_priority` node in `footstep_surface` (with a `surface` meta, M2-AUD-09's form)
    or in `audio_surface_<surface>` whose collision shapes hold the feet; else the scene's. Nothing on any branch
    marks an area yet (checked m2-slice, env-art, the lead branch, hero-integration and characters), so the reader
    is designed and documented, and M3-AUD-810 asks for the marks.
  - The old `step_*` rows (sfx_field.json) stay; a plain-string surface row still works.
- **Hook source:** HeroFieldActor (origin/claude/hero-integration 6cc3df57) has no contact signal. Its
  AnimationTree is mode (Transition) → scale (TimeScale) → loco (BlendSpace1D idle/walk/run), plus the act_a and act_b
  slots, manual-advanced. M2-CHR-12 (origin/claude/characters eee3099a) puts the heel markers in `locomotion.json`
  and in the clips as Animation markers. A probe on Godot 4.6.3 confirmed the `parameters/loco/<i>/current_position`
  params and the Animation marker API. The test stand-in mirrors that layout. Nothing of theirs was edited.
- **Tests:** `tests/unit/test_footstep_contacts_audio.gd`, 7/0, clean at exit when run alone, twice. It covers:
  - a method track emitting `foot_contact` (4 contacts → 4 steps, sand walk rows at walk_db, cloth every step,
    Asha's shells every 2nd, run rows when running);
  - the tree's markers (one step per walk or run crossing, run rows from the run clip, none at idle);
  - AnimationPlayer markers;
  - the distance fallback and the stall step;
  - a water Area3D and a higher-priority dock (`footstep_surface` + meta);
  - the halt scuff (once; not after a shuffle) and the turn scuff;
  - every named row existing on World and importing.
  `test_audio_data.py` gets one more case (gait rows, foley, contacts, areas).
- **Gates:**
  - validate_data: 0 errors.
  - taskboard --check: clean.
  - test_audio_data.py: 45/45 OK.
  - gdlint and gdformat: clean.
  - import: once.
  - Godot `--filter=audio`: 112/0, run twice.
  - `--filter=field`: 96/0.
  - test_audio_loudness: OK.
  - The "resources still in use" at exit in those filtered runs is pre-existing:
    - audio: 2 UI menu scripts (field_submenu.gd, battle_pause_menu.gd);
    - field: 248, the same count with this change reverted.
  - Skipped: screenshots, Blender and the full suite (no scene, shader or Blender source touched).
- **Known limits:**
  - Followers take no steps.
  - With the signal path, walk or run comes from the speed against 3.5 m/s, which needs a recheck if M2-HER-1107
    retunes the run below that (in M3-AUD-810).
  - Nothing has been heard on the real clips yet. Once claude/hero-integration and claude/characters merge, walk
    Rhen in Haluna and listen.

- 2026-10-24 (hero-integration's ADR 0191: the field walks at 1.0 m/s and runs at 3.6 m/s): footsteps.json's
  distance stepper is now walk_step_m 0.53 and run_step_m 1.0 (half a stride, per characters' locomotion.json);
  stall_m is 1.6 (3.2 m would be 3 s of silence at 1.0 m/s). run_above_m_s is now 2.3, the midpoint of the gaits:
  just under 3.6, the smoothed pace took about 0.5 s to class a run, so a run's first steps played as walk steps
  (the run-rows test caught it). The test speeds follow field_movement.json.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
  Note: `game/audio/footstep_audio.gd` still has the freed-cast hit tracked as M3-HER-1150 (KNOWN in
  tools/freed_cast_lint.py). That's a separate bug, not one of this task's criteria.
