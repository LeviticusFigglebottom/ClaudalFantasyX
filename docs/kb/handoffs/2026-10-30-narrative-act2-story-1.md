# Handoff — narrative (Act II story track, on claude/act2-plan) — 2026-10-30 #1
## Done
- ADR 0204 applied to all seven beat-sheet drafts.
- The consistency pass: `docs/kb/plan/act2_consistency.md`, about 90 rows, with a by-owner routing table.
- Paste-ready ownership and SESSION-BRIEFS rows in `docs/kb/plan/act2_tracks.md` §3 and §4.
- ADR 0205 (the story track starts now):
  - **every Act II script, Ch10–Ch16:** about 135 `.dlg` scenes in `game/data/dialogue/ch1[0-6]/`, compiled, with `dialogue.csv`;
  - **new speakers:** `owa`, `kirru`, `kirru_child`, `tobin`, `merel`, `malcor_venn`, `brannoc_hale`, `hull_captain`, `aldous_varrow`, `hull_widow`, `ullari`, `ullari_woman`, `householder`, `kesh`, each with a `CHAR_*` loc row and a `voices.json` row (audio to tune);
  - about 60 story flags;
  - 12 codex people;
  - `tests/unit/test_act2_dialogue.gd`.
- Tasks: M4-A2P-001…008 and M4-C10…C16-01 are all in review.
## In progress
- Nothing.
## Exact next step
- Act on review notes from cinematics (all chapters), the Lead (Ch14–Ch16) and ui-menus (008).
- Then help the owners close the requests in `live/act2-plan.md`:
  - hold_input prompt rows;
  - the encounter ids the scripts hand off to;
  - grade ids and a sideways drift in `cues.json`;
  - the farewell-tide's "Release" prompt.
## Known issues
- **Pre-existing Act I red:** `test_dialogue_box::test_every_act1_speaker_with_a_model_has_a_portrait` (Pell has no portrait). It's a LEAD-ASK, owned by ui-menus or characters.
- **Pre-existing Godot start warning:** "Invalid UTF-8 leading byte (a7)". No text file under game/ or tests/ is invalid.
- The scripts use no `grade=` and no held-light drift until `cues.json` gains Act II values.
## Files touched
- `game/data/dialogue/ch1[0-6]/**`, `game/data/dialogue/compiled/ch1*`, `game/data/dialogue/speakers.json`
- `game/data/loc/{dialogue,ch10,ch12,ch13,ch14,ch15,ch16,codex}.csv`
- `game/data/audio/voices.json`, `game/data/flags.tres`, `game/data/lore/codex.json`
- `tests/unit/test_act2_dialogue.gd`
- `docs/kb/story/beats/act2_ch1*.md`, `docs/kb/plan/*`, `docs/kb/tasks/M4/*`, `tools/banned_terms.txt` (Farplane)
