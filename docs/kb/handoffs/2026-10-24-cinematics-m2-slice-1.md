# Handoff — cinematics — 2026-10-24 (m2-slice) #1

Session: a worktree agent of m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `worktree-agent-a66430dfde9a74656`, from `claude/m2-slice` at f129d240. Not pushed. Task: **M3-C08-02**, Ch8 "The Seawall" playable as greybox. It's now `review`, reviewer **narrative**.

## Done
- **Dialogue:** 23 `.dlg` scripts in `game/data/dialogue/ch08/`, about 620 words. They cover B01-B18, B03's side scene "The Keeping Flame", four B02 barks and the trial's hint, compiled by dlgc.
  - The speaker `ivo` is appended to `speakers.json` and `voices.json`; the other Corrow speakers are Ch9's.
  - Names, places and prompts are appended to `game/data/loc/ch08.csv`.
  - 14 new body clips are appended to `requested_clips.json` (M3-CHR-01).
- **Flow:** `game/data/flow/chapters/ch08.json` is registered between Ch7 and Ch9. Its tunables are in `game/data/flow/ch08_field.json`.
  - Ch7's `leave` beat now goes to `ch08/corrow` at `Mole`. Ch8's B18 goes to `ch09/corrow_night` at `Strand`.
- **The stair meter** (the combat-14 handoff's "For M3-C08-02"):
  - A battle step takes `objective_flag`. ZoneStory puts it on the request with its current value (`BattleRequest.objective_flag` / `objective_start`).
  - After a win or a scripted escape, `FieldBattle` sets the flag to start + `engine.objective_count`. "Fight again" puts it back to start.
  - `tools/chapter_flow_check.py` accepts the key and checks the flag is declared.
- **Zones:**
  - `game/levels/ch08/corrow/` (`Ch08Zone`): day, storm and aftermath by flag `states` and `lights`.
  - `game/levels/ch08/coilspire/` (`Ch08CoilspireZone` + `CoilspireTrial`): the four-tier flue trial, the side flue's niche, Liss's seized key, the idle hint, and the climb kept in a numeric flag.
  - `Ch08Zone` adds the layout keys `start_hidden` and `states_when`, and `mend()`: at least half HP between waves, no MP.
- **Fights:**
  - The set piece's four, M3-CMB-01's encounters, run with the sim suites' parties. Each returns to `WallHead`, and the next arrival row mends the party, plays the beat between and opens the next fight.
  - Three new field fights on the creatures track's models: `ch08_headland_gulls` (two stormgulls), `ch08_headland_crabs` (two wallcrabs) and `ch08_flue_moths` (two flue moths). They have enemy rows, lore keys and `sim.py` suites.
- **Data rows:** 22 flags (appended), two `locations.json` rows, two F5 teleports, and a Ch8 chapter-select start. Ch8's completion flags are added to Ch9's start, and Ch9's label is updated.
- **Music stand-ins** (`sequencer.json`): `corrow_day` uses `corrow_seawall`, `coilspire_flues` uses `temple_trial`, and `undertow_reach` uses `undertows_reach_p1`.
- **Tests:**
  - `tests/integration/test_ch08_thread.gd`, six tests: the whole chapter, with the four set-piece fights in the real `FieldBattle`; the meter on "Fight again"; the trial's rules; only Liss frees the key; mend; the script rules.
  - `tools/tests/test_ch08_flow.py`, seven tests.
  - Ch7's thread test now expects the `go` to Corrow. Ch9's test messages are updated.
- **Docs:** chapter_flow.md "Ch8" (plus Ch7's exit and Ch9's entry), PLAYTEST's Ch8 section (plus Ch7 and Ch9's openings), and the task file.
- **Requests filed:**
  - M3-C08-100, combat: the needle item and the battle barks; the combat reviewer looks at the three new field suites;
  - M3-C08-101, audio;
  - M3-C08-102, environment: the kits.

## Numbers (`sim.py --check`, 1000 seeds)
| Suite | naive | role_answer | smart |
|---|---|---|---|
| `ch08_headland_gulls` (role_answer report only, as for `ch06_ridge_gulls`) | 58.7 | 73.3 | 97.9 |
| `ch08_headland_crabs` | 40.2 | 94.1 | 100.0 |
| `ch08_flue_moths` | 58.4 | 93.2 | 99.6 |

