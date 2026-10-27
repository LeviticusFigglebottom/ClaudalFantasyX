# Live log: act1-chapters environment

Branch `claude/act1-chapters`, cut by the Lead from `claude/m2-slice` @ 6c50823f (2026-10-25). Integration branch:
`claude/undertow-lead-handoff-ze8rrn`. Binding rules: CLAUDE.md and `docs/kb/handoffs/live/TRACK-RULES.md` (on the
integration branch).

## Scope
Act I from **Ch4 onward**: Ch4–Ch9 (greybox, built by m2-slice) and the chapters after them; the greybox-to-final swaps
with env-art's Act I kits; Ch7's real Reefball match; real casts; encounters per chapter; the cutscene quality bar;
greyboxing Ch10 onward to the end of Act I. **slice-polish** (`claude/m2-slice`) keeps the M2 slice, Ch1–Ch3, the
cutscene sequencer (`game/cutscene/**`), `game/flow/**` and the playtest fixes.

- **Id block:** tasks 1200–1299 (e.g. `M3-C04-1200`), ADRs 0200–0209, handoffs `<date>-cinematics-act1-chapters-<n>.md`.
- **Paths claimed** (docs/kb/ownership.md, last row): `game/levels/ch04/**`–`ch09/**` and later chapters,
  `game/data/dialogue/ch04/**` onward, `game/data/flow/chapters/ch04.json` onward, `game/data/flow/ch0[4-9]_*.json`,
  `game/data/loc/ch04.csv` onward, `docs/kb/story/beats/act1_ch04.md` onward, the Ch4+ thread tests.
  **For slice-polish:** Ch1 (`game/levels/ch01/**`, `game/data/dialogue/ch01/**`, `ch01.json`) stays yours with
  Ch2–Ch3. Ch5 and Ch7's zones subclass your `Ch01Zone`; I won't edit it (I'll ask via a task if I need a hook).
- **The Act I switches** in `first_playable.json` stay EMPTY until the human signs off M2 (the Lead flips them). F8
  chapter select reaches Ch4–Ch9 meanwhile.

## NEW ACCOUNT (from 2026-10-25)
- **MERGE-READY @ 14ea50b9**: the integration branch (big8, c6a960ab) merged in (d7b55c10).
  Conflicts: encounters.json (theirs' arenas + Ch8's rows), voices.json (theirs + Ivo; the 17 Act I speakers' `pending`
  flags cleared now they're in speakers.json), translations (union, +ch08), validate_data (both sides' checks),
  test_hero_clips (the all-dialogue check with M3-CHR-01's pending list), the two different combat-14 handoffs (both
  kept; m2-slice's renamed `-cmb01`), balance_report (theirs). Ownership claim for Ch4+.
  - **Checks run:** `--import`; Godot `--filter=ch0` 59 run, 0 failed; validate_data 0/0; dlgc --check 0/0;
    taskboard --check; gdlint, gdformat clean; `tools.tests.test_hero_clips` 9 OK.
  - **Checks skipped:** the full suite and sim (the merge touched no battle code on this side; the Lead gates the
    integration merge); coverage (no game/battle or progression change of mine); Blender (no source); shots (no
    scene of mine changed).

- **PROGRESS @ e2fed1fc (2026-10-27): M3-C06-1200, Ch6 greybox → final (pushed, not yet MERGE-READY).**
  `ZoneKitDressing` (ADR 0200, `game/levels/act1/`) dresses a greybox zone with env-art's kit from a generated layout
  (`tools/act1/ch06_brine_shoals_dressing.py`), keeping the greybox's collision, triggers and states; story pieces
  follow their blocks. Ch6 takes the ch06 sun and grade. Request M3-ENV-1201 (six story pieces the kit lacks).
  - **Checks run:** `--filter=zone_kit` 5/0, `--filter=ch06` 5/0, `tools.tests.test_fog_lamps` OK, validate_data,
    taskboard, gdlint, gdformat clean. First lavapipe views made and viewed; fixes in (greybox stand-ins hidden, plank
    walk smoothed); the re-render is being viewed now, then two baselines are registered and a MERGE-READY line follows.

- **MERGE-READY @ 09233381: M3-C06-1200 Ch6 greybox → final, done (status review, reviewer environment).**
  Since e2fed1fc: greybox stand-ins hidden (an ember bed for the fire, crates for the purser; the shrine is the
  wreck's bow), a smooth plank walk, a dusk shot rig, Ch04Zone `ramps` + `collision_path` (for Corrow next),
  baselines `ch06_brine_road`, `ch06_brine_camp` (viewed, approved).
  - **Checks run:** `--filter=zone_kit` 5/0, `--filter=ch06` 5/0; tools test_screenshots + test_fog_lamps 19 OK;
    validate_data, taskboard, gdlint, gdformat clean; the two new shots captured in isolation and viewed.
  - **Checks skipped:** the full suite (only Ch04Zone, the Ch6 zone and new files changed; Ch04/05/07/08/09 zones
    inherit Ch04Zone's new `_build_blocks`: `--filter=ch0` 59 run, 0 failed); coverage (no battle
    or progression code); Blender (no source); other shots (no other scene touched).

- **Merged the integration branch (big9) @ 1b1caea0**: requested_clips union, encounters (theirs + Ch8's headland
  rows), the Lead's combat-20 renumber (my -cmb01 copy dropped). `--filter=ch0` 59/0, zone_kit 5/0.
- **MERGE-READY @ bf9267fa: M3-C08-1202 Ch8 Corrow greybox → final, done (status review, reviewer environment).**
  Corrow now stands on the seawall kit's heights in the kit's own frame (`tools/act1/corrow_frame.py`; the layout
  migrated once by `ch08_corrow_relayout.py`): the walk at y 12 among the Watchers, the Fisher Stair on the wall's
  inner face (ramps under 45°), the low town at y 1, the Bastion a platform at walk height dressed with outward
  seawall revetments, the mole's pier and ramp over the parapet, the stair breach from M3-ENV-04B on the fall.
  Ch06Zone light rows can swap the Environment (`environment_res`: the fallen grade). ZoneKitDressing gained per-piece
  `kit_dir` and trimesh colliders. Request M3-ENV-1203 (the mole, the Bastion's own pieces, kites, gate, nets).
  - **Checks run:** `--filter=ch08` 19/0 (with the new `test_ch08_corrow_walkable`: the mole, the walk, the stair
    both ways, the town lane, every mark on a floor); zone_kit 6/0; validate_data, taskboard, gdlint, gdformat;
    tools test_screenshots, test_fog_lamps OK. Baselines `ch08_corrow_arrival`, `ch08_corrow_stair` viewed and
    approved (captured before the PC-rendering directive reached me; none since).
  - **Checks skipped:** the full suite and coverage (no battle or progression code); Blender (no source).
- **PROGRESS @ 180510e1: M3-C04-1204 Ch4 ferry (WIP, not merge-ready until its shots are approved).** Dressed with
  the ferry kit and the Seventh Terrace; collision from the kit's hull constants; `test_ch04_thread` 11/0. The two new
  shots fail `test_screenshots` (no baseline) until the PC render comes back.

- **MERGE-READY @ 69c8a5e6 for M3-C07-1206 only** (cherry-pickable: `ch07.json`, `game/levels/ch07/tidecup_match/`,
  `ch07_tidecup.json`, the two Ch7 tests, the task files): Ch7's real Reefball match replaces the stand-in. TidecupMatch
  plays `tidecup_opening` through the HUD by path (M3-UI-01, on claude/ui, not yet integrated), else the engine's AI
  plays both sides; flags and reward per act1_ch07.md §5.4; back to CatchPool. Requests M3-PRG-1207 (Oruvel Float:
  no accessory slot exists), M3-RBL-1208 (the opponent is Sorrin in the story, Pemakar in the data; the §5.3 barks).
  - **Checks run:** `--filter=ch07` 8/0; validate_data, taskboard, gdlint, gdformat. **Skipped:** shots (no scene with
    a camera changed), coverage (no battle/progression code), the full suite.
  - **Ch4 (180510e1) is still WIP in this branch's head** until its render request is answered.

### Render requests
RENDER-REQUEST @ 180510e1: ch04_ferry_deck, ch04_ferry_derelict; why: M3-C04-1204 dresses the Ch4 ferry and derelict with the ferry kit (new shots, no baseline yet)

## Exact next step
Ch9 `ch09/corrow_night` onto the Corrow frame (it reuses Corrow's kit and grade, ch09 night), then Ch4 `haluna_wake`,
Ch5 Pemakar (terraces: trimesh treads + ramps for flights) and Ashcrown, Ch7 Tamsule Bell, Ch1 is slice-polish's.
When the PC answers the render request above: view the out/diff PNGs, approve, and write the Ch4 MERGE-READY line.
