# Handoff: first-playable-1 (2026-10-23)

Session: session_01ELR13ohWMPrprcpcgLa7UR, branch `claude/first-playable`. Tasks M2-FP-01..04 are all in `review`.

## Done
- **M2-FP-01 Cutscene sequencer** (`game/cutscene/`, `docs/kb/tech/cutscenes.md`). Plays `.dlg` cues on a `CutsceneStage`:
  - the camera, through the field_camera.md contract (an await on every move, then an `is_leaving()` check);
  - waits, fades, letterbox and marks;
  - look-ats and `clip_marks` placeholders;
  - placeholder motes and stand-in music;
  - the dialogue box and a choice menu.

  It holds the autosave and freezes the player for the whole scene. E advances lines too. 11 unit tests.
- **M2-FP-02 Playable Haluna** (`game/levels/ch02/haluna/`, built in a worktree). It instances the mood scene unedited and adds:
  - runtime collision;
  - Rhen;
  - camera volumes plus a hub orbit;
  - spawns;
  - three villagers with bark `.dlg`s;
  - the tideline battle and causeway-head triggers;
  - Cutscene A's stage.

  The `locations.json` `ch02/haluna` row is now playable.
- **M2-FP-03 Flow** (`game/flow/`, `game/levels/prologue/`, `docs/kb/tech/first_playable_flow.md`, built in a worktree):
  - New Game goes to the prologue;
  - BattleRequest/FieldBattle extends the sandbox, unedited, and returns to the field;
  - the `ch02_tideline` encounter;
  - the end card.
- **M2-FP-04 Integration**:
  - `HalunaStory` (`game/flow/haluna_story.gd`): arrival cutscene, barks, battle and ending;
  - a placeholder Shell Shrine set for Cutscene B (`game/levels/ch03/first_verse/`);
  - `tests/integration/test_fp_thread.gd` (the whole thread);
  - `docs/PLAYTEST.md`.

## Verified
`tools/ci_local.sh` is green with 974 tests (`HYMN_SHOTS=boot_title`, Blender skipped: no asset changes). A real-runtime smoke run passed through the actual SceneRouter with Enter mashed: prologue → Haluna → Cutscene A → battle → back → causeway → Cutscene B → end card → title, with no script errors.

## Known issues
- Entering Haluna has one ~1.5 s frame under the fade (mood dressing plus collision build). SceneRouter warns that it is over budget.
- Cutscene B's closing `start_battle drownbell` goes to the end card, because the Drownbell does not exist yet.
- Music uses stand-ins (sequencer.json `music_stand_ins`). `@face` and `@anim` are placeholders, and Asha has no clips, so she holds her rest pose.
- `tools/validate_data.py` (Systems-owned) got a `place_at` player-detection fix from FP-03.
- M1-ENV-06 is effectively done, except that the shrine stays inside the mood scene (not ours to edit).

## Exact next step
The Lead merges `claude/first-playable` into the integration branch with the full screenshot manifest, then hands docs/PLAYTEST.md to the human.

## Files touched
- `game/cutscene/**`, `game/flow/**`, `game/levels/{ch02,ch03,prologue}/**`
- `game/data/{cutscene,flow}/**`, `game/data/dialogue/{ch02,prologue,test}/` (new `.dlg` files, compiled)
- Shared (appended only): `game/data/loc/*.csv`, `game/data/dialogue/speakers.json`, `game/data/flags.tres`, `game/data/world/locations.json`, `game/data/battle/encounters.json`
- `tools/validate_data.py` and its test
- tests, `docs/kb/tech/{cutscenes,first_playable_flow}.md`, `docs/kb/tasks/M2/M2-FP-*`, `docs/kb/ownership.md`, `docs/PLAYTEST.md`
