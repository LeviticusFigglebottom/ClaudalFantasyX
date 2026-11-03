# Handoff 2026-11-03 (2): cinematics, slice-polish (claude/m2-slice), FINAL

## Done
- **M3-CIN-1252 (FAST-TRACK, the storm vortex):**
  - `@storm view|off` (CutsceneStorm);
  - Ch1 O11E, the eye from above;
  - Ch8 F08W and F08E;
  - Ch8 W20 reframed onto the storm.
- **Beat audit on big45:**
  - every slice and Ch1 cutscene shot now holds a line or cue;
  - the vigil shot was fixed: the title card had delayed its line.
- **M5-A3P-1704:** the Ch18 revisit flags.
- **M5-A3P-1707:** the Ch17 ledger mount.
- **M5-A3P-1701 + 1203, the Ending's last stops:**
  - E5 at Haluna's dark dock, then the credits;
  - the beach-rite vignette;
  - PostCredits, then E7 in Oruvel, then the title.
- **Fixed:** CutsceneGrade now finds a GreyboxZone's environment.

## In progress
Nothing. Everything is committed and pushed.

## Exact next step
1. Merge `origin/claude/undertow-lead-handoff-ze8rrn`.
2. View the Lead's renders of the seven new pending shots (see the live log's FINAL section).
3. Work the PC-QUEUE.
4. Act III staging per ADR 0207 as each set lands (Act I FAST-TRACKs first).

## Known issues
- E11 is very dark under ending_dock on lavapipe (Asha's face; PC-QUEUE).
- F08E: dark ribbed arcs on the maelstrom rim (Rendering).
- W20: a sun glint and kites (routed by the Lead to env-art-b and act1-chapters).
- The beach rite has no `crowd` actor and no dawn grade.
- Nothing plays `ch18_backs_to_the_water` yet (M5-A3P-1004).

## Files touched (this part)
- Flow and code: game/flow/{haluna_story.gd, ending_beach_rite.*, post_credits.*}, game/levels/ch02/haluna/haluna_zone.gd,
  game/cutscene/cutscene_grade.gd, game/levels/ch17/ch17_zone.gd.
- Data: game/data/cutscene/ch0{1,2}/*, game/data/flow/{first_playable.json, chapters/ch01.json, chapters/ch17.json},
  game/data/ui/credits.json, game/data/flags.tres, game/data/dialogue/{ch18/ch18_revisit_*, ending/ending_*}.dlg,
  game/data/dialogue/cues.json.
- Tests: tests/integration/{test_ending_last_stops, test_ch18_revisit_flags, test_ch17_thread}.gd,
  tests/unit/{test_credits_roll, test_cutscene_grade}.gd, tests/screenshots/shots.json.
- Docs: the M5 task files and docs/kb/handoffs/live/slice-polish.md.
