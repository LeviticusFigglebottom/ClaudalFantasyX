# Handoff: audio, 2026-10-24, #802-1 (M3-AUD-802, worktree agent on claude/audio)

## Done
- M3-AUD-802 is in review (reviewer qa). The full notes are in docs/kb/tasks/M3/M3-AUD-802-hero-footsteps-foley.md.
- **Sounds:** `assets_src/sfx/hero_foley.py` renders 84 files in `assets/audio/sfx/foley/`:
  - steps: sand, stone, wood and the new shallow water, 6 variants each, walk and run;
  - halt and turn scuffs;
  - cloth foley, and gear foley for Rhen (lantern), Asha (shells) and Toma (leather).
- **Data and checks:** the rows are in `game/data/audio/sfx_foley.json`; targets.py has the new rules, and
  render_all.py a JOBS row. PROVENANCE has 84 rows.
- **Runtime:** `FootstepAudio` steps on the hero body's foot contacts, in this order:
  1. a `foot_contact` signal;
  2. AnimationTree markers `foot_l_down` / `foot_r_down`;
  3. AnimationPlayer markers;
  4. the distance stepper, when none of these exist.
  It also plays the foley layers and the halt and turn scuffs. The ground surface comes from the groups
  `audio_surface_<surface>` or `footstep_surface` + `surface` meta.
- **Request:** M3-AUD-810 (role character, request-from audio) lists exactly what audio reads.

## In progress
Nothing.

## Exact next step
Once claude/hero-integration (M2-HER-1101/1107) and claude/characters (M2-CHR-12) are on the integration branch,
check two things:
- `contact_source` on the live FootstepAudio reads `tree` (or `signal` if they add one);
- Rhen's walk in Haluna steps on the heels.

Then listen to the mix of steps, cloth and lantern at walk_db, and tune `foley.cloth_db` and `gear_db` in
footsteps.json if the layers read too loud.

## Known issues
- No level marks surface areas yet (M2-AUD-09 and M3-AUD-810 ask for them), so water and wood only sound inside
  marked areas.
- Followers take no steps.
- On the signal path, walk or run comes from the controller's speed against run_above_m_s (3.5).
- The filtered Godot runs end with pre-existing "resources still in use" from UI menu and field tests. The same
  counts show without this change; the new test file is clean alone.

## Files touched
- assets_src/sfx/hero_foley.py
- assets/audio/sfx/foley/* (84 .ogg + .import)
- game/data/audio/sfx_foley.json
- game/data/audio/footsteps.json
- game/audio/footstep_audio.gd
- tools/audio/targets.py, tools/audio/render_all.py, tools/audio/data_check.py
- tools/tests/test_audio_data.py
- tests/unit/test_footstep_contacts_audio.gd (+ .uid)
- assets/PROVENANCE.md
- docs/kb/tech/audio_runtime.md
- docs/kb/tasks/M3/M3-AUD-802-hero-footsteps-foley.md
- docs/kb/tasks/M3/M3-AUD-810-hero-foot-contacts-and-surface-areas.md
