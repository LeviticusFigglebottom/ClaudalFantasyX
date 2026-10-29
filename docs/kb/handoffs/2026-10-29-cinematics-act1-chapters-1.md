# Handoff: cinematics (act1-chapters), 2026-10-29, session 1

Lead: `session_01Bg3iP7cPGyjbX4CyniBahc`. Integration branch: `claude/new-session-mj8c3c` (merged @ b60a8f61).
Branch: `claude/act1-chapters`. Live log: `docs/kb/handoffs/live/act1-chapters.md`.

## Done
- Merged the integration branch. None of my filed requests had landed on it beyond what my branch already had.
- A fresh title → Ch9 playthrough:
  - every `_thread` test (40/0);
  - `tools/act1/cutscene_stills` over Ch1 and Ch4–Ch9 (185 + 24 stills, then re-renders with `STILLS_DEBUG`);
  - Ashcrown's field POIs.
- Fixed in my lane (details in `docs/kb/qa/act1_playthrough_ch04_ch09.md`, "Fourth pass"):
  - Ch4: the ink's H15;
  - Ch6: B10's wade (the party's stage bodies), W06_after;
  - Ch7: R07;
  - Ch8: the kites through the run back; Virel's own body in F07 (my request M3-CRE-627-virel-field-body, now in
    review); ZoneCast `cast_still`;
  - Ch9: D02;
  - Ch5 Ashcrown on its kit: A02, A11 with Kahre's own body behind the shut door, A12, `chamber_in`, seven POI
    camera volumes.
- Reviewed M3-ENV-1303 (Ashcrown on its kit): approved.
- Tasks:
  - to review: M3-C04-1204, C05-1213, C07-1211, C08-1210, C09-1209, M3-HER-1145, M3-ENV-744 (superseded),
    M3-C05-1215 (superseded);
  - M3-HER-1129 re-routed to env-art-b (a 0.12 m ramp edge remains);
  - new request M3-CIN-1232 to slice-polish (five Ch1 frames blocked or empty).
- Self-rendered: ch08_corrow_storm (no baseline; the kite lines now show, as the story has them).

## In progress
Nothing.

## Exact next step
When a filed request lands on the integration branch, re-run that zone's stills and POI views. The requests:
M3-ENV-1228/1229 (grades), M3-HER-1225 (Sefir), M3-CHR-506 (Pell), M3-RND-27/28 (storm wall and figure), M3-CIN-1231
(held box), M3-CIN-1232 (Ch1), M3-HER-1129 (Coilspire ramp).
- Stills: `python3 tools/act1/cutscene_stills_plan.py plan.json`, then
  `STILLS_PLAN=plan.json STILLS_OUT=dir STILLS_ONLY=<location> STILLS_DEBUG=1 godot-render --path . res://tools/act1/cutscene_stills.tscn`.
- POI views: `GODOT=godot-render python3 tools/act1/poi_views.py --zones <id> --render dir`.

## Known issues and gotchas
- `@mark` always walks; there's no in-scene teleport. Place actors with flow `place_actor` steps, or start them on
  their mark.
- Regenerate the stills plan after any flow edit: the plan embeds each beat's steps.
- `pgrep -f cutscene_stills.tscn` in a wait loop matches the loop's own command line. Wait on the PID, not the name.
- Two task files share the id M3-CRE-627 (LEAD-ASK in the live log).

## Files touched
game/levels/act1/zone_cast.gd; game/levels/ch04/haluna_wake, ch05/ashcrown, ch06/brine_shoals,
ch07/tamsule_bell_galleries, ch08/coilspire, ch08/corrow, ch09/corrow_night layouts (and Coilspire's dressing json);
game/data/flow/chapters/ch04, ch05, ch06.json; game/data/dialogue/ch08/ch08_binding.dlg;
tools/act1/ch04_haluna_wake.py (+ floors and points), tools/act1/ch08_coilspire_dressing.py (keep list);
tests: test_zone_cast, test_ch04/05/06/08_thread; docs: the playthrough doc, the task files above, the live log.
