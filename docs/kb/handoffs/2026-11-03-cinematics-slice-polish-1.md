# Handoff 2026-11-03: cinematics, slice-polish (claude/m2-slice)

## Done
- Merged `origin/claude/undertow-lead-handoff-ze8rrn` (big45).
- **M3-CIN-1252 (FAST-TRACK 4, the human's "the seagull/storm scene doesn't show the actual vortex"):**
  - `@storm view|off [look=]` (game/cutscene/cutscene_storm.gd; sequencer.json `storm`; cues.json `storm`):
    - the zone's Undertow runs its clock during a storm shot;
    - the zone fog thins and the sun lights the storm's top;
    - a bolt strikes facing the camera;
    - `off`, or the scene's end, restores everything.
  - Ch1 `ch01_the_rising`: O11, then O11E (the eye from 16 km up), then O11 for Rhen's line.
  - Ch8 `ch08_storm_against_wind`: F08W (the wall from the gallery), then F08E (down the eye), then F08.
  - Ch8 `ch08_wall_falls`: W20 re-aimed so the storm fills the frame over the breach.
  - Four new pending shots: ch01_rising_eye, ch08_storm_wall_f08w, ch08_storm_eye_f08e, ch08_wall_falls_w20. All
    were self-rendered and viewed.
  - Music checked: the storm cutscenes already play storm and dread cues. The uplifting music is in the storm fights
    (other tracks).
- Act I rows: 31 and 32 are fixed. Row 75's fix is on integration and waits for the PC's GPU re-check.

## In progress
- The beat audit re-run on big45: slice_prologue_vigil_line, slice_beach_h05_asha, slice_beach_h06_toma,
  slice_verse_steps, slice_dock_night_yes, ch01_hullgnaw_rises, ch01_going_under_u10 and ch01_sadi_mooring are
  rendering (see the live log for results).

## Exact next step
View the audit renders and fix any drift. Then take the next `todo` cinematics task
(`python3 tools/taskboard.py --role cinematics`), then Act II per ADR 0205.

## Known issues
- F08E: dark ribbed arcs on the maelstrom disc's near rim, looking steeply down the eye (Rendering's shader).
- W20: a sun glint on the sea under the storm, and the festival kites still flying (act1-chapters / env-art).
- The cutscene test filter takes over 25 min on 4 CPUs. Give it a long timeout, or run test_hero_cutscene_snaps on
  its own.

## Files touched
game/cutscene/cutscene_storm.gd (+.uid), game/cutscene/cutscene_sequencer.gd, game/data/cutscene/sequencer.json,
game/data/dialogue/cues.json, game/data/dialogue/ch01/ch01_the_rising.dlg, game/data/dialogue/ch08/ch08_storm_against_wind.dlg
(+ compiled), game/levels/ch01/oruvel/oruvel_layout.json, game/levels/ch08/coilspire/coilspire_layout.json,
game/levels/ch08/corrow/corrow_layout.json, tests/screenshots/shots.json, tests/unit/test_cutscene_storm.gd,
docs/kb/tasks/M3/M3-CIN-1252-storm-cutscenes-show-the-vortex.md, docs/kb/handoffs/live/slice-polish.md.