## In progress
Nothing.

## Exact next step
1. **The Lead merges this branch.**
   - Every shared-file change is an append in its own commit: `flags.tres`, speakers, `voices.json`, `ch08.csv`, `requested_clips.json`, `locations.json`, `teleports.json`, `chapter_select.json`, `enemies.json`, `encounters.json` and `targets.json`.
   - `dialogue.csv` is a dlgc output. If another chapter's branch lands first, re-run `python3 tools/dlgc.py` instead of hand-resolving it.
2. **Narrative reviews M3-C08-02.** The decisions are in the task file's Notes: the suites' parties, the lean word count, the wordless gate, and Ivo on the critical path.
3. **Combat looks at the three field suites** (M3-C08-100).

## Known issues
- **The stormgull suite is close to its edges** (naive 58.7 of a 60 ceiling; smart 97.9 of a 97 floor). Its `role_answer` is weaker than `naive`, the same flier pattern as Ch6's gulls.
- **There's no stair meter on screen** and there are no entry chips (M3-UI-100). The count is kept in `ch08_stair_groups_up`.
- **The flue trial has no visual telltale** for the right keys.
- **No smith or inn in Corrow;** the chandler is `brightwater_purser`, a stand-in.
- **The B09 autosave** is a `checkpoint` just before Wave 1, so "Return to last save" from any wave replays B08-B09 and Wave 1.
- **The greybox is flat:** the stair, the wall-head and the spire's tiers are painted slabs and rooms in a row.
- **Most music and every SFX is missing** (M3-C08-101), so the scenes warn "no music"/"no sound". Those aren't staging warnings.
- I updated no live handoff file: a worktree agent leaves that to the Lead (§7a).

## Gates (own XDG_DATA_HOME; scratch in the session scratchpad's `M3-C08-02/`)
- `validate_data`: 0 errors, 0 warnings. `taskboard --check`: OK. `dlgc --check`: 0 errors, 0 warnings.
- gdlint and gdformat are clean.
- Godot import, run twice: the second log is clean.
- Godot tests, each filter 0 failed:

  | Filter | Run |
  |---|---|
  | `ch0` | 59 |
  | `ch08` | 14 |
  | `zone_story` | 15 |
  | `chapter` | 2 |
  | `debug_overlay` | 14 |
  | `fp_thread` | 2 |
- **Skipped:**
  - coverage: nothing in `game/battle/` or `game/progression/` changed;
  - screenshots: no shot covers Ch8;
  - Blender: no Blender source touched.

## Files touched
- **Code:**
  - `game/flow/battle_request.gd`, `zone_story.gd` and `field_battle.gd`;
  - `game/levels/ch08/ch08_zone.gd`, `coilspire/coilspire_zone.gd` and `coilspire/coilspire_trial.gd`;
  - `tools/chapter_flow_check.py`.
- **Data:**
  - `game/data/dialogue/ch08/*.dlg` and `compiled/ch08_*.json`, plus `speakers.json`;
  - `game/data/flow/chapters/ch07.json`, `ch08.json`, `ch09.json` (its doc), `chapters.json` and `ch08_field.json`;
  - `game/data/battle/enemies.json` and `encounters.json`, and `tools/balance/targets.json`;
  - `game/data/flags.tres`, `game/data/loc/ch08.csv` and `dialogue.csv`, `game/data/audio/voices.json`;
  - `game/data/world/locations.json`, `game/data/debug/teleports.json` and `chapter_select.json`, `game/data/cutscene/sequencer.json`;
  - `assets_src/characters/requested_clips.json`.
- **Levels:** `game/levels/ch08/corrow/{corrow.tscn,corrow_layout.json}` and `game/levels/ch08/coilspire/{coilspire.tscn,coilspire_layout.json}`.
- **Tests:** `tests/integration/test_ch08_thread.gd` (new), `test_ch07_thread.gd`, `test_ch09_thread.gd`, and `tools/tests/test_ch08_flow.py` (new).
- **Docs:**
  - `docs/PLAYTEST.md` and `docs/kb/tech/chapter_flow.md`;
  - the tasks M3-C08-02, M3-C08-100, M3-C08-101 and M3-C08-102;
  - this handoff.
